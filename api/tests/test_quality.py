from __future__ import annotations

import cv2
import numpy as np

from ecg_api.quality import assess_image_quality
from ecg_api.schemas import CheckStatus


def test_clean_page_allows_analysis(clean_page: np.ndarray) -> None:
    report = assess_image_quality(clean_page)
    assert report.analysis_allowed is True
    assert report.overall_status in {CheckStatus.pass_, CheckStatus.warn}


def test_tiny_image_is_refused() -> None:
    path = __import__("pathlib").Path(__file__).resolve().parents[2] / "samples" / "synthetic" / "photo_tiny.png"
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    assert image is not None
    report = assess_image_quality(image)
    assert report.analysis_allowed is False
    assert report.refusal_reason
    assert any(check.id == "resolution" and check.status == CheckStatus.fail for check in report.checks)


def test_blurry_image_fails_sharpness() -> None:
    path = __import__("pathlib").Path(__file__).resolve().parents[2] / "samples" / "synthetic" / "photo_blurry.png"
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    assert image is not None
    report = assess_image_quality(image)
    blur = next(check for check in report.checks if check.id == "blur")
    assert blur.status == CheckStatus.fail
    assert report.analysis_allowed is False


def test_identifier_warning_on_text_banner(clean_page: np.ndarray) -> None:
    report = assess_image_quality(clean_page)
    assert report.may_contain_identifier_text is True
    assert report.identifier_warning is not None
