import base64
import os

from datetime import datetime
from os import path
from pathlib import Path

from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.webdriver import WebDriver
from selenium.webdriver import ActionChains
from selenium.common.exceptions import WebDriverException

from testui.elements.testui_element import e
from testui.support import logger
from testui.support.helpers import error_with_traceback
from testui.support.testui_images import get_point_match, ImageRecognition
from testui.support.configuration import Configuration


class TestUIDriver:
    __test__ = False

    def __init__(self, driver):
        self.__soft_assert = driver.soft_assert
        self.__appium_driver = driver.get_driver()
        self.__process = driver.process
        self.errors = []
        self.appium_port = driver.appium_port
        self.browser: bool = driver.browser
        self.logger_name = driver.logger_name
        self.soft_assert: bool = driver.soft_assert
        self.device_udid = driver.udid
        self.device_name = driver.device_name
        self.file_name = driver.file_name
        self.__configuration: Configuration = driver.configuration

    def switch_to_context(self, context=0, last=False):
        if last:
            context = len(self.__appium_driver.contexts) - 1
        try:
            if len(self.__appium_driver.contexts) == 1:
                logger.log(
                    f"{self.device_name}: There is only one context: "
                    f"{self.__appium_driver.contexts[context]}"
                )
            elif context >= len(self.__appium_driver.contexts):
                logger.log_warn(
                    f"{self.device_name}: Cannot switch to context {context}: "
                    f"there are just {len(self.__appium_driver.contexts)} "
                    "contexts"
                )
            self.__appium_driver.execute(
                "switchToContext",
                {"name": self.__appium_driver.contexts[context]},
            )
            logger.log(
                f"{self.device_name}: Switched to context: "
                f"{self.__appium_driver.contexts[context]}"
            )
        except Exception as err:
            if self.__soft_assert:
                logger.log_error(err)
            else:
                raise err
        return self

    @property
    def context(self):
        return self.__appium_driver.contexts

    def e(self, locator_type, locator):
        return e(self, locator_type, locator)

    def execute(self, driver_command, params=None):
        self.get_driver().execute(driver_command, params)

    def remove_log_file(self, when_no_errors=True):
        """
        removes appium log file. If when_no_errors is False, it will always
        remove errors, if True then just when there are errors.
        :param when_no_errors:
        :return:
        """
        if self.file_name is not None:
            try:
                if when_no_errors and len(self.errors) == 0:
                    os.remove(self.file_name)
                elif not when_no_errors:
                    os.remove(self.file_name)
            except FileNotFoundError:
                logger.log_debug("Log file already removed")

    def touch_actions(self):
        """
        This method is meant for Appium Drivers Only
        :return:
        """
        return TouchAction(self.get_driver())

    def actions(self):
        """
        This method is meant for Selenium or Browser views (Mobile and Desktop)
        :return:
        """
        return ActionChains(self.get_driver())

    def open_notifications(self):
        self.get_driver().open_notifications()

    def back(self):
        self.get_driver().back()
        return self

    def quit(self, stop_server=True):
        self.get_driver().quit()
        if self.__process is not None and stop_server:
            self.__process.kill()

    def navigate_to(self, url):
        self.get_driver().get(url)
        logger.log(f"{self.device_name}: Navigating to: {url}")

    def execute_script(self, driver_command, args: None):
        self.get_driver().execute_script(driver_command, args)

    @property
    def switch_to(self):
        return self.get_driver().switch_to

    def set_network_connection(self, number):
        self.__appium_driver.set_network_connection(number)

    @property
    def network_connection(self):
        return self.__appium_driver.network_connection

    def find_image_match(
        self,
        comparison,
        threshold=0.90,
        assertion=False,
        not_found=False,
        image_match="",
    ):
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d%H%M%S")
        image_name = f"{self.device_udid}{current_time}.png"
        image_path = self.save_screenshot(image_name)
        found, p = ImageRecognition(
            image_path, comparison, threshold, self.device_name, self.configuration.screenshot_path
        ).compare(image_match)
        if assertion and not found and not not_found:
            exception = self.new_error_message(
                "The images compared did not match"
                f"Threshold={threshold}, matched = {p}"
            )
            logger.log_error(error_with_traceback(exception))
            raise Exception(exception)
        os.remove(image_path)

        return found

    def click_by_image(self, image: str, threshold=0.9, webview=False):
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d%H%M%S")
        image_name = f"{self.device_udid}{current_time}.png"
        im_path = self.save_screenshot(image_name)
        x, y = get_point_match(
            im_path, image, threshold, self.device_name
        )
        ta = TouchAction(self.__appium_driver)
        if webview:
            y = y + 120
        ta.tap(x=x, y=y).perform()
        logger.log(f"{self.device_name}: element with image {image} clicked on point ({x},{y})")
        self.__delete_screenshot(im_path)

    def get_dimensions(self):
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d%H%M%S")
        image_name = f"{self.device_udid}{current_time}.png"
        self.save_screenshot(image_name)
        dimensions = ImageRecognition(
            original=image_name,
            path=self.configuration.screenshot_path
        ).image_original_size()
        im_path = os.path.join(
            self.configuration.screenshot_path,
            image_name
        )
        logger.log(f"Deleting screenshot: {im_path}")
        self.__delete_screenshot(im_path)
        return dimensions

    def click(self, x, y):
        ta = TouchAction(self.__appium_driver)
        ta.tap(x=x, y=y).perform()
        logger.log(f'Clicked over "x={x}: y={y}"')

    def save_screenshot(self, image_name=""):
        config = self.__configuration

        root_dir = config.screenshot_path
        if not config.screenshot_path:
            root_dir = path.dirname(
                path.dirname(path.dirname(path.abspath(__file__)))
            )
            root_dir = path.join(root_dir, "report_screenshots")

        Path(root_dir).mkdir(parents=True, exist_ok=True)

        current_time = datetime.now().strftime("%Y-%m-%d%H%M%S")

        if not image_name:
            image_name = f"ERROR-{self.device_name}-{current_time}.png"

        final_path = path.join(root_dir, image_name)

        self.get_driver().save_screenshot(final_path)

        logger.log_debug(
            self.new_error_message(f'Screenshot saved in "{final_path}"')
        )

        return final_path

    @classmethod
    def __delete_screenshot(cls, image_name):
        os.remove(image_name)

    def get_driver(self) -> WebDriver:
        driver = self.__appium_driver

        return driver

    @property
    def configuration(self) -> Configuration:
        return self.__configuration

    def set_error(self, error):
        self.errors.append(error)

    def raise_errors(self, remove_log_file=False):
        if len(self.errors) != 0:
            composed_error = "\n"
            i = 1
            for error in self.errors:
                composed_error += f"Error {i.__str__()}: {error}\n"
                i += 1
            self.errors = []
            raise Exception(composed_error)
        if remove_log_file:
            self.remove_log_file()

    def get_clipboard_text(self) -> str:
        return self.__appium_driver.get_clipboard_text()

    def set_power_capacity(self, capacity: int):
        try:
            self.get_driver().set_power_capacity(capacity)
        except WebDriverException as wd_exception:
            exception = self.new_error_message(
                "powerCapacity method is only available for emulators"
            )
            logger.log_error(error_with_traceback(exception))
            raise Exception(exception) from wd_exception

    def background_app(self, seconds):
        self.get_driver().background_app(seconds)

    def remove_app(self, app_id):
        self.get_driver().remove_app(app_id)

    def install_app(self, app_id):
        self.get_driver().install_app(app_id)

    def start_recording_screen(self):
        self.get_driver().start_recording_screen()

    def stop_recording_screen(self, file_name="testui-video.mp4"):
        file = self.get_driver().stop_recording_screen()
        decoded_string = base64.b64decode(file)
        root_dir = self.configuration.screenshot_path
        logger.log(f"Recording stopped in {os.path.join(root_dir, file_name)}")
        with open(os.path.join(root_dir, file_name), "wb") as wfile:
            wfile.write(decoded_string)

    def stop_recording_and_compare(
        self,
        comparison,
        threshold=0.9,
        fps_reduction=1,
        not_found=False,
        keep_image_as="",
        assertion=True,
    ):
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d%H%M%S")
        video_name = f"{self.device_udid}{current_time}.mp4"
        self.stop_recording_screen(video_name)
        root_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        found = ImageRecognition(
            video_name, comparison, threshold, device_name=self.device_name
        ).compare_video(keep_image_as, frame_rate_reduction=fps_reduction)

        os.remove(root_dir + f"/{video_name}")
        if not found and not not_found:
            if assertion:
                raise Exception(
                    self.new_error_message(
                        "The image and video compared did not match. "
                        f"Threshold={threshold}"
                    )
                )

            return False
        if found and not_found:
            if assertion:
                raise Exception(
                    self.new_error_message(
                        "The image and video compared matched. "
                        f"Threshold={threshold}"
                    )
                )

            return False
        return True

    def new_error_message(self, message) -> str:
        return f"{self.device_name}: {message}"

    def hide_keyboard(self):
        self.get_driver().hide_keyboard()
