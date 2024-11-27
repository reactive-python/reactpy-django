import os
import socket
from time import sleep

from playwright.sync_api import TimeoutError

from reactpy_django.models import ComponentSession
from reactpy_django.utils import strtobool

from .utils import GITHUB_ACTIONS, PlaywrightTestCase

CLICK_DELAY = 250 if strtobool(GITHUB_ACTIONS) else 25  # Delay in miliseconds.


class GenericComponentTests(PlaywrightTestCase):

    databases = {"default"}

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.page.goto(f"http://{cls.host}:{cls._port}")

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
        self.page.wait_for_selector("#button-from-js-module")

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

    def test_view_to_iframe_sync_func(self):
        self.page.frame_locator("#view_to_iframe_sync_func > iframe").locator(
            "#view_to_iframe_sync_func[data-success=true]"
        ).wait_for()

    def test_view_to_iframe_async_func(self):
        self.page.frame_locator("#view_to_iframe_async_func > iframe").locator(
            "#view_to_iframe_async_func[data-success=true]"
        ).wait_for()

    def test_view_to_iframe_sync_class(self):
        self.page.frame_locator("#view_to_iframe_sync_class > iframe").locator(
            "#ViewToIframeSyncClass[data-success=true]"
        ).wait_for()

    def test_view_to_iframe_async_class(self):
        self.page.frame_locator("#view_to_iframe_async_class > iframe").locator(
            "#ViewToIframeAsyncClass[data-success=true]"
        ).wait_for()

    def test_view_to_iframe_template_view_class(self):
        self.page.frame_locator("#view_to_iframe_template_view_class > iframe").locator(
            "#ViewToIframeTemplateViewClass[data-success=true]"
        ).wait_for()

    def test_view_to_iframe_args(self):
        self.page.frame_locator("#view_to_iframe_args > iframe").locator(
            "#view_to_iframe_args[data-success=Success]"
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
        component = self.page.locator("#button-from-js-module")
        component.wait_for()
        parent = component.locator("..")
        session_id = parent.get_attribute("id")
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        query = ComponentSession.objects.filter(uuid=session_id)
        query_exists = query.exists()
        os.environ.pop("DJANGO_ALLOW_ASYNC_UNSAFE")
        self.assertFalse(query_exists)

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


class PrerenderTests(PlaywrightTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.page.goto(f"http://{cls.host}:{cls._port}/prerender/")

    def test_prerender(self):
        """Verify if round-robin host selection is working."""
        string = self.page.locator("#prerender_string")
        vdom = self.page.locator("#prerender_vdom")
        component = self.page.locator("#prerender_component")
        use_root_id_http = self.page.locator("#use-root-id-http")
        use_root_id_ws = self.page.locator("#use-root-id-ws")
        use_user_http = self.page.locator("#use-user-http[data-success=True]")
        use_user_ws = self.page.locator("#use-user-ws[data-success=true]")

        # Check if the prerender occurred properly
        string.wait_for()
        vdom.wait_for()
        component.wait_for()
        use_root_id_http.wait_for()
        use_user_http.wait_for()
        self.assertEqual(string.all_inner_texts(), ["prerender_string: Prerendered"])
        self.assertEqual(vdom.all_inner_texts(), ["prerender_vdom: Prerendered"])
        self.assertEqual(
            component.all_inner_texts(), ["prerender_component: Prerendered"]
        )
        root_id_value = use_root_id_http.get_attribute("data-value")
        self.assertEqual(len(root_id_value), 36)

        # Check if the full render occurred
        sleep(2)
        self.assertEqual(string.all_inner_texts(), ["prerender_string: Fully Rendered"])
        self.assertEqual(vdom.all_inner_texts(), ["prerender_vdom: Fully Rendered"])
        self.assertEqual(
            component.all_inner_texts(), ["prerender_component: Fully Rendered"]
        )
        use_root_id_ws.wait_for()
        use_user_ws.wait_for()
        self.assertEqual(use_root_id_ws.get_attribute("data-value"), root_id_value)


class ErrorTests(PlaywrightTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.page.goto(f"http://{cls.host}:{cls._port}/errors/")

    def test_component_does_not_exist_error(self):
        broken_component = self.page.locator("#component_does_not_exist_error")
        broken_component.wait_for()
        self.assertIn("ComponentDoesNotExistError:", broken_component.text_content())

    def test_component_param_error(self):
        broken_component = self.page.locator("#component_param_error")
        broken_component.wait_for()
        self.assertIn("ComponentParamError:", broken_component.text_content())

    def test_invalid_host_error(self):
        broken_component = self.page.locator("#invalid_host_error")
        broken_component.wait_for()
        self.assertIn("InvalidHostError:", broken_component.text_content())

    def test_synchronous_only_operation_error(self):
        broken_component = self.page.locator("#broken_postprocessor_query pre")
        broken_component.wait_for()
        self.assertIn("SynchronousOnlyOperation:", broken_component.text_content())

    def test_view_not_registered_error(self):
        broken_component = self.page.locator("#view_to_iframe_not_registered pre")
        broken_component.wait_for()
        self.assertIn("ViewNotRegisteredError:", broken_component.text_content())

    def test_decorator_param_error(self):
        broken_component = self.page.locator("#incorrect_user_passes_test_decorator")
        broken_component.wait_for()
        self.assertIn("DecoratorParamError:", broken_component.text_content())


class UrlRouterTests(PlaywrightTestCase):

    def test_url_router(self):
        self.page.goto(f"{self.live_server_url}/router/")
        path = self.page.wait_for_selector("#router-path")
        self.assertIn("/router/", path.get_attribute("data-path"))
        string = self.page.query_selector("#router-string")
        self.assertEqual("/router/", string.text_content())

    def test_url_router_subroute(self):
        self.page.goto(f"{self.live_server_url}/router/subroute/")
        path = self.page.wait_for_selector("#router-path")
        self.assertIn("/router/subroute/", path.get_attribute("data-path"))
        string = self.page.query_selector("#router-string")
        self.assertEqual("subroute/", string.text_content())

    def test_url_unspecified(self):
        self.page.goto(f"{self.live_server_url}/router/unspecified/123/")
        path = self.page.wait_for_selector("#router-path")
        self.assertIn("/router/unspecified/123/", path.get_attribute("data-path"))
        string = self.page.query_selector("#router-string")
        self.assertEqual("/router/unspecified/<value>/", string.text_content())

    def test_url_router_integer(self):
        self.page.goto(f"{self.live_server_url}/router/integer/123/")
        path = self.page.wait_for_selector("#router-path")
        self.assertIn("/router/integer/123/", path.get_attribute("data-path"))
        string = self.page.query_selector("#router-string")
        self.assertEqual("/router/integer/<int:value>/", string.text_content())

    def test_url_router_path(self):
        self.page.goto(f"{self.live_server_url}/router/path/abc/123/")
        path = self.page.wait_for_selector("#router-path")
        self.assertIn("/router/path/abc/123/", path.get_attribute("data-path"))
        string = self.page.query_selector("#router-string")
        self.assertEqual("/router/path/<path:value>/", string.text_content())

    def test_url_router_slug(self):
        self.page.goto(f"{self.live_server_url}/router/slug/abc-123/")
        path = self.page.wait_for_selector("#router-path")
        self.assertIn("/router/slug/abc-123/", path.get_attribute("data-path"))
        string = self.page.query_selector("#router-string")
        self.assertEqual("/router/slug/<slug:value>/", string.text_content())

    def test_url_router_string(self):
        self.page.goto(f"{self.live_server_url}/router/string/abc/")
        path = self.page.wait_for_selector("#router-path")
        self.assertIn("/router/string/abc/", path.get_attribute("data-path"))
        string = self.page.query_selector("#router-string")
        self.assertEqual("/router/string/<str:value>/", string.text_content())

    def test_url_router_uuid(self):
        self.page.goto(
            f"{self.live_server_url}/router/uuid/123e4567-e89b-12d3-a456-426614174000/"
        )
        path = self.page.wait_for_selector("#router-path")
        self.assertIn(
            "/router/uuid/123e4567-e89b-12d3-a456-426614174000/",
            path.get_attribute("data-path"),
        )
        string = self.page.query_selector("#router-string")
        self.assertEqual("/router/uuid/<uuid:value>/", string.text_content())

    def test_url_router_any(self):
        self.page.goto(
            f"{self.live_server_url}/router/any/adslkjgklasdjhfah/6789543256/"
        )
        path = self.page.wait_for_selector("#router-path")
        self.assertIn(
            "/router/any/adslkjgklasdjhfah/6789543256/",
            path.get_attribute("data-path"),
        )
        string = self.page.query_selector("#router-string")
        self.assertEqual("/router/any/<any:name>", string.text_content())

    def test_url_router_int_and_string(self):
        self.page.goto(f"{self.live_server_url}/router/two/123/abc/")
        path = self.page.wait_for_selector("#router-path")
        self.assertIn("/router/two/123/abc/", path.get_attribute("data-path"))
        string = self.page.query_selector("#router-string")
        self.assertEqual("/router/two/<int:value>/<str:value2>/", string.text_content())


class ChannelLayersTests(PlaywrightTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.page.goto(f"http://{cls.host}:{cls._port}/channel-layers/")

    def test_channel_layer_components(self):
        sender = self.page.wait_for_selector("#sender")
        sender.type("test", delay=CLICK_DELAY)
        sender.press("Enter", delay=CLICK_DELAY)
        receiver = self.page.wait_for_selector("#receiver[data-message='test']")
        self.assertIsNotNone(receiver)

        sender = self.page.wait_for_selector("#group-sender")
        sender.type("1234", delay=CLICK_DELAY)
        sender.press("Enter", delay=CLICK_DELAY)
        receiver_1 = self.page.wait_for_selector(
            "#group-receiver-1[data-message='1234']"
        )
        receiver_2 = self.page.wait_for_selector(
            "#group-receiver-2[data-message='1234']"
        )
        receiver_3 = self.page.wait_for_selector(
            "#group-receiver-3[data-message='1234']"
        )
        self.assertIsNotNone(receiver_1)
        self.assertIsNotNone(receiver_2)
        self.assertIsNotNone(receiver_3)


class PyscriptTests(PlaywrightTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.page.goto(f"http://{cls.host}:{cls._port}/pyscript/")

    def test_0_hello_world(self):
        self.page.wait_for_selector("#hello-world-loading")
        self.page.wait_for_selector("#hello-world")

    def test_custom_root(self):
        self.page.wait_for_selector("#custom-root")

    def test_multifile(self):
        self.page.wait_for_selector("#multifile-parent")
        self.page.wait_for_selector("#multifile-child")

    def test_counter(self):
        self.page.wait_for_selector("#counter")
        self.page.wait_for_selector("#counter pre[data-value='0']")
        self.page.wait_for_selector("#counter .plus").click(delay=CLICK_DELAY)
        self.page.wait_for_selector("#counter pre[data-value='1']")
        self.page.wait_for_selector("#counter .plus").click(delay=CLICK_DELAY)
        self.page.wait_for_selector("#counter pre[data-value='2']")
        self.page.wait_for_selector("#counter .minus").click(delay=CLICK_DELAY)
        self.page.wait_for_selector("#counter pre[data-value='1']")

    def test_server_side_parent(self):
        self.page.wait_for_selector("#parent")
        self.page.wait_for_selector("#child")
        self.page.wait_for_selector("#child pre[data-value='0']")
        self.page.wait_for_selector("#child .plus").click(delay=CLICK_DELAY)
        self.page.wait_for_selector("#child pre[data-value='1']")
        self.page.wait_for_selector("#child .plus").click(delay=CLICK_DELAY)
        self.page.wait_for_selector("#child pre[data-value='2']")
        self.page.wait_for_selector("#child .minus").click(delay=CLICK_DELAY)
        self.page.wait_for_selector("#child pre[data-value='1']")

    def test_server_side_parent_with_toggle(self):
        self.page.wait_for_selector("#parent-toggle")
        self.page.wait_for_selector("#parent-toggle button").click(delay=CLICK_DELAY)
        self.page.wait_for_selector("#parent-toggle")
        self.page.wait_for_selector("#parent-toggle pre[data-value='0']")
        self.page.wait_for_selector("#parent-toggle .plus").click(delay=CLICK_DELAY)
        self.page.wait_for_selector("#parent-toggle pre[data-value='1']")
        self.page.wait_for_selector("#parent-toggle .plus").click(delay=CLICK_DELAY)
        self.page.wait_for_selector("#parent-toggle pre[data-value='2']")
        self.page.wait_for_selector("#parent-toggle .minus").click(delay=CLICK_DELAY)
        self.page.wait_for_selector("#parent-toggle pre[data-value='1']")

    def test_javascript_module_execution_within_pyscript(self):
        self.page.wait_for_selector("#moment[data-success=true]")


class DistributedComputingTests(PlaywrightTestCase):

    @classmethod
    def setUpServer(cls):
        super().setUpServer()
        cls._server_process2 = cls.ProtocolServerProcess(cls.host, cls.get_application)
        cls._server_process2.start()
        cls._server_process2.ready.wait()
        cls._port2 = cls._server_process2.port.value

    @classmethod
    def tearDownServer(cls):
        super().tearDownServer()
        cls._server_process2.terminate()
        cls._server_process2.join()

    def test_host_roundrobin(self):
        """Verify if round-robin host selection is working."""
        self.page.goto(
            f"{self.live_server_url}/roundrobin/{self._port}/{self._port2}/8"
        )
        elem0 = self.page.locator(".custom_host-0")
        elem1 = self.page.locator(".custom_host-1")
        elem2 = self.page.locator(".custom_host-2")
        elem3 = self.page.locator(".custom_host-3")

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

    def test_custom_host(self):
        """Make sure that the component is rendered by a separate server."""
        self.page.goto(f"{self.live_server_url}/port/{self._port2}/")
        elem = self.page.locator(".custom_host-0")
        elem.wait_for()
        self.assertIn(
            f"Server Port: {self._port2}",
            elem.text_content(),
        )

    def test_custom_host_wrong_port(self):
        """Make sure that other ports are not rendering components."""
        tmp_sock = socket.socket()
        tmp_sock.bind((self._server_process.host, 0))
        random_port = tmp_sock.getsockname()[1]
        self.page.goto(f"{self.live_server_url}/port/{random_port}/")
        with self.assertRaises(TimeoutError):
            self.page.locator(".custom_host").wait_for(timeout=1000)


class OfflineTests(PlaywrightTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.page.goto(f"http://{cls.host}:{cls._port}/offline/")

    def test_offline_components(self):
        self.page.wait_for_selector("div:not([hidden]) > #online")
        self.assertIsNotNone(self.page.query_selector("div[hidden] > #offline"))
        self._server_process.terminate()
        self._server_process.join()
        self.page.wait_for_selector("div:not([hidden]) > #offline")
        self.assertIsNotNone(self.page.query_selector("div[hidden] > #online"))
