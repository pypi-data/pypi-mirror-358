# Changelog

All notable changes to Xify will be documented in this file.

## v1.1.7 (2025-06-28)

### Bug Fixes

- switch main class init log to be info & add issues, changelog and pdm to project toml

## v1.1.6 (2025-06-28)

### Bug Fixes

- **release-changelog**: issues displaying changes in release description

## v1.1.5 (2025-06-28)

### Bug Fixes

- **request**: use unauthorized tag from httpstatus library instead of literal 401

## v1.1.4 (2025-06-28)

### Bug Fixes

- project not correclty uploading to pypi & changelog format

## v1.1.3 (2025-06-27)

### Fix

- set python project version and ci release workflow

## v1.1.2 (2025-06-26)

### Fix

- **pypi-publish**: automate pypi ci workflow
- **pypi-publish**: automate pypi ci workflow

## [1.1.2](https://github.com/filming/xify/compare/v1.1.1...v1.1.2) (2025-06-26)


### Fixed

* **pypi-publish:** automate pypi ci workflow ([8791b5b](https://github.com/filming/xify/commit/8791b5bb367fbaf3d200e4fbb031e584fd71a9f3))
* **pypi-publish:** automate pypi ci workflow ([8791b5b](https://github.com/filming/xify/commit/8791b5bb367fbaf3d200e4fbb031e584fd71a9f3))

## [1.1.1](https://github.com/filming/xify/compare/v1.1.0...v1.1.1) (2025-06-26)


### Fixed

* **readme:** Add clarification on script type ([c16f681](https://github.com/filming/xify/commit/c16f6818c03f1057d5e436488b7462215899fea9))
* **readme:** Add clarification on script type ([c16f681](https://github.com/filming/xify/commit/c16f6818c03f1057d5e436488b7462215899fea9))
* **readme:** Add clarification on script type ([deba0dc](https://github.com/filming/xify/commit/deba0dcbc2b87ff248d6a8598d553a6bb6d3cad8))

## [1.1.0](https://github.com/filming/xify/compare/v1.0.0...v1.1.0) (2025-06-26)


### Added

* **request:** Improve 401 authentication error message ([8385ec3](https://github.com/filming/xify/commit/8385ec3735578bc26382ad209f1680dfa2d42a1e))

## [1.0.0](https://github.com/filming/xify/compare/v0.1.0...v1.0.0) (2025-06-26)


### ⚠ BREAKING CHANGES

* **errors:** HTTP 4xx/5xx errors now raise APIError instead of RequestError. Code that previously caught RequestError for these failures must be updated to catch APIError.

### Bug Fixes

* **errors:** ensure APIError is raised with full response body ([c23093c](https://github.com/filming/xify/commit/c23093c2c503ff39d9d4b2f32fc71ceaa847e415))


### Documentation

* Add project changelog ([0dc902b](https://github.com/filming/xify/commit/0dc902b8edff969c96f37a1f8a15f8b33d55e550))
* Improve README grammar and information ([0f514ff](https://github.com/filming/xify/commit/0f514ffb6cc3fbe882e616f7d6f148e5a774df2c))

## [0.1.0] - 2025-06-25

### Added

- OAuth 1.0a authentication
- Async HTTP requests using aiohttp
- Post tweets programmatically
- Custom error handling for API and authentication issues
- Example usage script included

[0.1.0]: https://github.com/filming/xify/releases/tag/v0.1.0
