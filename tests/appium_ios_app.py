import pytest

from testui.support import logger
from testui.support.appium_driver import NewDriver
from testui.support.testui_driver import TestUIDriver


class TestStringMethods:
    @pytest.yield_fixture(autouse=True)
    def appium_driver(self):
        driver = (
            NewDriver()
            .set_bundle_id("com.apple.Preferences")
            .set_platform("ios")
            .set_udid("5671CF6A-373A-4A11-8FE3-AD8E29D70F35")  # Change UDID for iOS device
            .set_logger()
            .set_soft_assert(True)
            .set_appium_driver()
        )
        yield driver
        driver.quit()

    @pytest.mark.signup
    def test_ios_app(self, appium_driver: TestUIDriver):
        logger.log_test_name("T92701: Test IOS app")
        appium_driver.navigate_to("https://google.com")
        # landing_page = LandingScreen(selenium_driver)
        # landing_page.i_am_in_mobile_landing_screen()
        # selenium_driver.raise_errors()
