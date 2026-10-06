import threading
import time

from testui.elements.testui_element import Elements
from testui.support import logger
from testui.support.configuration import Configuration
from testui.support.helpers import error_with_traceback


class Error(Exception):
    """Base class for exceptions in this module"""


# pylint: disable=super-init-not-called
class CollectionException(Error):
    """Exception raised for errors in the input"""

    def __init__(self, message, expression=""):
        self.message = message
        self.expression = expression


class Collections:
    """
    Class for working with collections of elements
    """

    def __init__(self, args):
        """
        :param args: list of elements
        """
        self.args = args
        self.__errors = []

    def wait_until_all_visible(self, seconds=10.0, log=True):
        """
        Wait until all elements in collection are visible
        :param seconds: timeout
        :param log: log to console
        """
        start = time.time()
        all_found = self.__run_waits(
            [(arg.wait_until_visible, seconds, log) for arg in self.args]
        )
        if all_found:
            logger.log(
                f"{self.args[0].device_name}: Collection of elements has been "
                f"found after {time.time() - start}s"
            )
        else:
            compose_error = ""
            error: str
            for error in self.__errors:
                compose_error = compose_error + f"{error} \n"
            self.__show_error(
                f"{self.args[0].device_name}: Collection of elements has not "
                f"been found after {time.time() - start}s: \n {compose_error}"
            )

    def wait_until_all_exist(self, seconds=10.0, log=True):
        """
        Wait until all elements in collection are visible
        :param seconds: timeout
        :param log: log to console
        """
        start = time.time()
        all_found = self.__run_waits(
            [(arg.wait_until_exists, seconds, log) for arg in self.args]
        )
        if all_found:
            logger.log(
                f"{self.args[0].device_name}: Collection of elements has been "
                f"found after {time.time() - start}s"
            )
        else:
            compose_error = ""
            error: str
            for error in self.__errors:
                compose_error = compose_error + f"{error} \n"
            self.__show_error(
                f"{self.args[0].device_name}: Collection of elements has not "
                f"been found after {time.time() - start}s: \n {compose_error}"
            )

    def find_visible(self, seconds=10, return_el_number=False):
        """
        Find first visible element in collection
        :param seconds: timeout
        :param return_el_number: return element number
        :return: element
        """
        start = time.time()
        arg: Elements
        i = 0
        while time.time() < start + seconds or i < 1:
            for i, arg in enumerate(self.args):
                if arg.is_visible(log=False):
                    logger.log(
                        f"{self.args[i].device_name}: element "
                        f'"{self.args[i].locator_type}: '
                        f'{self.args[i].locator}" found visible'
                    )
                    if return_el_number:
                        return arg, i

                    return arg
            i += 1
            time.sleep(0.2)
        self.__show_error(
            f"{self.args[0].device_name}: No element within the collection was "
            f"found visible after {time.time() - start}s:"
        )

    def wait_until_attribute(self, attr_type: list, attr: list, seconds=10):
        """
        Wait until all elements in collection have the correct attribute
        :param attr_type: list of attribute types
        :param attr: list of attributes
        :param seconds: timeout
        """
        start = time.time()
        if len(attr_type) != len(self.args) or len(attr_type) != len(attr):
            raise Exception(
                "The number of attributes checked must be the same as number "
                "of elements in collection"
            )
        all_found = self.__run_waits(
            [
                (element.wait_until_attribute, attr_type[i], attr[i], seconds)
                for i, element in enumerate(self.args)
            ]
        )
        if all_found:
            logger.log(
                f"{self.args[0].device_name}: Collection of elements has been "
                "found with the correct attributes "
                f"after {time.time() - start}s"
            )
        else:
            compose_error = ""
            error: str
            for error in self.__errors:
                compose_error = compose_error + f"{error} \n"
            self.__show_error(
                f"{self.args[0].device_name}: Collection of elements has not "
                "been found with the correct attributes "
                f"after {time.time() - start}s: \n {compose_error}"
            )

    def get(self, index: int):
        """
        Get element by index
        :param index: element index
        :return: element
        """
        element: Elements = self.args[index]
        return element

    def __run_waits(self, waits) -> bool:
        """
        Runs each (wait, *args) in its own thread.
        :return: True if no wait raised or recorded a soft-assert error
        """
        self.__errors = []
        driver_errors = self.args[0].testui_driver.errors
        errors_before = len(driver_errors)
        threads = [
            threading.Thread(target=self.__run_wait, args=wait)
            for wait in waits
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        return not self.__errors and len(driver_errors) == errors_before

    def __run_wait(self, wait, *args):
        try:
            wait(*args)
        except Exception as err:
            self.__errors.append(err)

    def __show_error(self, exception) -> None:
        """
        Show error for provided expectation
        :param exception: exception
        """
        driver = self.args[0].testui_driver
        config: Configuration = driver.configuration

        if config.save_screenshot_on_fail:
            driver.save_screenshot()

        full_exception = exception
        if config.save_full_stacktrace:
            full_exception = error_with_traceback(exception)

        if driver.soft_assert:
            logger.log_error(full_exception)
            driver.set_error(full_exception)
        else:
            logger.log_error(full_exception)
            driver.set_error(full_exception)
            raise CollectionException(exception)


def ee(*args) -> Collections:
    """
    Create collection of elements
    Available locator types:
        id,
        css,
        className,
        name,
        xpath,
        accessibility,
        uiautomator,
        classChain,
        predicate
    :param args: list of elements
    :return: collection of elements
    """
    return Collections(args)
