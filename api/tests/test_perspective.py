from __future__ import annotations

import numpy as np
import pytest

from ecg_api.perspective import (
    detect_page_corners,
    full_frame_corners,
    order_corners,
    rectify_page,
)
from ecg_api.schemas import CornerSet, DetectionStatus, Point


def test_order_corners_sum_diff() -> None:
    unordered = np.array([[100, 10], [10, 10], [100, 90], [10, 90]], dtype=np.float32)
    corners = order_corners(unordered)
    assert corners.top_left.x == pytest.approx(10)
    assert corners.top_left.y == pytest.approx(10)
    assert corners.bottom_right.x == pytest.approx(100)
    assert corners.bottom_right.y == pytest.approx(90)


def test_detect_skewed_page_returns_corners(skewed_photo: np.ndarray) -> None:
    result = detect_page_corners(skewed_photo)
    assert result.status in {DetectionStatus.detected, DetectionStatus.fallback_full_frame}
    assert result.corners.top_left.x >= 0
    warped, w, h = rectify_page(skewed_photo, result.corners)
    assert warped.shape[1] == w
    assert warped.shape[0] == h
    assert w >= 200 and h >= 200


def test_rectify_rejects_tiny_quad(clean_page: np.ndarray) -> None:
    h, w = clean_page.shape[:2]
    tiny = CornerSet(
        top_left=Point(x=w / 2, y=h / 2),
        top_right=Point(x=w / 2 + 5, y=h / 2),
        bottom_right=Point(x=w / 2 + 5, y=h / 2 + 5),
        bottom_left=Point(x=w / 2, y=h / 2 + 5),
    )
    with pytest.raises(ValueError, match="too little"):
        rectify_page(clean_page, tiny)


def test_full_frame_rectify_preserves_content_bounds(clean_page: np.ndarray) -> None:
    corners = full_frame_corners(clean_page.shape[1], clean_page.shape[0])
    warped, w, h = rectify_page(clean_page, corners, output_width=400, output_height=300)
    assert (w, h) == (400, 300)
    assert warped.mean() > 100
