import time
from unittest import mock

import pytest

from fakes import FakeTestUIDriver, FakeWebElement
from testui.elements.testui_collection import CollectionException, Collections
from testui.elements.testui_element import ElementException, Elements


def test_location_and_dimensions_single_lookup():
    d = FakeTestUIDriver([FakeWebElement()])
    el = Elements(d, "id", "a")
    loc = el.location
    assert (loc.x, loc.y) == (10, 20) and d._driver.find_calls == 1
    dim = el.dimensions
    assert (dim.x, dim.y) == (30, 40) and d._driver.find_calls == 2


def test_find_by_attribute_missing_attribute_no_crash():
    d = FakeTestUIDriver(
        [FakeWebElement({}), FakeWebElement({"name": "Hello"})]
    )
    el = Elements(d, "id", "a")
    assert (
        el.find_by_attribute(
            "name", "hello", timeout=1, case_sensitive=False
        ).index
        == 1
    )


def test_swipe_until_text_needs_end_x_and_end_y():
    el = Elements(FakeTestUIDriver([FakeWebElement()]), "id", "a")
    with pytest.raises(Exception, match="end_x and end_y"):
        el.swipe_until_text(text="x")
    with pytest.raises(Exception, match="end_x and end_y"):
        el.swipe_until_text(end_y=100, text="x")
    with (
        mock.patch.object(Elements, "swipe") as swipe,
        mock.patch.object(Elements, "is_visible", side_effect=[False, True]),
    ):
        el.swipe_until_text(end_x=50, end_y=100, text="x", max_swipes=3)
    assert swipe.call_count == 1


def test_swipe_until_text_soft_mode_swipes_and_records_no_errors():
    d = FakeTestUIDriver([FakeWebElement()], soft_assert=True)
    el = Elements(d, "id", "a")
    with (
        mock.patch.object(Elements, "swipe") as swipe,
        mock.patch.object(Elements, "is_visible", return_value=False),
    ):
        el.swipe_until_text(end_x=50, end_y=100, text="x", max_swipes=3)
    assert swipe.call_count == 3 and d.errors == []


@pytest.mark.parametrize("soft", [False, True])
def test_collection_success_and_failure(soft):
    good = Elements(
        FakeTestUIDriver([FakeWebElement()], soft_assert=soft), "id", "a"
    )
    Collections([good, good]).wait_until_all_visible(seconds=0.5)
    assert good.testui_driver.errors == []
    d = FakeTestUIDriver([], soft_assert=soft)
    bad = Elements(d, "id", "b")
    if soft:
        Collections([bad]).wait_until_all_visible(seconds=0.3)
        assert any("Collection of elements has not" in str(e) for e in d.errors)
    else:
        with pytest.raises(CollectionException):
            Collections([bad]).wait_until_all_visible(seconds=0.3)


def test_collection_slow_but_successful_is_not_a_failure():
    el = Elements(FakeTestUIDriver([FakeWebElement()]), "id", "a")

    def slow_wait(seconds, log):
        time.sleep(seconds + 0.1)

    with mock.patch.object(el, "wait_until_visible", side_effect=slow_wait):
        Collections([el]).wait_until_all_visible(seconds=0.2)


def test_attribute_wait_polls_with_sleep():
    d = FakeTestUIDriver([FakeWebElement({"text": "no"})])
    with pytest.raises(ElementException):
        Elements(d, "id", "a").wait_until_attribute("text", "yes", seconds=1)
    assert d._driver.find_calls <= 7


def test_no_contains_attribute_negates():
    d = FakeTestUIDriver([FakeWebElement({"text": "hello world"})])
    with pytest.raises(ElementException):
        Elements(d, "id", "a").no().wait_until_contains_attribute(
            "text", "hello", seconds=0.3
        )
    Elements(d, "id", "a").no().wait_until_contains_attribute(
        "text", "bye", seconds=0.3
    )
    Elements(d, "id", "a").wait_until_contains_attribute(
        "text", "hello", seconds=0.3
    )


def test_press_hold_pause_in_seconds():
    d = FakeTestUIDriver([FakeWebElement()])
    actions = mock.MagicMock()
    d.actions = lambda: actions
    Elements(d, "id", "a").press_hold_for(500)
    actions.w3c_actions.pointer_action.pause.assert_called_with(0.5)
