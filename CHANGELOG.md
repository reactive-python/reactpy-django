# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
Types of changes are to be listed in this order
    - "Added" for new features.
    - "Changed" for changes in existing functionality.
    - "Deprecated" for soon-to-be removed features.
    - "Removed" for now removed features.
    - "Fixed" for any bug fixes.
    - "Security" in case of vulnerabilities.
 -->

## [Unreleased]

### Changed

- Bumped the minimum IDOM client version to 0.36.3

## [0.0.2] - 2022-01-30

### Added

- Ability to declare the HTML class of the top-level component `div`
- `name = ...` parameter to IDOM HTTP paths for use with `django.urls.reverse()`
- Cache versioning to automatically invalidate old web module files from the cache backend
- Automatic pre-population of the IDOM component registry
- Type hinting for `IdomWebsocket`

### Changed

- Fetching web modules from disk and/or cache is now fully async
- Static files are now contained within a `django_idom/` parent folder
- Upgraded IDOM to version `0.36.0`
- Minimum Django version required is now `4.0`
- Minimum Python version required is now `3.8`

### Removed

- `IDOM_WEB_MODULES_PATH` has been replaced with Django `include(...)`
- `IDOM_WS_MAX_RECONNECT_DELAY` has been renamed to `IDOM_WS_MAX_RECONNECT_TIMEOUT`
- `idom_web_modules` cache backend has been renamed to `idom`

### Fixed

- Increase test timeout values to prevent false positives
- Windows compatibility for building Django-IDOM

### Security

- Fixed potential directory travesal attack on the IDOM web modules URL

## [0.0.1] - 2021-08-18

### Added

- Support for IDOM within the Django

[unreleased]: https://github.com/idom-team/django-idom/compare/0.0.2...HEAD
[0.0.2]: https://github.com/idom-team/django-idom/compare/0.0.1...0.0.2
[0.0.1]: https://github.com/idom-team/django-idom/releases/tag/0.0.1
