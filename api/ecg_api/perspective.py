"""Page boundary detection and four-point perspective correction."""

from __future__ import annotations

import cv2
import numpy as np

from ecg_api.config import MIN_PAGE_AREA_FRACTION
from ecg_api.schemas import (
    CornerSet,
    DetectionStatus,
    PageDetectionResult,
    Point,
)


def full_frame_corners(width: int, height: int) -> CornerSet:
    return CornerSet(
        top_left=Point(x=0, y=0),
        top_right=Point(x=width - 1, y=0),
        bottom_right=Point(x=width - 1, y=height - 1),
        bottom_left=Point(x=0, y=height - 1),
    )


def order_corners(points: np.ndarray) -> CornerSet:
    """Order four points into TL, TR, BR, BL using sum/diff heuristics."""
    pts = np.asarray(points, dtype=np.float32).reshape(4, 2)
    sums = pts.sum(axis=1)
    diffs = np.diff(pts, axis=1).reshape(4)

    top_left = pts[np.argmin(sums)]
    bottom_right = pts[np.argmax(sums)]
    top_right = pts[np.argmin(diffs)]
    bottom_left = pts[np.argmax(diffs)]

    return CornerSet(
        top_left=Point(x=float(top_left[0]), y=float(top_left[1])),
        top_right=Point(x=float(top_right[0]), y=float(top_right[1])),
        bottom_right=Point(x=float(bottom_right[0]), y=float(bottom_right[1])),
        bottom_left=Point(x=float(bottom_left[0]), y=float(bottom_left[1])),
    )


def detect_page_corners(image_bgr: np.ndarray) -> PageDetectionResult:
    height, width = image_bgr.shape[:2]
    fallback = full_frame_corners(width, height)
    image_area = float(width * height)

    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    edges = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=1)

    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    candidates: list[tuple[float, np.ndarray]] = []

    for contour in contours:
        area = float(cv2.contourArea(contour))
        if area < image_area * MIN_PAGE_AREA_FRACTION:
            continue
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        if len(approx) == 4 and cv2.isContourConvex(approx):
            candidates.append((area, approx.reshape(4, 2)))

    if not candidates:
        return PageDetectionResult(
            status=DetectionStatus.fallback_full_frame,
            corners=fallback,
            page_area_fraction=None,
            detail=(
                "No quadrilateral page boundary met the area threshold. "
                "Showing full-frame corners for manual adjustment."
            ),
        )

    candidates.sort(key=lambda item: item[0], reverse=True)
    area, quad = candidates[0]
    corners = order_corners(quad)
    return PageDetectionResult(
        status=DetectionStatus.detected,
        corners=corners,
        page_area_fraction=area / image_area,
        detail=f"Detected a quadrilateral covering {area / image_area:.0%} of the image.",
    )


def _destination_size(
    corners: CornerSet,
    output_width: int | None,
    output_height: int | None,
) -> tuple[int, int]:
    pts = np.array(corners.as_array(), dtype=np.float32)
    width_a = np.linalg.norm(pts[1] - pts[0])
    width_b = np.linalg.norm(pts[2] - pts[3])
    height_a = np.linalg.norm(pts[3] - pts[0])
    height_b = np.linalg.norm(pts[2] - pts[1])
    est_w = int(round(max(width_a, width_b)))
    est_h = int(round(max(height_a, height_b)))
    width = output_width or max(200, est_w)
    height = output_height or max(200, est_h)
    return width, height


def rectify_page(
    image_bgr: np.ndarray,
    corners: CornerSet,
    output_width: int | None = None,
    output_height: int | None = None,
) -> tuple[np.ndarray, int, int]:
    height, width = image_bgr.shape[:2]
    _validate_corners(corners, width, height)

    out_w, out_h = _destination_size(corners, output_width, output_height)
    src = np.array(corners.as_array(), dtype=np.float32)
    dst = np.array(
        [
            [0.0, 0.0],
            [out_w - 1.0, 0.0],
            [out_w - 1.0, out_h - 1.0],
            [0.0, out_h - 1.0],
        ],
        dtype=np.float32,
    )
    matrix = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(image_bgr, matrix, (out_w, out_h))
    return warped, out_w, out_h


def _validate_corners(corners: CornerSet, width: int, height: int) -> None:
    points = corners.as_array()
    for x, y in points:
        if x < -1 or y < -1 or x > width or y > height:
            raise ValueError("Corner coordinates fall outside the image bounds.")

    # Reject degenerate quads (near-zero area or crossed).
    contour = np.array(points, dtype=np.float32).reshape(-1, 1, 2)
    area = abs(float(cv2.contourArea(contour)))
    if area < (width * height) * 0.05:
        raise ValueError("Selected corners cover too little of the image.")
    if not cv2.isContourConvex(contour):
        raise ValueError("Selected corners must form a convex quadrilateral.")
