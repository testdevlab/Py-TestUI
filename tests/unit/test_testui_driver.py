from unittest import mock

from fakes import FakeWebDriver
from testui.support import testui_driver as td


def test_execute_script_signatures():
    drv = td.TestUIDriver.__new__(td.TestUIDriver)
    fake = FakeWebDriver([])
    with mock.patch.object(
        td.TestUIDriver,
        "driver",
        new_callable=mock.PropertyMock,
        return_value=fake,
    ):
        drv.execute_script("return 1")
        drv.execute_script("x", [1, 2])
        drv.execute_script("x", None)
        drv.execute_script("x", args=5)
        drv.execute_script("x", 1, 2)
    assert fake.script_calls == [
        ("return 1", ()),
        ("x", ([1, 2],)),
        ("x", (None,)),
        ("x", (5,)),
        ("x", (1, 2)),
    ]


def test_click_by_image_taps_once_and_strict_is_passed():
    drv = td.TestUIDriver.__new__(td.TestUIDriver)
    drv.device_udid, drv.device_name = "u", "Device"
    with (
        mock.patch.object(
            td.TestUIDriver, "save_screenshot", return_value="s.png"
        ),
        mock.patch.object(td, "get_point_match", return_value=(5, 6)) as gpm,
        mock.patch.object(td.TestUIDriver, "click") as click,
        mock.patch.object(td.TestUIDriver, "_TestUIDriver__delete_screenshot"),
    ):
        drv.click_by_image("i.png", strict=True)
    assert click.call_count == 1 and gpm.call_args[0][-1] is True
