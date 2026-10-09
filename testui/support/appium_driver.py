import atexit
import copy
import functools
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path
from time import sleep

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

APPIUM_START_TIMEOUT = 120

BROWSER_DRIVERS = {
    "safari": (webdriver.Safari, webdriver.SafariOptions),
    "edge": (webdriver.Edge, webdriver.EdgeOptions),
    "ie": (webdriver.Ie, webdriver.IeOptions),
}


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
        self.__no_reset = True
        self.__debug = False
        self.soft_assert = False
        # TODO: Investigate if functionality can be implemented or should be
        # removed.
        # pylint: disable=unused-private-member
        self.__auto_accept_alerts = True
        self.process = None
        self.file_name = None
        self.__appium_log_file = "appium-stdout.log"
        self.__appium_args = []
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

    def set_appium_args(self, args: list):
        """
        Extra arguments for the locally started Appium server,
        e.g. ["--allow-insecure", "uiautomator2:adb_shell"]
        :param args: list of arguments
        :return: self
        """
        self.__appium_args = list(args)
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

    def set_no_reset(self, no_reset: bool):
        """
        Set no reset
        :param no_reset: True or False
        :return: self
        """
        self.__no_reset = no_reset
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

    def set_isolated_configuration(self):
        """
        Gives this driver its own copy of the configuration, so later changes
        don't affect other drivers. By default all drivers share one.
        """
        self.__configuration = copy.copy(self.__configuration)
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
            self.__desired_capabilities["appium:noReset"] = self.__no_reset
        if self.__version is not None:
            self.__desired_capabilities["appium:platformVersion"] = self.__version
        if self.udid is not None:
            self.__desired_capabilities["appium:udid"] = self.udid

    def __set_android_caps(self):
        """Set Android capabilities"""
        if self.__automation_name is None:
            self.__automation_name = "UiAutomator2"
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
        self.__set_force_app_launch()

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
        self.__set_force_app_launch()

    def __set_force_app_launch(self):
        """
        With noReset, Appium leaves an app that is already running in the
        background as it is, instead of restarting it
        """
        own_setting = {"forceAppLaunch", "appium:forceAppLaunch"}
        caps = self.__desired_capabilities
        if not self.browser and not own_setting & caps.keys():
            caps["appium:forceAppLaunch"] = True

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
            self.__appium_args,
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


def start_driver(
    desired_caps, url, debug, port, udid, log_file, appium_args=()
):
    """
    Starts the appium driver
    :param desired_caps: Desired capabilities
    :param url: Appium url
    :param debug: Debug mode
    :param port: Appium port
    :param udid: Device udid
    :param log_file: Appium log file
    :param appium_args: extra arguments for a locally started Appium server
    :return: Appium driver
    """
    logger.log("setting capabilities: " + str(desired_caps))
    logger.log("starting appium driver...")

    process = None
    if "android" in desired_caps["platformName"].lower():
        url, desired_caps, process, file = __local_run(
            url, desired_caps, port, udid, log_file, appium_args
        )
        options = UiAutomator2Options().load_capabilities(desired_caps)
    else:
        url, desired_caps, process, file = __local_run_ios(
            url, desired_caps, port, udid, log_file, appium_args
        )
        options = XCUITestOptions().load_capabilities(desired_caps)
    err = None
    for _ in range(2):
        try:
            driver = Remote(url, options=options)
            atexit.register(__quit_driver, driver, debug)
            logger.log(f"appium running on {url}. \n")
            return driver, process, file
        except Exception as error:
            err = error
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
                    if options is None:
                        options = FirefoxOptions()
                    for key, value in desired_caps.items():
                        options.set_capability(key, value)
                    logger.log(
                        f"final options: {str(options.to_capabilities())}"
                    )

                    driver = webdriver.Firefox(options=options)
                elif browser.lower() in BROWSER_DRIVERS:
                    driver_class, options_class = BROWSER_DRIVERS[
                        browser.lower()
                    ]
                    browser_options = options_class()
                    for key, value in desired_caps.items():
                        if key != "browserName":
                            browser_options.set_capability(key, value)
                    driver = driver_class(options=browser_options)
                elif browser.lower() == "opera":
                    raise Exception("Opera is not supported by Selenium 4.10+")
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


# Bypasses HTTP(S)_PROXY, which would otherwise receive localhost requests
_LOCAL_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def __appium_ready(url):
    try:
        with _LOCAL_OPENER.open(f"{url}/status", timeout=1) as response:
            return response.status == 200
    except OSError:
        return False


def __wait_for_appium_start(process, file_path, url):
    deadline = time.time() + APPIUM_START_TIMEOUT
    while time.time() < deadline:
        sleep(0.5)
        with open(file_path, encoding="utf-8", errors="replace") as log:
            text = log.read()
        if (
            "already be in use" in text
            or "listener started" in text
            or __appium_ready(url)
        ):
            return
        if process.poll() is not None:
            raise Exception(f"Appium exited before starting, see {file_path}")
    raise Exception(
        f"Appium did not start within {APPIUM_START_TIMEOUT}s, see {file_path}"
    )


@functools.lru_cache(maxsize=None)
def __appium_major_version():
    version = subprocess.run(["appium", "-v"], stdout=subprocess.PIPE).stdout
    try:
        return int(version.decode("utf-8").strip().split(".")[0])
    except (ValueError, IndexError):
        return 0


def __appium_base_path(appium_args):
    """
    The server's base path: from --base-path in the extra arguments, otherwise
    the default of the installed Appium version
    """
    for i, arg in enumerate(appium_args):
        value = None
        if arg.startswith("--base-path="):
            value = arg.split("=", 1)[1]
        elif arg in ("--base-path", "-pa") and i + 1 < len(appium_args):
            value = appium_args[i + 1]
        if value is not None:
            value = value.strip("/")
            return f"/{value}" if value else ""
    if __appium_major_version() >= 2:
        return ""
    return "/wd/hub"


def __local_run(url, desired_caps, use_port, udid, log_file, appium_args=()):
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
            device += int(os.getenv("PYTEST_XDIST_WORKER").split("w")[1])
            port += int(os.getenv("PYTEST_XDIST_WORKER").split("w")[1]) * 2
            desired_caps["systemPort"] = 8300 + int(
                os.getenv("PYTEST_XDIST_WORKER").split("w")[1]
            )
            bport += int(os.getenv("PYTEST_XDIST_WORKER").split("w")[1]) * 2
        command = ["appium", "-p", str(port), *appium_args]
        logger.log(f"running: {' '.join(command)}")
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
                command,
                stdout=out,
                stderr=subprocess.STDOUT,
            )
            atexit.register(process.kill)
        url = f"http://localhost:{port}{__appium_base_path(appium_args)}"
        __wait_for_appium_start(process, file_path, url)
        return url, desired_caps, process, file_path

    return url, desired_caps, None, None


def __local_run_ios(
    url, desired_caps, use_port, udid, log_file, appium_args=()
):
    """
    Starts appium server for iOS
    :param url: url to connect to
    :param desired_caps: desired capabilities
    :param use_port: port to use
    :param udid: device udid
    :param log_file: log file name
    :return: url, desired capabilities, appium process, log file
    """
    if url is None:
        port = use_port + 100
        device = 0
        if os.getenv("PYTEST_XDIST_WORKER") is not None:
            device += int(os.getenv("PYTEST_XDIST_WORKER").split("w")[1])
            port += int(os.getenv("PYTEST_XDIST_WORKER").split("w")[1]) * 2
            desired_caps["systemPort"] = 8300 + int(
                os.getenv("PYTEST_XDIST_WORKER").split("w")[1]
            )
            # WebDriverAgent and its video stream need their own ports per
            # parallel session; caps set through set_extra_caps take priority
            for cap, default_port in (
                ("wdaLocalPort", 8100), ("mjpegServerPort", 9100)
            ):
                if not {cap, f"appium:{cap}"} & desired_caps.keys():
                    desired_caps[f"appium:{cap}"] = default_port + device
        command = ["appium", "-p", str(port), *appium_args]
        logger.log(f"running: {' '.join(command)}")
        log_dir = os.path.join("./logs", "appium_logs")
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        file_path: str
        if log_file == "appium-stdout.log":
            file_path = os.path.join(log_dir, f"testui-{udid}-{time.time()}-" + log_file)
        else:
            file_path = os.path.join(log_dir, log_file)
        with open(file_path, "wb") as out:
            process = subprocess.Popen(
                command,
                stdout=out,
                stderr=subprocess.STDOUT,
            )
            atexit.register(process.kill)
        if udid is None:
            desired_caps = __set_ios_device(desired_caps, device)
        url = f"http://localhost:{port}{__appium_base_path(appium_args)}"
        __wait_for_appium_start(process, file_path, url)
        return url, desired_caps, process, file_path

    return url, desired_caps, None, None


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
    """
    Under pytest-xdist, gives each worker its own iOS device: connected real
    devices first, then booted simulators. Otherwise Appium chooses the device.
    :param desired_caps: desired capabilities
    :param number: device index
    :return: desired capabilities
    """
    if os.getenv("PYTEST_XDIST_WORKER") is None:
        return desired_caps
    devices = __ios_real_devices() + __ios_booted_simulators()
    if not devices:
        logger.log_warn("No iOS devices found, Appium will choose the device")
        return desired_caps
    desired_caps["appium:udid"] = __pick_device(devices, number)
    return desired_caps


def __ios_real_devices():
    with tempfile.TemporaryDirectory() as tmp_dir:
        json_path = os.path.join(tmp_dir, "devices.json")
        try:
            subprocess.run(
                ["xcrun", "devicectl", "list", "devices", "--json-output",
                 json_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
            with open(json_path, encoding="utf-8") as file:
                devices = json.load(file)["result"]["devices"]
        except (OSError, subprocess.CalledProcessError, ValueError, KeyError):
            return []
    udids = []
    for device in devices:
        hardware = device.get("hardwareProperties", {})
        # Paired devices that are out of reach have no transport type
        connected = device.get("connectionProperties", {}).get("transportType")
        if (
            connected
            and hardware.get("platform") == "iOS"
            and hardware.get("reality") == "physical"
            and hardware.get("udid")
        ):
            udids.append(hardware["udid"])
    return udids


def __ios_booted_simulators():
    try:
        output = subprocess.run(
            ["xcrun", "simctl", "list", "devices", "booted", "--json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=True,
        ).stdout
        runtimes = json.loads(output)["devices"]
    except (OSError, subprocess.CalledProcessError, ValueError, KeyError):
        return []
    return [
        simulator["udid"]
        for runtime, simulators in sorted(runtimes.items())
        if ".iOS-" in runtime
        for simulator in simulators
        if simulator.get("state") == "Booted"
    ]


def __pick_device(devices: list, number: int):
    """
    Picks the device at the index, wrapping around when there are fewer
    devices than the index
    :param devices: device udids
    :param number: device index
    :return: device udid
    """
    if len(devices) > number:
        logger.log(f"Setting device: {devices[number]}")
        return devices[number]

    new_number = number % len(devices)
    logger.log_warn(
        f"You choose device number {number + 1} but there are only "
        f"{len(devices)} connected. "
        f"Will use device number {new_number + 1} instead",
        jump_line=True,
    )
    return devices[new_number]


def __adb():
    # IDE runs may lack the shell PATH; Appium also finds adb via ANDROID_HOME
    sdk = os.getenv("ANDROID_HOME") or os.getenv("ANDROID_SDK_ROOT")
    if shutil.which("adb") is None and sdk:
        return os.path.join(sdk, "platform-tools", "adb")
    return "adb"


def __adb_devices():
    output = subprocess.run(
        [__adb(), "devices"], stdout=subprocess.PIPE, check=False
    ).stdout.decode("utf-8", "replace")
    return [
        line.split("\t")[0] for line in output.splitlines() if "\t" in line
    ]


def get_device_udid(number: int):
    """
    Get device udid by index
    :param number: device index
    :return: device udid
    """
    devices = __adb_devices()
    if len(devices) == 0:
        raise Exception("There are 0 devices connected to the computer!")
    return __pick_device(devices, number)


def check_device_exist(udid):
    """
    Check if device exist
    :param udid: device udid
    :return: device udid if exist, None otherwise
    """
    if udid in __adb_devices():
        return udid
    return None


def check_chrome_version(udid):
    """
    Check chrome version on device
    :param udid: device udid
    :return: matching chromedriver version, None if Chrome isn't installed
    """
    output = subprocess.Popen(
        [
            __adb(),
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
    stdout, _ = output.communicate()
    version_name = re.search(
        r"versionName=([\d.]+)", stdout.decode("utf-8", "replace")
    )
    if version_name:
        return get_chrome_version(version_name.group(1))

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
