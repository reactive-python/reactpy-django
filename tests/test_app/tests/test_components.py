import os
import sys
from unittest import SkipTest

from channels.testing import ChannelsLiveServerTestCase
from playwright.sync_api import TimeoutError, sync_playwright


class TestIdomCapabilities(ChannelsLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        if sys.platform == "win32":
            raise SkipTest("These tests are broken on Windows due to Selenium")
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        headed = bool(int(os.environ.get("PLAYWRIGHT_HEADED", 0)))
        cls.browser = cls.playwright.chromium.launch(headless=not headed)
        cls.page = cls.browser.new_page()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.page.close()
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        super().setUp()
        self.page.goto(self.live_server_url)

    def test_hello_world(self):
        self.page.wait_for_selector("#hello-world")

    def test_counter(self):
        for i in range(5):
            self.page.locator(f"#counter-num[data-count={i}]")
            self.page.locator("#counter-inc").click()

    def test_parametrized_component(self):
        self.page.locator("#parametrized-component[data-value='579']").wait_for()

    def test_component_from_web_module(self):
        self.page.wait_for_selector(".VictoryContainer")

    def test_use_websocket(self):
        self.page.locator("#use-websocket[data-success=true]").wait_for()

    def test_use_scope(self):
        self.page.locator("#use-scope[data-success=true]").wait_for()

    def test_use_location(self):
        self.page.locator("#use-location[data-success=true]").wait_for()

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

    def test_use_query_and_mutation(self):
        todo_input = self.page.wait_for_selector("#todo-input")

        item_ids = list(range(5))

        for i in item_ids:
            todo_input.type(f"sample-{i}", delay=10)
            todo_input.press("Enter")
            self.page.wait_for_selector(f"#todo-item-sample-{i}")
            self.page.wait_for_selector(f"#todo-item-sample-{i}-checkbox").click()
            self.assertRaises(
                TimeoutError,
                self.page.wait_for_selector,
                f"#todo-item-sample-{i}",
                timeout=1,
            )
