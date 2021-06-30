import pytest
from selenium.webdriver.chrome.options import Options

from tests.screens.landing import LandingScreen
from testui.elements.testui_element import e
from testui.support import logger
from testui.support.appium_driver import NewDriver
from testui.support.testui_driver import TestUIDriver
from selenium import webdriver
import os

class TestStringMethods(object):
    @pytest.yield_fixture(autouse=True)
    def selenium_driver(self):
        options = Options()
        options.add_argument("--remote-debugging-port=9222")
        # web_driver_path = "/Users/alvarolaserna/Github/Py-TestUI/node_modules/.bin/chromedriver"
        # service = webdriver.chrome.service.Service(web_driver_path)
        # service.start()
        # print(service.service_url)
        remote_app = webdriver.Remote(
        command_executor='http://127.0.0.1:9515',
        desired_capabilities={
            'browserName': 'chrome',
            'goog:chromeOptions': {
                'binary': "/Applications/Discord.app/Contents/MacOS/Discord",
                'args': ["--remote-debugging-port=9222"]
                }},
        options=options,
        browser_profile=None,
        proxy=None,
        keep_alive=False)
        driver = NewDriver() \
            .set_logger().set_driver(remote_app)
        e(driver, "xpath", "//*[contains(text(), \"Friends\")]").wait_until_visible(10)
        yield driver
        driver.quit()

    @pytest.mark.signup
    def test_sign_up_flow(self, selenium_driver: TestUIDriver):
        logger.log_test_name("T92701: Create an account")
        landing_page = LandingScreen(selenium_driver)
        landing_page.i_am_in_landing_screen()
        selenium_driver.raise_errors()
