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
    """
    This class is the main class for the TestUI framework. It is used to
    initialize the driver and to perform actions on the device.
    """

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
        """
        Switch to a specific context
        :param context: context number
        :param last: if True, switch to the last context
        :return: TestUIDriver
        """
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
        """
        Returns the current context
        :return: current context
        """
        return self.__appium_driver.contexts

    def e(self, locator_type, locator):
        """
        This method is meant for Selenium or Browser views (Mobile and Desktop)
        :param locator_type:
        :param locator:
        :return: Elements
        """
        return e(self, locator_type, locator)

    def execute(self, driver_command, params=None):
        """
        This method is meant for Appium Drivers only. Will execute a command
        in the current driver.
        :param driver_command:
        :param params:
        :return: TestUIDriver
        """
        self.get_driver.execute(driver_command, params)
        return self

    def remove_log_file(self, when_no_errors=True):
        """
        Removes appium log file. If when_no_errors is False, it will always
        remove errors, if True then just when there are errors.
        :param when_no_errors:
        :return: TestUIDriver
        """
        if self.file_name is not None:
            try:
                if when_no_errors and len(self.errors) == 0:
                    os.remove(self.file_name)
                elif not when_no_errors:
                    os.remove(self.file_name)
            except FileNotFoundError:
                logger.log_debug("Log file already removed")
        return self

    def touch_actions(self) -> TouchAction:
        """
        Deprecated function, soon to be removed, use actions instead.

        Will return a TouchAction object for the current driver. This is
        meant for Appium Drivers only.
        :return: TouchAction
        """
        return TouchAction(self.get_driver)

    def actions(self) -> ActionChains:
        """
        Will return an ActionChains object for the current driver.
        :return: ActionChains
        """
        return ActionChains(self.get_driver)

    def open_notifications(self):
        """
        Will open the notifications panel on the device. This method is meant
        for Appium Drivers only
        :return: TestUIDriver
        """
        self.get_driver.open_notifications()
        return self

    def back(self):
        """
        Will perform a back action on the device in browser history.
        :return: TestUIDriver
        """
        self.get_driver.back()
        return self

    def quit(self, stop_server=True):
        """
        Will quit the driver and stop the server if stop_server is True.
        :param stop_server:
        :return:
        """
        self.get_driver.quit()
        if self.__process is not None and stop_server:
            self.__process.kill()

    def navigate_to(self, url):
        """
        Will navigate to a specific url.
        :param url:
        :return: TestUIDriver
        """
        self.get_driver.get(url)
        logger.log(f"{self.device_name}: Navigating to: {url}")
        return self

    def execute_script(self, driver_command, args: None) -> dict:
        """
        Will execute a JavaScript script in the current window/frame.
        :param driver_command:
        :param args:
        :return: dict of the result of executed script
        """
        return self.get_driver.execute_script(driver_command, args)

    @property
    def switch_to(self):
        """
        Will return a SwitchTo object describing all options to switch focus.
        This method is meant for Appium Drivers only.
        :return:
        """
        return self.get_driver.switch_to

    def set_network_connection(self, number):
        """
        Will set the network connection type based on the network connection
        number. This method is meant for Appium Drivers Only
        :param number:
        :return: TestUIDriver
        """
        self.get_driver.set_network_connection(number)
        return self

    @property
    def network_connection(self) -> int:
        """
        Get the current network connection type. This method is meant for
        Appium Drivers only.
        :return:
        """
        return self.get_driver.network_connection

    def find_image_match(
        self,
        comparison,
        threshold=0.90,
        assertion=False,
        not_found=False,
        image_match="",
    ) -> bool:
        """
        Will find an image match based on the comparison type and threshold
        within the current screen.
        :param comparison:
        :param threshold:
        :param assertion:
        :param not_found:
        :param image_match:
        :return: bool
        """
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d%H%M%S")
        image_name = f"{self.device_udid}{current_time}.png"
        image_path = self.save_screenshot(image_name)
        comparison = os.path.join(
            self.__configuration.screenshot_path,
            comparison
        )
        found, p = ImageRecognition(
            image_path,
            comparison,
            threshold,
            self.device_name,
            self.configuration.screenshot_path,
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
        """
        Will click on an element based on the image provided if it can be found
        within the current screen.
        :param image:
        :param threshold:
        :param webview:
        :return: TestUIDriver
        """
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d%H%M%S")
        image_name = f"{self.device_udid}{current_time}.png"
        im_path = self.save_screenshot(image_name)
        x, y = get_point_match(im_path, image, threshold, self.device_name)
        ta = TouchAction(self.__appium_driver)
        if webview:
            y = y + 120
        ta.tap(x=x, y=y).perform()
        logger.log(
            f"{self.device_name}: element with image {image}"
            f"clicked on point ({x},{y})"
        )
        self.__delete_screenshot(im_path)

        return self

    def get_dimensions(self):
        """
        Will return the dimensions of the current screen.
        :return:
        """
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d%H%M%S")
        image_name = f"{self.device_udid}{current_time}.png"
        path_s = self.save_screenshot(image_name)
        dimensions = ImageRecognition(
            original=path_s, path=""
        ).image_original_size()
        logger.log(f"Deleting screenshot: {path_s}")
        self.__delete_screenshot(path_s)
        return dimensions

    def click(self, x, y):
        """
        Will execute a touch action on the current screen based on the x and y
        coordinates.
        :param x:
        :param y:
        :return: TestUIDriver
        """
        ta = TouchAction(self.__appium_driver)
        ta.tap(x=x, y=y).perform()
        logger.log(f'Clicked over "x={x}: y={y}"')
        return self

    def save_screenshot(self, image_name="") -> str:
        """
        Will save a screenshot of the current screen. If no image_name is
        provided, it will generate a name based on the current time.
        :param image_name:
        :return: str of the path where the screenshot was saved.
        """
        config = self.__configuration

        log_dir = config.screenshot_path
        if not config.screenshot_path:
            log_dir = "./logs"
            log_dir = path.join(log_dir, "report_screenshots")

        Path(log_dir).mkdir(parents=True, exist_ok=True)

        current_time = datetime.now().strftime("%Y-%m-%d%H%M%S")

        if not image_name:
            image_name = f"ERROR-{self.device_name}-{current_time}.png"

        final_path = path.join(log_dir, image_name)

        self.get_driver.save_screenshot(final_path)

        logger.log_debug(
            self.new_error_message(f'Screenshot saved in "{final_path}"')
        )

        return final_path

    @classmethod
    def __delete_screenshot(cls, image_name):
        """
        Will delete the provided screenshot.
        :param image_name:
        :return:
        """
        os.remove(image_name)

    @property
    def get_driver(self) -> WebDriver:
        """
        Will return the current driver.
        :return: WebDriver
        """
        driver = self.__appium_driver

        return driver

    @property
    def configuration(self) -> Configuration:
        """
        Will return the current configuration.
        :return: Configuration
        """
        return self.__configuration

    def set_error(self, error):
        """
        Will add an error to the current list of errors.
        :param error:
        :return:
        """
        self.errors.append(error)

    def raise_errors(self, remove_log_file=False):
        """
        Will raise all the errors in the current list of errors.
        :param remove_log_file: If True, appium logs will be deleted.
        :return:
        """
        if len(self.errors) != 0:
            composed_error = "\n"
            i = 1
            for error in self.errors:
                composed_error += f"Error {str(i)}: {error}\n"
                i += 1
            self.errors = []
            raise Exception(composed_error)
        if remove_log_file:
            self.remove_log_file()

    def get_clipboard_text(self) -> str:
        """
        Will return the current clipboard text.
        :return: The current clipboard text.
        """
        return self.get_driver.get_clipboard_text()

    def set_power_capacity(self, capacity: int):
        """
        Will set the power capacity of the current device.
        :param capacity: The power capacity to set.
        :return: TestUIDriver
        """
        try:
            self.get_driver.set_power_capacity(capacity)
        except WebDriverException as wd_exception:
            exception = self.new_error_message(
                "powerCapacity method is only available for emulators"
            )
            logger.log_error(error_with_traceback(exception))
            raise Exception(exception) from wd_exception
        return self

    def background_app(self, seconds):
        """
        Will background the current app for the provided seconds.
        :param seconds: The seconds to background the app.
        :return: TestUIDriver
        """
        self.get_driver.background_app(seconds)
        return self

    def remove_app(self, app_id):
        """
        Will remove the provided app from the current device.
        :param app_id: The app id to remove.
        :return: TestUIDriver
        """
        self.get_driver.remove_app(app_id)
        return self

    def install_app(self, app_id):
        """
        Will install the provided app in the current device.
        :param app_id: The app id to install.
        :return: TestUIDriver
        """
        self.get_driver.install_app(app_id)
        return self

    def start_recording_screen(self):
        """
        Start recording the screen on current device.
        :return: TestUIDriver
        """
        self.get_driver.start_recording_screen()
        return self

    def stop_recording_screen(self, file_name="testui-video.mp4"):
        """
        Stop recording the screen and save the video in the root directory.
        :param file_name:
        :return: TestUIDriver
        """
        file = self.get_driver.stop_recording_screen()
        decoded_string = base64.b64decode(file)
        log_dir = self.configuration.screenshot_path
        logger.log(f"Recording stopped in {os.path.join(log_dir, file_name)}")
        with open(os.path.join(log_dir, file_name), "wb") as wfile:
            wfile.write(decoded_string)

        return self

    def stop_recording_and_compare(
        self,
        comparison,
        threshold=0.9,
        fps_reduction=1,
        not_found=False,
        keep_image_as="",
        assertion=True,
    ) -> bool:
        """
        Stop recording the screen and compare the video with the given image
        :param comparison:
        :param threshold:
        :param fps_reduction:
        :param not_found:
        :param keep_image_as:
        :param assertion:
        :return: True if the image was found in the video, False otherwise
        """
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d%H%M%S")
        log_dir = self.__configuration.screenshot_path
        video_name = f"{self.device_udid}{current_time}.mp4"
        self.stop_recording_screen(os.path.join(log_dir, video_name))
        found = ImageRecognition(
            video_name,
            comparison,
            threshold,
            device_name=self.device_name,
            path=log_dir
        ).compare_video(keep_image_as, frame_rate_reduction=fps_reduction)

        os.remove(os.path.join(log_dir, video_name))
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
        """
        Create new error message with device name included
        :param message:
        :return: str containing the error message
        """
        return f"{self.device_name}: {message}"

    def hide_keyboard(self):
        """
        Hide the keyboard if it is showing.
        This method is meant for Appium Drivers Only.
        :return: TestUIDriver
        """
        self.get_driver.hide_keyboard()
        return self
