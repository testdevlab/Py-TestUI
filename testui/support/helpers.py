import os
import traceback

from testui.support import logger


def error_with_traceback(exception):
    root_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    line: str
    for line in traceback.extract_stack().format():
        if line.__contains__(root_dir) and not line.__contains__(
                'traceback.extract_stack()'):
            exception += logger.bcolors.FAIL + line + logger.bcolors.ENDC
    return exception
