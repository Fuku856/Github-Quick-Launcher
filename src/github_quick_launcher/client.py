from __future__ import annotations

import asyncio
import http.client
import json
import re
import ssl
import threading
import time
import zlib
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Mapping, Optional
from urllib.parse import urlencode

API_HOST = "api.github.com"
API_URL = f"https://{API_HOST}"
PER_PAGE = 100
MAX_PAGES = 10
SEARCH_LIMIT = 15
TIMEOUT_SECONDS = 10.0
# Enough for a background refresh and a search to run side by side; each
# worker keeps its own keep-alive connection, so typing reuses a warm one.
MAX_CONNECTIONS = 3

_now = time.time

_LINK_RE = re.compile(r'<([^>]+)>\s*;\s*rel="([^"]+)"')


class GitHubError(Exception):
    pass


class BadCredentials(GitHubError):
    pass


class NotFound(GitHubError):
    pass


class Offline(GitHubError):
    pass


class RateLimited(GitHubError):

    def __init__(self, reset_at: int) -> None:
        super().__init__("GitHub API rate limit exhausted")
        self.reset_at = reset_at


@dataclass(frozen=True)
class Repo:
    full_name: str
    description: str
    html_url: str
    avatar_url: str

    @classmethod
    def from_api(cls, item: Mapping[str, Any]) -> Repo:
        return cls(
            full_name=item["full_name"],
            description=item.get("description") or "",
            html_url=item["html_url"],
            avatar_url=(item.get("owner") or {}).get("avatar_url") or "",
        )


@dataclass(frozen=True)
class Listing:
    repos: Optional[List[Repo]]
    etag: Optional[str]


@dataclass
class Response:
    status_code: int
    headers: Dict[str, str] = field(default_factory=dict)
    body: bytes = b""

    def header(self, name: str) -> Optional[str]:
        return self.headers.get(name.lower())

    def json(self) -> Any:
        return json.loads(self.body.decode("utf-8"))

    @property
    def links(self) -> Dict[str, str]:
        return {rel: url for url, rel in _LINK_RE.findall(self.header("Link") or "")}


def _decode(body: bytes, encoding: Optional[str]) -> bytes:
    # A 304 carries GitHub's Content-Encoding header but no body at all.
    if not body:
        return body
    encoding = (encoding or "").strip().lower()
    if encoding == "gzip":
        return zlib.decompress(body, 16 + zlib.MAX_WBITS)
    if encoding == "deflate":
        return zlib.decompress(body)
    return body


ConnectionFactory = Callable[[], http.client.HTTPConnection]


def _https_factory() -> ConnectionFactory:
    # The default context uses the Windows certificate store, so corporate
    # roots work and no CA bundle has to ship with the plugin.
    context = ssl.create_default_context()

    def connect() -> http.client.HTTPConnection:
        return http.client.HTTPSConnection(API_HOST, timeout=TIMEOUT_SECONDS, context=context)
    return connect


class HttpClient:
    """A tiny GET-only client for api.github.com built on the standard library.

    Requests run on a small thread pool; each worker thread holds one
    keep-alive connection. Only the GitHub API host is ever contacted, so
    the token cannot follow a pagination link anywhere else.
    """

    def __init__(
        self, headers: Mapping[str, str], connect: Optional[ConnectionFactory] = None,
    ) -> None:
        self.headers: Dict[str, str] = dict(headers)
        self._connect = connect or _https_factory()
        self._executor = ThreadPoolExecutor(
            max_workers=MAX_CONNECTIONS, thread_name_prefix="github-http")
        self._local = threading.local()
        self._lock = threading.Lock()
        self._connections: List[http.client.HTTPConnection] = []
        self._closed = False

    async def get(
        self, url: str, params: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Response:
        if self._closed:
            raise Offline("client is closed")
        target = _target(url, params)
        merged = {**self.headers, **(headers or {})}
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, self._request, target, merged)

    def _connection(self) -> http.client.HTTPConnection:
        connection = getattr(self._local, "connection", None)
        if connection is None:
            connection = self._connect()
            self._local.connection = connection
            with self._lock:
                self._connections.append(connection)
        return connection

    def _drop(self) -> None:
        connection = getattr(self._local, "connection", None)
        self._local.connection = None
        if connection is not None:
            connection.close()
            with self._lock:
                if connection in self._connections:
                    self._connections.remove(connection)

    def _request(self, target: str, headers: Mapping[str, str]) -> Response:
        if self._closed:
            raise Offline("client is closed")
        for attempt in (1, 2):
            reused = getattr(self._local, "connection", None) is not None
            connection = self._connection()
            try:
                connection.request("GET", target, headers=dict(headers))
                raw = connection.getresponse()
                body = raw.read()
            except (http.client.RemoteDisconnected, ConnectionResetError, BrokenPipeError) as exc:
                self._drop()
                # GitHub closes idle keep-alive connections; one retry on a
                # fresh connection is safe because every request is a GET.
                if reused and attempt == 1:
                    continue
                raise Offline(str(exc) or type(exc).__name__) from exc
            except (OSError, http.client.HTTPException) as exc:
                self._drop()
                raise Offline(str(exc) or type(exc).__name__) from exc
            response_headers = {name.lower(): value for name, value in raw.getheaders()}
            if raw.will_close:
                self._drop()
            try:
                body = _decode(body, response_headers.get("content-encoding"))
            except zlib.error as exc:
                raise GitHubError("GitHub sent a response that could not be decoded") from exc
            return Response(raw.status, response_headers, body)
        raise Offline("connection closed")  # pragma: no cover - loop always returns

    def _close_all(self) -> None:
        with self._lock:
            connections, self._connections = self._connections, []
        for connection in connections:
            connection.close()

    async def aclose(self) -> None:
        self._closed = True
        self._close_all()
        self._executor.shutdown(wait=False)


def _target(url: str, params: Optional[Mapping[str, Any]]) -> str:
    if url.startswith(API_URL + "/"):
        url = url[len(API_URL):]
    elif not url.startswith("/"):
        raise GitHubError("Refusing to send a request outside the GitHub API")
    if params:
        url += ("&" if "?" in url else "?") + urlencode(params)
    return url


def build_http(token: str) -> HttpClient:
    headers = {
        "Accept": "application/vnd.github+json",
        "Accept-Encoding": "gzip",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "Github-Quick-Launcher",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return HttpClient(headers)


def _raise_for_status(response: Response) -> None:
    status = response.status_code
    if status < 400:
        return
    if status == 401:
        raise BadCredentials("GitHub rejected the token")
    if status == 404:
        raise NotFound("GitHub has no such user or repository list")
    if status in (403, 429):
        if response.header("X-RateLimit-Remaining") == "0":
            raise RateLimited(int(response.header("X-RateLimit-Reset") or "0"))
        retry_after = _retry_after_seconds(response)
        if retry_after is not None:
            raise RateLimited(int(_now()) + retry_after)
    raise GitHubError(f"GitHub returned HTTP {status}")


def _retry_after_seconds(response: Response) -> Optional[int]:
    header = response.header("Retry-After")
    if header is None:
        return None
    try:
        return max(0, int(header.strip()))
    except ValueError:
        return None


class GitHubClient:

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def _get(
        self, url: str, params: Optional[Mapping[str, Any]] = None, etag: Optional[str] = None,
    ) -> Response:
        headers = {"If-None-Match": etag} if etag else {}
        response = await self._http.get(url, params=params, headers=headers)
        _raise_for_status(response)
        return response

    def _parse(self, response: Response) -> Any:
        try:
            return response.json()
        except ValueError as exc:
            raise GitHubError("GitHub sent a response that is not JSON") from exc

    async def list_repos(self, path: str, etag: Optional[str] = None) -> Listing:
        response = await self._get(path, {"per_page": PER_PAGE, "sort": "updated"}, etag)
        if response.status_code == 304:
            return Listing(None, etag)
        fresh_etag = response.header("ETag")
        repos = [Repo.from_api(item) for item in self._parse(response)]
        pages = 1
        while "next" in response.links and pages < MAX_PAGES:
            response = await self._get(response.links["next"])
            repos.extend(Repo.from_api(item) for item in self._parse(response))
            pages += 1
        return Listing(repos, fresh_etag)

    async def search(self, q: str, limit: int = SEARCH_LIMIT) -> List[Repo]:
        response = await self._get("/search/repositories", {"q": q, "per_page": limit})
        return [Repo.from_api(item) for item in self._parse(response)["items"]]

    async def aclose(self) -> None:
        await self._http.aclose()
