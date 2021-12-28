import requests


def get_chrome_version(version: str):
    URL = "https://chromedriver.storage.googleapis.com/"
    r = requests.get(url=URL)

    # TODO: it is not pulling the version. I just updated all phones to
    # latest chrome
    chrome_version = ''
    for text in r.text.split(f'{version}.'):
        if text.__contains__('/chromedriver_mac64.zip'):
            new_chrome_version = f'{version}.{text.split("/chromedriver_mac64.zip")[0]}'
            if len(new_chrome_version) < 17:
                chrome_version = new_chrome_version
    return chrome_version
