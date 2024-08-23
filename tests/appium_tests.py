import time
import os
import pytest

from testui.support import logger
from testui.support.appium_driver import NewDriver
from testui.support.testui_driver import TestUIDriver

test_dir = os.path.dirname(__file__)

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
        driver.configuration.save_full_stacktrace = True
        yield driver
        driver.quit()

    @pytest.mark.signup
    def test_screenshot_methods(self, selenium_driver: TestUIDriver):
        logger.log_test_name("T92701: Create an account")
        print(selenium_driver.device_udid)
        selenium_driver.get_dimensions()
        selenium_driver.navigate_to(
            "https://github.com/testdevlab/Py-TestUI#image-recognition"
        )
        image_compare = os.path.join(test_dir, "..", "resources", "comp.png")
        selenium_driver.click_by_image(image=image_compare, threshold=0.6, ratio=0.5, webview=True)
        selenium_driver.start_recording_screen()
        time.sleep(1)
        image_result = os.path.join(test_dir, "..", "logs", "v-image.png")
        selenium_driver.stop_recording_and_compare(
            comparison=image_compare,
            fps_reduction=30,
            keep_image_as=image_result,
            threshold=0.6
        )
        selenium_driver.find_image_match(
            comparison=image_compare, threshold=0.6, assertion=True, image_match="./logs/image.png"
        )

        time.sleep(110)
        selenium_driver.raise_errors()
