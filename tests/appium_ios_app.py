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
            # Change UDID for iOS device
            .set_udid("CC69C1D7-352E-4856-BFD0-B3E908747170")
            .set_logger()
            .set_appium_driver()
        )
        yield driver
        driver.quit()

    @pytest.mark.signup
    def test_ios_app(self, appium_driver: TestUIDriver):
        logger.log_test_name("T92701: Test IOS app")
        appium_driver.navigate_to("https://google.com")
