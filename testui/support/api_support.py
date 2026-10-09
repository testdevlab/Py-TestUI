"""Module providing methods to get chrome drivers"""
import xml.etree.ElementTree as ET
import sys
import platform
import requests


CHROME_FOR_TESTING_URL = (
    "https://googlechromelabs.github.io/chrome-for-testing/"
)


def get_chrome_version(version: str):
    """
    Finds the chromedriver version that matches a Chrome version
    :param version: Chrome version, full ("149.0.7827.5") or major ("149")
    :return: chromedriver version, or "" if none was found
    """
    major = version.split(".")[0]
    if not major.isdigit():
        return ""
    if int(major) < 115:
        return __legacy_chromedriver_version(major)

    # Device builds are often missing from Chrome for Testing, so take the
    # newest patch of the same build, as Chrome's version selection does
    build = ".".join(version.split(".")[:3])
    builds = requests.get(
        CHROME_FOR_TESTING_URL + "latest-patch-versions-per-build.json",
        timeout=30,
    ).json()["builds"]
    if build in builds:
        return builds[build]["version"]
    milestones = requests.get(
        CHROME_FOR_TESTING_URL + "latest-versions-per-milestone.json",
        timeout=30,
    ).json()["milestones"]
    return milestones.get(major, {}).get("version", "")


def __legacy_chromedriver_version(major: str):
    """Chrome 114 and older, from the retired chromedriver index"""
    url = "https://chromedriver.storage.googleapis.com/"
    rq = requests.get(url=url, timeout=30)
    chrome_version = ""
    mytree = ET.ElementTree(ET.fromstring(rq.text))
    root = mytree.getroot()
    platform_name = chrome_name()
    for child in root:
        for child2 in child:
            if not f"{major}." in child2.text:
                continue
            if platform_name == "arm64" and (
                "m1" in child2.text or "mac_arm64" in child2.text
            ):
                chrome_version = child2.text.split("/")[0]
            elif platform_name in child2.text:
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
        if platform.machine() == "arm64":
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
