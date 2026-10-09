# Tests

Install TestUI and the dev tools from the repository root:

```bash
pip install -r requirements.txt
```

## Run in CI

These run on every pull request. To run them locally:

| Tests | Needs | Command |
| --- | --- | --- |
| `unit/` | Nothing | `python -m pytest tests/unit` |
| `selenium_tests.py` | Chrome | `python -m pytest tests/selenium_tests.py` |

To run both on every supported Python version, use `tox`.

## Run by hand

These need a device, so CI doesn't run them. TestUI starts and stops
Appium itself.

| Tests | Needs | Command |
| --- | --- | --- |
| `appium_app_test.py` | Appium with the `uiautomator2` driver, a running emulator or connected phone, `adb` on `PATH` or `ANDROID_HOME` set | `python -m pytest tests/appium_app_test.py` |
| `appium_ios_app.py` | Appium with the `xcuitest` driver, Xcode, a booted simulator (`xcrun simctl boot "iPhone 18 Pro"`) | `python -m pytest tests/appium_ios_app.py` |
| `selenium_firefox_tests.py` | Firefox | `python -m pytest tests/selenium_firefox_tests.py` |
