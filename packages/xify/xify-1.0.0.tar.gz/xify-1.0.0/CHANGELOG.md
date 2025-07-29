# Changelog

All notable changes to Xify will be documented in this file.

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
