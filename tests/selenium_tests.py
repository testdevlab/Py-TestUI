import pytest
import os
from selenium.webdriver.chrome.options import Options

from testui.elements.testui_element import e
from testui.support import logger
from testui.support.appium_driver import NewDriver
from testui.support.testui_driver import TestUIDriver


test_dir = os.path.dirname(__file__)

class TestStringMethods:
    @pytest.yield_fixture(autouse=True)
    def selenium_driver(self):
        options = Options()
        options.add_argument("disable-user-media-security")
        options.add_argument("headless")
        driver = (
            NewDriver()
            .set_logger()
            .set_browser("chrome")
            .set_soft_assert(True)
            .set_selenium_driver(chrome_options=options)
        )
        yield driver
        driver.quit()

    @pytest.mark.signup
    def test_template_matching(self, selenium_driver: TestUIDriver):
        logger.log_test_name("T92701: Create an account")
        selenium_driver.get_driver().set_window_size(1000, 1200)
        selenium_driver.navigate_to(
            "https://github.com/testdevlab/Py-TestUI#image-recognition"
        )
        image_result = os.path.join(test_dir, "..", "logs", "image.png")
        image_compare = os.path.join(test_dir, "..", "resources", "comp.png")
        selenium_driver.find_image_match(
            image_compare, 0.1, True, image_match=image_result
        )
        e(selenium_driver, 'xpath', '//h3[contains(text(), "Image Recognition:")]')\
            .wait_until_visible().press_hold_for()
        e(selenium_driver, 'xpath', '//h3[contains(text(), "Image Recognition:")]')\
            .swipe(start_x=50, start_y=50, end_x=100, end_y=100)
        selenium_driver.navigate_to(
            "https://www.testdevlab.com/"
        ).e('css', '#email').send_keys('some@email.com')
        selenium_driver.raise_errors()

    @pytest.mark.signup
    def test_get_dimensions(self, selenium_driver: TestUIDriver):
        logger.log_test_name("T92701: Create an account")
        selenium_driver.driver.set_window_size(1000, 1100)
        selenium_driver.navigate_to(
            "https://github.com/testdevlab/Py-TestUI#image-recognition"
        )
        selenium_driver.get_dimensions()
        selenium_driver.raise_errors()
