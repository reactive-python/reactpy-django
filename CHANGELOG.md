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

### Added

- Nothing (yet)

## [0.0.2] - 2022-01-30

### Added

- Support for declaring the HTML class of the component div via the `idom_component` tag
- `name = ...` parameter to IDOM HTTP paths for use with `django.urls.reverse()`
- Fully async method of fetching `web_modules` from disk
- Cache versioning to automatically invalidate old web module files from the cache backend
- Automatic pre-population of the IDOM component registry
- Type hinting for `IdomWebsocket`

### Changed

- Static files are now contained within a `django_idom/` parent folder
- `IDOM_WS_MAX_RECONNECT_DELAY` has been renamed to `IDOM_WS_MAX_RECONNECT_TIMEOUT`
- Upgraded IDOM to version `0.36.0`
- Minimum Django required is now `4.0`
- Minimum Python required is now `3.8`

### Removed

- `IDOM_WEB_MODULES_PATH` has been removed and replaced with Django `include(...)`
- `idom_web_modules` cache backend has been renamed to `idom`

### Fixed

- Increase test timeout values to prevent them from failing as a false positive
- Windows compatibility for building Django-IDOM

### Security

- Fixed potential directory travesal attack on the IDOM web modules URL

## [0.0.1] - 2021-08-18

### Added

- Support for IDOM within the Django

[unreleased]: https://github.com/idom-team/django-idom/compare/0.0.2...HEAD
[0.0.2]: https://github.com/idom-team/django-idom/compare/0.0.1...0.0.2
[0.0.1]: https://github.com/idom-team/django-idom/releases/tag/0.0.1
