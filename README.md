# Github Launcher

Quickly access your GitHub repositories and stars from Flow Launcher, with privacy-friendly defaults and a small, fast footprint.

[![CI](https://img.shields.io/github/actions/workflow/status/Fuku856/Github-Quick-Launcher/ci.yml)](https://github.com/Fuku856/Github-Quick-Launcher/actions/workflows/ci.yml) [![Release](https://img.shields.io/github/v/release/Fuku856/Github-Quick-Launcher)](https://github.com/Fuku856/Github-Quick-Launcher/releases/latest)

## Screenshots

![Searching all of GitHub](docs/screenshots/search-light.png#gh-light-mode-only)![Searching all of GitHub](docs/screenshots/search-dark.png#gh-dark-mode-only)

## Install

1. Download `Github-Quick-Launcher-<version>.zip` from the [latest release](https://github.com/Fuku856/Github-Quick-Launcher/releases/latest).
2. Extract it into a new folder under `%APPDATA%\FlowLauncher\Plugins`.
3. Restart Flow Launcher.

Once the plugin is listed in Flow Launcher's plugin store, `pm install github launcher` installs it, and Flow Launcher keeps it up to date. `pm install github quick launcher` installs the original plugin instead; this one has its own name and plugin ID, so the two never replace each other.

## Usage

The default action keyword is `gr`.

| Query | What it does |
| --- | --- |
| `gr flow launcher` | Search all of GitHub once you have typed three characters. Your own matching repositories are listed first. |
| `gr /` | List your repositories, most recently updated first. |
| `gr /dot` | Filter your repositories. |
| `gr *` or `gr *py` | List or filter your starred repositories. |
| `gr torvalds/` or `gr torvalds/lin` | Search another user's repositories. |
| `gr !refresh` | Fetch your repositories and stars again right now. |
| `gr !clear` | Delete the repository lists cached on this PC. |

### Your repositories

![A bare slash lists your own repositories](docs/screenshots/own-light.png#gh-light-mode-only)![A bare slash lists your own repositories](docs/screenshots/own-dark.png#gh-dark-mode-only)

`/` needs to know who you are. Set either option in the plugin settings:

| Setting | Default | Description |
| --- | --- | --- |
| GitHub username | empty | Lists that account's public repositories and stars. No token needed. |
| Personal access token | empty | Adds private repositories and raises the API rate limit. Prefer a fine-grained token with an expiry and read-only *Metadata* access; a classic token needs no scopes, plus `read:org` for organization repositories. |
| Cache lifetime (minutes) | 360 | How long the repository and star lists are reused before they are refreshed in the background. A filter that matches nothing, or a search that finds one of your repositories missing from the list, refreshes it early (at most once a minute). |
| Search all of GitHub as you type | on | Off keeps every query on this PC: only your cached repositories are searched. |
| Show owner avatars | on | Off shows the plugin icon instead of loading avatars from GitHub. |

### Stars

![Filtering starred repositories](docs/screenshots/stars-light.png#gh-light-mode-only)![Filtering starred repositories](docs/screenshots/stars-dark.png#gh-dark-mode-only)

### Another user's repositories

![Searching a user by name](docs/screenshots/user-light.png#gh-light-mode-only)![Searching a user by name](docs/screenshots/user-dark.png#gh-dark-mode-only)

### Context menu

Press Shift+Enter or right-click a repository to open it in GitHub Desktop or VS Code, or to copy its name, URL, or a clone command.

![Repository context menu](docs/screenshots/context-light.png#gh-light-mode-only)![Repository context menu](docs/screenshots/context-dark.png#gh-dark-mode-only)

## Speed

The first `/` or `*` after you set your username waits for GitHub. After that sync, your repositories and stars are kept in memory and on disk, so both answer from the local copy, even right after Flow Launcher starts. The list refreshes in the background once it is older than the cache lifetime, using conditional requests that do not count against GitHub's rate limit when nothing changed. Because GitHub marks a list as changed whenever any repository in it is pushed to, the lifetime is long; when a filter finds nothing, the plugin asks GitHub right away and waits up to three seconds for a fresh list.

## Privacy

The plugin talks only to GitHub and sends no telemetry.

- **Queries.** Filtering `/` and `*` runs locally. A global query is sent to GitHub's search API only after three characters and a short pause in typing, and never when *Search all of GitHub as you type* is off. With a token set, GitHub sees these searches as yours.
- **Avatars.** Owner avatars are loaded from `avatars.githubusercontent.com`, resized to what your display needs. Turn *Show owner avatars* off to load no images.
- **Cache.** Your repository and star lists are stored under `%APPDATA%\FlowLauncher\Settings\Plugins\Github Launcher\cache`. Lists fetched with a token include private repository names. They are deleted when you change or remove the username or token, and `gr !clear` deletes them at any time.
- **Token.** Flow Launcher stores plugin settings, including the token, unencrypted in its settings folder. The plugin masks tokens in its own log.

## Contributing

Issues and pull requests are welcome at [Fuku856/Github-Quick-Launcher](https://github.com/Fuku856/Github-Quick-Launcher).

Screenshots are re-rendered with `docs/screenshots/render.sh` from the repo root.

## License

MIT

## Credits

This plugin is based on [Garulf/Github-Quick-Launcher](https://github.com/Garulf/Github-Quick-Launcher) by [Garulf](https://github.com/Garulf), used under the MIT License. Thanks to Garulf for the original plugin and its design.

What changed in this version: lazy context menus and capped result lists, privacy settings (local-only search, optional and downsized avatars, cache cleanup, token masking in logs), a standard-library HTTP client in place of httpx, revalidation of every page of a list, a longer cache with refresh-on-miss, and a Japanese user interface.
