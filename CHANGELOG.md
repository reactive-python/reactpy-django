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

-   Nothing yet!

## [3.2.1] - 2023-06-29

### Added

-   Template tag exception details are now rendered on the webpage when `settings.py:DEBUG` is enabled.

### Fixed

-   Prevent exceptions within the `component` template tag from causing the whole template to fail to render.

## [3.2.0] - 2023-06-08

### Added

-   Added warning if poor system/cache/database performance is detected while in `DEBUG` mode.
-   Added `REACTPY_AUTH_BACKEND` setting to allow for custom authentication backends.

### Changed

-   Using `SessionMiddlewareStack` is now optional.
-   Using `AuthMiddlewareStack` is now optional.

## [3.1.0] - 2023-05-06

### Added

-   `use_query` now supports async functions.
-   `use_mutation` now supports async functions.
-   `reactpy_django.types.QueryOptions.thread_sensitive` option to customize how sync queries are executed.
-   `reactpy_django.hooks.use_mutation` now accepts `reactpy_django.types.MutationOptions` option to customize how mutations are executed.

### Changed

-   The `mutate` argument on `reactpy_django.hooks.use_mutation` has been renamed to `mutation`.

### Fixed

-   Fix bug where ReactPy utilizes Django's default cache timeout, which can prematurely expire the component cache.

## [3.0.1] - 2023-04-06

### Changed

-   `django-reactpy` database entries are no longer cleaned during Django application startup. Instead, it will occur on webpage loads if `REACTPY_RECONNECT_MAX` seconds has elapsed since the last cleaning.

## [3.0.0-reactpy] - 2023-03-30

### Changed

-   `django-idom` has been renamed to `reactpy-django`! Please note that all references to the word `idom` in your code should be changed to `reactpy`. See the docs for more details.

## [3.0.0] - 2023-03-08

???+ note

    This is Django-IDOM's biggest update yet!

    To upgrade from previous version you will need to...

    1. Install `django-idom >= 3.0.0`
    2. Run `idom rewrite-keys <DIR>` and `idom rewrite-camel-case-props <DIR>` to update your `idom.html.*` calls to the new syntax
    3. Run `python manage.py migrate` to create the new Django-IDOM database entries

### Added

-   The `idom` client will automatically configure itself to debug mode depending on `settings.py:DEBUG`.
-   `use_connection` hook for returning the browser's active `Connection`.
-   `IDOM_CACHE` is now configurable within `settings.py` to whatever cache name you wish.

### Changed

-   It is now mandatory to run `manage.py migrate` after installing IDOM.
-   Bumped the minimum IDOM version to 1.0.0. Due to IDOM 1.0.0, `idom.html.*`...
    -   HTML properties can now be `snake_case`. For example `className` now becomes `class_name`.
    -   `key=...` is now declared within the props `dict` (rather than as a `kwarg`).
-   The `component` template tag now supports both positional and keyword arguments.
-   The `component` template tag now supports non-serializable arguments.
-   `IDOM_WS_MAX_RECONNECT_TIMEOUT` setting has been renamed to `IDOM_RECONNECT_MAX`.

### Removed

-   `django_idom.hooks.use_websocket` has been removed. The similar replacement is `django_idom.hooks.use_connection`.
-   `django_idom.types.IdomWebsocket` has been removed. The similar replacement is `django_idom.types.Connection`.
-   `settings.py:CACHE['idom']` is no longer used by default. The name of the cache back-end must now be specified with the `IDOM_CACHE` setting.

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
-   IDOM preloader will now print out the exception stack when failing to import a module.

## [2.2.0] - 2022-12-28

### Added

-   Add `options: QueryOptions` parameter to `use_query` to allow for configuration of this hook.

### Changed

-   By default, `use_query` will recursively prefetch all many-to-many or many-to-one relationships to prevent `SynchronousOnlyOperation` exceptions.

### Removed

-   `django_idom.hooks._fetch_lazy_fields` has been deleted. The equivalent replacement is `django_idom.utils.django_query_postprocessor`.

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
-   IDOM preloader no longer attempts to parse commented out IDOM components.
-   Tests are now fully functional on Windows

## [1.2.0] - 2022-09-19

### Added

-   `auth_required` decorator to prevent your components from rendering to unauthenticated users.
-   `use_query` hook for fetching database values.
-   `use_mutation` hook for modifying database values.
-   `view_to_component` utility to convert legacy Django views to IDOM components.

### Changed

-   Bumped the minimum IDOM version to 0.40.2
-   Testing suite now uses `playwright` instead of `selenium`

### Fixed

-   IDOM preloader is no longer sensitive to whitespace within template tags.

## [1.1.0] - 2022-07-01

### Added

-   `django_css` and `django_js` components to defer loading CSS & JS files until needed.

### Changed

-   Bumped the minimum IDOM version to 0.39.0

## [1.0.0] - 2022-05-22

### Added

-   Django specific hooks! `use_websocket`, `use_scope`, and `use_location` are now available within the `django_idom.hooks` module.
-   Documentation has been placed into a formal docs webpage.
-   Logging for when a component fails to import, or if no components were found within Django.

### Changed

-   `idom_component` template tag has been renamed to `component`
-   Bumped the minimum IDOM version to 0.38.0

### Removed

-   `websocket` parameter for components has been removed. Functionally, it is replaced with `django_idom.hooks.use_websocket`.

## [0.0.5] - 2022-04-04

### Changed

-   Bumped the minimum IDOM version to 0.37.2

### Fixed

-   ModuleNotFoundError: No module named `idom.core.proto` caused by IDOM 0.37.2

## [0.0.4] - 2022-03-05

### Changed

-   Bumped the minimum IDOM version to 0.37.1

## [0.0.3] - 2022-02-19

### Changed

-   Bumped the minimum IDOM version to 0.36.3

## [0.0.2] - 2022-01-30

### Added

-   Ability to declare the HTML class of the top-level component `div`
-   `name = ...` parameter to IDOM HTTP paths for use with `django.urls.reverse()`
-   Cache versioning to automatically invalidate old web module files from the cache back-end
-   Automatic pre-population of the IDOM component registry
-   Type hinting for `IdomWebsocket`

### Changed

-   Fetching web modules from disk and/or cache is now fully async
-   Static files are now contained within a `django_idom/` parent folder
-   Upgraded IDOM to version `0.36.0`
-   Minimum Django version required is now `4.0`
-   Minimum Python version required is now `3.8`

### Removed

-   `IDOM_WEB_MODULES_PATH` has been replaced with Django `include(...)`
-   `IDOM_WS_MAX_RECONNECT_DELAY` has been renamed to `IDOM_WS_MAX_RECONNECT_TIMEOUT`
-   `idom_web_modules` cache back-end has been renamed to `idom`

### Fixed

-   Increase test timeout values to prevent false positives
-   Windows compatibility for building Django-IDOM

### Security

-   Fixed potential directory traversal attack on the IDOM web modules URL

## [0.0.1] - 2021-08-18

### Added

-   Support for IDOM within the Django

[unreleased]: https://github.com/reactive-python/reactpy-django/compare/3.2.1...HEAD
[3.2.1]: https://github.com/reactive-python/reactpy-django/compare/3.2.0...3.2.1
[3.2.0]: https://github.com/reactive-python/reactpy-django/compare/3.1.0...3.2.0
[3.1.0]: https://github.com/reactive-python/reactpy-django/compare/3.0.1...3.1.0
[3.0.1]: https://github.com/reactive-python/reactpy-django/compare/3.0.0-reactpy...3.0.1
[3.0.0-reactpy]: https://github.com/reactive-python/reactpy-django/compare/3.0.0...3.0.0-reactpy
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
