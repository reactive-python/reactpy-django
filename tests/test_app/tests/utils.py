# ruff: noqa: N802, RUF012
import asyncio
import os
import sys
from functools import partial
from typing import Callable

import decorator
from channels.testing import ChannelsLiveServerTestCase
from channels.testing.live import make_application
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.db import connections
from django.test.utils import modify_settings
from playwright.sync_api import sync_playwright

from reactpy_django.utils import str_to_bool

GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS", "False")


class PlaywrightTestCase(ChannelsLiveServerTestCase):
    from reactpy_django import config

    databases = {"default"}

    @classmethod
    def setUpClass(cls):
        # Repurposed from ChannelsLiveServerTestCase._pre_setup
        for connection in connections.all():
            if cls._is_in_memory_db(cls, connection):
                msg = "ChannelLiveServerTestCase can not be used with in memory databases"
                raise ImproperlyConfigured(msg)
        cls._live_server_modified_settings = modify_settings(ALLOWED_HOSTS={"append": cls.host})
        cls._live_server_modified_settings.enable()
        cls.get_application = partial(
            make_application,
            static_wrapper=cls.static_wrapper if cls.serve_static else None,
        )
        cls.setUpServer()

        # Open a Playwright browser window
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        cls.playwright = sync_playwright().start()
        headless = str_to_bool(os.environ.get("PLAYWRIGHT_HEADLESS", GITHUB_ACTIONS))
        cls.browser = cls.playwright.chromium.launch(headless=bool(headless))
        cls.page = cls.browser.new_page()
        cls.page.set_default_timeout(10000)

    @classmethod
    def setUpServer(cls):
        cls._server_process = cls.ProtocolServerProcess(cls.host, cls.get_application)
        cls._server_process.start()
        cls._server_process.ready.wait()
        cls._port = cls._server_process.port.value

    @classmethod
    def tearDownClass(cls):
        from reactpy_django import config

        # Close the Playwright browser
        cls.playwright.stop()

        # Close the other server processes
        cls.tearDownServer()

        # Repurposed from ChannelsLiveServerTestCase._post_teardown
        cls._live_server_modified_settings.disable()
        # Using set to prevent duplicates
        for db_name in {"default", config.REACTPY_DATABASE}:  # noqa: PLC0208
            call_command(
                "flush",
                verbosity=0,
                interactive=False,
                database=db_name,
                reset_sequences=False,
            )

    @classmethod
    def tearDownServer(cls):
        cls._server_process.terminate()
        cls._server_process.join()

    def _pre_setup(self):
        """Handled manually in `setUpClass` to speed things up."""

    def _post_teardown(self):
        """Handled manually in `tearDownClass` to prevent TransactionTestCase from doing
        database flushing. This is needed to prevent a `SynchronousOnlyOperation` from
        occurring due to a bug within `ChannelsLiveServerTestCase`."""


def navigate_to_page(path: str):
    def _decorator(func: Callable):
        @decorator.decorator
        def _wrapper(func: Callable, self: PlaywrightTestCase, *args, **kwargs):
            if self.page.url != path:
                self.page.goto(f"http://{self.host}:{self._port}/{path.lstrip('/')}")
            return func(self, *args, **kwargs)

        return _wrapper(func)

    return _decorator
