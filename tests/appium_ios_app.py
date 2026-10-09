import pytest

from testui.elements.testui_element import e
from testui.support import appium_driver, logger
from testui.support.appium_driver import NewDriver
from testui.support.testui_driver import TestUIDriver

GENERAL = "com.apple.settings.general"


def booted_simulator():
    simulators = getattr(appium_driver, "__ios_booted_simulators")()
    if not simulators:
        pytest.skip("Boot an iOS simulator first, e.g. with xcrun simctl boot")
    return simulators[0]


class TestStringMethods:
    @pytest.fixture(autouse=True)
    def appium_driver(self):
        driver = (
            NewDriver()
            .set_platform("ios")
            # Settings is on every iPhone and simulator and needs no account
            .set_bundle_id("com.apple.Preferences")
            .set_udid(booted_simulator())
            # The simulator is already booted, and Xcode 27 no longer ships
            # Simulator.app where Appium would open it
            .set_extra_caps({"appium:isHeadless": True})
            .set_logger()
            .set_soft_assert(True)
            .set_appium_driver()
        )
        yield driver
        driver.quit()

    @pytest.mark.signup
    def test_ios_app(self, appium_driver: TestUIDriver):
        logger.log_test_name("T92701: Test IOS app")
        general = e(
            appium_driver, "accessibility", GENERAL
        ).wait_until_visible()
        assert general.get_text() == "General"
        general.click()
        e(
            appium_driver, "accessibility", "com.apple.settings.general.about"
        ).wait_until_visible()
        appium_driver.back()
        general.wait_until_visible()
        appium_driver.raise_errors()
