from __future__ import annotations

import time
import os

from os import path
from typing import List

from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.webelement import WebElement
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy

from testui.support import logger
from testui.support.helpers import error_with_traceback
from testui.support.testui_images import Dimensions, ImageRecognition


def testui_error(driver, exception: str) -> None:
    config = driver.configuration

    if config.save_screenshot_on_fail:
        try:
            driver.save_screenshot()
        except Exception as error:
            exception += (
                f"{logger.bcolors.FAIL} \n"
                f"Could not take screenshot:{logger.bcolors.ENDC}\n {error}"
            )

    full_exception = exception
    if config.save_full_stacktrace:
        full_exception = error_with_traceback(exception)

    if driver.soft_assert:
        logger.log_error(full_exception)
        driver.set_error(full_exception)
    else:
        logger.log_error(full_exception)
        driver.set_error(full_exception)
        raise ElementException(
            "There were errors during the UI testing, check the logs"
        )


class Error(Exception):
    """Base class for exceptions in this module."""


# pylint: disable=super-init-not-called
class ElementException(Error):
    def __init__(self, message, expression=""):
        self.message = message
        self.expression = expression


class Elements:
    def __init__(self, driver, locator_type: str, locator: str):
        self.logger = driver.logger_name
        # TODO: Investigate if should be used in functionality or should be
        # removed.
        # pylint: disable=unused-private-member
        self.__soft_assert = driver.soft_assert
        self.testui_driver = driver
        self.device_name = driver.device_name
        self.driver = driver.get_driver()
        self.locator = locator
        self.locator_type = locator_type
        self.__is_collection = False
        self.index = 0
        # TODO: Investigate if should be used in functionality or should be
        # removed.
        # pylint: disable=unused-private-member
        self.__errors = []
        self.__is_not = False

    def __put_log(self, message):
        if self.logger is not None:
            if self.logger == "behave":
                logger.log(f"{message} \n")
            else:
                logger.log(message)

    def __show_error(self, exception):
        testui_error(self.testui_driver, exception)

    def get(self, index):
        self.__is_collection = True
        self.index = index

        return self

    def get_element(self, index=0) -> WebElement:
        if self.__is_collection:
            return self.__find_by_collection()[self.index]
        if index != 0:
            return self.__find_by_collection()[index]

        return self.__find_by_element()

    def __find_by_element(self) -> WebElement:
        if self.locator_type == "id":
            return self.driver.find_element(by=By.ID, value=self.locator)

        if self.locator_type == "css":
            return self.driver.find_element(
                by=By.CSS_SELECTOR, value=self.locator
            )

        if self.locator_type == "className":
            return self.driver.find_element(
                by=By.CLASS_NAME, value=self.locator
            )

        if self.locator_type == "name":
            return self.driver.find_element(By.NAME, self.locator)

        if self.locator_type == "xpath":
            return self.driver.find_element(By.XPATH, self.locator)

        if self.locator_type == "android_id_match":
            return self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
                                            f"resourceIdMatches(\"{self.locator}\")"
                                            )
        if self.locator_type == "accessibility":
            return self.driver.find_element(
                AppiumBy.ACCESSIBILITY_ID, self.locator)

        if self.locator_type == "uiautomator":
            return self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR, self.locator)

        if self.locator_type == "classChain":
            return self.driver.find_element(
                AppiumBy.IOS_CLASS_CHAIN, self.locator)

        if self.locator_type == "predicate":
            return self.driver.find_element(AppiumBy.IOS_PREDICATE, self.locator)

        raise ElementException(f"locator not supported: {self.locator_type}")

    def __find_by_collection(self) -> List[WebElement]:
        if self.locator_type == "id":
            return self.driver.find_elements(by=By.ID, value=self.locator)

        if self.locator_type == "css":
            return self.driver.find_elements(
                by=By.CSS_SELECTOR, value=self.locator
            )

        if self.locator_type == "className":
            return self.driver.find_elements(
                by=By.CLASS_NAME, value=self.locator
            )

        if self.locator_type == "name":
            return self.driver.find_elements(By.NAME, self.locator)

        if self.locator_type == "xpath":
            return self.driver.find_elements(By.XPATH, self.locator)

        if self.locator_type == "android_id_match":
            return self.driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR,
                                             f'resourceIdMatches("{self.locator}")'
                                             )

        if self.locator_type == "accessibility":
            return self.driver.find_elements(AppiumBy.ACCESSIBILITY_ID, self.locator)

        if self.locator_type == "uiautomator":
            return self.driver.find_elements(
                AppiumBy.ANDROID_UIAUTOMATOR,
                self.locator
            )
        if self.locator_type == "classChain":
            return self.driver.find_elements(AppiumBy.IOS_CLASS_CHAIN, self.locator)

        if self.locator_type == "predicate":
            return self.driver.find_elements(AppiumBy.IOS_PREDICATE, self.locator)

        raise ElementException(f"locator not supported: {self.locator_type}")

    def is_visible(self, log=True, **kwargs) -> bool:
        is_not = False

        # Allows passing "is_not" as a kwarg to not overwrite self.__is_not.
        # This is not meant to be used by the user.
        if "is_not" in kwargs:
            is_not = kwargs["is_not"]
        else:
            is_not = self.__is_not
            self.__is_not = False

        is_visible = False
        try:
            is_visible = self.get_element().is_displayed()

            if log:
                if is_visible:
                    self.__put_log(
                        f'{self.device_name}: element "{self.locator_type}: '
                        f'{self.locator}" is visible'
                    )
                else:
                    self.__put_log(
                        f'{self.device_name}: element "{self.locator_type}: '
                        f'{self.locator}" is not visible'
                    )
        except Exception:
            if log:
                self.__put_log(
                    f'{self.device_name}: element "{self.locator_type}: '
                    f'{self.locator}" is not visible'
                )

        if is_not:
            return not is_visible
        else:
            return is_visible

    def is_visible_in(self, seconds):
        start = time.time()
        is_not = self.__is_not
        while time.time() < start + seconds:
            self.__is_not = is_not
            if self.is_visible(log=False):
                return True
        return False

    def visible_for(self, seconds=1):
        start = time.time()
        is_not = self.__is_not
        err_text = "not"
        if self.__is_not:
            err_text = "is"
        while time.time() < start + seconds:
            self.__is_not = is_not
            if not self.is_visible():
                return self.__show_error(
                    f"{logger.bcolors.FAIL} {self.device_name} Element "
                    f"{err_text} found with the following locator: "
                    f'"{self.locator_type}:{self.locator}" during the time of '
                    f"{time.time() - start}s {logger.bcolors.ENDC}"
                )
        if is_not:
            self.__put_log(
                f'{self.device_name}: element "{self.locator_type}: '
                f'{self.locator}" is not visible for {seconds}s'
            )
        else:
            self.__put_log(
                f'{self.device_name}: element "{self.locator_type}: '
                f'{self.locator}" is visible for {seconds}s'
            )
        return self

    def wait_until_visible(self, seconds=10.0, log=True) -> "Elements":
        start = time.time()

        is_not = self.__is_not
        self.__is_not = False

        is_visible = self.is_visible(log=False, is_not=is_not)
        while time.time() < start + seconds and not is_visible:
            time.sleep(0.2)
            is_visible = self.is_visible(log=False, is_not=is_not)

        if is_visible:
            if log:
                self.__put_log(
                    f'{self.device_name}: Element "{self.locator_type}: '
                    f'{self.locator}" was visible in {time.time() - start}s'
                )

            return self

        err_text = "was not"
        if is_not:
            err_text = "was"

        self.__show_error(
            f"{self.device_name}: Element {err_text} found with the following "
            f'locator: "{self.locator_type}: {self.locator}" '
            f"after {time.time() - start}s"
        )

        return self

    def wait_until_attribute(self, attr, text, seconds=10):
        start = time.time()
        err = None
        value = ""
        err_text, info_text = "should have been", "="
        if self.__is_not:
            err_text, info_text = "should not have been", "!="
        while time.time() < start + seconds:
            try:
                value = self.get_element().get_attribute(attr)
                if (value == text) != self.__is_not:
                    self.__put_log(
                        f'{self.device_name}: element "{self.locator_type}: '
                        f'{self.locator}" has attribute "{attr}" -> "{value}" '
                        f'{info_text} "{text}" after {time.time() - start}s'
                    )
                    self.__is_not = False
                    return self
            except Exception as error:
                err = error
                time.sleep(0.2)
        if err is None:
            err = ""
        return self.__show_error(
            f"{logger.bcolors.FAIL}{err} {self.device_name} Element {err_text} "
            f"found with the following locator: "
            f'"{self.locator_type}:{self.locator}" and '
            f'attribute "{attr}" -> "{value}" {err_text} "{text}" after '
            f"{time.time() - start}s{logger.bcolors.ENDC}"
        )

    def wait_until_contains_attribute(self, attr, text, seconds=10):
        start = time.time()
        err = None
        value = ""
        info_text, err_text = "containing", " not"
        if self.__is_not:
            info_text, err_text = "not containing", " "
        while time.time() < start + seconds:
            try:
                value = self.get_element().get_attribute(attr)
                if value.__contains__(text) != self.__is_not:
                    self.__put_log(
                        f'element "{self.locator_type}: {self.locator}" has '
                        f'attribute "{attr}" {info_text} "{text}" after '
                        f"{time.time() - start}s"
                    )
                    self.__is_not = False
                    return self
            except Exception as error:
                err = error
                time.sleep(0.2)
        if err is None:
            err = ""
        return self.__show_error(
            f"{logger.bcolors.FAIL}{err} {self.device_name} Element{err_text} "
            f"found with the following locator: "
            f'"{self.locator_type}:{self.locator}" and '
            f'attribute "{attr}" -> "{value}" {info_text} "{text}" '
            f"after {time.time() - start}s {logger.bcolors.ENDC}"
        )

    def wait_until_contains_sensitive_attribute(
            self, attr, text, seconds=10.0, log=True
    ):
        start = time.time()
        err = None
        value = ""
        info_text, err_text = "contains", "not"
        if self.__is_not:
            info_text, err_text = "not contains", "is"
        while time.time() < start + seconds:
            try:
                value = self.get_element().get_attribute(attr)
                if value.lower().__contains__(text.lower()) != self.__is_not:
                    self.__put_log(
                        f'{self.device_name}: element "{self.locator_type}: '
                        f'{self.locator}" has attribute "{attr}" -> "{value}" '
                        f'{info_text} no case sensitive value "{text}" after '
                        f"{time.time() - start}s"
                    )
                    self.__is_not = False
                    return self
            except Exception as error:
                err = error
                time.sleep(0.2)
        if err is None:
            err = ""
        if log:
            return self.__show_error(
                f"{logger.bcolors.FAIL}{err} {self.device_name} Element "
                f"{err_text} found with the following locator: "
                f'"{self.locator_type}:{self.locator}" and attribute "{attr}" '
                f'containing no case sensitive value "{text}" {err_text} '
                f'"{value}" after {time.time() - start}s {logger.bcolors.ENDC}'
            )

        raise ElementException(err)

    def no(self, is_not=True):
        self.__is_not = is_not
        return self

    def click(self):
        timeout = 5  # [seconds]
        start = time.time()

        err = None
        while time.time() < start + timeout:
            try:
                element = self.get_element()
                element.click()
                self.__put_log(
                    f'{self.device_name}: element "{self.locator_type}: '
                    f'{self.locator}" pressed for {time.time() - start}s'
                )
                return self
            except Exception as error:
                err = error
                time.sleep(0.2)
        return self.__show_error(
            f"{logger.bcolors.FAIL}{err} {self.device_name}: Element "
            f'"{self.locator_type}: {self.locator}" could not be clicked after '
            f"{time.time() - start}s {logger.bcolors.ENDC}"
        )

    def press_hold_for(self, milliseconds=1000):
        timeout = 5  # [seconds]
        start = time.time()

        err = None
        while time.time() < start + timeout:
            try:
                self.get_element()
                try:
                    is_browser: str = self.testui_driver.context
                    if is_browser.__contains__("NATIVE"):
                        browser = False
                    else:
                        browser = True
                except Exception:
                    browser = True
                if not browser:
                    ta = TouchAction(self.driver)
                    ta.press(self.get_element()).wait(
                        milliseconds
                    ).release().perform()
                else:
                    ta = ActionChains(self.driver)
                    ta.click_and_hold(self.get_element()).pause(
                        milliseconds // 1000
                    ).release().perform()

                self.__put_log(
                    f'{self.device_name}: element "{self.locator_type}: '
                    f'{self.locator}" pressed for {time.time() - start}s'
                )
                return self
            except Exception as error:
                err = error
                time.sleep(0.2)
        return self.__show_error(
            f"{logger.bcolors.FAIL}{err} {self.device_name}: Element not found "
            f'with the following locator: "{self.locator_type}:{self.locator}" '
            f"after {time.time() - start}s {logger.bcolors.ENDC}"
        )

    def click_by_coordinates(self, x, y):
        timeout = 5  # [seconds]
        start = time.time()

        err = None
        while time.time() < start + timeout:
            try:
                self.get_element()
                time.sleep(1)
                ta = TouchAction(self.driver)
                ta.tap(x=x, y=y).perform()
                self.__put_log(
                    f'{self.device_name}: element "x={x}: y={y}" clicked after '
                    f"{time.time() - start}s"
                )
                return self
            except Exception as error:
                err = error
                time.sleep(0.2)
        return self.__show_error(
            f"{logger.bcolors.FAIL}{err} {self.device_name}: Element not found "
            f'with the following locator: "{self.locator_type}:{self.locator}" '
            f"after {time.time() - start}s {logger.bcolors.ENDC}"
        )

    @property
    def location(self):
        return Dimensions(
            self.get_element().location.get("x"),
            self.get_element().location.get("y"),
        )

    @property
    def dimensions(self):
        return Dimensions(
            self.get_element().size.get("width"),
            self.get_element().size.get("height"),
        )

    def screenshot(self, image_name="cropped_image.png"):
        """
        Takes screenshot of the specific element
        :param image_name: relative path to image taken
        :return:
        """
        self.wait_until_visible()
        try:
            self.get_element().screenshot(image_name)
        except Exception:
            path_img = self.testui_driver.save_screenshot(f"{self.device_name}-crop_image.png")
            dimensions = self.dimensions
            top_left = self.location
            logger.log_debug(f'crop dimensions (x,y,w,h):({top_left.x},{top_left.y},{dimensions.x},{dimensions.y})')
            ImageRecognition(
                path_img
            ).crop_original_image(
                (top_left.x + dimensions.x // 2),
                (top_left.y + dimensions.y // 2),
                dimensions.x,
                dimensions.y,
                image_name,
            )

            os.remove(path_img)

        return self

    def find_image_match(
            self,
            image_name,
            threshold=0.9,
            image_match="",
            max_scale=2.0,
            min_scale=0.3,
    ):
        """
        Takes screenshot of the element and compares it with the one you provide
        as 'image_name'
        :param min_scale:
        :param max_scale:
        :param image_match: returns the image with a rectangle showing the match
        :param image_name: relative path to image
        :param threshold: limit to consider image as a match (0 to 1)
        :return: Elements
        """
        is_not = self.__is_not
        self.__is_not = False
        self.screenshot(self.device_name + ".png")
        found, precision = ImageRecognition(
            self.device_name + ".png", image_name, threshold, self.device_name
        ).compare(
            image_match=image_match, max_scale=max_scale, min_scale=min_scale
        )
        if not found and not is_not:
            self.__show_error(
                f"{self.device_name}: The images compared did not match. "
                f"Threshold={threshold}, matched = {precision}"
            )
        if found and is_not:
            self.__is_not = False
            self.__show_error(
                f"{self.device_name}: The images compared matched. "
                f"Threshold={threshold}, matched = {precision}"
            )
        root_dir = self.testui_driver.configuration.screenshot_path
        os.remove(os.path.join(root_dir, self.device_name + ".png"))

        return self

    def is_image_match(
            self,
            image_name,
            threshold=0.9,
            image_match="",
            max_scale=2.0,
            min_scale=0.3,
    ):
        """
        Takes screenshot of the element and compares it with the one you provide
        as 'image_name'
        :param min_scale:
        :param max_scale:
        :param image_match: returns the image with a rectangle showing the match
        :param image_name: relative path to image
        :param threshold: limit to consider image as a match (0 to 1)
        :return: Elements
        """
        is_not = self.__is_not
        self.__is_not = False
        self.screenshot(self.device_name + ".png")
        found, _ = ImageRecognition(
            self.device_name + ".png", image_name, threshold, self.device_name
        ).compare(
            image_match=image_match, max_scale=max_scale, min_scale=min_scale
        )
        if not found and not is_not:
            return False
        if found and is_not:
            return False
        root_dir = self.testui_driver.configuration.screenshot_path
        os.remove(os.path.join(root_dir, self.device_name + ".png"))

        return True

    def swipe(
            self,
            start_x=None,
            start_y=None,
            end_x=None,
            end_y=None,
            el=None,
            duration=None,
    ):
        """
        It swipes from element to the el(second element) or to the coordinates
        you define with start_x, start_y, end_x, end_y. end_x and end_y are
        mandatory if el(second element) is not defined.
        :param start_x: Coordinate x from where it will begin swiping
        :param start_y: Coordinate y from where it will begin swiping
        :param end_x: Coordinate x from where it will end swiping
        :param end_y: Coordinate y from where it will end swiping
        :param el: element 'Elements' type from where it will end swiping
        (instead of end_x, end_y)
        :param duration: duration of the swiping action
        :return: Elements
        """
        timeout = 5  # [seconds]
        start = time.time()

        err = None
        while time.time() < start + timeout:
            try:
                location = self.location
                if start_x is None:
                    start_x = location.x
                if start_y is None:
                    start_y = location.y
                time.sleep(0.1)
                el: Elements
                if el is not None:
                    location2 = el.location
                    if end_x is None:
                        end_x = location2.x
                    if end_y is None:
                        end_y = location2.y
                    action = TouchAction(self.driver)
                    action.press(x=start_x, y=start_y).wait(duration).move_to(
                        x=end_x, y=end_y
                    ).release()
                    action.perform()
                else:
                    if end_x is None:
                        end_x = location.x
                    if end_y is None:
                        end_y = location.y
                    self.driver.swipe(
                        start_y=start_y,
                        start_x=start_x,
                        end_y=end_y,
                        end_x=end_x,
                        duration=duration,
                    )
                return self
            except Exception as error:
                err = error
        return self.__show_error(
            f"{logger.bcolors.FAIL}{err} {self.device_name}: Element not found "
            f'with the following locator: "{self.locator_type}:{self.locator}" '
            f"after {time.time() - start}s {logger.bcolors.ENDC}"
        )

    def slide_percentage(self, percentage, start_x=None):
        width = self.dimensions.x * percentage / 100
        end_width = width + self.location.x
        if start_x is None:
            start_x = self.location.x
        self.swipe(start_x=start_x, end_x=end_width)

    def swipe_until_text(
            self,
            start_x=None,
            start_y=None,
            end_x=None,
            end_y=None,
            text=None,
            el=None,
            max_swipes=50,
    ):
        """
        Swipe until an element with that text appears and Returns the element
        that contains the text.
        endX and endY are mandatory if el(element) is not defined.
        text is mandatory
        :param start_x:
        :param start_y:
        :param end_x:
        :param end_y:
        :param text:
        :param el:
        :param max_swipes:
        :return: Elements
        """

        if el is None and (start_x is None or end_y is None):
            raise Exception(
                "if element not specified, end_x and end_y are required "
                "to be able to swipe"
            )
        if text is None:
            raise Exception("text cannot be None for swipe_until_text method")
        start = time.time()
        for _ in range(max_swipes):
            try:
                e(
                    self.testui_driver, "uiautomator", f'textContains("{text}")'
                ).wait_until_visible(0.1, False)
                break
            except Exception:
                self.swipe(start_x, start_y, end_x, end_y, el, None)
        self.__put_log(
            f'{self.device_name}: element "{self.locator_type}: '
            f'{self.locator}" with text {text} '
            f"found after {time.time() - start}s"
        )
        return e(self.testui_driver, "uiautomator", f'textContains("{text}")')

    def send_keys(self, value, log=True):
        timeout = 10  # [seconds]
        start = time.time()
        if value is None:
            raise Exception("keys sent cannot be None type")
        err = None
        while time.time() < start + timeout:
            try:
                self.get_element().send_keys(value)
                if log:
                    self.__put_log(
                        f'{self.device_name}: element "{self.locator_type}: '
                        '{self.locator}" received keys "{value}" after '
                        f"{time.time() - start}s"
                    )
                return self
            except Exception as error:
                err = error
                time.sleep(0.2)
        return self.__show_error(
            f"{logger.bcolors.FAIL}{err} {self.device_name}: Element not found "
            f'with the following locator: "{self.locator_type}:{self.locator}" '
            f"after {time.time() - start}s {logger.bcolors.ENDC}"
        )

    def clear(self) -> "Elements":
        self.get_element().clear()

        return self

    def get_text(self):
        timeout = 10  # [seconds]
        start = time.time()

        err = None
        while time.time() < start + timeout:
            try:
                text = self.get_element().text
                self.__put_log(
                    f'{self.device_name}: element "{self.locator_type}: '
                    f'{self.locator}" has text "{text}" {time.time() - start}s'
                )
                return text
            except Exception as error:
                err = error
                time.sleep(0.2)
        self.__show_error(
            f"{logger.bcolors.FAIL}{err} {self.device_name}: Element not found "
            f'with the following locator: "{self.locator_type}:{self.locator}" '
            f"after {time.time() - start}s {logger.bcolors.ENDC}"
        )

    def get_value(self):
        timeout = 10  # [seconds]
        start = time.time()

        err = None
        while time.time() < start + timeout:
            try:
                text = self.get_element().get_attribute("value")
                self.__put_log(
                    f'{self.device_name}: element "{self.locator_type}: '
                    f'{self.locator}" has text "{text}" {time.time() - start}s'
                )
                return text
            except Exception as error:
                err = error
                time.sleep(0.2)
        self.__show_error(
            f"{logger.bcolors.FAIL}{err} {self.device_name}: Element not found "
            f'with the following locator: "{self.locator_type}:{self.locator}" '
            f"after {time.time() - start}s {logger.bcolors.ENDC}"
        )

    def get_name(self):
        timeout = 10  # [seconds]
        start = time.time()

        err = None
        while time.time() < start + timeout:
            try:
                text = self.get_element().get_attribute("name")
                self.__put_log(
                    f'{self.device_name}: element "{self.locator_type}: '
                    f'{self.locator}" has name "{text}" {time.time() - start}s'
                )
                return text
            except Exception as error:
                err = error
                time.sleep(0.2)
        self.__show_error(
            f"{logger.bcolors.FAIL}{err} {self.device_name}: Element not "
            "found with the following locator: "
            f'"{self.locator_type}:{self.locator}" after '
            f"{time.time() - start}s {logger.bcolors.ENDC}"
        )

    def get_attribute(self, att):
        timeout = 10  # [seconds]
        start = time.time()

        err = None
        while time.time() < start + timeout:
            try:
                text = self.get_element().get_attribute(att)
                self.__put_log(
                    f'{self.device_name}: element "{self.locator_type}: '
                    f'{self.locator}" has "{att}: {text}" '
                    f"{time.time() - start}s"
                )
                return text
            except Exception as error:
                err = error
                time.sleep(0.2)
        self.__show_error(
            f"{logger.bcolors.FAIL}{err} {self.device_name}: Element not found "
            f'with the following locator: "{self.locator_type}:{self.locator}" '
            f"after {time.time() - start}s {logger.bcolors.ENDC}"
        )

    def press_and_compare(
            self,
            image,
            milliseconds=1000,
            threshold=0.9,
            fps_reduction=1,
            keep_image_as="",
    ):
        self.testui_driver.start_recording_screen()
        self.press_hold_for(milliseconds)

        found = ""
        not_found = "not"
        if self.__is_not:
            found = "not"
            not_found = ""

        start = time.time()

        if self.testui_driver.stop_recording_and_compare(
                image, threshold, fps_reduction, self.__is_not, keep_image_as, False
        ):
            self.__put_log(
                f"{self.device_name}: image {found} found while pressing "
                f'element "{self.locator_type}: {self.locator}" '
                f"after {time.time() - start}s"
            )
        else:
            self.__show_error(
                f"{self.device_name}: image {not_found} found while pressing "
                f'element "{self.locator_type}: {self.locator}" '
                f"after {time.time() - start}s"
            )
        self.__is_not = False
        return self

    def collection_size(self):
        self.__is_collection = False
        index = self.index
        self.index = 0
        self.wait_until_visible()
        self.index = index
        self.__is_collection = True
        return len(self.__find_by_collection())

    def find_by_attribute(
            self, attribute, value: str, timeout=10, case_sensitive=True
    ):
        start = time.time()
        self.wait_until_visible()
        self.__is_collection = True
        while time.time() < start + timeout:
            for i, element in enumerate(self.__find_by_collection()):
                if case_sensitive and element.get_attribute(attribute) == value:
                    self.__put_log(
                        f"{self.device_name}: element in collection "
                        f'{self.locator_type}: {self.locator}" with attribute '
                        f'"{attribute}" = "{value}" found after '
                        f"{time.time() - start}s"
                    )
                    self.index = i
                    return self
                if (
                        not case_sensitive
                        and element.get_attribute(attribute).lower()
                        == value.lower()
                ):
                    self.__put_log(
                        f"{self.device_name}: element in collection "
                        f'{self.locator_type}: {self.locator}" with attribute '
                        f'"{attribute}" = "{value}" found after '
                        f"{time.time() - start}s"
                    )
                    self.index = i
                    return self
        self.__show_error(
            f"{self.device_name}: no element in collection "
            f'"{self.locator_type}: {self.locator}" had attribute '
            f'"{attribute}" = "{value}" after {time.time() - start}s'
        )


def e(driver, locator_type: str, locator: str) -> Elements:
    """
    Args:
        driver: Driver that is going to fetch element.
        locator_type (str): Type of the pattern in which locator is written.
        locator (str): Pattern which describes target.

    Possible locator types:
        id,
        css,
        className,
        name,
        xpath,
        accessibility,
        uiautomator,
        classChain,
        predicate
    """

    # TODO: Locator types should be enums.

    return Elements(driver, locator_type, locator)


def scroll_by_text(driver, text, element=None, exact_text=False) -> Elements:
    if exact_text:
        method_text = "text"
    else:
        method_text = "textContains"
    if element is None:
        element = "scrollable(true)"

    return e(
        driver,
        "uiautomator",
        (
            f"new UiScrollable(new UiSelector().{element})."
            f'scrollIntoView({method_text}("{text}"));'
        ),
    )


def scroll_by_resource_id(driver, res_id) -> Elements:
    locator = (
        "new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView"
        f'(new UiSelector().resourceId("{res_id}"));'
    )

    return e(driver, "uiautomator", locator)


class AndroidLocator:
    @classmethod
    def scroll(cls, method: str, scrollable_element=None):
        if scrollable_element is None:
            scrollable_element = "scrollable(true)"

        return (
            f"new UiScrollable(new UiSelector()."
            f"{scrollable_element}).scrollIntoView({method});"
        )

    @classmethod
    def text(cls, text: str):
        return f'text("{text}")'

    @classmethod
    def text_contains(cls, text: str):
        return f'textContains("{text}")'

    @classmethod
    def id_match(cls, text: str):
        return f'resourceIdMatches("{text}")'

    @classmethod
    def class_name(cls, text: str):
        return f'className("{text}")'

    @classmethod
    def parent(cls, parent_method, child_method):
        return f"fromParent({parent_method}).{child_method}"

    @classmethod
    def child(cls, parent_method, child_method):
        return f"childSelector({child_method}).{parent_method}"
