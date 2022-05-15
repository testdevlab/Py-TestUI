import pytest
from selenium.webdriver.chrome.options import Options

from testui.elements.testui_element import e
from testui.support import logger
from testui.support.appium_driver import NewDriver
from testui.support.testui_driver import TestUIDriver


class TestMethods:
    @pytest.yield_fixture(autouse=True)
    def selenium_driver(self):
        options = Options()
        options.add_argument("disable-user-media-security")
        driver = (
            NewDriver()
            .set_logger()
            .set_browser("chrome")
            .set_soft_assert(True)
            .set_selenium_driver(chrome_options=options)
        )
        yield driver
        driver.quit()

    @pytest.mark.sanity
    def test_sanity(self, selenium_driver: TestUIDriver):
        logger.log_test_name("T01: API command sanity test")
        # Navigate to demo page and login
        selenium_driver.navigate_to("https://saucedemo.com")
        e(selenium_driver, "css", "#user-name").send_keys("standard_user")
        e(selenium_driver, "css", "#password").send_keys("secret_sauce")
        e(selenium_driver, "css", "#login-button").click()

        # Make sure that page is loaded and use image recognition to verify that
        # the "robot" is visible.
        e(selenium_driver, "css", ".inventory_item_name").wait_until_visible()
        selenium_driver.find_image_match(
            "resources/image_reco_robot.png", 0.4, True, image_match="image.png"
        )
        selenium_driver.raise_errors()
