import os

from channels.testing import ChannelsLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait


class TestIdomCapabilities(ChannelsLiveServerTestCase):
    def setUp(self):
        self.driver = make_driver(5, 5)
        self.driver.get(self.live_server_url)

    def tearDown(self) -> None:
        self.driver.quit()

    def wait_until(self, condition, timeout=5):
        WebDriverWait(self.driver, timeout).until(lambda driver: condition())

    def test_hello_world(self):
        self.driver.find_element_by_id("hello-world")

    def test_counter(self):
        button = self.driver.find_element_by_id("counter-inc")
        count = self.driver.find_element_by_id("counter-num")

        for i in range(5):
            self.wait_until(lambda: count.get_attribute("data-count") == str(i))
            button.click()


def make_driver(page_load_timeout, implicit_wait_timeout):
    options = webdriver.ChromeOptions()
    options.headless = bool(int(os.environ.get("SELENIUM_HEADLESS", 0)))
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(page_load_timeout)
    driver.implicitly_wait(implicit_wait_timeout)
    return driver
