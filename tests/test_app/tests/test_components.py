import os
import sys

from channels.testing import ChannelsLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


# These tests are broken on Windows due to Selenium
if sys.platform != "win32":

    class TestIdomCapabilities(ChannelsLiveServerTestCase):
        def setUp(self):
            self.driver = make_driver(5, 5)
            self.driver.get(self.live_server_url)

        def tearDown(self) -> None:
            self.driver.quit()

        def wait(self, timeout=10):
            return WebDriverWait(self.driver, timeout)

        def wait_until(self, condition, timeout=10):
            return self.wait(timeout).until(lambda driver: condition())

        def test_hello_world(self):
            self.driver.find_element_by_id("hello-world")

        def test_counter(self):
            button = self.driver.find_element_by_id("counter-inc")
            count = self.driver.find_element_by_id("counter-num")

            for i in range(5):
                self.wait_until(lambda: count.get_attribute("data-count") == str(i))
                button.click()

        def test_parametrized_component(self):
            element = self.driver.find_element_by_id("parametrized-component")
            self.assertEqual(element.get_attribute("data-value"), "579")

        def test_component_from_web_module(self):
            self.wait(20).until(
                expected_conditions.visibility_of_element_located(
                    (By.CLASS_NAME, "VictoryContainer")
                )
            )

        def test_use_websocket(self):
            element = self.driver.find_element_by_id("use-websocket")
            self.assertEqual(element.get_attribute("data-success"), "true")

        def test_use_scope(self):
            element = self.driver.find_element_by_id("use-scope")
            self.assertEqual(element.get_attribute("data-success"), "true")

        def test_use_location(self):
            element = self.driver.find_element_by_id("use-location")
            self.assertEqual(element.get_attribute("data-success"), "true")

        def test_static_css(self):
            element = self.driver.find_element_by_css_selector("#django-css button")
            self.assertEqual(
                element.value_of_css_property("color"), "rgba(0, 0, 255, 1)"
            )

        def test_static_js(self):
            element = self.driver.find_element_by_id("django-js")
            self.assertEqual(element.get_attribute("data-success"), "true")

        def test_unauthorized_user(self):
            self.assertRaises(
                NoSuchElementException,
                self.driver.find_element_by_id,
                "unauthorized-user",
            )
            element = self.driver.find_element_by_id("unauthorized-user-fallback")
            self.assertIsNotNone(element)

        def test_authorized_user(self):
            self.assertRaises(
                NoSuchElementException,
                self.driver.find_element_by_id,
                "authorized-user-fallback",
            )
            element = self.driver.find_element_by_id("authorized-user")
            self.assertIsNotNone(element)


def make_driver(page_load_timeout, implicit_wait_timeout):
    options = webdriver.ChromeOptions()
    options.headless = bool(int(os.environ.get("SELENIUM_HEADLESS", 0)))
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(page_load_timeout)
    driver.implicitly_wait(implicit_wait_timeout)
    return driver
