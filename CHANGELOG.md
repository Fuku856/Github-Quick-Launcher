# Changelog

## [5.1.0](https://github.com/Fuku856/Github-Quick-Launcher/compare/v5.0.0...v5.1.0) (2026-11-11)


### Features

* cache lists for six hours and refresh early on a miss ([1232bce](https://github.com/Fuku856/Github-Quick-Launcher/commit/1232bce2059f1488dd2b03872c387caba559d017))
* keep queries, avatars and cached lists private by default ([f45b0f2](https://github.com/Fuku856/Github-Quick-Launcher/commit/f45b0f2105bf2d9202e989f850328fdab09ba3f4))
* rename the plugin to Github Launcher ([0cc6022](https://github.com/Fuku856/Github-Quick-Launcher/commit/0cc602201d93bb5521c805ad201462af8a977b7c))
* show settings and results in Japanese ([0b70413](https://github.com/Fuku856/Github-Quick-Launcher/commit/0b7041349a7aba28a0d1e5cafc3282af3955a193))


### Bug Fixes

* revalidate every page of a repository list, not just the first ([3735392](https://github.com/Fuku856/Github-Quick-Launcher/commit/3735392da8f31e8484f4812b30df6a21fd3443f2))


### Performance Improvements

* build context menus lazily and cap results per query ([5d79b29](https://github.com/Fuku856/Github-Quick-Launcher/commit/5d79b297d168a98cc684021f3526bc4af6fd8576))
* replace httpx with a small standard-library client ([7481abc](https://github.com/Fuku856/Github-Quick-Launcher/commit/7481abc3f310053eaf645df227f44b1cd7dd1dbd))

## [5.0.0](https://github.com/Garulf/Github-Quick-Launcher/compare/v4.0.0...v5.0.0) (2026-09-19)


### ⚠ BREAKING CHANGES

* restructure as a python_v2 package

### Features

* add username and token identities for repository lists ([ec1e20f](https://github.com/Garulf/Github-Quick-Launcher/commit/ec1e20fbb2d72c8efd21cb99627b6b3049fdcc41))
* answer queries from the persistent v2 process ([588bed7](https://github.com/Garulf/Github-Quick-Launcher/commit/588bed7e7de56dabd49128bd2211499e509eb861))
* replace PyGithub with a small async REST client ([e5ac546](https://github.com/Garulf/Github-Quick-Launcher/commit/e5ac5468b81dc40e1e03a88d47dc479382c9c3e2))
* restructure as a python_v2 package ([e8dd03a](https://github.com/Garulf/Github-Quick-Launcher/commit/e8dd03a1d226a13fa0e7479e2f9eeef027eeff0f))
* route a bare slash to the configured account ([af2f269](https://github.com/Garulf/Github-Quick-Launcher/commit/af2f26934d0dd327d8b5fd7f3f29783dc1ff0449))
* serve repositories from a stale-while-revalidate cache ([43a37a5](https://github.com/Garulf/Github-Quick-Launcher/commit/43a37a5324094882e163d329d7a9573f2b6ae1d2))


### Bug Fixes

* accept only valid GitHub logins as the username ([a7b0314](https://github.com/Garulf/Github-Quick-Launcher/commit/a7b031441e337364ad7d82b60dc0d0230ea991f9))
* answer global search without waiting on the repo list ([1812d84](https://github.com/Garulf/Github-Quick-Launcher/commit/1812d84800f3bb09471f54c8ce6883d43f6b150b))
* cap repository pagination and honour Retry-After ([fe4b6e9](https://github.com/Garulf/Github-Quick-Launcher/commit/fe4b6e90c3dbdbd8c2c2cccc01b589314ddc9f7e))
* clean up temporary render files when a screenshot fails ([faf33f5](https://github.com/Garulf/Github-Quick-Launcher/commit/faf33f573e87d5b8517dfc755994e3deccd1607f))
* record unexpected refresh failures instead of losing them ([f74863d](https://github.com/Garulf/Github-Quick-Launcher/commit/f74863d4d8dd469bb9b3cbb10290ff4fec62ebd7))
* render dark and light screenshots from per-theme configs ([39e4ed0](https://github.com/Garulf/Github-Quick-Launcher/commit/39e4ed0e6cfb2957b098f77d4291652d026fc525))
* report refresh problems honestly and tighten CI permissions ([4f2954a](https://github.com/Garulf/Github-Quick-Launcher/commit/4f2954aa30eca3388e6dc9369fe860734a173cab))
* resolve release dependencies for the declared Python floor ([d3a3e47](https://github.com/Garulf/Github-Quick-Launcher/commit/d3a3e47c4084359a438c9418f343560e207edfab))
* retire the old GitHub client gracefully when settings change ([73022b1](https://github.com/Garulf/Github-Quick-Launcher/commit/73022b1b24d96f827529f779e0bbbd551fec137d))
* stop retrying the repo list on every keystroke after a failure ([5e870f0](https://github.com/Garulf/Github-Quick-Launcher/commit/5e870f0a4c299bb359e7a9e76a4b285a10009815))
