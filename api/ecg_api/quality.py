"""Stage 1 image-quality checks for photographed ECG pages."""

from __future__ import annotations

import cv2
import numpy as np

from ecg_api.config import (
    BLUR_VARIANCE_THRESHOLD,
    GLARE_FRACTION_THRESHOLD,
    MIN_SHORT_SIDE_PX,
    SHADOW_FRACTION_THRESHOLD,
)
from ecg_api.schemas import CheckStatus, QualityCheck, QualityReport


def assess_image_quality(image_bgr: np.ndarray) -> QualityReport:
    height, width = image_bgr.shape[:2]
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

    checks = [
        _resolution_check(width, height),
        _blur_check(gray),
        _glare_check(gray),
        _shadow_check(gray),
        _coverage_check(gray),
        _rotation_hint_check(gray),
    ]

    identifier = _identifier_region_warning(gray)
    overall = _overall_status(checks)

    # Hard refusals: tiny images or extreme blur make later stages unsafe.
    hard_fails = {
        check.id
        for check in checks
        if check.status == CheckStatus.fail and check.id in {"resolution", "blur"}
    }
    analysis_allowed = len(hard_fails) == 0
    refusal_reason = None
    if not analysis_allowed:
        refusal_reason = (
            "Image quality is too poor for prototype page correction. "
            + " ".join(
                check.guidance or check.detail
                for check in checks
                if check.id in hard_fails and check.guidance
            )
        )

    return QualityReport(
        width_px=width,
        height_px=height,
        overall_status=overall,
        checks=checks,
        may_contain_identifier_text=identifier is not None,
        identifier_warning=identifier,
        analysis_allowed=analysis_allowed,
        refusal_reason=refusal_reason,
    )


def _resolution_check(width: int, height: int) -> QualityCheck:
    short_side = min(width, height)
    if short_side < MIN_SHORT_SIDE_PX:
        return QualityCheck(
            id="resolution",
            label="Resolution",
            status=CheckStatus.fail,
            detail=f"Short side is {short_side} px (minimum {MIN_SHORT_SIDE_PX}).",
            guidance="Move closer or use a higher-resolution capture so the full page fills the frame.",
        )
    if short_side < 700:
        return QualityCheck(
            id="resolution",
            label="Resolution",
            status=CheckStatus.warn,
            detail=f"Short side is {short_side} px.",
            guidance="A closer photo usually improves grid and trace visibility.",
        )
    return QualityCheck(
        id="resolution",
        label="Resolution",
        status=CheckStatus.pass_,
        detail=f"{width}×{height} px.",
    )


def _blur_check(gray: np.ndarray) -> QualityCheck:
    variance = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    if variance < BLUR_VARIANCE_THRESHOLD:
        return QualityCheck(
            id="blur",
            label="Sharpness",
            status=CheckStatus.fail,
            detail=f"Laplacian variance {variance:.1f} (threshold {BLUR_VARIANCE_THRESHOLD}).",
            guidance="Hold the camera steady and retake; avoid motion blur.",
        )
    if variance < BLUR_VARIANCE_THRESHOLD * 2:
        return QualityCheck(
            id="blur",
            label="Sharpness",
            status=CheckStatus.warn,
            detail=f"Laplacian variance {variance:.1f}.",
            guidance="Slight softness detected; a sharper retake is safer before trusting measurements.",
        )
    return QualityCheck(
        id="blur",
        label="Sharpness",
        status=CheckStatus.pass_,
        detail=f"Laplacian variance {variance:.1f}.",
    )


def _glare_check(gray: np.ndarray) -> QualityCheck:
    # Paper white (~240–248) is normal. Specular glare saturates near 255 in patches.
    saturated = float(np.mean(gray >= 252))
    if saturated >= GLARE_FRACTION_THRESHOLD:
        return QualityCheck(
            id="glare",
            label="Glare / overexposure",
            status=CheckStatus.fail,
            detail=f"{saturated:.1%} of pixels are saturated (≥252).",
            guidance="Avoid flash glare; tilt slightly or change lighting so the paper is evenly lit.",
        )
    if saturated >= GLARE_FRACTION_THRESHOLD * 0.5:
        return QualityCheck(
            id="glare",
            label="Glare / overexposure",
            status=CheckStatus.warn,
            detail=f"{saturated:.1%} of pixels are saturated (≥252).",
            guidance="Reduce specular highlights before relying on ST or baseline measurements.",
        )
    return QualityCheck(
        id="glare",
        label="Glare / overexposure",
        status=CheckStatus.pass_,
        detail=f"{saturated:.1%} saturated pixels.",
    )


def _shadow_check(gray: np.ndarray) -> QualityCheck:
    dark = float(np.mean(gray <= 40))
    if dark >= SHADOW_FRACTION_THRESHOLD:
        return QualityCheck(
            id="shadow",
            label="Shadows",
            status=CheckStatus.fail,
            detail=f"{dark:.1%} of pixels are very dark.",
            guidance="Retake in more even light; avoid casting a hand or phone shadow across the page.",
        )
    if dark >= SHADOW_FRACTION_THRESHOLD * 0.55:
        return QualityCheck(
            id="shadow",
            label="Shadows",
            status=CheckStatus.warn,
            detail=f"{dark:.1%} of pixels are very dark.",
            guidance="Uneven illumination may hide low-amplitude traces.",
        )
    return QualityCheck(
        id="shadow",
        label="Shadows",
        status=CheckStatus.pass_,
        detail=f"{dark:.1%} very dark pixels.",
    )


def _coverage_check(gray: np.ndarray) -> QualityCheck:
    """Estimate whether a light paper region occupies enough of the frame."""
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # Paper is usually brighter than background; take the larger bright blob family.
    bright_fraction = float(np.mean(binary > 0))
    if bright_fraction < 0.25:
        # Maybe inverted lighting; try the complement.
        bright_fraction = 1.0 - bright_fraction

    if bright_fraction < 0.35:
        return QualityCheck(
            id="coverage",
            label="ECG paper coverage",
            status=CheckStatus.fail,
            detail=f"Estimated paper coverage {bright_fraction:.0%}.",
            guidance="Include all four edges of the ECG paper in the frame.",
        )
    if bright_fraction < 0.5:
        return QualityCheck(
            id="coverage",
            label="ECG paper coverage",
            status=CheckStatus.warn,
            detail=f"Estimated paper coverage {bright_fraction:.0%}.",
            guidance="Step back slightly so the full page, including margins, is visible.",
        )
    return QualityCheck(
        id="coverage",
        label="ECG paper coverage",
        status=CheckStatus.pass_,
        detail=f"Estimated paper coverage {bright_fraction:.0%}.",
    )


def _rotation_hint_check(gray: np.ndarray) -> QualityCheck:
    """Rough deskew hint from the dominant line angle; not a precise page rotation."""
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=max(80, gray.shape[1] // 4))
    if lines is None:
        return QualityCheck(
            id="rotation",
            label="Rotation",
            status=CheckStatus.not_assessable,
            detail="No dominant line angle found.",
            guidance="Hold the camera parallel to the page if the print looks tilted.",
        )

    angles: list[float] = []
    for item in lines[:40]:
        rho_theta = item[0]
        theta = float(rho_theta[1])
        # Convert to degrees from horizontal; fold into [-45, 45].
        angle = (theta * 180.0 / np.pi) - 90.0
        while angle < -45:
            angle += 90
        while angle > 45:
            angle -= 90
        angles.append(angle)

    median_angle = float(np.median(angles))
    if abs(median_angle) >= 8:
        return QualityCheck(
            id="rotation",
            label="Rotation",
            status=CheckStatus.warn,
            detail=f"Approximate in-plane tilt {median_angle:.1f}°.",
            guidance="Hold the camera parallel to the page, or correct corners in the next step.",
        )
    return QualityCheck(
        id="rotation",
        label="Rotation",
        status=CheckStatus.pass_,
        detail=f"Approximate in-plane tilt {median_angle:.1f}°.",
    )


def _identifier_region_warning(gray: np.ndarray) -> str | None:
    """
    Heuristic only: dense high-frequency content in the top strip may be printed text.
    This is a warning mechanism, not anonymization.
    """
    height, width = gray.shape
    top = gray[: max(1, height // 8), :]
    edges = cv2.Canny(top, 80, 160)
    density = float(np.mean(edges > 0))
    if density < 0.045:
        return None
    return (
        "The top region of this image looks text-heavy. Do not upload identifiable "
        "clinical headers. This warning is not guaranteed anonymization."
    )


def _overall_status(checks: list[QualityCheck]) -> CheckStatus:
    statuses = {check.status for check in checks}
    if CheckStatus.fail in statuses:
        return CheckStatus.fail
    if CheckStatus.warn in statuses:
        return CheckStatus.warn
    if statuses == {CheckStatus.not_assessable}:
        return CheckStatus.not_assessable
    return CheckStatus.pass_
