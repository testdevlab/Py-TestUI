import pytest

from tests.screens.landing import LandingScreen
from testui.support import logger
from testui.support.appium_driver import NewDriver
from testui.support.testui_driver import TestUIDriver


@pytest.yield_fixture(autouse=True)
def driver() -> TestUIDriver:
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
def test_appium(driver: TestUIDriver):
    logger.log_test_name("T92701: Create an account")
    driver.navigate_to('https://google.com')
    landing_page = LandingScreen(driver)
    landing_page.i_am_in_mobile_landing_screen()
    driver.raise_errors()
