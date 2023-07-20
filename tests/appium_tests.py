import time

import pytest

from testui.support import logger
from testui.support.appium_driver import NewDriver
from testui.support.testui_driver import TestUIDriver


class TestStringMethods:
    @pytest.yield_fixture(autouse=True)
    def selenium_driver(self):
        driver = (
            NewDriver()
            .set_logger()
            .set_chrome_driver()
            .set_soft_assert(True)
            .set_appium_driver()
        )
        yield driver
        driver.quit()

    @pytest.mark.signup
    def test_screenshot_methods(self, selenium_driver: TestUIDriver):
        logger.log_test_name("T92701: Create an account")
        selenium_driver.get_dimensions()
        selenium_driver.navigate_to(
            "https://github.com/testdevlab/Py-TestUI#image-recognition"
        )
        selenium_driver.start_recording_screen()
        time.sleep(1)
        selenium_driver.stop_recording_and_compare(
            "./resources/comp.png",
            fps_reduction=30,
            keep_image_as="v_image.png",
        )
        selenium_driver.find_image_match(
            "./resources/comp.png", 0.9, True, image_match="image.png"
        )
        selenium_driver.click_by_image("./resources/comp.png")
        selenium_driver.raise_errors()
