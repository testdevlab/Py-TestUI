import os
import traceback

from testui.support import logger


def error_with_traceback(exception):
    """
    This function is used to get the full stacktrace of an exception
    :param exception: Exception
    :return: String
    """
    project_dir = os.getcwd()
    line: str
    for line in traceback.extract_stack().format():
        if (
            project_dir in line
            and "site-packages" not in line
            and "dist-packages" not in line
            and "traceback.extract_stack()" not in line
        ):
            exception += logger.bcolors.FAIL + line + logger.bcolors.ENDC
    return exception
