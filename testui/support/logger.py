import os
from datetime import datetime
from pathlib import Path

LOG_DIR = "./logs"

class bcolors:
    """
    Colors for console output
    """

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def log(message, jump_line=False):
    """
    Log a message to the console and to the log file
    :param message: String
    :param jump_line: Boolean
    """
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    new_line = ""
    if jump_line:
        new_line = "\n"
    print(f"{new_line}{bcolors.OKBLUE}[{current_time}] {message}{bcolors.ENDC}")
    file = open(__file_log(), "a+")
    file.write(f"{new_line}[{current_time}] {message}\n{new_line}")
    file.close()


def log_pass(message, jump_line=False):
    """
    Log a message to the console and to the log file
    :param message: String
    :param jump_line: Boolean
    """
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    new_line = ""
    if jump_line:
        new_line = "\n"
    print(
        f"{new_line}{bcolors.OKGREEN}[{current_time}] {message}{bcolors.ENDC}"
    )
    file = open(__file_log(), "a+")
    file.write(f"{new_line}[{current_time}] {message}\n{new_line}")
    file.close()


def log_error(message, use_date=False):
    """
    Log an error message to the console and to the log file
    :param message: String
    :param use_date: Boolean
    """
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    date = ""
    if use_date:
        date = f"[{current_time}] "
    print(f"{bcolors.FAIL}{date}{message}{bcolors.ENDC}")
    file = open(__file_log(), "a+")

    file.write(f"{date}{message}\n")
    file.close()


def log_debug(message):
    """
    Log a debug message to the console and to the log file
    :param message: String
    """
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    print(f"{bcolors.OKBLUE}[{current_time}] {message}{bcolors.ENDC}")
    file = open(__file_log(), "a+")
    file.write(f"[{current_time}] {message}\n")
    file.close()


def log_warn(message, jump_line=False):
    """
    Log a warning message to the console and to the log file
    :param message: String
    :param jump_line: Boolean
    """
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    new_line = ""
    if jump_line:
        new_line = "\n"
    print(
        f"{new_line}{bcolors.WARNING}[{current_time}] "
        f"{message}{bcolors.ENDC}{new_line}"
    )
    file = open(__file_log(), "a+")
    file.write(f"{new_line}[{current_time}] {message}\n{new_line}")
    file.close()


def log_test_name(message, jump_line=False):
    """
    Log a test name message to the console and to the log file
    :param message: String
    :param jump_line: Boolean
    """
    log_info(message, jump_line)
    new_line = ""
    if jump_line:
        new_line = "\n"
    file = open(__file_tests(), "a+")
    file.write(f"{message}\n{new_line}")
    file.close()


def log_info(message, jump_line=False):
    """
    Log a info message to the console and to the log file
    :param message: String
    :param jump_line: Boolean
    """
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    new_line = ""
    if jump_line:
        new_line = "\n"
    print(
        f"{new_line}{bcolors.HEADER}[{current_time}] "
        f"{message}{bcolors.ENDC}{new_line}"
    )
    file = open(__file_log(), "a+")
    file.write(f"{new_line}[{current_time}] {message}\n{new_line}")
    file.close()


def __file_log(log_file="stdout.log"):
    """
    Get the path of the log file
    :param log_file: String
    :return: String
    """
    Path(LOG_DIR).mkdir(parents=True, exist_ok=True)
    file_name: str
    if log_file == "stdout.log":
        file_name = os.path.join(LOG_DIR, f"TEST_UI-{log_file}")
    else:
        file_name = os.path.join(LOG_DIR, log_file)
    return file_name


def __file_tests(log_file="report_cases.txt"):
    """
    Get the path of the log file
    :param log_file: String
    :return: String
    """
    Path(LOG_DIR).mkdir(parents=True, exist_ok=True)
    return os.path.join(LOG_DIR, log_file)
