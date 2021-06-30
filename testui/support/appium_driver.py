import atexit
import os
import subprocess
import threading
from pathlib import Path
from time import sleep

from ppadb.client import Client as AdbClient
from appium.webdriver import Remote
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from webdriver_manager import chrome

from testui.support import logger
from testui.support.api_support import get_chrome_version
from testui.support.testui_driver import TestUIDriver
from testui.support.configuration import Configuration

class NewDriver:
    __configuration = Configuration()

    def __init__(self):
        self.browser = False
        self.__driver = None
        self.__app_path = None
        self.udid = None
        self.__appium_url = None
        self.__remote_url = None
        self.__browser_name = 'chrome'
        self.device_name = 'Device'
        self.appium_port = 4723
        self.__version = None
        self.__platform_name = 'Android'
        self.__app_package = None
        self.__app_activity = None
        self.__automation_name = None
        self.logger_name = None
        self.__full_reset = False
        self.__debug = False
        self.soft_assert = False
        self.__auto_accept_alerts = True
        self.process = None
        self.file_name = None
        self.__appium_log_file = 'appium-stdout.log'
        self.__chromedriverArgs = ['relaxed security']
        self.__desired_capabilities = {}
        self.__chrome_options = {}

    # Possible loggers str: behave, pytest, None
    def set_logger(self, logger_name='pytest'):
        self.logger_name = logger_name
        return self

    def set_appium_log_file(self, file='appium-stdout.log'):
        self.__appium_log_file = file
        return self

    def set_browser(self, browser):
        self.__browser_name = browser
        return self

    def set_remote_url(self, url):
        self.__remote_url = url
        return self

    def set_soft_assert(self, soft_assert: bool):
        self.soft_assert = soft_assert
        return self

    def set_appium_port(self, port: int):
        self.appium_port = port
        return self

    def set_full_reset(self, full_reset: bool):
        self.__full_reset = full_reset
        return self

    def set_appium_url(self, appium_url: str):
        self.__appium_url = appium_url
        return self

    def set_extra_caps(self, caps=None):
        if caps is None:
            caps = {}
        for cap in caps:
            self.__desired_capabilities[cap] = caps[cap]
        return self

    def set_app_path(self, path: str):
        self.__app_path = path
        if os.path.isabs(self.__app_path):
            return self
        else:
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.__app_path = os.path.join(root_dir, path)
            logger.log(self.__app_path)
            return self

    def set_udid(self, udid: str):
        self.udid = udid
        return self

    def set_udid_if_exists(self, udid: str, number=None):
        self.udid = check_device_exist(udid)
        if self.udid is None:
            self.udid = get_device_udid(number)
        return self

    def set_connected_device(self, number: int):
        self.udid = get_device_udid(number)
        return self

    def set_device_name(self, device_name: str):
        self.device_name = device_name
        return self

    def set_version(self, version: str):
        self.__version = version
        return self

    def set_grant_permissions(self, permissions: bool):
        self.__auto_accept_alerts = permissions
        return self

    def set_app_package_activity(self, app_package: str, app_activity: str):
        self.__app_package = app_package
        self.__app_activity = app_activity
        return self

    def get_driver(self):
        driver = self.__driver
        return driver

    @property
    def configuration(self) -> Configuration:
        return self.__configuration

    def get_testui_driver(self) -> TestUIDriver:
        return TestUIDriver(self)

    def set_chrome_driver(self, version=''):
        mobile_version = version
        if version == '':
            if self.udid is None:
                self.udid = get_device_udid(0)
            mobile_version = check_chrome_version(self.udid)
        chrome_driver = chrome.ChromeDriverManager(version=mobile_version).install()
        logger.log(f'Driver installed in {chrome_driver}', True)
        self.__desired_capabilities['chromedriverExecutable'] = chrome_driver
        return self

    def set_screenshot_path(self, screenshot_path: str):
        self.__configuration.screenshot_path = screenshot_path
        return self

    def set_save_screenshot_on_fail(self, save_screenshot_on_fail: bool):
        self.__configuration.save_full_stacktrace = save_screenshot_on_fail
        return self

    def set_save_full_stacktrace(self, save_full_stacktrace: bool):
        self.__configuration.save_full_stacktrace = save_full_stacktrace
        return self
    # Available platforms: Android, iOS
    def set_platform(self, platform):
        self.__platform_name = platform
        return self

    def __set_common_caps(self):
        self.__desired_capabilities['adbExecTimeout'] = 30000
        self.__desired_capabilities['platformName'] = self.__platform_name
        self.__desired_capabilities['automationName'] = self.__automation_name
        self.__desired_capabilities['deviceName'] = self.device_name
        if self.__full_reset:
            self.__desired_capabilities['enforceAppInstall'] = True
        else:
            self.__desired_capabilities['noReset'] = False
        if self.__version is not None:
            self.__desired_capabilities['platformVersion'] = self.__version
        if self.udid is not None:
            self.__desired_capabilities['udid'] = self.udid

    def __set_android_caps(self):
        if self.__automation_name is None:
            self.__automation_name = 'UiAutomator2'
        self.__desired_capabilities['chromeOptions'] = {'w3c': False}
        # ToDo It is not being passed to executable. Tried this
        # https://github.com/appium/appium/blob/master/docs/en/writing-running-appium/caps.md
        self.__desired_capabilities['chromedriverArgs'] = self.__chromedriverArgs

        self.__desired_capabilities['chromeDriverPort'] = self.appium_port - 4723 + 8100
        self.__desired_capabilities['systemPort'] = self.appium_port - 4723 + 8200
        if self.__app_path is None and self.__app_package is None:
            self.__desired_capabilities['browserName'] = "chrome"
            self.browser = True
        if self.__app_package is not None:
            self.__desired_capabilities['appPackage'] = self.__app_package
            self.__desired_capabilities['appActivity'] = self.__app_activity
        if self.__app_path is not None:
            self.__desired_capabilities['app'] = self.__app_path
            self.__desired_capabilities['androidInstallPath'] = self.__app_path

    def __set_ios_caps(self):
        if self.__automation_name is None:
            self.__automation_name = 'XCUITest'
        if self.__app_path is None and self.__app_package is None:
            self.__desired_capabilities['browserName'] = "safari"
            self.browser = True
        if self.__app_path is not None:
            self.__desired_capabilities['app'] = self.__app_path
        if self.__version is None:
            self.__desired_capabilities['platformVersion'] = '13.2'

    def __set_selenium_caps(self):
        self.__desired_capabilities['browserName'] = self.__browser_name

    def set_appium_driver(self) -> TestUIDriver:
        if self.__platform_name.lower() == 'android':
            self.__set_android_caps()
        else:
            self.__set_ios_caps()
        self.__set_common_caps()
        self.__driver, self.process, self.file_name = start_driver(
            self.__desired_capabilities, self.__appium_url, self.__debug,
            self.appium_port, self.udid, self.__appium_log_file
        )
        return self.get_testui_driver()

    def set_selenium_driver(self, chrome_options=None, firefox_options=None) -> TestUIDriver:
        self.__set_selenium_caps()
        self.__driver = start_selenium_driver(
            self.__desired_capabilities, self.__remote_url,
            self.__debug, self.__browser_name, chrome_options, firefox_options)
        return self.get_testui_driver()

    def set_driver(self, driver) -> TestUIDriver:
        self.__set_selenium_caps()
        self.__driver = driver
        return self.get_testui_driver()


def start_driver(desired_caps, url, debug, port, udid, log_file):
    lock = threading.Lock()
    lock.acquire()
    logger.log("setting capabilities: " + desired_caps.__str__())
    logger.log("starting appium driver...")
    process = None
    if desired_caps['platformName'].lower().__contains__('android'):
        url, desired_caps, process, file = __local_run(url, desired_caps, port, udid, log_file)
    else:
        url, desired_caps, file = __local_run_ios(url, desired_caps, port, udid, log_file)
    err = None
    for x in range(2):
        try:
            driver = Remote(url, desired_caps)
            atexit.register(__quit_driver, driver, debug)
            logger.log(f"appium running on {url}. \n")
            lock.release()
            return driver, process, file
        except Exception as error:
            err = error
    lock.release()
    raise err


def start_selenium_driver(desired_caps, url=None, debug=None, browser=None, chrome_options=None, firefox_options=None):
    options = chrome_options
    if firefox_options is not None:
        options = firefox_options

    if options is not None:
        logger.log("setting options: " + options.to_capabilities().__str__())

    logger.log("setting capabilities: " + desired_caps.__str__())
    logger.log(f"starting selenium {browser.lower()} driver...")
    err = None
    for x in range(2):
        try:
            if url is not None:
                logger.log(f"selenium running on {url}. \n")
                driver = webdriver.Remote(url, desired_caps, options=options)
            else:
                if browser.lower() == 'chrome':
                    driver = webdriver.Chrome(desired_capabilities=desired_caps, options=options)
                elif browser.lower() == 'firefox':
                    import geckodriver_autoinstaller
                    try:
                        geckodriver_autoinstaller.install()
                    except Exception as error:
                        logger.log_warn("Could not retrieve geckodriver: " + error.__str__())
                    if "marionette" not in desired_caps:
                        desired_caps["marionette"] = True
                    driver = webdriver.Firefox(firefox_options=options, desired_capabilities=desired_caps)
                elif browser.lower() == 'safari':
                    driver = webdriver.Safari(desired_capabilities=desired_caps)
                elif browser.lower() == 'edge':
                    driver = webdriver.Edge(capabilities=desired_caps)
                elif browser.lower() == 'ie':
                    driver = webdriver.Ie(capabilities=desired_caps)
                elif browser.lower() == 'opera':
                    driver = webdriver.Opera(desired_capabilities=desired_caps)
                elif browser.lower() == 'phantomjs':
                    driver = webdriver.PhantomJS(desired_capabilities=desired_caps)
                else:
                    raise Exception(f"Invalid browser '{browser}'. Please choose one from: chrome,firefox,safari,edge,"
                                    f"ie,opera,phantomjs")
            atexit.register(__quit_driver, driver, debug)
            return driver
        except Exception as error:
            err = error

    raise err


def __local_run(url, desired_caps, use_port, udid, log_file):
    if url is None:
        port = use_port
        bport = use_port + 1
        device = 0
        if os.getenv('PYTEST_XDIST_WORKER') is not None:
            device += os.getenv('PYTEST_XDIST_WORKER').split("w")[1]
            port += int(os.getenv('PYTEST_XDIST_WORKER').split("w")[1]) * 2
            desired_caps['chromeDriverPort'] = 8200 + int(os.getenv('PYTEST_XDIST_WORKER').split("w")[1])
            desired_caps['systemPort'] = 8300 + int(os.getenv('PYTEST_XDIST_WORKER').split("w")[1])
            bport += int(os.getenv('PYTEST_XDIST_WORKER').split("w")[1]) * 2
        logger.log(f"running: appium -p {port.__str__()} -bp {bport.__str__()}")
        if udid is None:
            desired_caps = __set_android_device(desired_caps, device)
        logger.log(f'setting device for automation: {desired_caps["udid"]}')
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/'
        Path(root_dir + "appium_logs").mkdir(parents=True, exist_ok=True)
        file_path: str
        if log_file == 'appium-stdout.log':
            file = f'appium_logs/testui-{udid}-' + log_file
        else:
            file = f'appium_logs/{log_file}'
        with open(root_dir + file, 'wb') as out:
            process = subprocess.Popen(
                ['appium', '-p', port.__str__(), '-bp', bport.__str__()],
                stdout=out, stderr=subprocess.STDOUT
            )
            atexit.register(process.kill)
        file_path = root_dir + file
        while True:
            sleep(0.5)
            out = open(file_path)
            text = out.read()
            if text.__contains__("already be in use") or text.__contains__("listener started"):
                out.close()
                break
            out.close()
        return f"http://localhost:{port.__str__()}/wd/hub", desired_caps, process, file_path
    return url, desired_caps, None


def __local_run_ios(url, desired_caps, use_port, udid, log_file):
    process = None
    if url is None:
        port = use_port + 100
        device = 0
        if os.getenv('PYTEST_XDIST_WORKER') is not None:
            device += os.getenv('PYTEST_XDIST_WORKER').split("w")[1]
            port += int(os.getenv('PYTEST_XDIST_WORKER').split("w")[1]) * 2
            desired_caps['chromeDriverPort'] = 8200 + int(os.getenv('PYTEST_XDIST_WORKER').split("w")[1])
            desired_caps['systemPort'] = 8300 + int(os.getenv('PYTEST_XDIST_WORKER').split("w")[1])
        logger.log(f"running: appium -p {port.__str__()}")
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/'
        Path(root_dir + "appium_logs").mkdir(parents=True, exist_ok=True)
        file_path: str
        if log_file == 'appium-stdout.log':
            file = f'appium_logs/testui-{udid}-' + log_file
        else:
            file = f'appium_logs/{log_file}'
        with open(root_dir + file, 'wb') as out:
            process = subprocess.Popen(
                ['appium', '-p', port.__str__()],
                stdout=out, stderr=subprocess.STDOUT
            )
            atexit.register(process.kill)
        file_path = root_dir + file
        if udid is None:
            desired_caps = __set_ios_device(desired_caps, device)
        while True:
            sleep(0.5)
            out = open(file_path)
            text = out.read()
            if text.__contains__("already be in use") or text.__contains__("listener started"):
                out.close()
                break
            out.close()
        return f"http://localhost:{port.__str__()}/wd/hub", desired_caps, file_path
    return url, desired_caps, process


def __set_android_device(desired_caps, number: int):
    desired_caps['udid'] = get_device_udid(number)
    return desired_caps


def __set_ios_device(desired_caps, number: int):
    # TODO
    return desired_caps


def get_device_udid(number: int):
    client = AdbClient(host="127.0.0.1", port=5037)
    devices = client.devices()
    if len(devices) == 0:
        raise Exception("There are 0 devices connected to the computer!")
    if len(devices) > number:
        return devices[number].get_serial_no()
    else:
        new_number = number - (number // len(devices)) * len(devices)
        logger.log_warn(f'You choose device number {number + 1} but there are only {len(devices)} connected. '
                        f'Will use device number {new_number + 1} instead', jump_line=True)
        return devices[new_number].get_serial_no()


def check_device_exist(udid):
    client = AdbClient(host="127.0.0.1", port=5037)
    devices = client.devices()
    for device in devices:
        if device.get_serial_no() == udid:
            return udid
    return None


def check_chrome_version(udid):
    output = subprocess.Popen(['adb', '-s', udid, 'shell', 'dumpsys', 'package', 'com.android.chrome',
                               '|', 'grep', 'versionName'], stdout=subprocess.PIPE)
    response = output.communicate()
    if response.__str__().__contains__('versionName='):
        return get_chrome_version(response.__str__().split('versionName=')[1].split('.')[0])


def __quit_driver(driver, debug):
    try:
        driver.quit()
    except Exception as err:
        if debug:
            logger.log_debug(f"appium was probably closed {err}. \n")
