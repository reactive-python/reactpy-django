# Changelog

All notable changes to this project will be documented in this file.

<!--attr-start-->

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--attr-end-->

<!--
Using the following categories, list your changes in this order:

### Added
-   for new features.

### Changed
-   for changes in existing functionality.

### Deprecated
-   for soon-to-be removed features.

### Removed
-   for removed features.

### Fixed
-   for bug fixes.

### Security
-   for vulnerability fixes.
 -->

<!--changelog-start-->

## [Unreleased]

-   Nothing (yet)

## [3.0.0] - 2023-03-08

???+ note

    This is ReactPy-Django's biggest update yet!

    To upgrade from previous version you will need to...

    1. Install `reactpy-django >= 3.0.0`
    2. Run `reactpy rewrite-keys <DIR>` and `reactpy rewrite-camel-case-props <DIR>` to update your `reactpy.html.*` calls to the new syntax
    3. Run `python manage.py migrate` to create the new ReactPy-Django database entries

### Added

-   The `reactpy` client will automatically configure itself to debug mode depending on `settings.py:DEBUG`.
-   `use_connection` hook for returning the browser's active `Connection`.
-   `REACTPY_CACHE` is now configurable within `settings.py` to whatever cache name you wish.

### Changed

-   It is now mandatory to run `manage.py migrate` after installing ReactPy.
-   Bumped the minimum ReactPy version to 1.0.0. Due to ReactPy 1.0.0, `reactpy.html.*`...
    -   HTML properties can now be `snake_case`. For example `className` now becomes `class_name`.
    -   `key=...` is now declared within the props `dict` (rather than as a `kwarg`).
-   The `component` template tag now supports both positional and keyword arguments.
-   The `component` template tag now supports non-serializable arguments.
-   `REACTPY_WS_MAX_RECONNECT_TIMEOUT` setting has been renamed to `REACTPY_RECONNECT_MAX`.

### Removed

-   `reactpy_django.hooks.use_websocket` has been removed. The similar replacement is `reactpy_django.hooks.use_connection`.
-   `reactpy_django.types.ReactPyWebsocket` has been removed. The similar replacement is `reactpy_django.types.Connection`.
-   `settings.py:CACHE['reactpy']` is no longer used by default. The name of the cache backend must now be specified with the `REACTPY_CACHE` setting.

### Fixed

-   `view_to_component` will now retain the contents of a `<head>` tag when rendering.
-   React client is now set to `production` rather than `development`.
-   `use_query` will now utilize `field.related_name` when postprocessing many-to-one relationships.

### Security

-   Fixed a potential method of component template tag argument spoofing.
-   Exception information will no longer be displayed on the page, based on the value of `settings.py:DEBUG`.

## [2.2.1] - 2023-01-09

### Fixed

-   Fixed bug where `use_query` would not recursively fetch many-to-one relationships.
-   ReactPy preloader will now print out the exception stack when failing to import a module.

## [2.2.0] - 2022-12-28

### Added

-   Add `options: QueryOptions` parameter to `use_query` to allow for configuration of this hook.

### Changed

-   By default, `use_query` will recursively prefetch all many-to-many or many-to-one relationships to prevent `SynchronousOnlyOperation` exceptions.

### Removed

-   `reactpy_django.hooks._fetch_lazy_fields` has been deleted. The equivalent replacement is `reactpy_django.utils.django_query_postprocessor`.

## [2.1.0] - 2022-11-01

### Changed

-   Minimum `channels` version is now `4.0.0`.

### Fixed

-   Change type hint on `view_to_component` callable to have `request` argument be optional.
-   Change type hint on `view_to_component` to represent it as a decorator with parenthesis (such as `@view_to_component(compatibility=True)`)

### Security

-   Add note to docs about potential information exposure via `view_to_component` when using `compatibility=True`.

## [2.0.1] - 2022-10-18

### Fixed

-   Ability to use `key=...` parameter on all prefabricated components.

## [2.0.0] - 2022-10-17

### Added

-   `use_origin` hook for returning the browser's `location.origin`.

### Changed

-   `view_to_component` now returns a `Callable`, instead of directly returning a `Component`. Check the docs for new usage info.
-   `use_mutation` and `use_query` will now log any query failures.

### Fixed

-   Allow `use_mutation` to have `refetch=None`, as the docs suggest is possible.
-   `use_query` will now prefetch all fields to prevent `SynchronousOnlyOperation` exceptions.
-   `view_to_component`, `django_css`, and `django_js` type hints will now display like normal functions.
-   ReactPy preloader no longer attempts to parse commented out ReactPy components.
-   Tests are now fully functional on Windows

## [1.2.0] - 2022-09-19

### Added

-   `auth_required` decorator to prevent your components from rendering to unauthenticated users.
-   `use_query` hook for fetching database values.
-   `use_mutation` hook for modifying database values.
-   `view_to_component` utility to convert legacy Django views to ReactPy components.

### Changed

-   Bumped the minimum ReactPy version to 0.40.2
-   Testing suite now uses `playwright` instead of `selenium`

### Fixed

-   ReactPy preloader is no longer sensitive to whitespace within template tags.

## [1.1.0] - 2022-07-01

### Added

-   `django_css` and `django_js` components to defer loading CSS & JS files until needed.

### Changed

-   Bumped the minimum ReactPy version to 0.39.0

## [1.0.0] - 2022-05-22

### Added

-   Django-specific hooks! `use_websocket`, `use_scope`, and `use_location` are now available within the `reactpy_django.hooks` module.
-   Documentation has been placed into a formal docs webpage.
-   Logging for when a component fails to import, or if no components were found within Django.

### Changed

-   `reactpy_component` template tag has been renamed to `component`
-   Bumped the minimum ReactPy version to 0.38.0

### Removed

-   `websocket` parameter for components has been removed. Functionally, it is replaced with `reactpy_django.hooks.use_websocket`.

## [0.0.5] - 2022-04-04

### Changed

-   Bumped the minimum ReactPy version to 0.37.2

### Fixed

-   ModuleNotFoundError: No module named `reactpy.core.proto` caused by ReactPy 0.37.2

## [0.0.4] - 2022-03-05

### Changed

-   Bumped the minimum ReactPy version to 0.37.1

## [0.0.3] - 2022-02-19

### Changed

-   Bumped the minimum ReactPy version to 0.36.3

## [0.0.2] - 2022-01-30

### Added

-   Ability to declare the HTML class of the top-level component `div`
-   `name = ...` parameter to ReactPy HTTP paths for use with `django.urls.reverse()`
-   Cache versioning to automatically invalidate old web module files from the cache backend
-   Automatic pre-population of the ReactPy component registry
-   Type hinting for `ReactPyWebsocket`

### Changed

-   Fetching web modules from disk and/or cache is now fully async
-   Static files are now contained within a `reactpy_django/` parent folder
-   Upgraded ReactPy to version `0.36.0`
-   Minimum Django version required is now `4.0`
-   Minimum Python version required is now `3.8`

### Removed

-   `REACTPY_WEB_MODULES_PATH` has been replaced with Django `include(...)`
-   `REACTPY_WS_MAX_RECONNECT_DELAY` has been renamed to `REACTPY_WS_MAX_RECONNECT_TIMEOUT`
-   `reactpy_web_modules` cache backend has been renamed to `reactpy`

### Fixed

-   Increase test timeout values to prevent false positives
-   Windows compatibility for building ReactPy-Django

### Security

-   Fixed potential directory traversal attack on the ReactPy web modules URL

## [0.0.1] - 2021-08-18

### Added

-   Support for ReactPy within the Django

[unreleased]: https://github.com/reactive-python/reactpy-django/compare/3.0.0...HEAD
[3.0.0]: https://github.com/reactive-python/reactpy-django/compare/2.2.1...3.0.0
[2.2.1]: https://github.com/reactive-python/reactpy-django/compare/2.2.0...2.2.1
[2.2.0]: https://github.com/reactive-python/reactpy-django/compare/2.1.0...2.2.0
[2.1.0]: https://github.com/reactive-python/reactpy-django/compare/2.0.1...2.1.0
[2.0.1]: https://github.com/reactive-python/reactpy-django/compare/2.0.0...2.0.1
[2.0.0]: https://github.com/reactive-python/reactpy-django/compare/1.2.0...2.0.0
[1.2.0]: https://github.com/reactive-python/reactpy-django/compare/1.1.0...1.2.0
[1.1.0]: https://github.com/reactive-python/reactpy-django/compare/1.0.0...1.1.0
[1.0.0]: https://github.com/reactive-python/reactpy-django/compare/0.0.5...1.0.0
[0.0.5]: https://github.com/reactive-python/reactpy-django/compare/0.0.4...0.0.5
[0.0.4]: https://github.com/reactive-python/reactpy-django/compare/0.0.3...0.0.4
[0.0.3]: https://github.com/reactive-python/reactpy-django/compare/0.0.2...0.0.3
[0.0.2]: https://github.com/reactive-python/reactpy-django/compare/0.0.1...0.0.2
[0.0.1]: https://github.com/reactive-python/reactpy-django/releases/tag/0.0.1
