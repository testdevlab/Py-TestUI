from time import sleep

import pytest

from tests.screens.landing import LandingScreen
from testui.support import logger
from testui.support.appium_driver import NewDriver
from testui.support.testui_driver import TestUIDriver


class TestStringMethods(object):
    @pytest.yield_fixture(autouse=True)
    def selenium_driver(self):
        driver = NewDriver() \
            .set_logger("pytest").set_soft_assert(True).set_selenium_driver()
        yield driver
        driver.quit()

    @pytest.mark.signup
    def test_sign_up_flow(self, selenium_driver: TestUIDriver):
        logger.log_test_name("T92701: Create an account")
        selenium_driver.navigate_to('https://app.bitrise.io/artifact/30283321/p/eb48e3bff79dec86a9257dfe9de3ac6c')
        sleep(5)
        # landing_page = LandingScreen(selenium_driver)
        # landing_page.i_am_in_landing_screen()
        # selenium_driver.raise_errors()
