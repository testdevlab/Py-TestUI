import pytest

from tests.screens.landing import LandingScreen
from testui.support import logger
from testui.support.appium_driver import NewDriver
from testui.support.testui_driver import TestUIDriver


class TestStringMethods(object):
    @pytest.yield_fixture(autouse=True)
    def appium_driver(self):
        driver = (
            NewDriver()
            .set_app_package_activity(
                "com.android.vending", ".AssetBrowserActivity"
            )
            .set_logger()
            .set_soft_assert(True)
            .set_appium_driver()
        )
        yield driver
        driver.quit()

    @pytest.mark.signup
    def test_appium_app(self, appium_driver: TestUIDriver):
        logger.log_test_name("T92701: Check appium app")
        landing_page = LandingScreen(appium_driver)
        landing_page.i_am_in_google_play_landing_screen()
        appium_driver.raise_errors()
