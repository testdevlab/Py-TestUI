import os
import threading
import time
from datetime import datetime
from pathlib import Path

from testui.elements.testui_element import Elements
from testui.support import logger


def ee(*args):
    """locator types: id, css, className, name, xpath, accessibility, uiautomator, classChain, predicate"""
    return Collections(args)


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class CollectionException(Error):
    def __init__(self, message, expression=''):
        self.message = message
        self.expression = expression


class Collections(object):

    def __init__(self, args):
        self.args = args
        self.__errors = list()

    def wait_until_all_visible(self, seconds=10.0, log=True):
        start = time.time()
        threads = list()
        for arg in self.args:
            threads.append(threading.Thread(target=arg.wait_until_visible, args=(seconds, log)))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        if time.time() < start + seconds:
            logger.log(
                f"{self.args[0].device_name}: Collection of elements has been found after {time.time() - start}s"
            )
        else:
            compose_error = ''
            error: str
            for error in self.__errors:
                compose_error = compose_error + f'{error} \n'
            self.__show_error(
                f'{self.args[0].device_name}: Collection of elements has not been found '
                f'after {time.time() - start}s: \n {compose_error}')

    def find_visible(self, seconds=10, return_el_number=False):
        start = time.time()
        arg: Elements
        i = 0
        while time.time() < start + seconds or i < 1:
            for i, arg in enumerate(self.args):
                if arg.is_visible(log=False):
                    logger.log(f'{self.args[i].device_name}: element '
                               f'"{self.args[i].locator_type}: {self.args[i].locator}" found visible')
                    if return_el_number:
                        return arg, i
                    else:
                        return arg
            i += 1
        self.__show_error(
            f"{self.args[0].device_name}: No element within the collection was found visible "
            f"after {time.time() - start}s:")

    def wait_until_attribute(self, attr_type: list, attr: list, seconds=10):
        start = time.time()
        if len(attr_type) != len(self.args) or len(attr_type) != len(attr):
            raise Exception('The number of attributes checked must be the same as number of elements in collection')
        threads = list()
        i = 0
        element: Elements
        for element in self.args:
            threads.append(
                threading.Thread(target=self.__wait_until_attribute, args=(element, attr_type[i], attr[i], seconds)))
            i += 1
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        if time.time() < start + seconds:
            logger.log(
                f"{self.args[0].device_name}: Collection of elements has been found with the correct attributes "
                f"after {time.time() - start}s"
            )
        else:
            compose_error = ''
            error: str
            for error in self.__errors:
                compose_error = compose_error + f'{error} \n'
            self.__show_error(
                '{self.args[0].device_name}: Collection of elements has not been found with the correct attributes '
                f'after {time.time() - start}s: \n {compose_error}')

    def get(self, index: int):
        element: Elements = self.args[index]
        return element

    def __wait_until_attribute(self, element: Elements, attr_type, attr, seconds):
        try:
            element.wait_until_attribute(attr_type, attr, seconds)
        except Exception as err:
            self.__errors.append(err)

    def __show_error(self, exception):
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d%H%M%S")
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        Path(root_dir + "/report_screenshots").mkdir(parents=True, exist_ok=True)
        image_name = f'ERROR-{self.args[0].device_name}-{current_time}.png'
        self.args[0].testui_driver.save_screenshot(image_name, directory='report_screenshots/')
        exception = exception + f'{logger.bcolors.FAIL} \n Screenshot taken and saved as: ' \
                                f'report_screenshots/testui-{image_name}{logger.bcolors.ENDC}'
        from testui.support.helpers import error_with_traceback
        full_exception = error_with_traceback(exception)
        if self.args[0].testui_driver.soft_assert:
            logger.log_error(full_exception)
            self.args[0].testui_driver.set_error(full_exception)
            return self
        else:
            logger.log_error(full_exception)
            self.args[0].testui_driver.set_error(full_exception)
            raise CollectionException(exception)
