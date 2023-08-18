import asyncio
import os
import socket
import sys
from functools import partial

from channels.testing import ChannelsLiveServerTestCase
from channels.testing.live import make_application
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.db import connections
from django.test.utils import modify_settings
from playwright.sync_api import TimeoutError, sync_playwright
from reactpy_django.models import ComponentSession

GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS")
CLICK_DELAY = 250 if GITHUB_ACTIONS else 25  # Delay in miliseconds.


class ComponentTests(ChannelsLiveServerTestCase):
    databases = {"default"}

    @classmethod
    def setUpClass(cls):
        # Repurposed from ChannelsLiveServerTestCase._pre_setup
        for connection in connections.all():
            if cls._is_in_memory_db(cls, connection):
                raise ImproperlyConfigured(
                    "ChannelLiveServerTestCase can not be used with in memory databases"
                )
        cls._live_server_modified_settings = modify_settings(
            ALLOWED_HOSTS={"append": cls.host}
        )
        cls._live_server_modified_settings.enable()
        get_application = partial(
            make_application,
            static_wrapper=cls.static_wrapper if cls.serve_static else None,
        )
        cls._server_process = cls.ProtocolServerProcess(cls.host, get_application)
        cls._server_process.start()
        cls._server_process.ready.wait()
        cls._port = cls._server_process.port.value

        # Open the second server process
        cls._server_process2 = cls.ProtocolServerProcess(cls.host, get_application)
        cls._server_process2.start()
        cls._server_process2.ready.wait()
        cls._port2 = cls._server_process2.port.value

        # Open a Playwright browser window
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        cls.playwright = sync_playwright().start()
        headed = bool(int(os.environ.get("PLAYWRIGHT_HEADED", not GITHUB_ACTIONS)))
        cls.browser = cls.playwright.chromium.launch(headless=not headed)
        cls.page = cls.browser.new_page()

    @classmethod
    def tearDownClass(cls):
        # Close the Playwright browser
        cls.playwright.stop()

        # Close the second server process
        cls._server_process2.terminate()
        cls._server_process2.join()

        # Repurposed from ChannelsLiveServerTestCase._post_teardown
        cls._server_process.terminate()
        cls._server_process.join()
        cls._live_server_modified_settings.disable()
        for db_name in {"default", "reactpy"}:
            call_command(
                "flush",
                verbosity=0,
                interactive=False,
                database=db_name,
                reset_sequences=False,
            )

    def _pre_setup(self):
        """Handled manually in `setUpClass` to speed things up."""
        pass

    def _post_teardown(self):
        """Handled manually in `tearDownClass` to prevent TransactionTestCase from doing
        database flushing. This is needed to prevent a `SynchronousOnlyOperation` from
        occuring due to a bug within `ChannelsLiveServerTestCase`."""
        pass

    def setUp(self):
        if self.page.url == "about:blank":
            self.page.goto(self.live_server_url)

    def test_hello_world(self):
        self.page.wait_for_selector("#hello-world")

    def test_counter(self):
        for i in range(5):
            self.page.locator(f"#counter-num[data-count={i}]")
            self.page.locator("#counter-inc").click()

    def test_parametrized_component(self):
        self.page.locator("#parametrized-component[data-value='579']").wait_for()

    def test_object_in_templatetag(self):
        self.page.locator("#object_in_templatetag[data-success=true]").wait_for()

    def test_component_from_web_module(self):
        self.page.wait_for_selector("#simple-button")

    def test_use_connection(self):
        self.page.locator("#use-connection[data-success=true]").wait_for()

    def test_use_scope(self):
        self.page.locator("#use-scope[data-success=true]").wait_for()

    def test_use_location(self):
        self.page.locator("#use-location[data-success=true]").wait_for()

    def test_use_origin(self):
        self.page.locator("#use-origin[data-success=true]").wait_for()

    def test_static_css(self):
        self.assertEqual(
            self.page.wait_for_selector("#django-css button").evaluate(
                "e => window.getComputedStyle(e).getPropertyValue('color')"
            ),
            "rgb(0, 0, 255)",
        )

    def test_static_js(self):
        self.page.locator("#django-js[data-success=true]").wait_for()

    def test_unauthorized_user(self):
        self.assertRaises(
            TimeoutError,
            self.page.wait_for_selector,
            "#unauthorized-user",
            timeout=1,
        )
        self.page.wait_for_selector("#unauthorized-user-fallback")

    def test_authorized_user(self):
        self.assertRaises(
            TimeoutError,
            self.page.wait_for_selector,
            "#authorized-user-fallback",
            timeout=1,
        )
        self.page.wait_for_selector("#authorized-user")

    def test_relational_query(self):
        self.page.locator("#relational-query[data-success=true]").wait_for()

    def test_async_relational_query(self):
        self.page.locator("#async-relational-query[data-success=true]").wait_for()

    def test_use_query_and_mutation(self):
        todo_input = self.page.wait_for_selector("#todo-input")

        item_ids = list(range(5))

        for i in item_ids:
            todo_input.type(f"sample-{i}", delay=CLICK_DELAY)
            todo_input.press("Enter", delay=CLICK_DELAY)
            self.page.wait_for_selector(f"#todo-list #todo-item-sample-{i}")
            self.page.wait_for_selector(
                f"#todo-list #todo-item-sample-{i}-checkbox"
            ).click()
            self.assertRaises(
                TimeoutError,
                self.page.wait_for_selector,
                f"#todo-list #todo-item-sample-{i}",
                timeout=1,
            )

    def test_async_use_query_and_mutation(self):
        todo_input = self.page.wait_for_selector("#async-todo-input")

        item_ids = list(range(5))

        for i in item_ids:
            todo_input.type(f"sample-{i}", delay=CLICK_DELAY)
            todo_input.press("Enter", delay=CLICK_DELAY)
            self.page.wait_for_selector(f"#async-todo-list #todo-item-sample-{i}")
            self.page.wait_for_selector(
                f"#async-todo-list #todo-item-sample-{i}-checkbox"
            ).click()
            self.assertRaises(
                TimeoutError,
                self.page.wait_for_selector,
                f"#async-todo-list #todo-item-sample-{i}",
                timeout=1,
            )

    def test_view_to_component_sync_func(self):
        self.page.locator("#view_to_component_sync_func[data-success=true]").wait_for()

    def test_view_to_component_async_func(self):
        self.page.locator("#view_to_component_async_func[data-success=true]").wait_for()

    def test_view_to_component_sync_class(self):
        self.page.locator("#ViewToComponentSyncClass[data-success=true]").wait_for()

    def test_view_to_component_async_class(self):
        self.page.locator("#ViewToComponentAsyncClass[data-success=true]").wait_for()

    def test_view_to_component_template_view_class(self):
        self.page.locator(
            "#ViewToComponentTemplateViewClass[data-success=true]"
        ).wait_for()

    def _click_btn_and_check_success(self, name):
        self.page.locator(f"#{name}:not([data-success=true])").wait_for()
        self.page.wait_for_selector(f"#{name}_btn").click()
        self.page.locator(f"#{name}[data-success=true]").wait_for()

    def test_view_to_component_script(self):
        self._click_btn_and_check_success("view_to_component_script")

    def test_view_to_component_request(self):
        self._click_btn_and_check_success("view_to_component_request")

    def test_view_to_component_args(self):
        self._click_btn_and_check_success("view_to_component_args")

    def test_view_to_component_kwargs(self):
        self._click_btn_and_check_success("view_to_component_kwargs")

    def test_view_to_component_sync_func_compatibility(self):
        self.page.frame_locator(
            "#view_to_component_sync_func_compatibility > iframe"
        ).locator(
            "#view_to_component_sync_func_compatibility[data-success=true]"
        ).wait_for()

    def test_view_to_component_async_func_compatibility(self):
        self.page.frame_locator(
            "#view_to_component_async_func_compatibility > iframe"
        ).locator(
            "#view_to_component_async_func_compatibility[data-success=true]"
        ).wait_for()

    def test_view_to_component_sync_class_compatibility(self):
        self.page.frame_locator(
            "#view_to_component_sync_class_compatibility > iframe"
        ).locator(
            "#ViewToComponentSyncClassCompatibility[data-success=true]"
        ).wait_for()

    def test_view_to_component_async_class_compatibility(self):
        self.page.frame_locator(
            "#view_to_component_async_class_compatibility > iframe"
        ).locator(
            "#ViewToComponentAsyncClassCompatibility[data-success=true]"
        ).wait_for()

    def test_view_to_component_template_view_class_compatibility(self):
        self.page.frame_locator(
            "#view_to_component_template_view_class_compatibility > iframe"
        ).locator(
            "#ViewToComponentTemplateViewClassCompatibility[data-success=true]"
        ).wait_for()

    def test_view_to_component_decorator(self):
        self.page.locator("#view_to_component_decorator[data-success=true]").wait_for()

    def test_view_to_component_decorator_args(self):
        self.page.locator(
            "#view_to_component_decorator_args[data-success=true]"
        ).wait_for()

    def test_component_does_not_exist_error(self):
        broken_component = self.page.locator("#component_does_not_exist_error")
        broken_component.wait_for()
        self.assertIn("ComponentDoesNotExistError:", broken_component.text_content())

    def test_component_param_error(self):
        broken_component = self.page.locator("#component_param_error")
        broken_component.wait_for()
        self.assertIn("ComponentParamError:", broken_component.text_content())

    def test_component_session_exists(self):
        """Session should exist for components with args/kwargs."""
        component = self.page.locator("#parametrized-component")
        component.wait_for()
        parent = component.locator("..")
        session_id = parent.get_attribute("id")
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        query = ComponentSession.objects.filter(uuid=session_id)
        query_exists = query.exists()
        os.environ.pop("DJANGO_ALLOW_ASYNC_UNSAFE")
        self.assertTrue(query_exists)

    def test_component_session_missing(self):
        """No session should exist for components that don't have args/kwargs."""
        component = self.page.locator("#simple-button")
        component.wait_for()
        parent = component.locator("..")
        session_id = parent.get_attribute("id")
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        query = ComponentSession.objects.filter(uuid=session_id)
        query_exists = query.exists()
        os.environ.pop("DJANGO_ALLOW_ASYNC_UNSAFE")
        self.assertFalse(query_exists)

    def test_custom_host(self):
        """Make sure that the component is rendered by a separate server."""
        new_page = self.browser.new_page()
        try:
            new_page.goto(f"{self.live_server_url}/port/{self._port2}/")
            elem = new_page.locator(".custom_host-0")
            elem.wait_for()
            self.assertIn(
                f"Server Port: {self._port2}",
                elem.text_content(),
            )
        finally:
            new_page.close()

    def test_custom_host_wrong_port(self):
        """Make sure that other ports are not rendering components."""
        new_page = self.browser.new_page()
        try:
            tmp_sock = socket.socket()
            tmp_sock.bind((self._server_process.host, 0))
            random_port = tmp_sock.getsockname()[1]
            new_page.goto(f"{self.live_server_url}/port/{random_port}/")
            with self.assertRaises(TimeoutError):
                new_page.locator(".custom_host").wait_for(timeout=1000)
        finally:
            new_page.close()

    def test_host_roundrobin(self):
        """Verify if round-robin host selection is working."""
        new_page = self.browser.new_page()
        try:
            new_page.goto(
                f"{self.live_server_url}/roundrobin/{self._port}/{self._port2}/8"
            )
            elem0 = new_page.locator(".custom_host-0")
            elem1 = new_page.locator(".custom_host-1")
            elem2 = new_page.locator(".custom_host-2")
            elem3 = new_page.locator(".custom_host-3")

            elem0.wait_for()
            elem1.wait_for()
            elem2.wait_for()
            elem3.wait_for()

            current_ports = {
                elem0.get_attribute("data-port"),
                elem1.get_attribute("data-port"),
                elem2.get_attribute("data-port"),
                elem3.get_attribute("data-port"),
            }
            correct_ports = {
                str(self._port),
                str(self._port2),
            }

            # There should only be two ports in the set
            self.assertEqual(current_ports, correct_ports)
            self.assertEqual(len(current_ports), 2)
        finally:
            new_page.close()

    def test_invalid_host_error(self):
        broken_component = self.page.locator("#invalid_host_error")
        broken_component.wait_for()
        self.assertIn("InvalidHostError:", broken_component.text_content())
