# type: ignore
# ruff: noqa: RUF012, N802
import os
import socket
from time import sleep
from uuid import uuid4

import pytest
from playwright.sync_api import TimeoutError, expect

from reactpy_django.models import ComponentSession
from reactpy_django.utils import str_to_bool

from .utils import GITHUB_ACTIONS, PlaywrightTestCase, navigate_to_page

CLICK_DELAY = 250 if str_to_bool(GITHUB_ACTIONS) else 25  # Delay in miliseconds.


class ComponentTests(PlaywrightTestCase):
    databases = {"default"}

    ###########################
    # Generic Component Tests #
    ###########################

    @navigate_to_page("/")
    def test_component_hello_world(self):
        self.page.wait_for_selector("#hello-world")

    @navigate_to_page("/")
    def test_component_counter(self):
        for i in range(5):
            self.page.locator(f"#counter-num[data-count={i}]")
            self.page.locator("#counter-inc").click(delay=CLICK_DELAY)

    @navigate_to_page("/")
    def test_component_parametrized_component(self):
        self.page.locator("#parametrized-component[data-value='579']").wait_for()

    @navigate_to_page("/")
    def test_component_object_in_templatetag(self):
        self.page.locator("#object_in_templatetag[data-success=true]").wait_for()

    @navigate_to_page("/")
    def test_component_from_web_module(self):
        self.page.wait_for_selector("#button-from-js-module")

    @navigate_to_page("/")
    def test_component_use_connection(self):
        self.page.locator("#use-connection[data-success=true]").wait_for()

    @navigate_to_page("/")
    def test_component_use_scope(self):
        self.page.locator("#use-scope[data-success=true]").wait_for()

    @navigate_to_page("/")
    def test_component_use_location(self):
        self.page.locator("#use-location[data-success=true]").wait_for()

    @navigate_to_page("/")
    def test_component_use_origin(self):
        self.page.locator("#use-origin[data-success=true]").wait_for()

    @navigate_to_page("/")
    def test_component_static_css(self):
        assert (
            self.page.wait_for_selector("#django-css button").evaluate(
                "e => window.getComputedStyle(e).getPropertyValue('color')"
            )
            == "rgb(0, 0, 255)"
        )

    @navigate_to_page("/")
    def test_component_static_js(self):
        self.page.locator("#django-js[data-success=true]").wait_for()

    @navigate_to_page("/")
    def test_component_unauthorized_user(self):
        with pytest.raises(TimeoutError):
            self.page.wait_for_selector("#unauthorized-user", timeout=1)
        self.page.wait_for_selector("#unauthorized-user-fallback")

    @navigate_to_page("/")
    def test_component_authorized_user(self):
        with pytest.raises(TimeoutError):
            self.page.wait_for_selector("#authorized-user-fallback", timeout=1)
        self.page.wait_for_selector("#authorized-user")

    @navigate_to_page("/")
    def test_component_relational_query(self):
        self.page.locator("#relational-query").wait_for()
        self.page.locator("#relational-query[data-success=true]").wait_for()

    @navigate_to_page("/")
    def test_component_async_relational_query(self):
        self.page.locator("#async-relational-query").wait_for()
        self.page.locator("#async-relational-query[data-success=true]").wait_for()

    @navigate_to_page("/")
    def test_component_use_query_and_mutation(self):
        todo_input = self.page.wait_for_selector("#todo-input")

        item_ids = list(range(5))

        for i in item_ids:
            todo_input.type(f"sample-{i}", delay=CLICK_DELAY)
            todo_input.press("Enter", delay=CLICK_DELAY)
            self.page.wait_for_selector(f"#todo-list #todo-item-sample-{i}")
            self.page.wait_for_selector(f"#todo-list #todo-item-sample-{i}-checkbox").click(delay=CLICK_DELAY)
            with pytest.raises(TimeoutError):
                self.page.wait_for_selector(f"#todo-list #todo-item-sample-{i}", timeout=1)

    @navigate_to_page("/")
    def test_component_async_use_query_and_mutation(self):
        todo_input = self.page.wait_for_selector("#async-todo-input")

        item_ids = list(range(5))

        for i in item_ids:
            todo_input.type(f"sample-{i}", delay=CLICK_DELAY)
            todo_input.press("Enter", delay=CLICK_DELAY)
            self.page.wait_for_selector(f"#async-todo-list #todo-item-sample-{i}")
            self.page.wait_for_selector(f"#async-todo-list #todo-item-sample-{i}-checkbox").click(delay=CLICK_DELAY)
            with pytest.raises(TimeoutError):
                self.page.wait_for_selector(f"#async-todo-list #todo-item-sample-{i}", timeout=1)

    @navigate_to_page("/")
    def test_component_view_to_component_sync_func(self):
        self.page.locator("#view_to_component_sync_func[data-success=true]").wait_for()

    @navigate_to_page("/")
    def test_component_view_to_component_async_func(self):
        self.page.locator("#view_to_component_async_func[data-success=true]").wait_for()

    @navigate_to_page("/")
    def test_component_view_to_component_sync_class(self):
        self.page.locator("#ViewToComponentSyncClass[data-success=true]").wait_for()

    @navigate_to_page("/")
    def test_component_view_to_component_async_class(self):
        self.page.locator("#ViewToComponentAsyncClass[data-success=true]").wait_for()

    @navigate_to_page("/")
    def test_component_view_to_component_template_view_class(self):
        self.page.locator("#ViewToComponentTemplateViewClass[data-success=true]").wait_for()

    @navigate_to_page("/")
    def _click_btn_and_check_success(self, name):
        self.page.locator(f"#{name}:not([data-success=true])").wait_for()
        self.page.wait_for_selector(f"#{name}_btn").click(delay=CLICK_DELAY)
        self.page.locator(f"#{name}[data-success=true]").wait_for()

    @navigate_to_page("/")
    def test_component_view_to_component_script(self):
        self._click_btn_and_check_success("view_to_component_script")

    @navigate_to_page("/")
    def test_component_view_to_component_request(self):
        self._click_btn_and_check_success("view_to_component_request")

    @navigate_to_page("/")
    def test_component_view_to_component_args(self):
        self._click_btn_and_check_success("view_to_component_args")

    @navigate_to_page("/")
    def test_component_view_to_component_kwargs(self):
        self._click_btn_and_check_success("view_to_component_kwargs")

    @navigate_to_page("/")
    def test_component_view_to_iframe_sync_func(self):
        self.page.frame_locator("#view_to_iframe_sync_func > iframe").locator(
            "#view_to_iframe_sync_func[data-success=true]"
        ).wait_for()

    @navigate_to_page("/")
    def test_component_view_to_iframe_async_func(self):
        self.page.frame_locator("#view_to_iframe_async_func > iframe").locator(
            "#view_to_iframe_async_func[data-success=true]"
        ).wait_for()

    @navigate_to_page("/")
    def test_component_view_to_iframe_sync_class(self):
        self.page.frame_locator("#view_to_iframe_sync_class > iframe").locator(
            "#ViewToIframeSyncClass[data-success=true]"
        ).wait_for()

    @navigate_to_page("/")
    def test_component_view_to_iframe_async_class(self):
        self.page.frame_locator("#view_to_iframe_async_class > iframe").locator(
            "#ViewToIframeAsyncClass[data-success=true]"
        ).wait_for()

    @navigate_to_page("/")
    def test_component_view_to_iframe_template_view_class(self):
        self.page.frame_locator("#view_to_iframe_template_view_class > iframe").locator(
            "#ViewToIframeTemplateViewClass[data-success=true]"
        ).wait_for()

    @navigate_to_page("/")
    def test_component_view_to_iframe_args(self):
        self.page.frame_locator("#view_to_iframe_args > iframe").locator(
            "#view_to_iframe_args[data-success=Success]"
        ).wait_for()

    @navigate_to_page("/")
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
        assert query_exists

    @navigate_to_page("/")
    def test_component_session_missing(self):
        """No session should exist for components that don't have args/kwargs."""
        component = self.page.locator("#use-scope")
        component.wait_for()
        parent = component.locator("..")
        session_id = parent.get_attribute("id")
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        query = ComponentSession.objects.filter(uuid=session_id)
        query_exists = query.exists()
        os.environ.pop("DJANGO_ALLOW_ASYNC_UNSAFE")
        assert not query_exists

    @navigate_to_page("/")
    def test_component_use_user_data(self):
        text_input = self.page.wait_for_selector("#use-user-data input")
        login_1 = self.page.wait_for_selector("#use-user-data .login-1")
        login_2 = self.page.wait_for_selector("#use-user-data .login-2")
        logout = self.page.wait_for_selector("#use-user-data .logout")
        clear = self.page.wait_for_selector("#use-user-data .clear")

        # Test AnonymousUser data
        user_data_div = self.page.wait_for_selector(
            "#use-user-data[data-success=false][data-fetch-error=false][data-mutation-error=false][data-loading=false][data-username=AnonymousUser]"
        )
        assert "Data: None" in user_data_div.text_content()

        # Test first user's data
        login_1.click(delay=CLICK_DELAY)
        user_data_div = self.page.wait_for_selector(
            "#use-user-data[data-success=false][data-fetch-error=false][data-mutation-error=false][data-loading=false][data-username=user_1]"
        )
        assert "Data: {}" in user_data_div.text_content()
        text_input.type("test", delay=CLICK_DELAY)
        text_input.press("Enter", delay=CLICK_DELAY)
        user_data_div = self.page.wait_for_selector(
            "#use-user-data[data-success=true][data-fetch-error=false][data-mutation-error=false][data-loading=false][data-username=user_1]"
        )
        assert "Data: {'test': 'test'}" in user_data_div.text_content()

        # Test second user's data
        login_2.click(delay=CLICK_DELAY)
        user_data_div = self.page.wait_for_selector(
            "#use-user-data[data-success=false][data-fetch-error=false][data-mutation-error=false][data-loading=false][data-username=user_2]"
        )
        assert "Data: {}" in user_data_div.text_content()
        text_input.press("Control+A", delay=CLICK_DELAY)
        text_input.press("Backspace", delay=CLICK_DELAY)
        text_input.type("test 2", delay=CLICK_DELAY)
        text_input.press("Enter", delay=CLICK_DELAY)
        user_data_div = self.page.wait_for_selector(
            "#use-user-data[data-success=true][data-fetch-error=false][data-mutation-error=false][data-loading=false][data-username=user_2]"
        )
        assert "Data: {'test 2': 'test 2'}" in user_data_div.text_content()

        # Attempt to clear data
        clear.click(delay=CLICK_DELAY)
        user_data_div = self.page.wait_for_selector(
            "#use-user-data[data-success=false][data-fetch-error=false][data-mutation-error=false][data-loading=false][data-username=user_2]"
        )
        assert "Data: {}" in user_data_div.text_content()

        # Attempt to logout
        logout.click(delay=CLICK_DELAY)
        user_data_div = self.page.wait_for_selector(
            "#use-user-data[data-success=false][data-fetch-error=false][data-mutation-error=false][data-loading=false][data-username=AnonymousUser]"
        )
        assert "Data: None" in user_data_div.text_content()

    @navigate_to_page("/")
    def test_component_use_user_data_with_default(self):
        text_input = self.page.wait_for_selector("#use-user-data-with-default input")
        login_3 = self.page.wait_for_selector("#use-user-data-with-default .login-3")
        clear = self.page.wait_for_selector("#use-user-data-with-default .clear")

        # Test AnonymousUser data
        user_data_div = self.page.wait_for_selector(
            "#use-user-data-with-default[data-fetch-error=false][data-mutation-error=false][data-loading=false][data-username=AnonymousUser]"
        )
        assert "Data: None" in user_data_div.text_content()

        # Test first user's data
        login_3.click(delay=CLICK_DELAY)
        user_data_div = self.page.wait_for_selector(
            "#use-user-data-with-default[data-fetch-error=false][data-mutation-error=false][data-loading=false][data-username=user_3]"
        )
        assert "Data: {'default1': 'value', 'default2': 'value2', 'default3': 'value3'}" in user_data_div.text_content()
        text_input.type("test", delay=CLICK_DELAY)
        text_input.press("Enter", delay=CLICK_DELAY)
        user_data_div = self.page.wait_for_selector(
            "#use-user-data-with-default[data-fetch-error=false][data-mutation-error=false][data-loading=false][data-username=user_3]"
        )
        assert (
            "Data: {'default1': 'value', 'default2': 'value2', 'default3': 'value3', 'test': 'test'}"
            in user_data_div.text_content()
        )

        # Attempt to clear data
        clear.click(delay=CLICK_DELAY)
        sleep(0.25)
        user_data_div = self.page.wait_for_selector(
            "#use-user-data-with-default[data-fetch-error=false][data-mutation-error=false][data-loading=false][data-username=user_3]"
        )
        assert "Data: {'default1': 'value', 'default2': 'value2', 'default3': 'value3'}" in user_data_div.text_content()

    @navigate_to_page("/")
    def test_component_use_auth(self):
        uuid = self.page.wait_for_selector("#use-auth").get_attribute("data-uuid")
        assert len(uuid) == 36

        self.page.wait_for_selector("#use-auth .login").click(delay=CLICK_DELAY)

        # Wait for #use-auth[data-username="user_4"] to appear
        self.page.wait_for_selector("#use-auth[data-username='user_4']")
        self.page.wait_for_selector(f"#use-auth[data-uuid='{uuid}']")

        # Press disconnect and wait for #use-auth[data-uuid=...] to disappear
        self.page.wait_for_selector("#use-auth .disconnect").click(delay=CLICK_DELAY)
        expect(self.page.locator(f"#use-auth[data-uuid='{uuid}']")).to_have_count(0)

        # Double check that the same user is logged in
        self.page.wait_for_selector("#use-auth[data-username='user_4']")

        # Press logout and wait for #use-auth[data-username="AnonymousUser"] to appear
        self.page.wait_for_selector("#use-auth .logout").click(delay=CLICK_DELAY)
        self.page.wait_for_selector("#use-auth[data-username='AnonymousUser']")

        # Press disconnect and wait for #use-auth[data-uuid=...] to disappear
        self.page.wait_for_selector("#use-auth .disconnect").click(delay=CLICK_DELAY)
        expect(self.page.locator(f"#use-auth[data-uuid='{uuid}']")).to_have_count(0)

        # Double check that the user stayed logged out
        self.page.wait_for_selector("#use-auth[data-username='AnonymousUser']")

    # FIXME: This test is flaky on GitHub Actions for unknown reasons.
    # Fails at: self.page.wait_for_selector("#use-auth-no-rerender[data-username='user_5']")

    # @navigate_to_page("/")
    # def test_component_use_auth_no_rerender(self):
    #     uuid = self.page.wait_for_selector("#use-auth-no-rerender").get_attribute("data-uuid")
    #     assert len(uuid) == 36

    #     self.page.wait_for_selector("#use-auth-no-rerender .login").click(delay=CLICK_DELAY)

    #     # Make sure #use-auth[data-username="user_5"] does not appear
    #     with pytest.raises(TimeoutError):
    #         self.page.wait_for_selector("#use-auth-no-rerender[data-username='user_5']", timeout=1)

    #     # Press disconnect and see if #use-auth[data-username="user_5"] appears
    #     self.page.wait_for_selector("#use-auth-no-rerender .disconnect").click(delay=CLICK_DELAY)
    #     self.page.wait_for_selector("#use-auth-no-rerender[data-username='user_5']")

    #     # Press logout and make sure #use-auth[data-username="AnonymousUser"] does not appear
    #     with pytest.raises(TimeoutError):
    #         self.page.wait_for_selector("#use-auth-no-rerender[data-username='AnonymousUser']", timeout=1)

    #     # Press disconnect and see if #use-auth[data-username="AnonymousUser"] appears
    #     self.page.wait_for_selector("#use-auth-no-rerender .disconnect").click(delay=CLICK_DELAY)

    @navigate_to_page("/")
    def test_component_use_rerender(self):
        initial_uuid = self.page.wait_for_selector("#use-rerender").get_attribute("data-uuid")
        assert len(initial_uuid) == 36

        rerender_button = self.page.wait_for_selector("#use-rerender button")
        rerender_button.click(delay=CLICK_DELAY)

        # Wait for #use-rerender[data-uuid=...] to disappear
        expect(self.page.locator(f"#use-rerender[data-uuid='{initial_uuid}']")).to_have_count(0)

        # Find the new #use-rerender[data-uuid=...]
        self.page.wait_for_selector("#use-rerender")
        new_uuid = self.page.wait_for_selector("#use-rerender").get_attribute("data-uuid")
        assert len(new_uuid) == 36
        assert new_uuid != initial_uuid

    ###################
    # Prerender Tests #
    ###################

    @navigate_to_page("/prerender/")
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
        assert string.all_inner_texts() == ["prerender_string: Prerendered"]
        assert vdom.all_inner_texts() == ["prerender_vdom: Prerendered"]
        assert component.all_inner_texts() == ["prerender_component: Prerendered"]
        root_id_value = use_root_id_http.get_attribute("data-value")
        assert len(root_id_value) == 36

        # Check if the full render occurred
        sleep(2)
        assert string.all_inner_texts() == ["prerender_string: Fully Rendered"]
        assert vdom.all_inner_texts() == ["prerender_vdom: Fully Rendered"]
        assert component.all_inner_texts() == ["prerender_component: Fully Rendered"]
        use_root_id_ws.wait_for()
        use_user_ws.wait_for()
        assert use_root_id_ws.get_attribute("data-value") == root_id_value

    ###############
    # Error Tests #
    ###############

    @navigate_to_page("/errors/")
    def test_error_component_does_not_exist(self):
        broken_component = self.page.locator("#component_does_not_exist_error")
        broken_component.wait_for()
        assert "ComponentDoesNotExistError:" in broken_component.text_content()

    @navigate_to_page("/errors/")
    def test_error_component_param(self):
        broken_component = self.page.locator("#component_param_error")
        broken_component.wait_for()
        assert "ComponentParamError:" in broken_component.text_content()

    @navigate_to_page("/errors/")
    def test_error_invalid_host(self):
        broken_component = self.page.locator("#invalid_host_error")
        broken_component.wait_for()
        assert "InvalidHostError:" in broken_component.text_content()

    @navigate_to_page("/errors/")
    def test_error_synchronous_only_operation(self):
        broken_component = self.page.locator("#broken_postprocessor_query pre")
        broken_component.wait_for()
        assert "SynchronousOnlyOperation:" in broken_component.text_content()

    @navigate_to_page("/errors/")
    def test_error_view_not_registered(self):
        broken_component = self.page.locator("#view_to_iframe_not_registered pre")
        broken_component.wait_for()
        assert "ViewNotRegisteredError:" in broken_component.text_content()

    @navigate_to_page("/errors/")
    def test_error_decorator_param(self):
        broken_component = self.page.locator("#incorrect_user_passes_test_decorator")
        broken_component.wait_for()
        assert "DecoratorParamError:" in broken_component.text_content()

    ####################
    # URL Router Tests #
    ####################

    def test_url_router(self):
        self.page.goto(f"{self.live_server_url}/router/")
        path = self.page.wait_for_selector("#router-path")
        assert "/router/" in path.get_attribute("data-path")
        string = self.page.query_selector("#router-string")
        assert string.text_content() == "/router/"

    def test_url_router_subroute(self):
        self.page.goto(f"{self.live_server_url}/router/subroute/")
        path = self.page.wait_for_selector("#router-path")
        assert "/router/subroute/" in path.get_attribute("data-path")
        string = self.page.query_selector("#router-string")
        assert string.text_content() == "subroute/"

    def test_url_unspecified(self):
        self.page.goto(f"{self.live_server_url}/router/unspecified/123/")
        path = self.page.wait_for_selector("#router-path")
        assert "/router/unspecified/123/" in path.get_attribute("data-path")
        string = self.page.query_selector("#router-string")
        assert string.text_content() == "/router/unspecified/<value>/"

    def test_url_router_integer(self):
        self.page.goto(f"{self.live_server_url}/router/integer/123/")
        path = self.page.wait_for_selector("#router-path")
        assert "/router/integer/123/" in path.get_attribute("data-path")
        string = self.page.query_selector("#router-string")
        assert string.text_content() == "/router/integer/<int:value>/"

    def test_url_router_path(self):
        self.page.goto(f"{self.live_server_url}/router/path/abc/123/")
        path = self.page.wait_for_selector("#router-path")
        assert "/router/path/abc/123/" in path.get_attribute("data-path")
        string = self.page.query_selector("#router-string")
        assert string.text_content() == "/router/path/<path:value>/"

    def test_url_router_slug(self):
        self.page.goto(f"{self.live_server_url}/router/slug/abc-123/")
        path = self.page.wait_for_selector("#router-path")
        assert "/router/slug/abc-123/" in path.get_attribute("data-path")
        string = self.page.query_selector("#router-string")
        assert string.text_content() == "/router/slug/<slug:value>/"

    def test_url_router_string(self):
        self.page.goto(f"{self.live_server_url}/router/string/abc/")
        path = self.page.wait_for_selector("#router-path")
        assert "/router/string/abc/" in path.get_attribute("data-path")
        string = self.page.query_selector("#router-string")
        assert string.text_content() == "/router/string/<str:value>/"

    def test_url_router_uuid(self):
        self.page.goto(f"{self.live_server_url}/router/uuid/123e4567-e89b-12d3-a456-426614174000/")
        path = self.page.wait_for_selector("#router-path")
        assert "/router/uuid/123e4567-e89b-12d3-a456-426614174000/" in path.get_attribute("data-path")
        string = self.page.query_selector("#router-string")
        assert string.text_content() == "/router/uuid/<uuid:value>/"

    def test_url_router_any(self):
        self.page.goto(f"{self.live_server_url}/router/any/adslkjgklasdjhfah/6789543256/")
        path = self.page.wait_for_selector("#router-path")
        assert "/router/any/adslkjgklasdjhfah/6789543256/" in path.get_attribute("data-path")
        string = self.page.query_selector("#router-string")
        assert string.text_content() == "/router/any/<any:name>"

    def test_url_router_int_and_string(self):
        self.page.goto(f"{self.live_server_url}/router/two/123/abc/")
        path = self.page.wait_for_selector("#router-path")
        assert "/router/two/123/abc/" in path.get_attribute("data-path")
        string = self.page.query_selector("#router-string")
        assert string.text_content() == "/router/two/<int:value>/<str:value2>/"

    #######################
    # Channel Layer Tests #
    #######################

    @navigate_to_page("/channel-layers/")
    def test_channel_layer_components(self):
        sender = self.page.wait_for_selector("#sender")
        sender.type("test", delay=CLICK_DELAY)
        sender.press("Enter", delay=CLICK_DELAY)
        receiver = self.page.wait_for_selector("#receiver[data-message='test']")
        assert receiver is not None

        sender = self.page.wait_for_selector("#group-sender")
        sender.type("1234", delay=CLICK_DELAY)
        sender.press("Enter", delay=CLICK_DELAY)
        receiver_1 = self.page.wait_for_selector("#group-receiver-1[data-message='1234']")
        receiver_2 = self.page.wait_for_selector("#group-receiver-2[data-message='1234']")
        receiver_3 = self.page.wait_for_selector("#group-receiver-3[data-message='1234']")
        assert receiver_1 is not None
        assert receiver_2 is not None
        assert receiver_3 is not None

    ##################
    # PyScript Tests #
    ##################

    @navigate_to_page("/pyscript/")
    def test_pyscript_0_hello_world(self):
        # Use this test to wait for PyScript to fully load on the page
        self.page.wait_for_selector("#hello-world-loading")
        self.page.wait_for_selector("#hello-world")

    @navigate_to_page("/pyscript/")
    def test_pyscript_1_custom_root(self):
        self.page.wait_for_selector("#custom-root")

    @navigate_to_page("/pyscript/")
    def test_pyscript_1_multifile(self):
        self.page.wait_for_selector("#multifile-parent")
        self.page.wait_for_selector("#multifile-child")

    @navigate_to_page("/pyscript/")
    def test_pyscript_1_counter(self):
        self.page.wait_for_selector("#counter")
        self.page.wait_for_selector("#counter pre[data-value='0']")
        self.page.wait_for_selector("#counter .plus").click(delay=CLICK_DELAY)
        self.page.wait_for_selector("#counter pre[data-value='1']")
        self.page.wait_for_selector("#counter .plus").click(delay=CLICK_DELAY)
        self.page.wait_for_selector("#counter pre[data-value='2']")
        self.page.wait_for_selector("#counter .minus").click(delay=CLICK_DELAY)
        self.page.wait_for_selector("#counter pre[data-value='1']")

    @navigate_to_page("/pyscript/")
    def test_pyscript_1_server_side_parent(self):
        self.page.wait_for_selector("#parent")
        self.page.wait_for_selector("#child")
        self.page.wait_for_selector("#child pre[data-value='0']")
        self.page.wait_for_selector("#child .plus").click(delay=CLICK_DELAY)
        self.page.wait_for_selector("#child pre[data-value='1']")
        self.page.wait_for_selector("#child .plus").click(delay=CLICK_DELAY)
        self.page.wait_for_selector("#child pre[data-value='2']")
        self.page.wait_for_selector("#child .minus").click(delay=CLICK_DELAY)
        self.page.wait_for_selector("#child pre[data-value='1']")

    @navigate_to_page("/pyscript/")
    def test_pyscript_1_server_side_parent_with_toggle(self):
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

    @navigate_to_page("/pyscript/")
    def test_pyscript_1_javascript_module_execution_within_pyscript(self):
        self.page.wait_for_selector("#moment[data-success=true]")

    ###############################
    # Distributed Computing Tests #
    ###############################

    def test_distributed_host_roundrobin(self):
        """Verify if round-robin host selection is working."""
        self.page.goto(f"{self.live_server_url}/roundrobin/{self._port_2}/{self._port_3}/8")
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
            str(self._port_2),
            str(self._port_3),
        }

        # There should only be two ports in the set
        assert current_ports == correct_ports
        assert len(current_ports) == 2

    def test_distributed_custom_host(self):
        """Make sure that the component is rendered by a separate server."""
        self.page.goto(f"{self.live_server_url}/port/{self._port_2}/")
        elem = self.page.locator(".custom_host-0")
        elem.wait_for()
        assert f"Server Port: {self._port_2}" in elem.text_content()

    def test_distributed_custom_host_wrong_port(self):
        """Make sure that other ports are not rendering components."""
        tmp_sock = socket.socket()
        tmp_sock.bind((self._server_process_0.host, 0))
        random_port = tmp_sock.getsockname()[1]
        self.page.goto(f"{self.live_server_url}/port/{random_port}/")
        with pytest.raises(TimeoutError):
            self.page.locator(".custom_host").wait_for(timeout=1000)

    #################
    # Offline Tests #
    #################

    @navigate_to_page("/offline/", server_num=1)
    def test_offline_component(self):
        self.page.wait_for_selector("div:not([hidden]) > #online")
        assert self.page.query_selector("div[hidden] > #offline") is not None
        self._server_process_1.terminate()
        self._server_process_1.join()
        self.page.wait_for_selector("div:not([hidden]) > #offline")
        assert self.page.query_selector("div[hidden] > #online") is not None

    ##############
    # Form Tests #
    ##############

    @navigate_to_page("/form/")
    def test_form_basic(self):
        try:
            from test_app.models import TodoItem

            os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

            if TodoItem.objects.count() == 0:
                TodoItem(done=False, text="First").save()
                TodoItem(done=True, text="Second").save()
                TodoItem(done=False, text="Third").save()
        finally:
            os.environ.pop("DJANGO_ALLOW_ASYNC_UNSAFE")

        self.page.wait_for_selector("form")
        self.page.wait_for_selector("#id_boolean_field")
        self.page.wait_for_selector("#id_char_field")
        self.page.wait_for_selector("#id_choice_field")
        self.page.wait_for_selector("#id_date_field")
        self.page.wait_for_selector("#id_date_time_field")
        self.page.wait_for_selector("#id_decimal_field")
        self.page.wait_for_selector("#id_duration_field")
        self.page.wait_for_selector("#id_email_field")
        self.page.wait_for_selector("#id_file_path_field")
        self.page.wait_for_selector("#id_float_field")
        self.page.wait_for_selector("#id_generic_ip_address_field")
        self.page.wait_for_selector("#id_integer_field")
        self.page.wait_for_selector("#id_float_field")
        self.page.wait_for_selector("#id_json_field")
        self.page.wait_for_selector("#id_multiple_choice_field")
        self.page.wait_for_selector("#id_null_boolean_field")
        self.page.wait_for_selector("#id_regex_field")
        self.page.wait_for_selector("#id_slug_field")
        self.page.wait_for_selector("#id_time_field")
        self.page.wait_for_selector("#id_typed_choice_field")
        self.page.wait_for_selector("#id_typed_multiple_choice_field")
        self.page.wait_for_selector("#id_url_field")
        self.page.wait_for_selector("#id_uuid_field")
        self.page.wait_for_selector("#id_combo_field")
        self.page.wait_for_selector("#id_password_field")
        self.page.wait_for_selector("#id_model_choice_field")
        self.page.wait_for_selector("#id_model_multiple_choice_field")

        sleep(1)
        self.page.wait_for_selector("input[type=submit]").click(delay=CLICK_DELAY)
        self.page.wait_for_selector(".errorlist")

        # Submitting an empty form should result in 22 error elements.
        # The number of errors may change if/when new test form elements are created.
        assert len(self.page.query_selector_all(".errorlist")) == 22

        # Fill out the form
        self.page.wait_for_selector("#id_boolean_field").click(delay=CLICK_DELAY)
        expect(self.page.locator("#id_boolean_field")).to_be_checked()

        self.page.locator("#id_char_field").type("test", delay=CLICK_DELAY)
        self.page.locator("#id_choice_field").select_option("2")
        self.page.locator("#id_date_field").type("2021-01-01", delay=CLICK_DELAY)
        self.page.locator("#id_date_time_field").type("2021-01-01 01:01:00", delay=CLICK_DELAY)
        self.page.locator("#id_decimal_field").type("0.123", delay=CLICK_DELAY)
        self.page.locator("#id_duration_field").type("1", delay=CLICK_DELAY)
        self.page.locator("#id_email_field").type("test@example.com", delay=CLICK_DELAY)
        file_path_field_options = self.page.query_selector_all("#id_file_path_field option")
        file_path_field_values: list[str] = [option.get_attribute("value") for option in file_path_field_options]
        self.page.locator("#id_file_path_field").select_option(file_path_field_values[1])
        self.page.locator("#id_float_field").type("1.2345", delay=CLICK_DELAY)
        self.page.locator("#id_generic_ip_address_field").type("127.0.0.1", delay=CLICK_DELAY)
        self.page.locator("#id_integer_field").type("123", delay=CLICK_DELAY)
        self.page.locator("#id_json_field").clear()
        self.page.locator("#id_json_field").type('{"key": "value"}', delay=CLICK_DELAY)
        self.page.locator("#id_multiple_choice_field").select_option(["2", "3"])
        self.page.locator("#id_null_boolean_field").select_option("false")
        self.page.locator("#id_regex_field").type("12", delay=CLICK_DELAY)
        self.page.locator("#id_slug_field").type("my-slug-text", delay=CLICK_DELAY)
        self.page.locator("#id_time_field").type("01:01:00", delay=CLICK_DELAY)
        self.page.locator("#id_typed_choice_field").select_option("2")
        self.page.locator("#id_typed_multiple_choice_field").select_option(["1", "2"])
        self.page.locator("#id_url_field").type("http://example.com", delay=CLICK_DELAY)
        self.page.locator("#id_uuid_field").type("550e8400-e29b-41d4-a716-446655440000", delay=CLICK_DELAY)
        self.page.locator("#id_combo_field").type("test@example.com", delay=CLICK_DELAY)
        self.page.locator("#id_password_field").type("password", delay=CLICK_DELAY)
        model_choice_field_options = self.page.query_selector_all("#id_model_multiple_choice_field option")
        model_choice_field_values: list[str] = [option.get_attribute("value") for option in model_choice_field_options]
        self.page.locator("#id_model_choice_field").select_option(model_choice_field_values[0])
        self.page.locator("#id_model_multiple_choice_field").select_option([
            model_choice_field_values[1],
            model_choice_field_values[2],
        ])

        self.page.wait_for_selector("input[type=submit]").click(delay=CLICK_DELAY)

        # Wait for one of the error messages to disappear (indicating that the form has been re-rendered)
        expect(self.page.locator(".errorlist").all()[0]).not_to_be_attached()
        # Make sure no errors remain
        assert len(self.page.query_selector_all(".errorlist")) == 0

    @navigate_to_page("/form/bootstrap/")
    def test_form_bootstrap(self):
        try:
            from test_app.models import TodoItem

            os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

            if TodoItem.objects.count() == 0:
                TodoItem(done=False, text="First").save()
                TodoItem(done=True, text="Second").save()
                TodoItem(done=False, text="Third").save()
        finally:
            os.environ.pop("DJANGO_ALLOW_ASYNC_UNSAFE")

        self.page.wait_for_selector("form")
        self.page.wait_for_selector("#id_boolean_field")
        self.page.wait_for_selector("#id_char_field")
        self.page.wait_for_selector("#id_choice_field")
        self.page.wait_for_selector("#id_date_field")
        self.page.wait_for_selector("#id_date_time_field")
        self.page.wait_for_selector("#id_decimal_field")
        self.page.wait_for_selector("#id_duration_field")
        self.page.wait_for_selector("#id_email_field")
        self.page.wait_for_selector("#id_file_path_field")
        self.page.wait_for_selector("#id_float_field")
        self.page.wait_for_selector("#id_generic_ip_address_field")
        self.page.wait_for_selector("#id_integer_field")
        self.page.wait_for_selector("#id_float_field")
        self.page.wait_for_selector("#id_json_field")
        self.page.wait_for_selector("#id_multiple_choice_field")
        self.page.wait_for_selector("#id_null_boolean_field")
        self.page.wait_for_selector("#id_regex_field")
        self.page.wait_for_selector("#id_slug_field")
        self.page.wait_for_selector("#id_time_field")
        self.page.wait_for_selector("#id_typed_choice_field")
        self.page.wait_for_selector("#id_typed_multiple_choice_field")
        self.page.wait_for_selector("#id_url_field")
        self.page.wait_for_selector("#id_uuid_field")
        self.page.wait_for_selector("#id_combo_field")
        self.page.wait_for_selector("#id_password_field")
        self.page.wait_for_selector("#id_model_choice_field")
        self.page.wait_for_selector("#id_model_multiple_choice_field")

        sleep(1)
        self.page.wait_for_selector("button[type=submit]").click(delay=CLICK_DELAY)
        self.page.wait_for_selector(".invalid-feedback")

        # Submitting an empty form should result in 22 error elements.
        # The number of errors may change if/when new test form elements are created.
        assert len(self.page.query_selector_all(".invalid-feedback")) == 22

        # Fill out the form
        self.page.wait_for_selector("#id_boolean_field").click(delay=CLICK_DELAY)
        expect(self.page.locator("#id_boolean_field")).to_be_checked()

        self.page.locator("#id_char_field").type("test", delay=CLICK_DELAY)
        self.page.locator("#id_choice_field").select_option("2")
        self.page.locator("#id_date_field").type("2021-01-01", delay=CLICK_DELAY)
        self.page.locator("#id_date_time_field").type("2021-01-01 01:01:00", delay=CLICK_DELAY)
        self.page.locator("#id_decimal_field").type("0.123", delay=CLICK_DELAY)
        self.page.locator("#id_duration_field").type("1", delay=CLICK_DELAY)
        self.page.locator("#id_email_field").type("test@example.com", delay=CLICK_DELAY)
        file_path_field_options = self.page.query_selector_all("#id_file_path_field option")
        file_path_field_values: list[str] = [option.get_attribute("value") for option in file_path_field_options]
        self.page.locator("#id_file_path_field").select_option(file_path_field_values[1])
        self.page.locator("#id_float_field").type("1.2345", delay=CLICK_DELAY)
        self.page.locator("#id_generic_ip_address_field").type("127.0.0.1", delay=CLICK_DELAY)
        self.page.locator("#id_integer_field").type("123", delay=CLICK_DELAY)
        self.page.locator("#id_json_field").clear()
        self.page.locator("#id_json_field").type('{"key": "value"}', delay=CLICK_DELAY)
        self.page.locator("#id_multiple_choice_field").select_option(["2", "3"])
        self.page.locator("#id_null_boolean_field").select_option("false")
        self.page.locator("#id_regex_field").type("12", delay=CLICK_DELAY)
        self.page.locator("#id_slug_field").type("my-slug-text", delay=CLICK_DELAY)
        self.page.locator("#id_time_field").type("01:01:00", delay=CLICK_DELAY)
        self.page.locator("#id_typed_choice_field").select_option("2")
        self.page.locator("#id_typed_multiple_choice_field").select_option(["1", "2"])
        self.page.locator("#id_url_field").type("http://example.com", delay=CLICK_DELAY)
        self.page.locator("#id_uuid_field").type("550e8400-e29b-41d4-a716-446655440000", delay=CLICK_DELAY)
        self.page.locator("#id_combo_field").type("test@example.com", delay=CLICK_DELAY)
        self.page.locator("#id_password_field").type("password", delay=CLICK_DELAY)

        model_choice_field_options = self.page.query_selector_all("#id_model_multiple_choice_field option")
        model_choice_field_values: list[str] = [option.get_attribute("value") for option in model_choice_field_options]
        self.page.locator("#id_model_choice_field").select_option(model_choice_field_values[0])
        self.page.locator("#id_model_multiple_choice_field").select_option([
            model_choice_field_values[1],
            model_choice_field_values[2],
        ])

        self.page.wait_for_selector("button[type=submit]").click(delay=CLICK_DELAY)

        # Wait for one of the error messages to disappear (indicating that the form has been re-rendered)
        expect(self.page.locator(".invalid-feedback").all()[0]).not_to_be_attached()
        # Make sure no errors remain
        assert len(self.page.query_selector_all(".invalid-feedback")) == 0

    @navigate_to_page("/form/model/")
    def test_form_orm_model(self):
        uuid = uuid4().hex
        self.page.wait_for_selector("form")

        sleep(1)
        self.page.wait_for_selector("input[type=submit]").click(delay=CLICK_DELAY)
        self.page.wait_for_selector(".errorlist")

        # Submitting an empty form should result in 1 error element.
        error_list = self.page.locator(".errorlist").all()
        assert len(error_list) == 1

        # Fill out the form
        self.page.locator("#id_text").type(uuid, delay=CLICK_DELAY)

        # Submit the form
        self.page.wait_for_selector("input[type=submit]").click(delay=CLICK_DELAY)

        # Wait for the error message to disappear (indicating that the form has been re-rendered)
        expect(error_list[0]).not_to_be_attached()

        # Make sure no errors remain
        assert len(self.page.query_selector_all(".errorlist")) == 0

        # Check if `auto_save` created the TodoItem's database entry
        try:
            from test_app.models import TodoItem

            os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

            assert TodoItem.objects.filter(text=uuid).exists()
        finally:
            os.environ.pop("DJANGO_ALLOW_ASYNC_UNSAFE")

    # FIXME: Remove the `reruns` value once we fix flakiness of `test_sync_form_events`
    # https://github.com/reactive-python/reactpy-django/issues/272

    # @navigate_to_page("/form/sync_event/")
    # def test_form_sync_events(self):
    #     self.page.wait_for_selector("form")

    #     # Check initial state
    #     self.page.wait_for_selector("#success[data-value='false']")
    #     self.page.wait_for_selector("#error[data-value='false']")
    #     self.page.wait_for_selector("#receive_data[data-value='false']")
    #     self.page.wait_for_selector("#change[data-value='false']")

    #     # Submit empty the form
    #     sleep(1)
    #     self.page.wait_for_selector("input[type=submit]").click(delay=CLICK_DELAY)

    #     # The empty form was submitted, should result in an error
    #     self.page.wait_for_selector("#success[data-value='false']")
    #     self.page.wait_for_selector("#error[data-value='true']")
    #     self.page.wait_for_selector("#receive_data[data-value='true']")
    #     self.page.wait_for_selector("#change[data-value='false']")

    #     # Fill out the form and re-submit
    #     self.page.wait_for_selector("#id_char_field").type("test", delay=CLICK_DELAY)
    #     self.page.wait_for_selector("input[type=submit]").click(delay=CLICK_DELAY)

    #     # Form should have been successfully submitted
    #     self.page.wait_for_selector("#success[data-value='true']")
    #     self.page.wait_for_selector("#error[data-value='true']")
    #     self.page.wait_for_selector("#receive_data[data-value='true']")
    #     self.page.wait_for_selector("#change[data-value='true']")

    @navigate_to_page("/form/async_event/")
    def test_form_async_events(self):
        self.page.wait_for_selector("form")

        # Check initial state
        self.page.wait_for_selector("#success[data-value='false']")
        self.page.wait_for_selector("#error[data-value='false']")
        self.page.wait_for_selector("#receive_data[data-value='false']")
        self.page.wait_for_selector("#change[data-value='false']")

        # Submit empty the form
        sleep(1)
        self.page.wait_for_selector("input[type=submit]").click(delay=CLICK_DELAY)

        # The empty form was submitted, should result in an error
        self.page.wait_for_selector("#success[data-value='false']")
        self.page.wait_for_selector("#error[data-value='true']")
        self.page.wait_for_selector("#receive_data[data-value='true']")
        self.page.wait_for_selector("#change[data-value='false']")

        # Fill out the form and re-submit
        self.page.wait_for_selector("#id_char_field").type("test", delay=CLICK_DELAY)
        self.page.wait_for_selector("input[type=submit]").click(delay=CLICK_DELAY)

        # Form should have been successfully submitted
        self.page.wait_for_selector("#success[data-value='true']")
        self.page.wait_for_selector("#error[data-value='true']")
        self.page.wait_for_selector("#receive_data[data-value='true']")
        self.page.wait_for_selector("#change[data-value='true']")
