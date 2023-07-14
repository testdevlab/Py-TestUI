"""Module providing methods to get chrome drivers"""
import xml.etree.ElementTree as ET
import sys
import platform
import requests


def get_chrome_version(version: str):
    """
    gets all the available chromedriver versios from api
    and returns the path for the one asked
    :param version:
    """
    url = "https://chromedriver.storage.googleapis.com/"
    rq = requests.get(url=url)

    # TODO: it is not pulling the version. I just updated all phones to
    # latest chrome
    chrome_version = ""
    mytree = ET.ElementTree(ET.fromstring(rq.text))
    root = mytree.getroot()
    for child in root:
        for child2 in child:
            if not f"{version}." in child2.text:
                continue
            if chrome_name() == "arm64" and \
                    "m1" in child2.text or \
                    "mac_arm64" in child2.text:
                chrome_version = child2.text.split("/")[0]
            elif chrome_name() in child2.text:
                chrome_version = child2.text.split("/")[0]

    return chrome_version


def chrome_name():
    """
    returns the chromedriver path depending on platform
    :return: chromedriver_path string
    """
    pl = sys.platform
    if "linux" in pl:
        return "/chromedriver_linux64.zip"
    if pl == "darwin":
        if os_architecture() == 64:
            return "arm64"
        return "/chromedriver_mac64.zip"
    if pl == "win32":
        return "/chromedriver_win32.zip"
    return ""


def os_architecture():
    """
    returns the platform architecture
    :return: platform_arch int
    """
    if platform.machine().endswith("64"):
        return 64
    return 32
