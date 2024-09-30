import pytest

from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from testui.support import logger
from testui.support.appium_driver import NewDriver
from testui.support.testui_driver import TestUIDriver


class TestStringMethods:
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
        # Deprecated
        # appium_driver.touch_actions().press(x=500, y=10)\
        # .move_to(x=500, y=1000).release().perform()

        actions = ActionBuilder(
            appium_driver.get_driver(),
            mouse=PointerInput(interaction.POINTER_TOUCH, "touch")
        )

        actions.pointer_action.move_to_location(x=500, y=10)
        actions.pointer_action.pointer_down()
        actions.pointer_action.pause(1)
        actions.pointer_action.move_to_location(x=500, y=1000)
        actions.pointer_action.release()
        actions.perform()

        appium_driver.raise_errors()
