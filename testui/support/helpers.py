import os
import traceback

from testui.support import logger


def error_with_traceback(exception):
    """
    This function is used to get the full stacktrace of an exception
    :param exception: Exception
    :return: String
    """
    root_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    line: str
    for line in traceback.extract_stack().format():
        if root_dir in line and "traceback.extract_stack()" not in line:
            exception += logger.bcolors.FAIL + line + logger.bcolors.ENDC
    return exception
