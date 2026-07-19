"""Explainable OpenCV baseline for extracting one lead trace from a ROI."""

from __future__ import annotations

import cv2
import numpy as np

from ecg_api.decode import encode_png_base64
from ecg_api.layout import clip_region_to_image
from ecg_api.schemas import (
    CheckStatus,
    LeadRegion,
    TraceExtractionResult,
    TraceSample,
    TraceStatus,
)

# Minimum dark-ink coverage inside the ROI before we attempt centerline tracking.
MIN_INK_FRACTION = 0.004
# Maximum consecutive empty columns before counting a continuity gap.
MAX_GAP_RUN = 6
# If more than this many gaps remain after limited repair, mark extraction failed.
MAX_ALLOWED_GAPS = 12


def extract_lead_trace(
    image_bgr: np.ndarray,
    region: LeadRegion,
    *,
    include_debug: bool = True,
) -> TraceExtractionResult:
    height, width = image_bgr.shape[:2]
    region = clip_region_to_image(region, width, height)
    crop = _crop(image_bgr, region)
    source_b64 = encode_png_base64(crop)

    mask, ink_fraction = _ink_mask(crop)
    if ink_fraction < MIN_INK_FRACTION:
        debug_b64 = encode_png_base64(_debug_overlay(crop, mask, [])) if include_debug else None
        return TraceExtractionResult(
            status=TraceStatus.failed,
            lead_id=region.lead_id,
            region=region,
            samples=[],
            ink_fraction=ink_fraction,
            gap_count=0,
            quality_status=CheckStatus.fail,
            failure_reason=(
                f"Too little ink in lead {region.lead_id} "
                f"(ink fraction {ink_fraction:.4f} < {MIN_INK_FRACTION})."
            ),
            method="column_centerline_v1",
            source_crop_base64=source_b64,
            debug_overlay_base64=debug_b64,
            note="Extraction refused. Adjust the lead box or retake a sharper photo.",
        )

    samples, gap_count = _column_centerline(mask)
    if gap_count > MAX_ALLOWED_GAPS or len(samples) < max(20, mask.shape[1] // 8):
        debug_b64 = encode_png_base64(_debug_overlay(crop, mask, samples)) if include_debug else None
        return TraceExtractionResult(
            status=TraceStatus.failed,
            lead_id=region.lead_id,
            region=region,
            samples=samples,
            ink_fraction=ink_fraction,
            gap_count=gap_count,
            quality_status=CheckStatus.fail,
            failure_reason=(
                f"Trace continuity failed for lead {region.lead_id} "
                f"({gap_count} gaps, {len(samples)} samples)."
            ),
            method="column_centerline_v1",
            source_crop_base64=source_b64,
            debug_overlay_base64=debug_b64,
            note="Partial samples may still help you inspect the ROI, but do not treat them as a digitization.",
        )

    quality = CheckStatus.pass_ if gap_count <= 3 else CheckStatus.warn
    debug_b64 = encode_png_base64(_debug_overlay(crop, mask, samples)) if include_debug else None
    return TraceExtractionResult(
        status=TraceStatus.extracted,
        lead_id=region.lead_id,
        region=region,
        samples=samples,
        ink_fraction=ink_fraction,
        gap_count=gap_count,
        quality_status=quality,
        failure_reason=None,
        method="column_centerline_v1",
        source_crop_base64=source_b64,
        debug_overlay_base64=debug_b64,
        note=(
            "Centerline extracted with grid suppression and column medians. "
            "Compare the overlay with the source crop before trusting later measurements."
        ),
    )


def _crop(image_bgr: np.ndarray, region: LeadRegion) -> np.ndarray:
    x0 = int(np.floor(region.rect.x))
    y0 = int(np.floor(region.rect.y))
    x1 = int(np.ceil(region.rect.x + region.rect.width))
    y1 = int(np.ceil(region.rect.y + region.rect.height))
    return image_bgr[y0:y1, x0:x1].copy()


def _ink_mask(crop_bgr: np.ndarray) -> tuple[np.ndarray, float]:
    """
    Suppress reddish grid when present, then keep dark strokes.

    HSV masking is applied only when red/pink saturation is strong enough;
    otherwise it can erase faint traces on grayscale scans.
    """
    hsv = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2HSV)
    # Pink/red grid band commonly used on ECG paper.
    red_a = cv2.inRange(hsv, (0, 40, 80), (12, 255, 255))
    red_b = cv2.inRange(hsv, (165, 40, 80), (180, 255, 255))
    grid = cv2.bitwise_or(red_a, red_b)
    grid_fraction = float(np.mean(grid > 0))

    gray = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2GRAY)
    working = gray.copy()
    if grid_fraction > 0.02:
        working = working.copy()
        working[grid > 0] = np.median(working)

    blurred = cv2.GaussianBlur(working, (3, 3), 0)
    # Ink is darker than paper; invert so adaptive threshold keeps strokes.
    binary = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        21,
        8,
    )
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)

    # Drop tiny speckles.
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
    cleaned = np.zeros_like(binary)
    min_area = max(8, (crop_bgr.shape[0] * crop_bgr.shape[1]) // 8000)
    for label in range(1, num_labels):
        area = int(stats[label, cv2.CC_STAT_AREA])
        if area >= min_area:
            cleaned[labels == label] = 255

    ink_fraction = float(np.mean(cleaned > 0))
    return cleaned, ink_fraction


def _column_centerline(mask: np.ndarray) -> tuple[list[TraceSample], int]:
    height, width = mask.shape
    ys: list[float | None] = []
    for x in range(width):
        column = np.where(mask[:, x] > 0)[0]
        if column.size == 0:
            ys.append(None)
        else:
            ys.append(float(np.median(column)))

    repaired, gap_count = _repair_gaps(ys, max_run=MAX_GAP_RUN)
    samples: list[TraceSample] = []
    for x, y in enumerate(repaired):
        if y is None:
            continue
        samples.append(
            TraceSample(
                x=x / max(1, width - 1),
                y=float(y),
            )
        )
    return samples, gap_count


def _repair_gaps(
    ys: list[float | None],
    max_run: int,
) -> tuple[list[float | None], int]:
    """Linear-fill short gaps only. Longer gaps remain and are counted."""
    out = list(ys)
    n = len(out)
    i = 0
    gap_count = 0
    while i < n:
        if out[i] is not None:
            i += 1
            continue
        j = i
        while j < n and out[j] is None:
            j += 1
        run = j - i
        left = out[i - 1] if i > 0 else None
        right = out[j] if j < n else None
        if run <= max_run and left is not None and right is not None:
            for k in range(i, j):
                t = (k - i + 1) / (run + 1)
                out[k] = left * (1 - t) + right * t
        else:
            gap_count += 1
        i = j
    return out, gap_count


def _debug_overlay(
    crop_bgr: np.ndarray,
    mask: np.ndarray,
    samples: list[TraceSample],
) -> np.ndarray:
    overlay = crop_bgr.copy()
    # Show retained ink in green.
    ink_color = np.zeros_like(overlay)
    ink_color[mask > 0] = (40, 180, 40)
    overlay = cv2.addWeighted(overlay, 0.75, ink_color, 0.35, 0)

    if samples:
        height, width = mask.shape
        pts = np.array(
            [[int(round(s.x * (width - 1))), int(round(s.y))] for s in samples],
            dtype=np.int32,
        )
        cv2.polylines(overlay, [pts], False, (0, 0, 220), 2, cv2.LINE_AA)
    return overlay
