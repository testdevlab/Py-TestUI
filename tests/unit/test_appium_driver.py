import http.server
import os
import subprocess
import threading
from unittest import mock

import pytest

from testui.support import appium_driver as ad


def private(name):
    return getattr(ad, name)


def test_wait_for_appium_start_times_out_and_detects_exit(
    tmp_path, monkeypatch
):
    wait = private("__wait_for_appium_start")
    log = tmp_path / "appium.log"
    log.write_text("starting...")
    closed_port = "http://127.0.0.1:9"
    running = mock.Mock(poll=mock.Mock(return_value=None))
    monkeypatch.setattr(ad, "APPIUM_START_TIMEOUT", 1)
    with pytest.raises(Exception, match="did not start within"):
        wait(running, str(log), closed_port)
    exited = mock.Mock(poll=mock.Mock(return_value=1))
    with pytest.raises(Exception, match="exited before starting"):
        wait(exited, str(log), closed_port)
    log.write_text("REST http interface listener started on 0.0.0.0:4723")
    wait(running, str(log), closed_port)


@pytest.mark.parametrize(
    "version,path",
    [(b"1.22.3\n", "/wd/hub"), (b"2.11.0\n", ""), (b"3.5.1\n", "")],
)
def test_appium_base_path_by_version(version, path):
    private("__appium_major_version").cache_clear()
    with mock.patch.object(
        subprocess, "run", return_value=mock.Mock(stdout=version)
    ) as run:
        assert private("__appium_base_path")([]) == path
        private("__appium_base_path")([])
    assert run.call_count == 1
    private("__appium_major_version").cache_clear()


@pytest.mark.parametrize(
    "args,path",
    [
        (["--base-path", "/wd/hub/"], "/wd/hub"),
        (["--base-path=/custom"], "/custom"),
        (["-pa", "/"], ""),
    ],
)
def test_appium_base_path_from_args(args, path):
    assert private("__appium_base_path")(args) == path


def test_appium_ready():
    class Status(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200 if self.path == "/status" else 404)
            self.end_headers()

        def log_message(self, *args):
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), Status)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_port}"
    assert private("__appium_ready")(url)
    server.shutdown()
    server.server_close()
    assert not private("__appium_ready")(url)


@pytest.fixture
def local_appium(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    popen = mock.Mock(return_value=mock.Mock())
    monkeypatch.setattr(subprocess, "Popen", popen)
    monkeypatch.setattr(ad, "__wait_for_appium_start", lambda *args: None)
    monkeypatch.setattr(ad, "__appium_base_path", lambda args: "")
    return popen


def test_xdist_worker_gets_own_port_and_device(monkeypatch, local_appium):
    monkeypatch.setenv("PYTEST_XDIST_WORKER", "gw1")
    monkeypatch.setattr(ad, "get_device_udid", lambda n: f"udid{n}")
    url, caps, process, _ = private("__local_run")(
        None, {}, 4723, None, "appium-stdout.log"
    )
    assert url == "http://localhost:4725" and caps["appium:udid"] == "udid1"
    assert process is local_appium.return_value


def test_ios_local_run_returns_process(local_appium):
    url, _, process, _ = private("__local_run_ios")(
        None, {}, 4723, "x", "appium-stdout.log", ["--a"]
    )
    assert (
        url == "http://localhost:4823" and process is local_appium.return_value
    )
    assert local_appium.call_args[0][0] == ["appium", "-p", "4823", "--a"]
    assert private("__local_run_ios")("http://h", {}, 4723, "x", "l") == (
        "http://h",
        {},
        None,
        None,
    )


def test_start_driver_keeps_ios_process(monkeypatch):
    process = mock.Mock()
    monkeypatch.setattr(
        ad,
        "__local_run_ios",
        lambda *args: ("http://u", {"platformName": "iOS"}, process, "log"),
    )
    monkeypatch.setattr(ad, "Remote", mock.Mock())
    _, started, log_file = ad.start_driver(
        {"platformName": "iOS"}, None, False, 4723, "x", "l"
    )
    assert started is process and log_file == "log"


def test_adb_devices_parsing():
    out = (
        b"* daemon started successfully\nList of devices attached\n"
        b"emulator-5554\tdevice\nR58M\tunauthorized\n\n"
    )
    with mock.patch.object(
        subprocess, "run", return_value=mock.Mock(stdout=out)
    ):
        assert private("__adb_devices")() == ["emulator-5554", "R58M"]
        assert ad.get_device_udid(1) == "R58M"
        assert ad.check_device_exist("R58M") == "R58M"
        assert ad.check_device_exist("nope") is None


def test_adb_falls_back_to_android_home(monkeypatch):
    monkeypatch.setenv("ANDROID_HOME", "/sdk")
    monkeypatch.setattr(ad.shutil, "which", lambda name: None)
    assert private("__adb")() == os.path.join("/sdk", "platform-tools", "adb")
    monkeypatch.setattr(ad.shutil, "which", lambda name: "/usr/bin/adb")
    assert private("__adb")() == "adb"


def test_check_chrome_version_uses_full_device_version():
    adb = mock.Mock(
        communicate=mock.Mock(
            return_value=(b"    versionName=149.0.7827.5\n", None)
        )
    )
    with (
        mock.patch.object(subprocess, "Popen", return_value=adb),
        mock.patch.object(
            ad, "get_chrome_version", return_value="149.0.7827.155"
        ) as lookup,
    ):
        assert ad.check_chrome_version("udid") == "149.0.7827.155"
    lookup.assert_called_with("149.0.7827.5")


def test_isolated_configuration():
    shared_a, shared_b = ad.NewDriver(), ad.NewDriver()
    original = shared_b.configuration.screenshot_path
    isolated = (
        ad.NewDriver()
        .set_isolated_configuration()
        .set_screenshot_path("only-me")
    )
    assert shared_a.configuration.screenshot_path == original
    assert isolated.configuration.screenshot_path == "only-me"
    shared_a.set_screenshot_path("shared")
    assert shared_b.configuration.screenshot_path == "shared"
    shared_a.set_screenshot_path(original)


def platform_caps(driver, platform):
    getattr(driver, f"_NewDriver__set_{platform}_caps")()
    return getattr(driver, "_NewDriver__desired_capabilities")


@pytest.mark.parametrize(
    "platform,app",
    [
        ("android", lambda d: d.set_app_package_activity("p", ".A")),
        ("android", lambda d: d.set_app_path("a.apk")),
        ("ios", lambda d: d.set_bundle_id("com.apple.Preferences")),
    ],
)
def test_app_is_restarted_at_session_start(platform, app):
    caps = platform_caps(app(ad.NewDriver()), platform)
    assert caps["appium:forceAppLaunch"] is True


@pytest.mark.parametrize("platform", ["android", "ios"])
def test_browser_session_is_not_restarted(platform):
    assert "appium:forceAppLaunch" not in platform_caps(
        ad.NewDriver(), platform
    )


@pytest.mark.parametrize("key", ["forceAppLaunch", "appium:forceAppLaunch"])
def test_own_force_app_launch_is_kept(key):
    driver = ad.NewDriver().set_app_path("a.apk").set_extra_caps({key: False})
    caps = platform_caps(driver, "android")
    own = {"forceAppLaunch", "appium:forceAppLaunch"} & caps.keys()
    assert caps[key] is False and own == {key}
