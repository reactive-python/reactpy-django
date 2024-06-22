import asyncio
import os
import socket
import sys
from functools import partial
from time import sleep

from channels.testing import ChannelsLiveServerTestCase
from channels.testing.live import make_application
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.db import connections
from django.test.utils import modify_settings
from playwright.sync_api import TimeoutError, sync_playwright
from reactpy_django.models import ComponentSession
from reactpy_django.utils import strtobool

GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS", "False")
CLICK_DELAY = 250 if strtobool(GITHUB_ACTIONS) else 25  # Delay in miliseconds.


class ComponentTests(ChannelsLiveServerTestCase):
    from django.db import DEFAULT_DB_ALIAS
    from reactpy_django import config

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

        # Open the second server process, used for testing custom hosts
        cls._server_process2 = cls.ProtocolServerProcess(cls.host, get_application)
        cls._server_process2.start()
        cls._server_process2.ready.wait()
        cls._port2 = cls._server_process2.port.value

        # Open the third server process, used for testing offline fallback
        cls._server_process3 = cls.ProtocolServerProcess(cls.host, get_application)
        cls._server_process3.start()
        cls._server_process3.ready.wait()
        cls._port3 = cls._server_process3.port.value

        # Open a Playwright browser window
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        cls.playwright = sync_playwright().start()
        headless = strtobool(os.environ.get("PLAYWRIGHT_HEADLESS", GITHUB_ACTIONS))
        cls.browser = cls.playwright.chromium.launch(headless=bool(headless))
        cls.page = cls.browser.new_page()

    @classmethod
    def tearDownClass(cls):
        from reactpy_django import config

        # Close the Playwright browser
        cls.playwright.stop()

        # Close the other server processes
        cls._server_process2.terminate()
        cls._server_process2.join()
        cls._server_process3.terminate()
        cls._server_process3.join()

        # Repurposed from ChannelsLiveServerTestCase._post_teardown
        cls._server_process.terminate()
        cls._server_process.join()
        cls._live_server_modified_settings.disable()
        for db_name in {"default", config.REACTPY_DATABASE}:
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

    def test_unauthorized_user_test(self):
        self.assertRaises(
            TimeoutError,
            self.page.wait_for_selector,
            "#unauthorized-user-test",
            timeout=1,
        )
        self.page.wait_for_selector("#unauthorized-user-test-fallback")

    def test_authorized_user_test(self):
        self.assertRaises(
            TimeoutError,
            self.page.wait_for_selector,
            "#authorized-user-test-fallback",
            timeout=1,
        )
        self.page.wait_for_selector("#authorized-user-test")

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

    def test_view_to_iframe_args(self):
        self.page.frame_locator("#view_to_iframe_args > iframe").locator(
            "#view_to_iframe_args[data-success=Success]"
        ).wait_for()

    def test_view_to_component_decorator(self):
        self.page.locator("#view_to_component_decorator[data-success=true]").wait_for()

    def test_view_to_component_decorator_args(self):
        self.page.locator(
            "#view_to_component_decorator_args[data-success=true]"
        ).wait_for()

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
        new_page.goto(f"{self.live_server_url}/port/{self._port2}/")
        try:
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
        new_page.goto(f"{self.live_server_url}/roundrobin/{self._port}/{self._port2}/8")
        try:
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

    def test_prerender(self):
        """Verify if round-robin host selection is working."""
        new_page = self.browser.new_page()
        new_page.goto(f"{self.live_server_url}/prerender/")
        try:
            string = new_page.locator("#prerender_string")
            vdom = new_page.locator("#prerender_vdom")
            component = new_page.locator("#prerender_component")
            use_root_id_http = new_page.locator("#use-root-id-http")
            use_root_id_ws = new_page.locator("#use-root-id-ws")
            use_user_http = new_page.locator("#use-user-http[data-success=True]")
            use_user_ws = new_page.locator("#use-user-ws[data-success=true]")

            string.wait_for()
            vdom.wait_for()
            component.wait_for()
            use_root_id_http.wait_for()
            use_user_http.wait_for()

            # Check if the prerender occurred
            self.assertEqual(
                string.all_inner_texts(), ["prerender_string: Prerendered"]
            )
            self.assertEqual(vdom.all_inner_texts(), ["prerender_vdom: Prerendered"])
            self.assertEqual(
                component.all_inner_texts(), ["prerender_component: Prerendered"]
            )
            root_id_value = use_root_id_http.get_attribute("data-value")
            self.assertEqual(len(root_id_value), 36)

            # Check if the full render occurred
            sleep(1)
            self.assertEqual(
                string.all_inner_texts(), ["prerender_string: Fully Rendered"]
            )
            self.assertEqual(vdom.all_inner_texts(), ["prerender_vdom: Fully Rendered"])
            self.assertEqual(
                component.all_inner_texts(), ["prerender_component: Fully Rendered"]
            )
            use_root_id_ws.wait_for()
            use_user_ws.wait_for()
            self.assertEqual(use_root_id_ws.get_attribute("data-value"), root_id_value)

        finally:
            new_page.close()

    def test_component_errors(self):
        new_page = self.browser.new_page()
        new_page.goto(f"{self.live_server_url}/errors/")
        try:
            # ComponentDoesNotExistError
            broken_component = new_page.locator("#component_does_not_exist_error")
            broken_component.wait_for()
            self.assertIn(
                "ComponentDoesNotExistError:", broken_component.text_content()
            )

            # ComponentParamError
            broken_component = new_page.locator("#component_param_error")
            broken_component.wait_for()
            self.assertIn("ComponentParamError:", broken_component.text_content())

            # InvalidHostError
            broken_component = new_page.locator("#invalid_host_error")
            broken_component.wait_for()
            self.assertIn("InvalidHostError:", broken_component.text_content())

            # SynchronousOnlyOperation
            broken_component = new_page.locator("#broken_postprocessor_query pre")
            broken_component.wait_for()
            self.assertIn("SynchronousOnlyOperation:", broken_component.text_content())

            # ViewNotRegisteredError
            broken_component = new_page.locator("#view_to_iframe_not_registered pre")
            broken_component.wait_for()
            self.assertIn("ViewNotRegisteredError:", broken_component.text_content())

            # DecoratorParamError
            broken_component = new_page.locator("#incorrect_user_passes_test_decorator")
            broken_component.wait_for()
            self.assertIn("DecoratorParamError:", broken_component.text_content())
        finally:
            new_page.close()

    def test_use_user_data(self):
        text_input = self.page.wait_for_selector("#use-user-data input")
        login_1 = self.page.wait_for_selector("#use-user-data .login-1")
        login_2 = self.page.wait_for_selector("#use-user-data .login-2")
        logout = self.page.wait_for_selector("#use-user-data .logout")
        clear = self.page.wait_for_selector("#use-user-data .clear")

        # Test AnonymousUser data
        user_data_div = self.page.wait_for_selector(
            "#use-user-data[data-success=false][data-fetch-error=false][data-mutation-error=false][data-loading=false][data-username=AnonymousUser]"
        )
        self.assertIn("Data: None", user_data_div.text_content())

        # Test first user's data
        login_1.click()
        user_data_div = self.page.wait_for_selector(
            "#use-user-data[data-success=false][data-fetch-error=false][data-mutation-error=false][data-loading=false][data-username=user_1]"
        )
        self.assertIn(r"Data: {}", user_data_div.text_content())
        text_input.type("test", delay=CLICK_DELAY)
        text_input.press("Enter", delay=CLICK_DELAY)
        user_data_div = self.page.wait_for_selector(
            "#use-user-data[data-success=true][data-fetch-error=false][data-mutation-error=false][data-loading=false][data-username=user_1]"
        )
        self.assertIn("Data: {'test': 'test'}", user_data_div.text_content())

        # Test second user's data
        login_2.click()
        user_data_div = self.page.wait_for_selector(
            "#use-user-data[data-success=false][data-fetch-error=false][data-mutation-error=false][data-loading=false][data-username=user_2]"
        )
        self.assertIn(r"Data: {}", user_data_div.text_content())
        text_input.press("Control+A", delay=CLICK_DELAY)
        text_input.press("Backspace", delay=CLICK_DELAY)
        text_input.type("test 2", delay=CLICK_DELAY)
        text_input.press("Enter", delay=CLICK_DELAY)
        user_data_div = self.page.wait_for_selector(
            "#use-user-data[data-success=true][data-fetch-error=false][data-mutation-error=false][data-loading=false][data-username=user_2]"
        )
        self.assertIn("Data: {'test 2': 'test 2'}", user_data_div.text_content())

        # Attempt to clear data
        clear.click()
        user_data_div = self.page.wait_for_selector(
            "#use-user-data[data-success=false][data-fetch-error=false][data-mutation-error=false][data-loading=false][data-username=user_2]"
        )
        self.assertIn(r"Data: {}", user_data_div.text_content())

        # Attempt to logout
        logout.click()
        user_data_div = self.page.wait_for_selector(
            "#use-user-data[data-success=false][data-fetch-error=false][data-mutation-error=false][data-loading=false][data-username=AnonymousUser]"
        )
        self.assertIn(r"Data: None", user_data_div.text_content())

    def test_use_user_data_with_default(self):
        text_input = self.page.wait_for_selector("#use-user-data-with-default input")
        login_3 = self.page.wait_for_selector("#use-user-data-with-default .login-3")
        clear = self.page.wait_for_selector("#use-user-data-with-default .clear")

        # Test AnonymousUser data
        user_data_div = self.page.wait_for_selector(
            "#use-user-data-with-default[data-fetch-error=false][data-mutation-error=false][data-loading=false][data-username=AnonymousUser]"
        )
        self.assertIn("Data: None", user_data_div.text_content())

        # Test first user's data
        login_3.click()
        user_data_div = self.page.wait_for_selector(
            "#use-user-data-with-default[data-fetch-error=false][data-mutation-error=false][data-loading=false][data-username=user_3]"
        )
        self.assertIn(
            "Data: {'default1': 'value', 'default2': 'value2', 'default3': 'value3'}",
            user_data_div.text_content(),
        )
        text_input.type("test", delay=CLICK_DELAY)
        text_input.press("Enter", delay=CLICK_DELAY)
        user_data_div = self.page.wait_for_selector(
            "#use-user-data-with-default[data-fetch-error=false][data-mutation-error=false][data-loading=false][data-username=user_3]"
        )
        self.assertIn(
            "Data: {'default1': 'value', 'default2': 'value2', 'default3': 'value3', 'test': 'test'}",
            user_data_div.text_content(),
        )

        # Attempt to clear data
        clear.click()
        sleep(0.25)
        user_data_div = self.page.wait_for_selector(
            "#use-user-data-with-default[data-fetch-error=false][data-mutation-error=false][data-loading=false][data-username=user_3]"
        )
        self.assertIn(
            "Data: {'default1': 'value', 'default2': 'value2', 'default3': 'value3'}",
            user_data_div.text_content(),
        )

    def test_url_router(self):
        new_page = self.browser.new_page()
        try:
            new_page.goto(f"{self.live_server_url}/router/")
            path = new_page.wait_for_selector("#router-path")
            self.assertIn("/router/", path.get_attribute("data-path"))

            new_page.goto(f"{self.live_server_url}/router/any/123/")
            path = new_page.wait_for_selector("#router-path")
            self.assertIn("/router/any/123/", path.get_attribute("data-path"))

            new_page.goto(f"{self.live_server_url}/router/integer/123/")
            path = new_page.wait_for_selector("#router-path")
            self.assertIn("/router/integer/123/", path.get_attribute("data-path"))

            new_page.goto(f"{self.live_server_url}/router/path/abc/123/")
            path = new_page.wait_for_selector("#router-path")
            self.assertIn("/router/path/abc/123/", path.get_attribute("data-path"))

            new_page.goto(f"{self.live_server_url}/router/slug/abc-123/")
            path = new_page.wait_for_selector("#router-path")
            self.assertIn("/router/slug/abc-123/", path.get_attribute("data-path"))

            new_page.goto(f"{self.live_server_url}/router/string/abc/")
            path = new_page.wait_for_selector("#router-path")
            self.assertIn("/router/string/abc/", path.get_attribute("data-path"))

            new_page.goto(
                f"{self.live_server_url}/router/uuid/123e4567-e89b-12d3-a456-426614174000/"
            )
            path = new_page.wait_for_selector("#router-path")
            self.assertIn(
                "/router/uuid/123e4567-e89b-12d3-a456-426614174000/",
                path.get_attribute("data-path"),
            )

            new_page.goto(f"{self.live_server_url}/router/abc/")
            path = new_page.wait_for_selector("#router-path")
            self.assertIn("/router/abc/", path.get_attribute("data-path"))

            new_page.goto(f"{self.live_server_url}/router/two/123/abc/")
            path = new_page.wait_for_selector("#router-path")
            self.assertIn("/router/two/123/abc/", path.get_attribute("data-path"))

            new_page.goto(f"{self.live_server_url}/router/star/one/")
            path = new_page.wait_for_selector("#router-path")
            self.assertIn("/router/star/one/", path.get_attribute("data-path"))

            new_page.goto(
                f"{self.live_server_url}/router/star/adslkjgklasdjhfah/6789543256/"
            )
            path = new_page.wait_for_selector("#router-path")
            self.assertIn(
                "/router/star/adslkjgklasdjhfah/6789543256/",
                path.get_attribute("data-path"),
            )
            string = new_page.query_selector("#router-string")
            self.assertEqual("Path 12", string.text_content())

        finally:
            new_page.close()

    def test_offline_components(self):
        new_page = self.browser.new_page()
        try:
            server3_url = self.live_server_url.replace(
                str(self._port), str(self._port3)
            )
            new_page.goto(f"{server3_url}/offline/")
            new_page.wait_for_selector("div:not([hidden]) > #online")
            self.assertIsNotNone(new_page.query_selector("div[hidden] > #offline"))
            self._server_process3.terminate()
            self._server_process3.join()
            new_page.wait_for_selector("div:not([hidden]) > #offline")
            self.assertIsNotNone(new_page.query_selector("div[hidden] > #online"))

        finally:
            new_page.close()

    def test_channel_layer_components(self):
        new_page = self.browser.new_page()
        try:
            new_page.goto(f"{self.live_server_url}/channel-layers/")
            sender = new_page.wait_for_selector("#sender")
            sender.type("test", delay=CLICK_DELAY)
            sender.press("Enter", delay=CLICK_DELAY)
            receiver = new_page.wait_for_selector("#receiver[data-message='test']")
            self.assertIsNotNone(receiver)

            sender = new_page.wait_for_selector("#group-sender")
            sender.type("1234", delay=CLICK_DELAY)
            sender.press("Enter", delay=CLICK_DELAY)
            receiver_1 = new_page.wait_for_selector(
                "#group-receiver-1[data-message='1234']"
            )
            receiver_2 = new_page.wait_for_selector(
                "#group-receiver-2[data-message='1234']"
            )
            receiver_3 = new_page.wait_for_selector(
                "#group-receiver-3[data-message='1234']"
            )
            self.assertIsNotNone(receiver_1)
            self.assertIsNotNone(receiver_2)
            self.assertIsNotNone(receiver_3)

        finally:
            new_page.close()

    def test_pyscript_components(self):
        new_page = self.browser.new_page()
        try:
            new_page.goto(f"{self.live_server_url}/pyscript/")
            new_page.wait_for_selector("#hello-world-loading")
            new_page.wait_for_selector("#hello-world")
            new_page.wait_for_selector("#custom-root")
            new_page.wait_for_selector("#multifile-parent")
            new_page.wait_for_selector("#multifile-child")

            new_page.wait_for_selector("#counter")
            new_page.wait_for_selector("#counter pre[data-value='0']")
            new_page.wait_for_selector("#counter .plus").click(delay=CLICK_DELAY)
            new_page.wait_for_selector("#counter pre[data-value='1']")
            new_page.wait_for_selector("#counter .plus").click(delay=CLICK_DELAY)
            new_page.wait_for_selector("#counter pre[data-value='2']")
            new_page.wait_for_selector("#counter .minus").click(delay=CLICK_DELAY)
            new_page.wait_for_selector("#counter pre[data-value='1']")

            new_page.wait_for_selector("#parent")
            new_page.wait_for_selector("#child")
            new_page.wait_for_selector("#child pre[data-value='0']")
            new_page.wait_for_selector("#child .plus").click(delay=CLICK_DELAY)
            new_page.wait_for_selector("#child pre[data-value='1']")
            new_page.wait_for_selector("#child .plus").click(delay=CLICK_DELAY)
            new_page.wait_for_selector("#child pre[data-value='2']")
            new_page.wait_for_selector("#child .minus").click(delay=CLICK_DELAY)
            new_page.wait_for_selector("#child pre[data-value='1']")

            new_page.wait_for_selector("#parent-toggle")
            new_page.wait_for_selector("#parent-toggle button").click(delay=CLICK_DELAY)
            new_page.wait_for_selector("#parent-toggle")
            new_page.wait_for_selector("#parent-toggle pre[data-value='0']")
            new_page.wait_for_selector("#parent-toggle .plus").click(delay=CLICK_DELAY)
            new_page.wait_for_selector("#parent-toggle pre[data-value='1']")
            new_page.wait_for_selector("#parent-toggle .plus").click(delay=CLICK_DELAY)
            new_page.wait_for_selector("#parent-toggle pre[data-value='2']")
            new_page.wait_for_selector("#parent-toggle .minus").click(delay=CLICK_DELAY)
            new_page.wait_for_selector("#parent-toggle pre[data-value='1']")

            new_page.wait_for_selector("#moment[data-success=true]")
        finally:
            new_page.close()
