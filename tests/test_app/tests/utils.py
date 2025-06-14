# ruff: noqa: N802, RUF012, T201
import asyncio
import os
import sys
from collections.abc import Iterable
from functools import partial
from logging import getLogger
from typing import TYPE_CHECKING, Any, Callable

import decorator
from channels.routing import get_default_application
from channels.testing import ChannelsLiveServerTestCase
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.db import connections
from django.test.utils import modify_settings
from playwright.sync_api import sync_playwright

from reactpy_django.utils import str_to_bool

if TYPE_CHECKING:
    from daphne.testing import DaphneProcess

GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS", "False")
_logger = getLogger(__name__)


class PlaywrightTestCase(ChannelsLiveServerTestCase):
    databases = {"default"}
    total_servers = 4
    _server_process_0: "DaphneProcess"
    _server_process_1: "DaphneProcess"  # For Offline Tests
    _server_process_2: "DaphneProcess"  # For Distributed Computing Tests
    _server_process_3: "DaphneProcess"  # For Distributed Computing Tests
    _port_0: int
    _port_1: int
    _port_2: int
    _port_3: int

    ####################################################
    # Overrides for ChannelsLiveServerTestCase methods #
    ####################################################
    @classmethod
    def setUpClass(cls):
        # Repurposed from ChannelsLiveServerTestCase._pre_setup
        for connection in connections.all():
            if connection.vendor == "sqlite" and connection.is_in_memory_db():
                msg = "ChannelLiveServerTestCase can not be used with in memory databases"
                raise ImproperlyConfigured(msg)
        cls._live_server_modified_settings = modify_settings(ALLOWED_HOSTS={"append": cls.host})
        cls._live_server_modified_settings.enable()
        cls.get_application = partial(get_default_application)

        # Start the Django webserver(s)
        for i in range(cls.total_servers):
            cls.start_django_webserver(i)

        # Wipe the databases
        from reactpy_django import config

        cls.flush_databases({"default", config.REACTPY_DATABASE})

        # Open a Playwright browser window
        cls.start_playwright_client()

    @classmethod
    def tearDownClass(cls):
        # Close the Playwright browser
        cls.shutdown_playwright_client()

        # Shutdown the Django webserver
        for i in range(cls.total_servers):
            cls.shutdown_django_webserver(i)
        cls._live_server_modified_settings.disable()

        # Wipe the databases
        from reactpy_django import config

        cls.flush_databases({"default", config.REACTPY_DATABASE})

    def _pre_setup(self):
        """Handled manually in `setUpClass` to speed things up."""

    def _post_teardown(self):
        """Handled manually in `tearDownClass` to prevent TransactionTestCase from doing
        database flushing in between tests. This also fixes a `SynchronousOnlyOperation` caused
        by a bug within `ChannelsLiveServerTestCase`."""

    @property
    def live_server_url(self):
        """Provides the URL to the FIRST SPAWNED Django webserver."""
        return f"http://{self.host}:{self._port_0}"

    #########################
    # Custom helper methods #
    #########################
    @classmethod
    def start_django_webserver(cls, num=0):
        setattr(cls, f"_server_process_{num}", cls.ProtocolServerProcess(cls.host, cls.get_application))
        server_process: DaphneProcess = getattr(cls, f"_server_process_{num}")
        server_process.start()
        server_process.ready.wait()
        setattr(cls, f"_port_{num}", server_process.port.value)

    @classmethod
    def shutdown_django_webserver(cls, num=0):
        server_process: DaphneProcess = getattr(cls, f"_server_process_{num}")
        server_process.terminate()
        server_process.join()

    @classmethod
    def start_playwright_client(cls):
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        cls.playwright = sync_playwright().start()
        headless = str_to_bool(os.environ.get("PLAYWRIGHT_HEADLESS", GITHUB_ACTIONS))
        cls.browser = cls.playwright.chromium.launch(headless=bool(headless))
        cls.page = cls.browser.new_page()
        cls.page.set_default_timeout(10000)
        cls.page.on("console", lambda msg: print(f"{msg.type.upper()}: {msg.text}"))
        cls.page.on("pageerror", lambda err: print(f"ERROR: {err.name}: {err.message}"))

    @classmethod
    def shutdown_playwright_client(cls):
        cls.browser.close()
        cls.playwright.stop()

    @staticmethod
    def flush_databases(db_names: Iterable[Any]):
        for db_name in db_names:
            call_command(
                "flush",
                verbosity=0,
                interactive=False,
                database=db_name,
                reset_sequences=False,
            )


def navigate_to_page(path: str, *, server_num=0):
    """Decorator to make sure the browser is on a specific page before running a test."""

    def _decorator(func: Callable):
        @decorator.decorator
        def _wrapper(func: Callable, self: PlaywrightTestCase, *args, **kwargs):
            _port = getattr(self, f"_port_{server_num}")
            _path = f"http://{self.host}:{_port}/{path.lstrip('/')}"
            if self.page.url != _path:
                self.page.goto(_path)
            return func(self, *args, **kwargs)

        return _wrapper(func)

    return _decorator
