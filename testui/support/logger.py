import os
from datetime import datetime
from pathlib import Path


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def log(message, jump_line=False):
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
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    print(f"{bcolors.OKBLUE}[{current_time}] {message}{bcolors.ENDC}")
    file = open(__file_log(), "a+")
    file.write(f"[{current_time}] {message}\n")
    file.close()


def log_warn(message, jump_line=False):
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    new_line = ""
    if jump_line:
        new_line = "\n"
    print(
        f"{new_line}{bcolors.WARNING}[{current_time}] {message}{bcolors.ENDC}{new_line}"
    )
    file = open(__file_log(), "a+")
    file.write(f"{new_line}[{current_time}] {message}\n{new_line}")
    file.close()


def log_test_name(message, jump_line=False):
    log_info(message, jump_line)
    new_line = ""
    if jump_line:
        new_line = "\n"
    file = open(__file_tests(), "a+")
    file.write(f"{message}\n{new_line}")
    file.close()


def log_info(message, jump_line=False):
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    new_line = ""
    if jump_line:
        new_line = "\n"
    print(
        f"{new_line}{bcolors.HEADER}[{current_time}] {message}{bcolors.ENDC}{new_line}"
    )
    file = open(__file_log(), "a+")
    file.write(f"{new_line}[{current_time}] {message}\n{new_line}")
    file.close()


def __file_log(log_file="stdout.log"):
    root_dir = (
        os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        + "/"
    )
    Path(root_dir + "appium_logs").mkdir(parents=True, exist_ok=True)
    file_name: str
    if log_file == "stdout.log":
        file_name = f"appium_logs/TEST_UI-{log_file}"
    else:
        file_name = f"appium_logs/{log_file}"
    return root_dir + file_name


def __file_tests(log_file="report_cases.txt"):
    root_dir = (
        os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        + "/"
    )
    Path(root_dir + "appium_logs").mkdir(parents=True, exist_ok=True)
    return root_dir + log_file
