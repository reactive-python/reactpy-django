# Changelog

All notable changes to this project will be documented in this file.

<!--attr-start-->

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--attr-end-->

<!--
Using the following categories, list your changes in this order:
[Added, Changed, Deprecated, Removed, Fixed, Security]

Don't forget to remove deprecated code on each major release!
-->

<!--changelog-start-->

## [Unreleased]

### Changed

-   Updated the interface for `reactpy.hooks.use_channel_layer` to be more intuitive.
    -   Arguments now must be provided as keyworded arguments.
    -   The `name` argument has been renamed to `channel`.
    -   The `group_name` argument has been renamed to `group`.
    -   The `group_add` and `group_discard` arguments have been removed for simplicity.
-   To improve performance, `preact` is now used as the default client-side library instead of `react`.

### [5.2.1] - 2025-01-10

### Changed

-   Use the latest version of `@reactpy/client` which includes a fix for needless client-side component re-creation.

### [5.2.0] - 2024-12-29

### Added

-   User login/logout features!
    -   `reactpy_django.hooks.use_auth` to provide **persistent** `login` and `logout` functionality to your components.
    -   `settings.py:REACTPY_AUTH_TOKEN_MAX_AGE` to control the maximum seconds before ReactPy's login token expires.
    -   `settings.py:REACTPY_CLEAN_AUTH_TOKENS` to control whether ReactPy should clean up expired authentication tokens during automatic cleanups.
-   Automatically convert Django forms to ReactPy forms via the new `reactpy_django.components.django_form` component!
-   The ReactPy component tree can now be forcibly re-rendered via the new `reactpy_django.hooks.use_rerender` hook.

### Changed

-   Refactoring of internal code to improve maintainability. No changes to publicly documented API.

### Fixed

-   Fixed bug where pre-rendered components could generate a `SynchronousOnlyOperation` exception if they access a freshly logged out Django user object.

## [5.1.1] - 2024-12-02

### Fixed

-   Fixed regression from the previous release where components would sometimes not output debug messages when `settings.py:DEBUG` is enabled.

### Changed

-   Set upper limit on ReactPy version to `<2.0.0`.
-   ReactPy web modules are now streamed in chunks.
-   ReactPy web modules are now streamed using asynchronous file reading to improve performance.
-   Performed refactoring to utilize `ruff` as this repository's linter.

## [5.1.0] - 2024-11-24

### Added

-   `settings.py:REACTPY_ASYNC_RENDERING` to enable asynchronous rendering of components.

### Changed

-   Bumped the minimum ReactPy version to `1.1.0`.

## [5.0.0] - 2024-10-22

### Changed

-   Now using ReactPy-Router v1 for URL routing, which comes with a slightly different API than before.
-   Removed dependency on `aiofile`.

### Removed

-   Removed the following **deprecated** features:
    -   The `compatibility` argument on `reactpy_django.components.view_to_component`
    -   `reactpy_django.components.view_to_component` **usage as a decorator**
    -   `reactpy_django.decorators.auth_required`
    -   `reactpy_django.REACTPY_WEBSOCKET_PATH`
    -   `settings.py:REACTPY_WEBSOCKET_URL`

## [4.0.0] - 2024-06-22

### Added

-   Client-side Python components can now be rendered via the new `{% pyscript_component %}` template tag
    -   You must first call the `{% pyscript_setup %}` template tag to load PyScript dependencies
-   Client-side components can be embedded into existing server-side components via `reactpy_django.components.pyscript_component`.
-   Tired of writing JavaScript? You can now write PyScript code that runs directly within client browser via the `reactpy_django.html.pyscript` element.
    -   This is a viable substitution for most JavaScript code.

### Changed

-   New syntax for `use_query` and `use_mutation` hooks. Here's a quick comparison of the changes:

    ```python
    query = use_query(QueryOptions(thread_sensitive=True), get_items, foo="bar") # Old
    query = use_query(get_items, {"foo":"bar"}, thread_sensitive=True) # New

    mutation = use_mutation(MutationOptions(thread_sensitive=True), remove_item) # Old
    mutation = use_mutation(remove_item, thread_sensitive=True) # New
    ```

### Removed

-   `QueryOptions` and `MutationOptions` have been removed. The value contained within these objects are now passed directly into the hook.

### Fixed

-   Resolved a bug where Django-ReactPy would not properly detect `settings.py:DEBUG`.

## [3.8.1] - 2024-05-07

### Added

-   Python 3.12 compatibility

## [3.8.0] - 2024-02-20

### Added

-   Built-in cross-process communication mechanism via the `reactpy_django.hooks.use_channel_layer` hook.
-   Access to the root component's `id` via the `reactpy_django.hooks.use_root_id` hook.
-   More robust control over ReactPy clean up tasks!
    -   `settings.py:REACTPY_CLEAN_INTERVAL` to control how often ReactPy automatically performs cleaning tasks.
    -   `settings.py:REACTPY_CLEAN_SESSIONS` to control whether ReactPy should clean up expired sessions during automatic cleanups.
    -   `settings.py:REACTPY_CLEAN_USER_DATA` to control whether ReactPy should clean up orphaned user data during automatic cleanups.
    -   `python manage.py clean_reactpy` command to manually perform ReactPy clean up tasks.

### Changed

-   Simplified code for cascading deletion of user data.

## [3.7.0] - 2024-01-30

### Added

-   An "offline component" can now be displayed when the client disconnects from the server.
-   URL router now supports a `*` wildcard to create default routes.

## [3.6.0] - 2024-01-10

### Added

-   Built-in Single Page Application (SPA) support!
    -   `reactpy_django.router.django_router` can be used to render your Django application as a SPA.
-   SEO compatible rendering!
    -   `settings.py:REACTPY_PRERENDER` can be set to `True` to make components pre-render by default.
    -   Or, you can enable it on individual components via the template tag: `{% component "..." prerender="True" %}`.
-   New `view_to_iframe` feature!
    -   `reactpy_django.components.view_to_iframe` uses an `<iframe>` to render a Django view.
    -   `reactpy_django.utils.register_iframe` tells ReactPy which views `view_to_iframe` can use.
-   New Django `User` related features!
    -   `reactpy_django.hooks.use_user` can be used to access the current user.
    -   `reactpy_django.hooks.use_user_data` provides a simplified interface for storing user key-value data.
    -   `reactpy_django.decorators.user_passes_test` is inspired by the [equivalent Django decorator](http://docs.djangoproject.com/en/stable/topics/auth/default/#django.contrib.auth.decorators.user_passes_test), but ours works with ReactPy components.
    -   `settings.py:REACTPY_AUTO_RELOGIN` will cause component WebSocket connections to automatically [re-login](https://channels.readthedocs.io/en/latest/topics/authentication.html#how-to-log-a-user-in-out) users that are already authenticated. This is useful to continuously update `last_login` timestamps and refresh the [Django login session](https://docs.djangoproject.com/en/stable/topics/http/sessions/).

### Changed

-   Renamed undocumented utility function `ComponentPreloader` to `RootComponentFinder`.
-   It is now recommended to call `as_view()` when using `view_to_component` or `view_to_iframe` with Class Based Views.
-   For thread safety, `thread_sensitive=True` has been enabled in all `sync_to_async` functions where ORM queries are possible.
-   `reactpy_django.hooks.use_mutation` now has a `__call__` method. So rather than writing `my_mutation.execute(...)`, you can now write `my_mutation(...)`.

### Deprecated

-   The `compatibility` argument on `reactpy_django.components.view_to_component` is deprecated.
    -   Use `view_to_iframe` as a replacement.
-   `reactpy_django.components.view_to_component` **usage as a decorator** is deprecated.
    -   Check the docs on how to use `view_to_component` as a function instead.
-   `reactpy_django.decorators.auth_required` is deprecated.
    -   Use `reactpy_django.decorators.user_passes_test` instead.
    -   An equivalent to `auth_required`'s default is `@user_passes_test(lambda user: user.is_active)`.

### Fixed

-   Fixed a bug where exception stacks would not print on failed component renders.

## [3.5.1] - 2023-09-07

### Added

-   Warning W018 (`Suspicious position of 'reactpy_django' in INSTALLED_APPS`) has been added.

### Changed

-   The default postprocessor can now disabled by setting `REACTPY_DEFAULT_QUERY_POSTPROCESSOR` to `None`.
-   Massive overhaul of docs styling.

## [3.5.0] - 2023-08-26

### Added

-   More customization for reconnection behavior through new settings!
    -   `REACTPY_RECONNECT_INTERVAL`
    -   `REACTPY_RECONNECT_MAX_INTERVAL`
    -   `REACTPY_RECONNECT_MAX_RETRIES`
    -   `REACTPY_RECONNECT_BACKOFF_MULTIPLIER`
-   [ReactPy-Django docs](https://reactive-python.github.io/reactpy-django/) are now version controlled via [mike](https://github.com/jimporter/mike)!

### Changed

-   Bumped the minimum ReactPy version to `1.0.2`.
-   Prettier WebSocket URLs for components that do not have sessions.
-   Template tag will now only validate `args`/`kwargs` if `settings.py:DEBUG` is enabled.
-   Bumped the minimum `@reactpy/client` version to `0.3.1`
-   Use TypeScript instead of JavaScript for this repository.
-   Bumped the minimum Django version to `4.2`.

???+ note "Django 4.2+ is required"

    ReactPy-Django will continue bumping minimum Django requirements to versions that increase async support.

    This "latest-only" trend will continue until Django has all async features that ReactPy benefits from. After this point, ReactPy-Django will begin supporting all maintained Django versions.

### Removed

-   `settings.py:REACTPY_RECONNECT_MAX` is removed. See the docs for the new `REACTPY_RECONNECT_*` settings.

## [3.4.0] - 2023-08-18

### Added

-   **Distributed Computing:** ReactPy components can now optionally be rendered by a completely separate server!
    -   `REACTPY_DEFAULT_HOSTS` setting can round-robin a list of ReactPy rendering hosts.
    -   `host` argument has been added to the `component` template tag to force components to render on a specific host.
-   `reactpy_django.utils.register_component` function can manually register root components.
    -   Useful if you have dedicated ReactPy rendering application(s) that do not use HTML templates.

### Changed

-   ReactPy will now provide a warning if your HTTP URLs are not on the same prefix as your WebSockets.
-   Cleaner logging output for auto-detected ReactPy root components.

### Deprecated

-   `reactpy_django.REACTPY_WEBSOCKET_PATH` is deprecated. The identical replacement is `REACTPY_WEBSOCKET_ROUTE`.
-   `settings.py:REACTPY_WEBSOCKET_URL` is deprecated. The similar replacement is `REACTPY_URL_PREFIX`.

### Removed

-   Warning W007 (`REACTPY_WEBSOCKET_URL doesn't end with a slash`) has been removed. ReactPy now automatically handles slashes.
-   Warning W008 (`REACTPY_WEBSOCKET_URL doesn't start with an alphanumeric character`) has been removed. ReactPy now automatically handles this scenario.
-   Error E009 (`channels is not in settings.py:INSTALLED_APPS`) has been removed. Newer versions of `channels` do not require installation via `INSTALLED_APPS` to receive an ASGI web server.

## [3.3.2] - 2023-08-13

### Added

-   ReactPy WebSocket will now decode messages via `orjson` resulting in an ~6% overall performance improvement.
-   Built-in `asyncio` event loops are now patched via `nest_asyncio`, resulting in an ~10% overall performance improvement. This has no performance impact if you are running your web server with `uvloop`.

### Fixed

-   Fix bug where `REACTPY_WEBSOCKET_URL` always generates a warning if unset.
-   Fixed bug on Windows where `assert f is self._write_fut` would be raised by `uvicorn` when `REACTPY_BACKHAUL_THREAD = True`.
-   Fixed bug on Windows where rendering behavior would be jittery with `daphne` when `REACTPY_BACKHAUL_THREAD = True`.

## [3.3.1] - 2023-08-08

### Added

-   Additional system checks for ReactPy misconfigurations.

### Changed

-   `REACTPY_BACKHAUL_THREAD` now defaults to `False`.

## [3.3.0] - 2023-08-05

### Added

-   Added system checks for a variety of common ReactPy misconfigurations.
-   `REACTPY_BACKHAUL_THREAD` setting to enable/disable threading behavior.

### Changed

-   If using `settings.py:REACTPY_DATABASE`, `reactpy_django.database.Router` must now be registered in `settings.py:DATABASE_ROUTERS`.
-   By default, ReactPy will now use a backhaul thread to increase performance.
-   Minimum Python version required is now `3.9`
-   A thread-safe cache is no longer required.

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

-   `reactpy-django` database entries are no longer cleaned during Django application startup. Instead, it will occur on webpage loads if `REACTPY_RECONNECT_MAX` seconds has elapsed since the last cleaning.

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

[Unreleased]: https://github.com/reactive-python/reactpy-django/compare/5.2.1...HEAD
[5.2.1]: https://github.com/reactive-python/reactpy-django/compare/5.2.0...5.2.1
[5.2.0]: https://github.com/reactive-python/reactpy-django/compare/5.1.1...5.2.0
[5.1.1]: https://github.com/reactive-python/reactpy-django/compare/5.1.0...5.1.1
[5.1.0]: https://github.com/reactive-python/reactpy-django/compare/5.0.0...5.1.0
[5.0.0]: https://github.com/reactive-python/reactpy-django/compare/4.0.0...5.0.0
[4.0.0]: https://github.com/reactive-python/reactpy-django/compare/3.8.1...4.0.0
[3.8.1]: https://github.com/reactive-python/reactpy-django/compare/3.8.0...3.8.1
[3.8.0]: https://github.com/reactive-python/reactpy-django/compare/3.7.0...3.8.0
[3.7.0]: https://github.com/reactive-python/reactpy-django/compare/3.6.0...3.7.0
[3.6.0]: https://github.com/reactive-python/reactpy-django/compare/3.5.1...3.6.0
[3.5.1]: https://github.com/reactive-python/reactpy-django/compare/3.5.0...3.5.1
[3.5.0]: https://github.com/reactive-python/reactpy-django/compare/3.4.0...3.5.0
[3.4.0]: https://github.com/reactive-python/reactpy-django/compare/3.3.2...3.4.0
[3.3.2]: https://github.com/reactive-python/reactpy-django/compare/3.3.1...3.3.2
[3.3.1]: https://github.com/reactive-python/reactpy-django/compare/3.3.0...3.3.1
[3.3.0]: https://github.com/reactive-python/reactpy-django/compare/3.2.1...3.3.0
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
