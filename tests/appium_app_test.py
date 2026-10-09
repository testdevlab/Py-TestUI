import pytest

from testui.elements.testui_element import e
from testui.support import logger
from testui.support.appium_driver import NewDriver
from testui.support.testui_driver import TestUIDriver

SEARCH_BAR = "com.android.settings:id/search_action_bar"


class TestStringMethods:
    @pytest.fixture(autouse=True)
    def appium_driver(self):
        driver = (
            NewDriver()
            # Settings is on every Android device and needs no account
            .set_app_package_activity("com.android.settings", ".Settings")
            .set_logger()
            .set_soft_assert(True)
            .set_appium_driver()
        )
        yield driver
        driver.quit()

    @pytest.mark.signup
    def test_appium_app(self, appium_driver: TestUIDriver):
        logger.log_test_name("T92701: Check appium app")
        e(appium_driver, "id", SEARCH_BAR).wait_until_visible()
        item = e(appium_driver, "id", "android:id/title").wait_until_visible()
        assert item.get_text()
        item.click()
        e(appium_driver, "id", SEARCH_BAR).no().wait_until_visible()
        appium_driver.back()
        e(appium_driver, "id", SEARCH_BAR).wait_until_visible()
        appium_driver.raise_errors()
