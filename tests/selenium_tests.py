import pytest

from selenium.webdriver.chrome.options import Options

from tests.screens.landing import LandingScreen
from testui.support import logger
from testui.support.appium_driver import NewDriver
from testui.support.testui_driver import TestUIDriver


@pytest.fixture(autouse=True)
def driver() -> TestUIDriver:
    options = Options()
    options.add_argument("disable-user-media-security")
    
    driver = (
        NewDriver()
        .set_logger()
        .set_browser('chrome')
        .set_remote_url("http://localhost:4444/wd/hub")
        .set_soft_assert(True) 
        .set_selenium_driver(chrome_options=options)
    )

    yield driver
    
    driver.quit()

@pytest.mark.signup
def test_sign_up_flow(driver: TestUIDriver):
    logger.log_test_name("T92701: Create an account")
    
    driver.navigate_to('https://google.com')
    landing_page = LandingScreen(driver)
    landing_page.i_am_in_landing_screen()
    
    driver.raise_errors()
