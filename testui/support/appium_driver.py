import atexit
import os
import subprocess
import threading
import time
from pathlib import Path
from time import sleep

import geckodriver_autoinstaller

from ppadb.client import Client as AdbClient
from appium.webdriver import Remote
from appium.webdriver.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium import webdriver
from webdriver_manager import chrome
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions


from testui.support import logger
from testui.support.api_support import get_chrome_version
from testui.support.testui_driver import TestUIDriver
from testui.support.configuration import Configuration


class NewDriver:
    """
    Class for creating appium driver
    """

    __configuration = Configuration()

    def __init__(self):
        self.browser = False
        self.__driver: WebDriver = None
        self.__app_path = None
        self.__bundle_id = None
        self.udid = None
        self.__appium_url = None
        self.__remote_url = None
        self.__browser_name = "chrome"
        self.device_name = "Device"
        self.appium_port = 4723
        self.__version = None
        self.__platform_name = "Android"
        self.__app_package = None
        self.__app_activity = None
        self.__automation_name = None
        self.logger_name = None
        self.__full_reset = False
        self.__debug = False
        self.soft_assert = False
        # TODO: Investigate if functionality can be implemented or should be
        # removed.
        # pylint: disable=unused-private-member
        self.__auto_accept_alerts = True
        self.process = None
        self.file_name = None
        self.__appium_log_file = "appium-stdout.log"
        self.__desired_capabilities = {}
        # TODO: Investigate if should be used in functionality or should be
        # removed.
        # pylint: disable=unused-private-member
        self.__chrome_options = {}

    def set_logger(self, logger_name: str or None = "pytest"):
        """
        Set logger
        Possible loggers str: behave, pytest, None
        :param logger_name: logger name
        """
        self.logger_name = logger_name
        return self

    def set_appium_log_file(self, file="appium-stdout.log"):
        """
        Set path to appium log file
        :param file: file name
        :return: self
        """
        self.__appium_log_file = file
        return self

    def set_browser(self, browser: str) -> "NewDriver":
        """
        Set browser
        :param browser: browser name
        :return: self
        """
        self.__browser_name = browser
        return self

    def set_remote_url(self, url):
        """
        Set remote url
        :param url: url
        :return: self
        """
        self.__remote_url = url
        return self

    def set_soft_assert(self, soft_assert: bool):
        """
        Set soft assert
        :param soft_assert: True or False
        :return: self
        """
        self.soft_assert = soft_assert
        return self

    def set_appium_port(self, port: int):
        """
        Set appium port
        :param port: port
        :return: self
        """
        self.appium_port = port
        return self

    def set_full_reset(self, full_reset: bool):
        """
        Set full reset
        :param full_reset: True or False
        :return: self
        """
        self.__full_reset = full_reset
        return self

    def set_appium_url(self, appium_url: str):
        """
        Set appium url
        :param appium_url: appium url
        :return: self
        """
        self.__appium_url = appium_url
        return self

    def set_extra_caps(self, caps=None):
        """
        Set extra capabilities
        :param caps: capabilities
        :return: self
        """
        if caps is None:
            caps = {}
        for cap in caps:
            self.__desired_capabilities[cap] = caps[cap]
        return self

    def set_app_path(self, path: str):
        """
        Set app path
        :param path: path to app
        :return: self
        """
        self.__app_path = path
        if os.path.isabs(self.__app_path):
            return self

        root_dir = self.configuration.screenshot_path
        self.__app_path = os.path.join(root_dir, path)
        logger.log(self.__app_path)
        return self

    def set_udid(self, udid: str):
        """
        Set udid
        :param udid: udid
        :return: self
        """
        self.udid = udid
        return self

    def set_bundle_id(self, bundle_id: str):
        self.__bundle_id = bundle_id
        return self

    def set_udid_if_exists(self, udid: str, number=None):
        """
        Set udid if exists
        :param udid: udid
        :param number: number of device
        :return: self
        """
        self.udid = check_device_exist(udid)
        if self.udid is None:
            self.udid = get_device_udid(number)
        return self

    def set_connected_device(self, number: int):
        """
        Set connected device
        :param number: number of device
        :return: self
        """
        self.udid = get_device_udid(number)
        return self

    def set_device_name(self, device_name: str):
        """
        Set device name
        :param device_name: device name
        :return: self
        """
        self.device_name = device_name
        return self

    def set_version(self, version: str):
        """
        Set version
        :param version: version
        :return: self
        """
        self.__version = version
        return self

    def set_grant_permissions(self, permissions: bool):
        """
        Set grant permissions
        :param permissions: True or False
        :return: self
        """
        # pylint: disable=unused-private-member
        self.__auto_accept_alerts = permissions
        return self

    def set_app_package_activity(self, app_package: str, app_activity: str):
        """Set app package and activity"""
        self.__app_package = app_package
        self.__app_activity = app_activity
        return self

    def get_driver(self) -> WebDriver:
        """Get driver"""
        driver = self.__driver
        return driver

    @property
    def configuration(self) -> Configuration:
        """Get configuration"""
        return self.__configuration

    def get_testui_driver(self) -> TestUIDriver:
        """Get TestUIDriver"""
        return TestUIDriver(self)

    def set_chrome_driver(self, version="") -> "NewDriver":
        """Set chrome driver"""
        mobile_version = version
        if version == "":
            if self.udid is None:
                self.udid = get_device_udid(0)
            mobile_version = check_chrome_version(self.udid)
        logger.log(f"Installing chromedriver version: {mobile_version}")
        chrome_driver = chrome.ChromeDriverManager(
            driver_version=mobile_version
        ).install()
        logger.log(f"Driver installed in {chrome_driver}", True)
        self.__desired_capabilities["chromedriverExecutable"] = chrome_driver
        return self

    def set_screenshot_path(self, screenshot_path: str):
        """Set screenshot path"""
        self.__configuration.screenshot_path = screenshot_path
        return self

    def set_save_screenshot_on_fail(self, save_screenshot_on_fail: bool):
        """Set save screenshot on fail"""
        self.__configuration.save_screenshot_on_fail = save_screenshot_on_fail
        return self

    def set_save_full_stacktrace(self, save_full_stacktrace: bool):
        """Set save full stacktrace"""
        self.__configuration.save_full_stacktrace = save_full_stacktrace
        return self

    def set_platform(self, platform):
        """
        Set platform
        Available platforms: Android, iOS
        """
        self.__platform_name = platform
        return self

    def __set_common_caps(self):
        """Set common capabilities"""
        self.__desired_capabilities["appium:adbExecTimeout"] = 30000
        self.__desired_capabilities["platformName"] = self.__platform_name
        self.__desired_capabilities["appium:automationName"] = self.__automation_name
        self.__desired_capabilities["appium:deviceName"] = self.device_name
        if self.__full_reset:
            self.__desired_capabilities["appium:enforceAppInstall"] = True
        else:
            self.__desired_capabilities["appium:noReset"] = True
        if self.__version is not None:
            self.__desired_capabilities["appium:platformVersion"] = self.__version
        if self.udid is not None:
            self.__desired_capabilities["appium:udid"] = self.udid

    def __set_android_caps(self):
        """Set Android capabilities"""
        if self.__automation_name is None:
            self.__automation_name = "UiAutomator2"
        self.__desired_capabilities["appium:chromeDriverPort"] = (
            self.appium_port - 4723 + 8100
        )
        self.__desired_capabilities["appium:systemPort"] = (
            self.appium_port - 4723 + 8200
        )
        if self.__app_path is None and self.__app_package is None:
            self.__desired_capabilities["browserName"] = "chrome"
            self.browser = True
        if self.__app_package is not None:
            self.__desired_capabilities["appium:appPackage"] = self.__app_package
            self.__desired_capabilities["appium:appActivity"] = self.__app_activity
        if self.__app_path is not None:
            self.__desired_capabilities["appium:app"] = self.__app_path
            self.__desired_capabilities["appium:androidInstallPath"] = self.__app_path

    def __set_ios_caps(self):
        """Sets the iOS capabilities"""
        if self.__automation_name is None:
            self.__automation_name = "XCUITest"
        if (
            self.__app_path is None
            and self.__bundle_id is None
            and self.__app_package is None
        ):
            self.__desired_capabilities["browserName"] = "safari"
            self.browser = True
        if self.__app_path is not None:
            self.__desired_capabilities["appium:app"] = self.__app_path
        if self.__bundle_id is not None:
            self.__desired_capabilities["appium:bundleId"] = self.__bundle_id

    def __set_selenium_caps(self):
        """Sets the selenium capabilities"""
        self.__desired_capabilities["browserName"] = self.__browser_name

    def set_appium_driver(self) -> TestUIDriver:
        """
        Sets the appium driver
        :return: TestUIDriver
        """
        if self.__platform_name.lower() == "android":
            self.__set_android_caps()
        else:
            self.__set_ios_caps()
        self.__set_common_caps()
        self.__driver, self.process, self.file_name = start_driver(
            self.__desired_capabilities,
            self.__appium_url,
            self.__debug,
            self.appium_port,
            self.udid,
            self.__appium_log_file,
        )
        return self.get_testui_driver()

    def set_selenium_driver(
        self,
        chrome_options: ChromeOptions or None = None,
        firefox_options: FirefoxOptions or None = None,
    ) -> TestUIDriver:
        """
        Sets the selenium driver
        :param chrome_options: Chrome options
        :param firefox_options: Firefox options
        :return: TestUIDriver
        """
        self.__set_selenium_caps()
        self.__driver = start_selenium_driver(
            self.__desired_capabilities,
            self.__remote_url,
            self.__debug,
            self.__browser_name,
            chrome_options,
            firefox_options,
        )

        return self.get_testui_driver()

    def set_driver(self, driver) -> TestUIDriver:
        """
        Sets the driver
        :param driver: Driver
        :return: TestUIDriver
        """
        self.__set_selenium_caps()
        self.__driver = driver
        return self.get_testui_driver()


def start_driver(desired_caps, url, debug, port, udid, log_file):
    """
    Starts the appium driver
    :param desired_caps: Desired capabilities
    :param url: Appium url
    :param debug: Debug mode
    :param port: Appium port
    :param udid: Device udid
    :param log_file: Appium log file
    :return: Appium driver
    """
    lock = threading.Lock()
    lock.acquire()

    logger.log("setting capabilities: " + str(desired_caps))
    logger.log("starting appium driver...")

    process = None
    if "android" in desired_caps["platformName"].lower():
        url, desired_caps, process, file = __local_run(
            url, desired_caps, port, udid, log_file
        )
        options = UiAutomator2Options().load_capabilities(desired_caps)
    else:
        url, desired_caps, file = __local_run_ios(
            url, desired_caps, port, udid, log_file
        )
        options = XCUITestOptions().load_capabilities(desired_caps)
    err = None
    for _ in range(2):
        try:
            import warnings

            with warnings.catch_warnings():
                # To suppress a warning from an issue on selenium side
                warnings.filterwarnings("ignore", category=DeprecationWarning)
                driver = Remote(url, options=options)
            atexit.register(__quit_driver, driver, debug)
            logger.log(f"appium running on {url}. \n")
            lock.release()
            return driver, process, file
        except Exception as error:
            err = error
    lock.release()
    raise err


def start_selenium_driver(
    desired_caps,
    url=None,
    debug=None,
    browser: str or None = None,
    chrome_options: ChromeOptions or None = None,
    firefox_options: FirefoxOptions or None = None,
) -> WebDriver:
    """
    Starts a new local session of the specified browser
    :param desired_caps: Desired capabilities
    :param url: Remote url
    :param debug: Debug mode
    :param browser: Browser name
    :param chrome_options: Chrome options
    :param firefox_options: Firefox options
    :return: WebDriver
    """

    options = chrome_options
    if firefox_options is not None:
        options = firefox_options

    if options is not None:
        logger.log(f"setting options: {str(options.to_capabilities())}")

    logger.log(f"setting capabilities: {str(desired_caps)}")
    logger.log(f"starting selenium {browser.lower()} driver...")

    err = None
    for _ in range(2):
        try:
            if url is not None:
                logger.log(f"selenium running on {url}. \n")

                if options is None:
                    options = ChromeOptions()
                for key, value in desired_caps.items():
                    options.set_capability(key, value)
                logger.log(f"final options: {str(options.to_capabilities())}")
                driver = webdriver.Remote(command_executor=url, options=options)
            else:
                if browser.lower() == "chrome":
                    if options is None:
                        options = ChromeOptions()
                    for key, value in desired_caps.items():
                        options.set_capability(key, value)
                    logger.log(f"final options: {str(options.to_capabilities())}")
                    driver = webdriver.Chrome(options=options)
                elif browser.lower() == "firefox":
                    try:
                        geckodriver_autoinstaller.install()
                    except Exception as error:
                        logger.log_warn(
                            "Could not retrieve geckodriver: " + str(error)
                        )

                    if options is None:
                        options = FirefoxOptions()
                    for key, value in desired_caps.items():
                        options.set_capability(key, value)
                    logger.log(
                        f"final options: {str(options.to_capabilities())}"
                    )

                    driver = webdriver.Firefox(options=options)
                elif browser.lower() == "safari":
                    driver = webdriver.Safari(desired_capabilities=desired_caps)
                elif browser.lower() == "edge":
                    driver = webdriver.Edge(capabilities=desired_caps)
                elif browser.lower() == "ie":
                    driver = webdriver.Ie(capabilities=desired_caps)
                elif browser.lower() == "opera":
                    driver = webdriver.Opera(desired_capabilities=desired_caps)
                else:
                    raise Exception(
                        f"Invalid browser '{browser}'. Please choose one "
                        f"from: chrome, firefox, safari, edge, ie, opera"
                    )
            atexit.register(__quit_driver, driver, debug)
            return driver
        except Exception as error:
            err = error

    raise err


def __local_run(url, desired_caps, use_port, udid, log_file):
    """
    Starts appium server locally
    :param url: url to connect to
    :param desired_caps: desired capabilities
    :param use_port: port to use
    :param udid: device udid
    :param log_file: log file
    :return: url, desired capabilities, appium process, log file
    """
    if url is None:
        port = use_port
        bport = use_port + 1
        device = 0
        if os.getenv("PYTEST_XDIST_WORKER") is not None:
            device += os.getenv("PYTEST_XDIST_WORKER").split("w")[1]
            port += int(os.getenv("PYTEST_XDIST_WORKER").split("w")[1]) * 2
            desired_caps["chromeDriverPort"] = 8200 + int(
                os.getenv("PYTEST_XDIST_WORKER").split("w")[1]
            )
            desired_caps["systemPort"] = 8300 + int(
                os.getenv("PYTEST_XDIST_WORKER").split("w")[1]
            )
            bport += int(os.getenv("PYTEST_XDIST_WORKER").split("w")[1]) * 2
        logger.log(f"running: appium -p {str(port)}")
        if udid is None:
            desired_caps = __set_android_device(desired_caps, device)
        logger.log(f'setting device for automation: {desired_caps["appium:udid"]}')
        log_dir = os.path.join("./logs", "appium_logs")
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        file_path: str
        if log_file == "appium-stdout.log":
            file_path = os.path.join(log_dir, f"testui-{udid}-{time.time()}-" + log_file)
        else:
            file_path = os.path.join(log_dir, log_file)
        with open(file_path, "wb") as out:
            process = subprocess.Popen(
                ["appium", "-p", str(port)],
                stdout=out,
                stderr=subprocess.STDOUT,
            )
            atexit.register(process.kill)
        while True:
            sleep(0.5)
            out = open(file_path)
            text = out.read()
            if "already be in use" in text or "listener started" in text:
                out.close()
                break
            out.close()
        # Check Appium Version
        result = subprocess.run(["appium", "-v"], stdout=subprocess.PIPE).stdout
        url = f"http://localhost:{str(port)}/wd/hub"
        if result.decode('utf-8').startswith("2."):
            # for Appium version > 2.0.0
            url = f"http://localhost:{str(port)}"
        return url, desired_caps, process, file_path

    return url, desired_caps, None, None


def __local_run_ios(url, desired_caps, use_port, udid, log_file):
    """
    Starts appium server for iOS
    :param url: url to connect to
    :param desired_caps: desired capabilities
    :param use_port: port to use
    :param udid: device udid
    :param log_file: log file name
    :return: url, desired capabilities, process
    """
    process = None
    if url is None:
        port = use_port + 100
        device = 0
        if os.getenv("PYTEST_XDIST_WORKER") is not None:
            device += os.getenv("PYTEST_XDIST_WORKER").split("w")[1]
            port += int(os.getenv("PYTEST_XDIST_WORKER").split("w")[1]) * 2
            desired_caps["chromeDriverPort"] = 8200 + int(
                os.getenv("PYTEST_XDIST_WORKER").split("w")[1]
            )
            desired_caps["systemPort"] = 8300 + int(
                os.getenv("PYTEST_XDIST_WORKER").split("w")[1]
            )
        logger.log(f"running: appium -p {str(port)}")
        log_dir = os.path.join("./logs", "appium_logs")
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        file_path: str
        if log_file == "appium-stdout.log":
            file_path = os.path.join(log_dir, f"testui-{udid}-{time.time()}-" + log_file)
        else:
            file_path = os.path.join(log_dir, log_file)
        with open(file_path, "wb") as out:
            process = subprocess.Popen(
                ["appium", "-p", str(port)],
                stdout=out,
                stderr=subprocess.STDOUT,
            )
            atexit.register(process.kill)
        if udid is None:
            desired_caps = __set_ios_device(desired_caps, device)
        while True:
            sleep(0.5)
            out = open(file_path)
            text = out.read()
            if "already be in use" in text or "listener started" in text:
                out.close()
                break
            out.close()
        # Check Appium Version
        url = f"http://localhost:{str(port)}/wd/hub"
        result = subprocess.run(["appium", "-v"], stdout=subprocess.PIPE).stdout
        if result.decode('utf-8').startswith("2."):
            # for Appium version > 2.0.0
            url = f"http://localhost:{str(port)}"
        return url, desired_caps, file_path

    return url, desired_caps, process


def __set_android_device(desired_caps, number: int):
    """
    Set android device by index
    :param desired_caps: desired capabilities
    :param number: device index
    :return: desired capabilities
    """
    desired_caps["appium:udid"] = get_device_udid(number)
    return desired_caps


def __set_ios_device(desired_caps, number: int):
    # TODO implement function
    _ = number

    return desired_caps


def get_device_udid(number: int):
    """
    Get device udid by index
    :param number: device index
    :return: device udid
    """
    client = AdbClient(host="127.0.0.1", port=5037)
    devices = client.devices()
    if len(devices) == 0:
        raise Exception("There are 0 devices connected to the computer!")
    if len(devices) > number:
        logger.log(f"Setting device: {devices[number].get_serial_no()}")
        return devices[number].get_serial_no()

    new_number = number - (number // len(devices)) * len(devices)
    logger.log_warn(
        f"You choose device number {number + 1} but there are only "
        f"{len(devices)} connected. "
        f"Will use device number {new_number + 1} instead",
        jump_line=True,
    )
    return devices[new_number].get_serial_no()


def check_device_exist(udid):
    """
    Check if device exist
    :param udid: device udid
    :return: device udid if exist, None otherwise
    """
    client = AdbClient(host="127.0.0.1", port=5037)
    devices = client.devices()
    for device in devices:
        if device.get_serial_no() == udid:
            return udid
    return None


def check_chrome_version(udid):
    """
    Check chrome version on device
    :param udid: device udid
    :return: chrome version if exist, None otherwise
    """
    output = subprocess.Popen(
        [
            "adb",
            "-s",
            udid,
            "shell",
            "dumpsys",
            "package",
            "com.android.chrome",
            "|",
            "grep",
            "versionName",
        ],
        stdout=subprocess.PIPE,
    )
    response = output.communicate()
    if "versionName=" in str(response):
        return get_chrome_version(
            str(response).split("versionName=")[1].split(".")[0]
        )

    return None


def __quit_driver(driver, debug):
    """
    Quit driver
    :param driver: driver
    :param debug: debug mode
    """
    try:
        driver.quit()
    except Exception as err:
        if debug:
            logger.log_debug(f"appium was probably closed {err}. \n")
