from __future__ import annotations

import gzip
import http.client
import json
from typing import Any, Dict, List, Optional, Tuple, Union

import pytest

from github_quick_launcher import client as client_module
from github_quick_launcher.client import (
    MAX_PAGES, BadCredentials, GitHubClient, GitHubError, HttpClient, NotFound, Offline,
    RateLimited, Repo, build_http,
)

API = "https://api.github.com"
FIRST_PAGE = "/user/repos?per_page=100&sort=updated"


def api_repo(full_name: str) -> dict:
    owner = full_name.split("/")[0]
    return {
        "full_name": full_name,
        "description": None,
        "html_url": f"https://github.com/{full_name}",
        "owner": {"avatar_url": f"https://avatars.example/{owner}"},
    }


Reply = Union[Tuple[int, Dict[str, str], Any], BaseException]


class FakeRaw:

    def __init__(self, status: int, headers: Dict[str, str], body: bytes) -> None:
        self.status = status
        self._headers = headers
        self._body = body
        self.will_close = headers.get("Connection", "").lower() == "close"

    def getheaders(self) -> List[Tuple[str, str]]:
        return list(self._headers.items())

    def read(self) -> bytes:
        return self._body


class FakeServer:
    """Answers requests by target; a reply may be reused if marked so."""

    def __init__(self) -> None:
        self.routes: Dict[str, List[Reply]] = {}
        self.reusable: Dict[str, Reply] = {}
        self.requests: List[Tuple[str, Dict[str, str]]] = []
        self.connections: List["FakeConnection"] = []

    def add(self, target: str, status: int = 200, json_body: Any = None,
            headers: Optional[Dict[str, str]] = None, body: Optional[bytes] = None,
            reusable: bool = False) -> None:
        if body is None:
            body = b"" if json_body is None else json.dumps(json_body).encode()
        reply: Reply = (status, headers or {}, body)
        if reusable:
            self.reusable[target] = reply
        else:
            self.routes.setdefault(target, []).append(reply)

    def fail(self, target: str, exc: BaseException) -> None:
        self.routes.setdefault(target, []).append(exc)

    def connect(self) -> "FakeConnection":
        connection = FakeConnection(self)
        self.connections.append(connection)
        return connection


class FakeConnection:

    def __init__(self, server: FakeServer) -> None:
        self.server = server
        self.closed = False
        self._pending: Optional[Reply] = None

    def request(self, method: str, target: str, headers: Dict[str, str]) -> None:
        assert method == "GET"
        self.server.requests.append((target, headers))
        queue = self.server.routes.get(target)
        if queue:
            self._pending = queue.pop(0)
        elif target in self.server.reusable:
            self._pending = self.server.reusable[target]
        else:
            raise AssertionError(f"unexpected request {target}")

    def getresponse(self) -> FakeRaw:
        reply = self._pending
        assert reply is not None
        if isinstance(reply, BaseException):
            raise reply
        status, headers, body = reply
        return FakeRaw(status, headers, body)

    def close(self) -> None:
        self.closed = True


@pytest.fixture
def server() -> FakeServer:
    return FakeServer()


@pytest.fixture
async def client(server):
    http = HttpClient(build_http("").headers, connect=server.connect)  # type: ignore[arg-type]
    github = GitHubClient(http)
    yield github
    await github.aclose()


def test_build_http_sends_bearer_token_only_when_set():
    assert "Authorization" not in build_http("").headers
    assert build_http("abc").headers["Authorization"] == "Bearer abc"


async def test_list_repos_follows_pagination(client, server):
    second_page = f"{API}/user/repos?per_page=100&sort=updated&page=2"
    server.add(FIRST_PAGE, json_body=[api_repo("me/one")],
               headers={"ETag": '"v1"', "Link": f'<{second_page}>; rel="next"'})
    server.add("/user/repos?per_page=100&sort=updated&page=2", json_body=[api_repo("me/two")])

    listing = await client.list_repos("/user/repos")

    assert [repo.full_name for repo in listing.repos] == ["me/one", "me/two"]
    assert listing.etag == '"v1"'
    assert listing.repos[0] == Repo(
        "me/one", "", "https://github.com/me/one", "https://avatars.example/me")


async def test_list_repos_stops_following_pages_at_the_cap(client, server):
    next_page = "/user/repos?per_page=100&sort=updated&page=2"
    link = {"Link": f'<{API}{next_page}>; rel="next"'}
    server.add(FIRST_PAGE, json_body=[api_repo("me/one")], headers=link)
    server.add(next_page, json_body=[api_repo("me/two")], headers=link, reusable=True)

    listing = await client.list_repos("/user/repos")

    assert len(server.requests) == MAX_PAGES
    assert len(listing.repos) == MAX_PAGES


async def test_pagination_never_leaves_the_api_host(client, server):
    server.add(FIRST_PAGE, json_body=[api_repo("me/one")],
               headers={"Link": '<https://evil.example/steal?page=2>; rel="next"'})

    with pytest.raises(GitHubError):
        await client.list_repos("/user/repos")
    assert len(server.requests) == 1


async def test_retry_after_becomes_a_rate_limit(client, server, monkeypatch):
    monkeypatch.setattr(client_module, "_now", lambda: 5000.0)
    server.add(FIRST_PAGE, status=403, headers={"Retry-After": "120"})
    with pytest.raises(RateLimited) as raised:
        await client.list_repos("/user/repos")
    assert raised.value.reset_at == 5000 + 120


async def test_list_repos_sends_etag_and_reports_not_modified(client, server):
    # GitHub keeps Content-Encoding on a 304 even though there is no body.
    server.add(FIRST_PAGE, status=304, headers={"Content-Encoding": "gzip"})

    listing = await client.list_repos("/user/repos", etag='"v1"')

    assert listing.repos is None
    assert listing.etag == '"v1"'
    assert server.requests[0][1]["If-None-Match"] == '"v1"'


async def test_search_returns_limited_items(client, server):
    server.add("/search/repositories?q=user%3Agarulf+flow&per_page=15",
               json_body={"items": [api_repo("garulf/flow")]})
    repos = await client.search("user:garulf flow")
    assert [repo.full_name for repo in repos] == ["garulf/flow"]


async def test_gzip_bodies_are_decoded_and_requested(client, server):
    body = gzip.compress(json.dumps({"items": [api_repo("me/zip")]}).encode())
    server.add("/search/repositories?q=zip&per_page=15", body=body,
               headers={"Content-Encoding": "gzip"})

    repos = await client.search("zip")

    assert [repo.full_name for repo in repos] == ["me/zip"]
    assert server.requests[0][1]["Accept-Encoding"] == "gzip"


async def test_connection_is_kept_alive_between_requests(client, server):
    server.add("/search/repositories?q=a&per_page=15", json_body={"items": []}, reusable=True)

    for _ in range(3):
        await client.search("a")

    assert len(server.connections) == 1


async def test_a_stale_keep_alive_connection_is_retried_once(client, server):
    target = "/search/repositories?q=a&per_page=15"
    server.add(target, json_body={"items": []})
    await client.search("a")
    server.fail(target, http.client.RemoteDisconnected("idle timeout"))
    server.add(target, json_body={"items": [api_repo("me/again")]})

    repos = await client.search("a")

    assert [repo.full_name for repo in repos] == ["me/again"]
    assert server.connections[0].closed is True
    assert len(server.connections) == 2


async def test_401_raises_bad_credentials(client, server):
    server.add(FIRST_PAGE, status=401)
    with pytest.raises(BadCredentials):
        await client.list_repos("/user/repos")


async def test_exhausted_rate_limit_raises_rate_limited(client, server):
    server.add(FIRST_PAGE, status=403,
               headers={"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "1700000000"})
    with pytest.raises(RateLimited) as raised:
        await client.list_repos("/user/repos")
    assert raised.value.reset_at == 1700000000


async def test_404_raises_not_found(client, server):
    server.add("/users/ghost/repos?per_page=100&sort=updated", status=404)
    with pytest.raises(NotFound):
        await client.list_repos("/users/ghost/repos")


async def test_transport_failure_raises_offline(client, server):
    server.fail(FIRST_PAGE, ConnectionRefusedError("no route"))
    with pytest.raises(Offline):
        await client.list_repos("/user/repos")


async def test_non_json_body_is_a_github_error(client, server):
    server.add(FIRST_PAGE, body=b"<html>oops</html>")
    with pytest.raises(GitHubError):
        await client.list_repos("/user/repos")


async def test_closed_client_refuses_requests(server):
    http = HttpClient({}, connect=server.connect)  # type: ignore[arg-type]
    await http.aclose()
    with pytest.raises(Offline):
        await http.get("/user/repos")
