import pytest
from selenium.webdriver.chrome.options import Options

from tests.screens.landing import LandingScreen
from testui.support import logger
from testui.support.appium_driver import NewDriver
from testui.support.testui_driver import TestUIDriver

REPORTS_DIRECTORY = "./target"

class TestStringMethods:
    @pytest.yield_fixture(autouse=True)
    def selenium_driver(self):
        options = Options()
        options.add_argument("disable-user-media-security")
        options.add_argument("headless")
        driver = (
            NewDriver()
            .set_logger()
            .set_screenshot_path(str(REPORTS_DIRECTORY))
            .set_browser("chrome")
            .set_soft_assert(True)
            .set_selenium_driver(chrome_options=options)
        )
        yield driver
        driver.quit()

    @pytest.mark.signup
    def test_template_matching(self, selenium_driver: TestUIDriver):
        logger.log_test_name("T92701: Create an account")
        selenium_driver.get_driver().set_window_size(1000, 1100)
        selenium_driver.navigate_to(
            "https://github.com/testdevlab/Py-TestUI#image-recognition"
        )
        selenium_driver.find_image_match(
            "resources/comp.png", 0.9, True, image_match="image.png"
        )
        selenium_driver.raise_errors()

    @pytest.mark.signup
    def test_get_dimensions(self, selenium_driver: TestUIDriver):
        logger.log_test_name("T92701: Create an account")
        selenium_driver.get_driver().set_window_size(1000, 1100)
        selenium_driver.navigate_to(
            "https://github.com/testdevlab/Py-TestUI#image-recognition"
        )
        selenium_driver.get_dimensions()
        selenium_driver.raise_errors()
