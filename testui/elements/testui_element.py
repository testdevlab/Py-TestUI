import os
import time
from datetime import datetime
from pathlib import Path

from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.common.by import By

from testui.support import logger
from testui.support.helpers import error_with_traceback
from testui.support.testui_images import Dimensions, ImageRecognition


def e(driver, locator_type, locator):
    """locator types: id, css, className, name, xpath, accessibility, uiautomator, classChain, predicate"""
    return Elements(driver, locator_type, locator)


def scroll_by_text(driver, text, element=None, exact_text=False):
    if exact_text:
        method_text = 'text'
    else:
        method_text = 'textContains'
    if element is None:
        locator = f'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView({method_text}("{text}"));'
    else:
        locator = f'new UiScrollable(new UiSelector().{element}).scrollIntoView({method_text}("{text}"));'
    e(driver, "uiautomator", locator)
    return Elements(driver, "uiautomator", locator)


def scroll_by_resource_id(driver, id):
    locator = "new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView(new UiSelector()." \
              f"resourceId(\"{id}\"));"
    e(driver, "uiautomator", locator)
    return Elements(driver, "uiautomator", locator)


def testui_error(driver, exception):
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d%H%M%S")
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    Path(root_dir + "/report_screenshots").mkdir(parents=True, exist_ok=True)
    image_name = f'ERROR-{driver.device_name}-{current_time}.png'
    try:
        driver.save_screenshot(image_name, directory='report_screenshots/')
        exception += f'{logger.bcolors.FAIL} \n Screenshot taken and saved as: ' \
                     f'report_screenshots/testui-{image_name}{logger.bcolors.ENDC}\n'
    except Exception as error:
        exception += f'{logger.bcolors.FAIL} \nCould not take screenshot:{logger.bcolors.ENDC}\n {error}'
    full_exception = error_with_traceback(exception)
    if driver.soft_assert:
        logger.log_error(full_exception)
        driver.set_error(full_exception)
    else:
        driver.set_error(full_exception)
        logger.log_error(full_exception)
        raise ElementException('There were errors during the UI testing, check the logs')


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class ElementException(Error):
    def __init__(self, message, expression=''):
        self.message = message
        self.expression = expression


class Elements(object):
    def __init__(self, driver, locator_type: str, locator: str):
        self.logger = driver.logger_name
        self.__soft_assert = driver.soft_assert
        self.testui_driver = driver
        self.device_name = driver.device_name
        self.driver = driver.get_driver()
        self.locator = locator
        self.locator_type = locator_type
        self.__is_collection = False
        self.index = 0
        self.__errors = []
        self.__is_not = False

    def __put_log(self, message):
        if self.logger is not None:
            if self.logger == 'behave':
                logger.log(f'{message} \n')
            else:
                logger.log(message)

    def __show_error(self, exception):
        testui_error(self.testui_driver, exception)

    def get(self, index):
        self.__is_collection = True
        self.index = index
        return self

    def get_element(self, index=0):
        if self.__is_collection:
            return self.__find_by_collection()[self.index]
        elif index != 0:
            return self.__find_by_collection()[index]
        else:
            return self.__find_by_element()

    def __find_by_element(self):
        if self.locator_type == "id":
            return self.driver.find_element_by_id(self.locator)
        if self.locator_type == "android_id_match":
            return self.driver.find_element_by_android_uiautomator(f'resourceIdMatches("{self.locator}")')
        elif self.locator_type == "css":
            return self.driver.find_element_by_css_selector(self.locator)
        elif self.locator_type == "className":
            return self.driver.find_element_by_class_name(self.locator)
        elif self.locator_type == "name":
            return self.driver.find_element(By.NAME, self.locator)
        elif self.locator_type == "xpath":
            return self.driver.find_element(By.XPATH, self.locator)
        elif self.locator_type == "accessibility":
            return self.driver.find_element_by_accessibility_id(self.locator)
        elif self.locator_type == "uiautomator":
            return self.driver.find_element_by_android_uiautomator(self.locator)
        elif self.locator_type == "classChain":
            return self.driver.find_element_by_ios_class_chain(self.locator)
        elif self.locator_type == "predicate":
            return self.driver.find_element_by_ios_predicate(self.locator)
        else:
            raise ElementException(f"locator not supported: {self.locator_type}")

    def __find_by_collection(self):
        if self.locator_type == "id":
            return self.driver.find_elements_by_id(self.locator)
        if self.locator_type == "android_id_match":
            return self.driver.find_elements_by_android_uiautomator(f'resourceIdMatches("{self.locator}")')
        elif self.locator_type == "css":
            return self.driver.find_elements_by_css_selector(self.locator)
        elif self.locator_type == "className":
            return self.driver.find_elements_by_class_name(self.locator)
        elif self.locator_type == "name":
            return self.driver.find_elements(By.NAME, self.locator)
        elif self.locator_type == "xpath":
            return self.driver.find_elements(By.XPATH, self.locator)
        elif self.locator_type == "accessibility":
            return self.driver.find_elements_by_accessibility_id(self.locator)
        elif self.locator_type == "uiautomator":
            return self.driver.find_elements_by_android_uiautomator(self.locator)
        elif self.locator_type == "classChain":
            return self.driver.find_elements_by_ios_class_chain(self.locator)
        elif self.locator_type == "predicate":
            return self.driver.find_elements_by_ios_predicate(self.locator)
        else:
            raise ElementException(f"locator not supported: {self.locator_type}")

    def is_visible(self, log=True):
        is_not = self.__is_not
        try:
            self.get_element()
            if log:
                self.__put_log(f'{self.device_name}: element "{self.locator_type}: {self.locator}" is visible')
            if is_not:
                self.__is_not = False
                return False
            return True
        except Exception:
            if log:
                self.__put_log(f'{self.device_name}: element "{self.locator_type}: {self.locator}" is not visible')
            if self.__is_not:
                self.__is_not = False
                return True
            return False

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
        err_text = 'not'
        if self.__is_not:
            err_text = 'is'
        while time.time() < start + seconds:
            self.__is_not = is_not
            if not self.is_visible():
                return self.__show_error(
                    f'{logger.bcolors.FAIL} {self.device_name} Element {err_text} found with the following locator: '
                    f'"{self.locator_type}:{self.locator}" during the time of {time.time() - start}s'
                    f'{logger.bcolors.ENDC}'
                )
        if is_not:
            self.__put_log(f'{self.device_name}: element "{self.locator_type}: {self.locator}" is not visible '
                           f'for {seconds}s')
        else:
            self.__put_log(f'{self.device_name}: element "{self.locator_type}: {self.locator}" is visible '
                           f'for {seconds}s')
        return self

    def wait_until_visible(self, seconds=10.0, log=True):
        start = time.time()
        err = None
        err_text = 'not'
        if self.__is_not:
            err_text = 'is'
        i = 0
        while time.time() < start + seconds or i < 1:
            try:
                self.get_element()
                if not self.__is_not:
                    if log:
                        self.__put_log(f'{self.device_name}: element "{self.locator_type}: {self.locator}" '
                                       f'found after {time.time() - start}s')
                    self.__is_not = False
                    return self
            except Exception as error:
                if self.__is_not:
                    if log:
                        self.__put_log(f'{self.device_name}: element "{self.locator_type}: {self.locator}" not visible '
                                       f'after {time.time() - start}s')
                    self.__is_not = False
                    return self
                err = error
                time.sleep(0.2)
            i += 1
        if err is None:
            err = ''
        if log:
            return self.__show_error(
                f'{logger.bcolors.FAIL}{err} {self.device_name} Element {err_text} found with the following locator: '
                f'"{self.locator_type}: {self.locator}" after {time.time() - start}s {logger.bcolors.ENDC}'
            )
        else:
            raise ElementException(error_with_traceback(err))

    def wait_until_attribute(self, attr, text, seconds=10):
        start = time.time()
        err = None
        value = ''
        err_text, info_text = 'should have been', '='
        if self.__is_not:
            err_text, info_text = 'should not have been', '!='
        while time.time() < start + seconds:
            try:
                value = self.get_element().get_attribute(attr)
                if (value == text) != self.__is_not:
                    self.__put_log(
                        f'{self.device_name}: element "{self.locator_type}: {self.locator}" has attribute '
                        f'"{attr}" -> "{value}" {info_text} "{text}" after {time.time() - start}s'
                    )
                    self.__is_not = False
                    return self
            except Exception as error:
                err = error
                time.sleep(0.2)
        if err is None:
            err = ''
        return self.__show_error(
            f'{logger.bcolors.FAIL}{err} {self.device_name} Element {err_text} found with the following locator: '
            f'"{self.locator_type}:{self.locator}" and '
            f'attribute "{attr}" -> "{value}" {err_text} "{text}" after {time.time() - start}s{logger.bcolors.ENDC}'
        )

    def wait_until_contains_attribute(self, attr, text, seconds=10):
        start = time.time()
        err = None
        value = ''
        info_text, err_text = 'containing', ' not'
        if self.__is_not:
            info_text, err_text = 'not containing', ' '
        while time.time() < start + seconds:
            try:
                value = self.get_element().get_attribute(attr)
                if value.__contains__(text) != self.__is_not:
                    self.__put_log(
                        f'element "{self.locator_type}: {self.locator}" has attribute '
                        f'"{attr}" {info_text} "{text}" after {time.time() - start}s'
                    )
                    self.__is_not = False
                    return self
            except Exception as error:
                err = error
                time.sleep(0.2)
        if err is None:
            err = ''
        return self.__show_error(
            f'{logger.bcolors.FAIL}{err} {self.device_name} Element{err_text} found with the following locator: '
            f'"{self.locator_type}:{self.locator}" and '
            f'attribute "{attr}" -> "{value}" {info_text} "{text}" after {time.time() - start}s {logger.bcolors.ENDC}'
        )

    def wait_until_contains_sensitive_attribute(self, attr, text, seconds=10.0, log=True):
        start = time.time()
        err = None
        value = ''
        info_text, err_text = 'contains', 'not'
        if self.__is_not:
            info_text, err_text = 'not contains', 'is'
        while time.time() < start + seconds:
            try:
                value = self.get_element().get_attribute(attr)
                if value.lower().__contains__(text.lower()) != self.__is_not:
                    self.__put_log(
                        f'{self.device_name}: element "{self.locator_type}: {self.locator}" has attribute '
                        f'"{attr}" -> "{value}" {info_text} no case sensitive value "{text}" after '
                        f'{time.time() - start}s'
                    )
                    self.__is_not = False
                    return self
            except Exception as error:
                err = error
                time.sleep(0.2)
        if err is None:
            err = ''
        if log:
            return self.__show_error(
                f'{logger.bcolors.FAIL}{err} {self.device_name} Element {err_text} found with the following locator: '
                f'"{self.locator_type}:{self.locator}" and attribute "{attr}" containing no case '
                f'sensitive value "{text}" {err_text} "{value}" after {time.time() - start}s {logger.bcolors.ENDC}'
            )
        else:
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
                    f'{self.device_name}: element "{self.locator_type}: {self.locator}" clicked after '
                    f'{time.time() - start}s'
                )
                return self
            except Exception as error:
                err = error
                time.sleep(0.2)
        return self.__show_error(
            f'{logger.bcolors.FAIL}{err} {self.device_name}: Element "{self.locator_type}: {self.locator}" '
            f'could not be clicked after {time.time() - start}s {logger.bcolors.ENDC}'
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
                    if is_browser.__contains__('NATIVE'):
                        browser = False
                    else:
                        browser = True
                except Exception:
                    browser = True
                if not browser:
                    ta = TouchAction(self.driver)
                    ta.press(self.get_element()).wait(milliseconds).release().perform()
                    self.__put_log(
                        f'{self.device_name}: element "{self.locator_type}: {self.locator}" pressed for '
                        f'{time.time() - start}s'
                    )
                    return self
                else:
                    from selenium.webdriver import ActionChains
                    ta = ActionChains(self.driver)
                    ta.click_and_hold(self.get_element()).pause(milliseconds // 1000).release().perform()
                    self.__put_log(
                        f'{self.device_name}: element "{self.locator_type}: {self.locator}" pressed for '
                        f'{time.time() - start}s'
                    )
                    return self
            except Exception as error:
                err = error
                time.sleep(0.2)
        return self.__show_error(
            f'{logger.bcolors.FAIL}{err} {self.device_name}: Element not found with the following locator: '
            f'"{self.locator_type}:{self.locator}" after {time.time() - start}s {logger.bcolors.ENDC}'
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
                    f'{self.device_name}: element "x={x}: y={y}" clicked after {time.time() - start}s'
                )
                return self
            except Exception as error:
                err = error
                time.sleep(0.2)
        return self.__show_error(
            f'{logger.bcolors.FAIL}{err} {self.device_name}: Element not found with the following locator: '
            f'"{self.locator_type}:{self.locator}" after {time.time() - start}s {logger.bcolors.ENDC}'
        )

    @property
    def location(self):
        return Dimensions(self.get_element().location.get('x'), self.get_element().location.get('y'))

    @property
    def dimensions(self):
        return Dimensions(self.get_element().size.get('width'), self.get_element().size.get('height'))

    def screenshot(self, image_name='cropped_image.png'):
        """
        Takes screenshot of the specific element
        :param image_name: relative path to image taken
        :return:
        """
        self.wait_until_visible()
        self.testui_driver.save_screenshot(f'{self.device_name}-crop_image.png')
        dimensions = self.dimensions
        top_left = self.location
        ImageRecognition(f'testui-{self.device_name}-crop_image.png').crop_original_image(
            top_left.x + dimensions.x // 2, top_left.y + dimensions.y // 2, dimensions.x, dimensions.y, image_name
        )
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        os.remove(root_dir + f'/testui-{self.device_name}-crop_image.png')

        return self

    def find_image_match(self, image_name, threshold=0.9, image_match='', max_scale=2.0, min_scale=0.3):
        """
        Takes screenshot of the element and compares it with the one you provide as 'image_name'
        :param min_scale:
        :param max_scale:
        :param image_match: returns the image with a rectangle showing the match
        :param image_name: relative path to image
        :param threshold: limit to consider image as a match (0 to 1)
        :return: Elements
        """
        is_not = self.__is_not
        self.__is_not = False
        self.screenshot(self.device_name + '.png')
        found, p = ImageRecognition(self.device_name + '.png', image_name, threshold, self.device_name) \
            .compare(image_match=image_match, max_scale=max_scale, min_scale=min_scale)
        if not found and not is_not:
            self.__show_error(f'{self.device_name}: The images compared did not match. threshold={threshold}. '
                              f'Matched = {p}')
        if found and is_not:
            self.__is_not = False
            self.__show_error(f'{self.device_name}: The images compared matched. threshold={threshold}. '
                              f'Matched = {p}')
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/'
        os.remove(root_dir + self.device_name + '.png')

        return self

    def is_image_match(self, image_name, threshold=0.9, image_match='', max_scale=2.0, min_scale=0.3):
        """
        Takes screenshot of the element and compares it with the one you provide as 'image_name'
        :param min_scale:
        :param max_scale:
        :param image_match: returns the image with a rectangle showing the match
        :param image_name: relative path to image
        :param threshold: limit to consider image as a match (0 to 1)
        :return: Elements
        """
        is_not = self.__is_not
        self.__is_not = False
        self.screenshot(self.device_name + '.png')
        found, p = ImageRecognition(self.device_name + '.png', image_name, threshold, self.device_name) \
            .compare(image_match=image_match, max_scale=max_scale, min_scale=min_scale)
        if not found and not is_not:
            return False
        if found and is_not:
            return False
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/'
        os.remove(root_dir + self.device_name + '.png')

        return True

    def swipe(self, start_x=None, start_y=None, end_x=None, end_y=None, el=None, duration=None):
        """
        It swipes from element to the el(second element) or to the coordinates you define with start_x, start_y,
        end_x, end_y. end_x and end_y are mandatory if el(second element) is not defined.
        :param start_x: Coordinate x from where it will begin swiping
        :param start_y: Coordinate y from where it will begin swiping
        :param end_x: Coordinate x from where it will end swiping
        :param end_y: Coordinate y from where it will end swiping
        :param el: element 'Elements' type from where it will end swiping (instead of end_x, end_y)
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
                    action \
                        .press(x=start_x, y=start_y) \
                        .wait(duration) \
                        .move_to(x=end_x, y=end_y) \
                        .release()
                    action.perform()
                else:
                    if end_x is None:
                        end_x = location.x
                    if end_y is None:
                        end_y = location.y
                    self.driver.swipe(start_y=start_y, start_x=start_x, end_y=end_y, end_x=end_x, duration=duration)
                return self
            except Exception as error:
                err = error
        return self.__show_error(
            f'{logger.bcolors.FAIL}{err} {self.device_name}: Element not found with the following locator: '
            f'"{self.locator_type}:{self.locator}" after {time.time() - start}s {logger.bcolors.ENDC}'
        )

    def slide_percentage(self, percentage, start_x=None):
        width = self.dimensions.x * percentage / 100
        end_width = width + self.location.x
        if start_x is None:
            start_x = self.location.x
        self.swipe(start_x=start_x, end_x=end_width)

    def swipe_until_text(self, start_x=None, start_y=None, end_x=None, end_y=None, text=None, el=None, max_swipes=50):
        """
        Swipe until an element with that text appears and Returns the element that contains the text. endX and
        endY are mandatory if el(element) is not defined. text is mandatory
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
            raise Exception("if element not specified, end_x and end_y must be to be able to swipe")
        if text is None:
            raise Exception('text cannot be None for swipe_until_text method')
        start = time.time()
        for i in range(max_swipes):
            try:
                e(self.testui_driver, 'uiautomator', f'textContains("{text}")').wait_until_visible(0.1, False)
                break
            except Exception:
                self.swipe(start_x, start_y, end_x, end_y, el, None)
        self.__put_log(f'{self.device_name}: element "{self.locator_type}: {self.locator}" with text {text} '
                       f'found after {time.time() - start}s')
        return e(self.testui_driver, 'uiautomator', f'textContains("{text}")')

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
                        f'{self.device_name}: element "{self.locator_type}: {self.locator}" '
                        f'received keys "{value}" after {time.time() - start}s'
                    )
                return self
            except Exception as error:
                err = error
                time.sleep(0.2)
        return self.__show_error(
            f'{logger.bcolors.FAIL}{err} {self.device_name}: Element not found with the following locator: '
            f'"{self.locator_type}:{self.locator}" after {time.time() - start}s {logger.bcolors.ENDC}'
        )

    def get_text(self):
        timeout = 10  # [seconds]
        start = time.time()

        err = None
        while time.time() < start + timeout:
            try:
                text = self.get_element().get_attribute("text")
                self.__put_log(
                    f'{self.device_name}: element "{self.locator_type}: {self.locator}" '
                    f'has text "{text}" {time.time() - start}s'
                )
                return text
            except Exception as error:
                err = error
                time.sleep(0.2)
        self.__show_error(
            f'{logger.bcolors.FAIL}{err} {self.device_name}: Element not found with the following locator: '
            f'"{self.locator_type}:{self.locator}" after {time.time() - start}s {logger.bcolors.ENDC}'
        )

    def get_value(self):
        timeout = 10  # [seconds]
        start = time.time()

        err = None
        while time.time() < start + timeout:
            try:
                text = self.get_element().get_attribute("value")
                self.__put_log(
                    f'{self.device_name}: element "{self.locator_type}: {self.locator}" '
                    f' has text "{text}" {time.time() - start}s'
                )
                return text
            except Exception as error:
                err = error
                time.sleep(0.2)
        self.__show_error(
            f'{logger.bcolors.FAIL}{err} {self.device_name}: Element not found with the following locator: '
            f'"{self.locator_type}:{self.locator}" after {time.time() - start}s {logger.bcolors.ENDC}'
        )

    def get_name(self):
        timeout = 10  # [seconds]
        start = time.time()

        err = None
        while time.time() < start + timeout:
            try:
                text = self.get_element().get_attribute("name")
                self.__put_log(
                    f'{self.device_name}: element "{self.locator_type}: {self.locator}" '
                    f'has name "{text}" {time.time() - start}s'
                )
                return text
            except Exception as error:
                err = error
                time.sleep(0.2)
        self.__show_error(
            f'{logger.bcolors.FAIL}{err} {self.device_name}: Element not found with the following locator: '
            f'"{self.locator_type}:{self.locator}" after {time.time() - start}s {logger.bcolors.ENDC}'
        )

    def get_attribute(self, att):
        timeout = 10  # [seconds]
        start = time.time()

        err = None
        while time.time() < start + timeout:
            try:
                text = self.get_element().get_attribute(att)
                self.__put_log(
                    f'{self.device_name}: element "{self.locator_type}: {self.locator}" '
                    f' has "{att}: {text}" {time.time() - start}s'
                )
                return text
            except Exception as error:
                err = error
                time.sleep(0.2)
        self.__show_error(
            f'{logger.bcolors.FAIL}{err} {self.device_name}: Element not found with the following locator: '
            f'"{self.locator_type}:{self.locator}" after {time.time() - start}s {logger.bcolors.ENDC}'
        )

    def press_and_compare(self, image, milliseconds=1000, threshold=0.9, fps_reduction=1, keep_image_as=''):
        self.testui_driver.start_recording_screen()
        self.press_hold_for(milliseconds)
        found = ''
        if self.__is_not:
            found = 'not'
        not_found = 'not'
        start = time.time()
        if self.__is_not:
            not_found = ''
        if self.testui_driver.stop_recording_and_compare(
                image, threshold, fps_reduction, self.__is_not, keep_image_as, False):
            self.__put_log(
                f'{self.device_name}: image {found} found while pressing element "{self.locator_type}: {self.locator}" '
                f'after {time.time() - start}s'
            )
        else:
            self.__show_error(
                f'{self.device_name}: image {not_found} found while pressing element '
                f'"{self.locator_type}: {self.locator}" after {time.time() - start}s'
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

    def find_by_attribute(self, attribute, value: str, timeout=10, case_sensitive=True):
        start = time.time()
        self.wait_until_visible()
        self.__is_collection = True
        while time.time() < start + timeout:
            for i, element in enumerate(self.__find_by_collection()):
                if case_sensitive and element.get_attribute(attribute) == value:
                    self.__put_log(
                        f'{self.device_name}: element in collection "{self.locator_type}: {self.locator}" '
                        f'with attribute "{attribute}" = "{value}" found after {time.time() - start}s'
                    )
                    self.index = i
                    return self
                if not case_sensitive and element.get_attribute(attribute).lower() == value.lower():
                    self.__put_log(
                        f'{self.device_name}: element in collection "{self.locator_type}: {self.locator}" '
                        f'with attribute "{attribute}" = "{value}" found after {time.time() - start}s'
                    )
                    self.index = i
                    return self
        self.__show_error(
            f'{self.device_name}: no element in collection '
            f'"{self.locator_type}: {self.locator}" had attribute "{attribute}" = "{value}" after {time.time() - start}s'
        )


class AndroidLocator(object):
    @classmethod
    def scroll(cls, method: str, scrollable_element=None):
        if scrollable_element is None:
            locator = f'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView({method});'
        else:
            locator = f'new UiScrollable(new UiSelector().{scrollable_element}).scrollIntoView({method});'
        return locator

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
        return f'fromParent({parent_method}).{child_method}'

    @classmethod
    def child(cls, parent_method, child_method):
        return f'childSelector({child_method}).{parent_method}'
