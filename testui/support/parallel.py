import os
import multiprocessing as mp
import argparse
import time

from testui.support import logger


def parallel_testui():
    remove_logs()
    args = __arg_parser()
    try:
        os.remove('report_fails.txt')
    except FileNotFoundError:
        pass
    number_of_cases = get_total_number_of_cases(args)
    logger.log_test_name(f'------------ Total Number of Test Cases: {number_of_cases} ---------------')
    start = time.time()
    __start_processes(args.markers, args)
    end_time = time.time() - start
    f = open('fails.txt')
    fails = f.read()

    passed = 0
    fail = 0
    for letter in fails:
        if letter == '0':
            passed += 1
        if letter == '2':
            fail += 1
    if fail != 0:
        os.remove('fails.txt')
        number_of_fails = __check_number_of_fails()
        percentage = 100 - 100 * number_of_fails / number_of_cases
        logger.log_error(f'------------ Total Number of Test Cases: {number_of_cases}. '
                         f'Percentage Passed {percentage.__round__(3)}% ---------------')
        logger.log_error(f'------------ Tests Finished with errors! {fail} markers failed and {passed} passed.'
                         f' Execution Time {__seconds_to_minutes(end_time)} ---------------')
        logger.log_error(f'------------ Total Number of Test Failed: {__check_number_of_fails()} ---------------')
        logger.log_error(f'There were test fails: \n\n{__check_txt_fails()}')
        raise Exception(f'------------ Tests Finished with errors! ---------------')

    try:
        os.remove('fails.txt')
    except FileNotFoundError:
        logger.log_error('There were not errors file, there might be some other issues during the execution...')
    logger.log_pass(f'------------- Total Number of Test Cases: {number_of_cases} -------------')
    logger.log_pass(f'------------- Tests Finished successfully. {passed} markers passed. '
                    f'Total Execution Time {__seconds_to_minutes(end_time)} -------------')


def remove_logs():
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from testui.support import logger
    i = 0
    try:
        for filename in os.listdir(root_dir + '/report_screenshots'):
            file_path = os.path.join(root_dir + '/report_screenshots/', filename)
            os.remove(file_path)
            if i == 0:
                logger.log('Cleaning report_screenshots folder...')
                i += 1
    except FileNotFoundError:
        pass
    i = 0
    try:
        for filename in os.listdir(root_dir + '/appium_logs'):
            file_path = os.path.join(root_dir + '/appium_logs/', filename)
            os.remove(file_path)
            if i == 0:
                logger.log('Cleaning appium_logs folder...')
                i += 1
    except FileNotFoundError:
        pass


def get_total_number_of_cases(args):
    number_of_cases = 0
    import subprocess
    for marker in args.markers:
        output = subprocess.run(['pytest', '-m', f'{marker} {args.general_markers}', f'--collect-only'],
                                stdout=subprocess.PIPE)
        response = output.stdout
        string_response = response.__str__()
        if string_response.__contains__(' / '):
            for cases in string_response.split(' / '):
                if cases.__contains__(' selected'):
                    number = cases.split(' selected')[0]
                    number_of_cases += int(number)
    if args.single_thread_marker is not None:
        output = subprocess.run(['pytest', '-m', f'{args.single_thread_marker} {args.general_markers}', f'--collect-only'],
                                stdout=subprocess.PIPE)
        response = output.stdout
        string_response = response.__str__()
        if string_response.__contains__(' / '):
            for cases in string_response.split(' / '):
                if cases.__contains__(' selected'):
                    number = cases.split(' selected')[0]
                    number_of_cases += int(number)
    return number_of_cases


def __seconds_to_minutes(time_seconds):
    minutes = int(time_seconds // 60)
    seconds = int(time_seconds % 60)
    if minutes < 10:
        ms = f'0{minutes}'
    else:
        ms = f'{minutes}'
    if seconds < 10:
        s = f'0{seconds}'
    else:
        s = f'{seconds}'
    return f'{ms}:{s} ({time_seconds}s)'


def __arg_parser():
    parser = argparse.ArgumentParser(description='Parallel Testing')
    parser.add_argument('markers', metavar='N', type=str, nargs='+',
                        help='an string for the accumulator')

    parser.add_argument('--parallel', type=int,
                        help='number of parallel threads')

    parser.add_argument('--s',  type=__str2bool, nargs='?',
                        const=True, default=False,
                        help='make more verbose logs (pytest -s)')

    parser.add_argument('--general', type=str,
                        help='general flags to put in all threads')

    parser.add_argument('--general_markers', type=str,
                        help='markers included in all tests')

    parser.add_argument('--single_thread_marker', type=str,
                        help='marker to run without any thread running in parallel')

    parser.add_argument("--udids", nargs="*", type=str, default=[],
                        help='device udids')

    args = parser.parse_args()
    logger.log(f'Test Run for {args.markers}')
    if args.general_markers is None:
        args.general_markers = ''
    else:
        logger.log(f'General marker added: {args.general_markers}')
    if args.udids:
        logger.log(f'Devices to use for automation: {args.udids}')
        for i, udid in enumerate(args.udids):
            os.environ[f'UDID{i}'] = udid
    if args.parallel is None:
        args.parallel = 1
    if args.parallel > len(args.markers):
        args.parallel = len(args.markers)
    logger.log(f'Number of parallel threads: {args.parallel}')

    if args.general is None:
        args.general = ''
    else:
        logger.log(f'General flags: {args.general}')
    if args.single_thread_marker is not None:
        logger.log_test_name(f'Single Thread marker: {args.single_thread_marker} {args.general_markers}')
    return args


def __str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def __start_processes(markers: list, args):
    ps = list()
    amount = len(markers) // args.parallel
    amount_plus = 0
    if len(markers) % args.parallel != 0:
        amount_plus = len(markers) % args.parallel
    i = 0
    for j in range(args.parallel):
        tags = list()
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
        logger.log_test_name(f'Thread {j} has markers: {tags}')
        ps.append(mp.Process(target=__process, args=(tags, args, j)))
    for p in ps:
        p.daemon = True
        p.start()
    for p in ps:
        p.join()
    if args.single_thread_marker is not None:
        __process([args.single_thread_marker], args)


def __process(markers: list, args, thread=0):
    for i, marker in enumerate(markers):
        try:
            os.remove(f'.my_cache_dir_{thread}/v/cache/lastfailed')
            os.remove(f'.my_cache_dir_{thread}/v/cache/nodeids')
            os.remove(f'.my_cache_dir_{thread}/v/cache/stepwise')
        except FileNotFoundError:
            pass
        quiet = '-q'
        if args.s:
            quiet = '-s'
        cache = f'-o cache_dir=.my_cache_dir_{thread}'
        start_1 = time.time()
        logger.log(f'Starting: pytest {quiet} -m "{marker} {args.general_markers}" {args.general} {cache}')
        pr_1 = os.system(f'pytest {quiet} -m "{marker} {args.general_markers}" {args.general} {cache}')
        file = open('fails.txt', 'a+')
        file.write(f'{pr_1}')
        file.close()
        if f'{pr_1}' == '0':
            logger.log_pass(
                f'FINISHED RUN WITH MARKERS: "{marker} {args.general_markers}" '
                f'AFTER {__seconds_to_minutes(time.time() - start_1)}')
        else:
            logger.log_error(
                f'FINISHED RUN WITH ERRORS AFTER {__seconds_to_minutes(time.time() - start_1)}. '
                f'MARKERS: "{marker} {args.general_markers}"')
        __set_fails_file(f'.my_cache_dir_{thread}')


def __set_fails_file(cache_dir):
    fails = __check_fails(cache_dir)
    for fail in fails:
        file = open('report_fails.txt', 'a+')
        file.write(f'{fail} \n')
        file.close()


def __check_number_of_fails():
    try:
        file = open('report_fails.txt')
        fails = file.read()
        file.close()
        return len(fails.split('tests/')) - 1
    except FileNotFoundError:
        pass


def __check_txt_fails():
    try:
        file = open('report_fails.txt')
        text = file.read()
        file.close()
        return text
    except FileNotFoundError:
        return ''


def __check_fails(cache='.pytest_cache'):
    try:
        f = open(f'{cache}/v/cache/lastfailed')
        fails = f.read()
        fails_tests = list()
        i = 0
        for fail in fails.split('true'):
            if i == 0:
                fails_tests.append(__clean_str(fail))
            elif i == len(fails) - 1:
                f.close()
                os.remove(f'{cache}')
                return fails_tests
            else:
                fails_tests.append(__clean_str(fail))
            i += 1
        return fails_tests
    except FileNotFoundError:
        return list()


def __clean_str(string: str):
    return string.replace('"', '').replace('}', '').replace('{', '').replace(',', '').replace('\n', '').replace(' ', '')
