import requests
import sys
import platform

from testui.support import logger
import xml.etree.ElementTree as ET


def get_chrome_version(version: str):
    URL = "https://chromedriver.storage.googleapis.com/"
    r = requests.get(url=URL)

    # TODO: it is not pulling the version. I just updated all phones to
    # latest chrome
    chrome_version = ""
    mytree = ET.ElementTree(ET.fromstring(r.text))
    root = mytree.getroot()
    for child in root:
        for child2 in child:
            if not child2.text.__contains__(f"{version}."):
                continue
            if chrome_name() == "arm64" and \
                    child2.text.__contains__("m1") or \
                    child2.text.__contains__("mac_arm64"):
                chrome_version = child2.text.split("/")[0]
            elif child2.text.__contains__(chrome_name()):
                chrome_version = child2.text.split("/")[0]

    return chrome_version


def chrome_name():
    pl = sys.platform
    if pl == "linux" or pl == "linux2":
        return "/chromedriver_linux64.zip"
    elif pl == "darwin":
        if os_architecture() == 64:
            return "arm64"
        else:
            return "/chromedriver_mac64.zip"
    elif pl == "win32":
        return "/chromedriver_win32.zip"


def os_architecture():
    if platform.machine().endswith("64"):
        return 64
    else:
        return 32
