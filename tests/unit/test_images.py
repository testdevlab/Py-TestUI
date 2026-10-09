from unittest import mock

import cv2
import numpy as np
import pytest

from testui.support.testui_images import ImageRecognition, get_point_match


@pytest.fixture
def images(tmp_path):
    rng = np.random.default_rng(2)
    big = (rng.random((200, 200, 3)) * 255).astype("uint8")
    paths = {
        name: str(tmp_path / f"{name}.png") for name in ("big", "hit", "miss")
    }
    cv2.imwrite(paths["big"], big)
    cv2.imwrite(paths["hit"], big[50:90, 60:100])
    cv2.imwrite(paths["miss"], (rng.random((40, 40, 3)) * 255).astype("uint8"))
    return paths


def test_point_match(images):
    point = get_point_match(images["big"], images["hit"])
    assert abs(point[0] - 80) <= 2 and abs(point[1] - 70) <= 2
    assert (
        ImageRecognition(images["big"], images["hit"]).get_middle_point()
        == point
    )


def test_point_match_below_threshold_warns_or_raises_when_strict(images):
    with mock.patch("testui.support.logger.log_warn") as warn:
        get_point_match(images["big"], images["miss"])
    assert warn.called
    with pytest.raises(Exception, match="below threshold"):
        get_point_match(images["big"], images["miss"], strict=True)


def test_grayscale_compare(images):
    assert ImageRecognition(images["big"], images["hit"], path="").compare(
        grayscale=True
    )


def test_crop_clamps_to_screen_edge(tmp_path):
    img = (np.random.default_rng(0).random((100, 100, 3)) * 255).astype("uint8")
    cv2.imwrite(str(tmp_path / "o.png"), img)
    out = str(tmp_path / "c.png")
    ImageRecognition("o.png", path=str(tmp_path)).crop_original_image(
        5, 5, 20, 20, out
    )
    assert np.array_equal(cv2.imread(out), img[0:20, 0:20])
