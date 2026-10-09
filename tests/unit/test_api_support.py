from unittest import mock

import pytest

from testui.support import api_support

BUILDS = {"builds": {"149.0.7827": {"version": "149.0.7827.155"}}}
MILESTONES = {
    "milestones": {
        "149": {"version": "149.0.7827.155"},
        "150": {"version": "150.0.7900.10"},
    }
}


def fake_get(url, **kwargs):
    data = BUILDS if "per-build" in url else MILESTONES
    return mock.Mock(json=mock.Mock(return_value=data))


@pytest.mark.parametrize(
    "chrome,driver",
    [
        ("149.0.7827.5", "149.0.7827.155"),
        ("150.0.7901.3", "150.0.7900.10"),
        ("149", "149.0.7827.155"),
        ("151.0.1.2", ""),
    ],
)
def test_chrome_for_testing_lookup(chrome, driver):
    with mock.patch.object(api_support.requests, "get", side_effect=fake_get):
        assert api_support.get_chrome_version(chrome) == driver


def test_old_chrome_uses_legacy_index():
    with (
        mock.patch.object(
            api_support,
            "__legacy_chromedriver_version",
            return_value="114.0.5735.90",
        ) as legacy,
        mock.patch.object(api_support.requests, "get") as get,
    ):
        assert (
            api_support.get_chrome_version("114.0.5735.198") == "114.0.5735.90"
        )
    legacy.assert_called_with("114")
    get.assert_not_called()


def test_unknown_version_returns_empty():
    assert api_support.get_chrome_version("") == ""
