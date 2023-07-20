import argparse
import multiprocessing as mp
import os
import time
import subprocess

from testui.support import logger


def parallel_testui():
    """
    This function is the main function of the parallel execution.
    It will start the execution of the test cases in parallel.
    """
    remove_logs()
    args = __arg_parser()
    try:
        os.remove("report_fails.txt")
    except FileNotFoundError:
        pass
    try:
        os.remove("report_cases.txt")
    except FileNotFoundError:
        pass
    test_run_id = None
    if args.testrail_id is not None:
        test_run_id = args.testrail_id
        logger.log_info(f"Starting testrail run {test_run_id}")
    elif args.testrail is not None:
        test_run_id = __start_run_id(args, args.testrail)
        logger.log_info(
            f"Created testrail run {test_run_id} "
            f"with testrail name: {args.testrail}"
        )
    number_of_cases = get_total_number_of_cases(args)
    logger.log_info(
        f"----------- Total Number of Test Cases: {number_of_cases} -----------"
    )
    start = time.time()
    __start_processes(args.markers, args, test_run_id)
    end_time = time.time() - start
    f = open("fails.txt")
    fails = f.read()

    passed = 0
    fail = 0
    for letter in fails:
        if letter == "0":
            passed += 1
        if letter == "2":
            fail += 1
    if fail != 0:
        os.remove("fails.txt")
        number_of_fails = __check_number_of_fails()
        percentage = 100 - 100 * number_of_fails / number_of_cases
        logger.log_error(
            f"----------- Total Number of Test Cases: {number_of_cases}. "
            f"Percentage Passed {percentage.__round__(3)}% -----------"
        )
        logger.log_error(
            f"----------- Tests Finished with errors! "
            f"{fail} markers failed and {passed} passed."
            f" Execution Time {__seconds_to_minutes(end_time)} -----------"
        )
        logger.log_error(
            "----------- Total Number of Test Failed: "
            f"{__check_number_of_fails()} -----------"
        )
        logger.log_error(f"There were test fails: \n\n{__check_txt_fails()}")
        raise Exception("----------- Tests Finished with errors! -----------")

    try:
        os.remove("fails.txt")
    except FileNotFoundError:
        logger.log_error(
            "There were not errors file, there might be some other issues "
            "during the execution..."
        )
    logger.log_pass(
        f"----------- Total Number of Test Cases: {number_of_cases} -----------"
    )
    logger.log_pass(
        f"----------- Tests Finished successfully. {passed} markers passed. "
        f"Total Execution Time {__seconds_to_minutes(end_time)} -----------"
    )


def remove_logs():
    """
    Will remove the logs from the previous execution.
    """
    root_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    i = 0
    try:
        for filename in os.listdir(root_dir + "/report_screenshots"):
            file_path = os.path.join(
                root_dir + "/report_screenshots/", filename
            )
            os.remove(file_path)
            if i == 0:
                logger.log("Cleaning report_screenshots folder...")
                i += 1
    except FileNotFoundError:
        pass
    i = 0
    try:
        for filename in os.listdir(root_dir + "/appium_logs"):
            file_path = os.path.join(root_dir + "/appium_logs/", filename)
            os.remove(file_path)
            if i == 0:
                logger.log("Cleaning appium_logs folder...")
                i += 1
    except FileNotFoundError:
        pass


def get_total_number_of_cases(args):
    """
    Will get the total number of cases that will be executed.
    :param args: The arguments that will be used to execute the test cases.
    :return: The total number of cases that will be executed.
    """
    number_of_cases = 0
    for marker in args.markers:
        output = subprocess.run(
            [
                "pytest",
                "-m",
                f"{marker} {args.general_markers}",
                "--collect-only",
            ],
            stdout=subprocess.PIPE,
            check=False,
        )
        response = output.stdout
        string_response = str(response)
        if " / " in string_response:
            for cases in string_response.split(" / "):
                if " selected" in cases:
                    number = cases.split(" selected")[0]
                    number_of_cases += int(number)
    if args.single_thread_marker is not None:
        output = subprocess.run(
            [
                "pytest",
                "-m",
                f"{args.single_thread_marker} {args.general_markers}",
                "--collect-only",
            ],
            stdout=subprocess.PIPE,
            check=False,
        )
        response = output.stdout
        string_response = str(response)
        if " / " in string_response:
            for cases in string_response.split(" / "):
                if " selected" in cases:
                    number = cases.split(" selected")[0]
                    number_of_cases += int(number)
    return number_of_cases


def __seconds_to_minutes(time_seconds):
    """
    Will convert seconds to minutes.
    :param time_seconds: The time in seconds.
    :return: The time in minutes.
    """
    minutes = int(time_seconds // 60)
    seconds = int(time_seconds % 60)
    ms = f"0{minutes}" if minutes < 10 else f"{minutes}"
    s = f"0{seconds}" if seconds < 10 else f"{seconds}"
    return f"{ms}:{s} ({time_seconds}s)"


def __arg_parser():
    """
    Will parse the arguments that will be used to execute the test cases.
    :return: The arguments that will be used to execute the test cases.
    """
    parser = argparse.ArgumentParser(description="Parallel Testing")
    parser.add_argument(
        "markers",
        metavar="N",
        type=str,
        nargs="+",
        help="an string for the accumulator",
    )

    parser.add_argument(
        "--parallel", type=int, help="number of parallel threads"
    )

    parser.add_argument(
        "--s",
        type=__str2bool,
        nargs="?",
        const=True,
        default=False,
        help="make more verbose logs (pytest -s)",
    )

    parser.add_argument(
        "--testrail",
        type=str,
        help="Use test rail and specify name. "
        "You will have to add a file testrail.cfg in root project dir",
    )

    parser.add_argument(
        "--testrail_id",
        type=str,
        help="Use test rail and specify testrail id. "
        "You will have to add a file testrail.cfg in root project dir",
    )

    parser.add_argument(
        "--testrail_pwd",
        type=str,
        help="Use test rail and specify password. "
        "You will have to add a file testrail.cfg in root project dir",
    )

    parser.add_argument(
        "--general", type=str, help="general flags to put in all threads"
    )

    parser.add_argument(
        "--general_markers", type=str, help="markers included in all tests"
    )

    parser.add_argument(
        "--single_thread_marker",
        type=str,
        help="marker to run without any thread running in parallel",
    )

    parser.add_argument(
        "--udids", nargs="*", type=str, default=[], help="device udids"
    )

    args = parser.parse_args()
    logger.log(f"Test Run for {args.markers}")
    if args.general_markers is None:
        args.general_markers = ""
    else:
        logger.log(f"General marker added: {args.general_markers}")
    if args.udids:
        logger.log(f"Devices to use for automation: {args.udids}")
        for i, udid in enumerate(args.udids):
            os.environ[f"UDID{i}"] = udid
    if args.parallel is None:
        args.parallel = 1
    if args.parallel > len(args.markers):
        args.parallel = len(args.markers)
    logger.log(f"Number of parallel threads: {args.parallel}")

    if args.general is None:
        args.general = ""
    else:
        logger.log(f"General flags: {args.general}")
    if args.single_thread_marker is not None:
        logger.log_info(
            "Single Thread marker: "
            f"{args.single_thread_marker} {args.general_markers}"
        )
    return args


def __str2bool(v):
    """
    Will convert a string to a boolean.
    :param v: The string to be converted.
    :return: The boolean value.
    """
    if isinstance(v, bool):
        return v

    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    if v.lower() in ("no", "false", "f", "n", "0"):
        return False

    raise argparse.ArgumentTypeError("Boolean value expected.")


def __start_processes(markers: list, args, test_run_id=None):
    """
    Will start the processes for parallel test execution.
    :param markers: The markers to be used.
    :param args: The arguments to be used.
    :param test_run_id: The test run id.
    """
    ps = []
    amount = len(markers) // args.parallel
    amount_plus = 0
    if len(markers) % args.parallel != 0:
        amount_plus = len(markers) % args.parallel
    i = 0
    for j in range(args.parallel):
        tags = []
        if j != args.parallel - 1:
            for _ in range(amount):
                if len(markers) > i:
                    tags.append(markers[i])
                    i += 1
        else:
            for _ in range(amount + amount_plus):
                if len(markers) > i:
                    tags.append(markers[i])
                    i += 1
        logger.log_info(f"Thread {j} has markers: {tags}")
        ps.append(
            mp.Process(target=__process, args=(tags, args, j, test_run_id))
        )
    for p in ps:
        p.daemon = True
        p.start()
    for p in ps:
        p.join()
    if args.single_thread_marker is not None:
        __process([args.single_thread_marker], args, 0, test_run_id)


def __start_run_id(args, test_run_name):
    """
    Will start the test run id.
    :param args: The arguments to be used.
    :param test_run_name: The test run name.
    :return: The test run id.
    """
    end_marker = ""
    for i, marker in enumerate(args.markers):
        if i == len(args.markers):
            end_marker += f"{marker} {args.general_markers}"
        else:
            end_marker += f"{marker} {args.general_markers} or "
    if args.single_thread_marker is not None:
        end_marker += f"{args.single_thread_marker} {args.general_markers}"
    with open("testrail_id_file.txt", "wb") as out:
        cmd = [
            "pytest",
            "-m",
            end_marker,
            "--testrail",
            "--tr-config=testrail.cfg",
            f"--tr-testrun-name={test_run_name}",
        ]
        if args.testrail_pwd is not None:
            cmd.append(f"--tr-password={args.testrail_pwd}")
        process = subprocess.Popen(cmd, stdout=out, stderr=out)
    i = 0
    while True:
        time.sleep(0.1)
        out = open("testrail_id_file.txt")
        text = out.read()
        if "New testrun created" in text or i > 50:
            out.close()
            process.terminate()
            process.wait()
            os.remove("testrail_id_file.txt")
            if "ID=" in text:
                id_test = text.split("ID=")[1]
                if "\n" in text.split("ID=")[1]:
                    id_test = text.split("ID=")[1].split("\n")[0]
                logger.log_info(f"Test run: {id_test}")
                return id_test
            raise Exception("Failed to create Test Run")
        if "Failed to create testrun" in text:
            out.close()
            process.send_signal(signal=2)
            process.terminate()
            process.wait()
            os.remove("testrail_id_file.txt")
            logger.log_error(f"Failed to create Test Run: \n {text}")
            raise Exception("Failed to create Test Run")
        out.close()
        i += 1


def __process(markers: list, args, thread=0, test_run_id=None):
    """
    Will start a single test process.
    :param markers: The markers to be used.
    :param args: The arguments to be used.
    :param thread: The thread number.
    :param test_run_id: The test run id.
    """
    for marker in markers:
        try:
            os.remove(f".my_cache_dir_{thread}/v/cache/lastfailed")
            os.remove(f".my_cache_dir_{thread}/v/cache/nodeids")
            os.remove(f".my_cache_dir_{thread}/v/cache/stepwise")
        except FileNotFoundError:
            pass
        quiet = "-q"
        if args.s:
            quiet = "-s"
        testrail = ""
        if test_run_id is not None:
            testrail = (
                f"--testrail --tr-config=testrail.cfg --tr-run-id={test_run_id}"
            )
            if args.testrail_pwd is not None:
                testrail += f" --tr-password={args.testrail_pwd}"
        cache = f"-o cache_dir=.my_cache_dir_{thread}"
        start_1 = time.time()
        logger.log(
            f'Starting: pytest {quiet} -m "{marker} {args.general_markers}" '
            f"{testrail} {args.general} {cache}"
        )
        pr_1 = os.system(
            f'pytest {quiet} -m "{marker} {args.general_markers}" '
            f"{testrail} {args.general} {cache}"
        )
        file = open("fails.txt", "a+")
        file.write(f"{pr_1}")
        file.close()
        if f"{pr_1}" == "0":
            logger.log_pass(
                f'FINISHED RUN WITH MARKERS: "{marker} {args.general_markers}" '
                f"AFTER {__seconds_to_minutes(time.time() - start_1)}"
            )
        else:
            logger.log_error(
                "FINISHED RUN WITH ERRORS AFTER "
                f"{__seconds_to_minutes(time.time() - start_1)}. "
                f'MARKERS: "{marker} {args.general_markers}"'
            )
        __set_fails_file(f".my_cache_dir_{thread}")


def __set_fails_file(cache_dir):
    """
    Will set the fails file.
    :param cache_dir: The cache directory.
    """
    fails = __check_fails(cache_dir)
    for fail in fails:
        file = open("report_fails.txt", "a+")
        file.write(f"{fail} \n")
        file.close()


def __check_number_of_fails():
    """
    Will check the number of fails within report file.
    :return: The number of fails.

    """
    try:
        file = open("report_fails.txt")
        fails = file.read()
        file.close()
        return len(fails.split("tests/")) - 1
    except FileNotFoundError:
        return 0


def __check_txt_fails():
    """
    Will return content of reported fails.
    :return: The fails.
    """
    try:
        file = open("report_fails.txt")
        text = file.read()
        file.close()
        return text
    except FileNotFoundError:
        return ""


def __check_fails(cache=".pytest_cache"):
    """
    Will check latest fails wihin cache.
    :param cache: The cache directory.
    :return: The fails.
    """
    try:
        f = open(f"{cache}/v/cache/lastfailed")
        fails = f.read()
        fails_tests = []
        i = 0
        for fail in fails.split("true"):
            if i == 0:
                fails_tests.append(__clean_str(fail))
            elif i == len(fails) - 1:
                f.close()
                os.remove(f"{cache}")
                return fails_tests
            else:
                fails_tests.append(__clean_str(fail))
            i += 1
        return fails_tests
    except FileNotFoundError:
        return []


def __clean_str(string: str):
    """
    Will clean the provided string from unnecessary characters.
    :param string: The string to be cleaned.
    :return: The cleaned string.
    """
    return (
        string.replace('"', "")
        .replace("}", "")
        .replace("{", "")
        .replace(",", "")
        .replace("\n", "")
        .replace(" ", "")
    )
