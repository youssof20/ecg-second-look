from __future__ import annotations

import cv2
import numpy as np

from ecg_api.layout import propose_lead_regions
from ecg_api.schemas import TraceStatus
from ecg_api.trace import extract_lead_trace


def test_propose_layout_has_twelve_regions(clean_page: np.ndarray) -> None:
    h, w = clean_page.shape[:2]
    proposal = propose_lead_regions(w, h)
    assert proposal.layout_id == "grid_3x4_standard"
    assert len(proposal.regions) == 12
    assert [r.lead_id for r in proposal.regions[:4]] == ["I", "aVR", "V1", "V4"]


def test_extract_lead_ii_from_clean_page(clean_page: np.ndarray) -> None:
    h, w = clean_page.shape[:2]
    proposal = propose_lead_regions(w, h)
    lead_ii = next(r for r in proposal.regions if r.lead_id == "II")
    result = extract_lead_trace(clean_page, lead_ii, include_debug=True)
    assert result.status == TraceStatus.extracted
    assert len(result.samples) > 40
    assert result.source_crop_base64
    assert result.debug_overlay_base64
    assert result.failure_reason is None


def test_extract_fails_on_blank_region(clean_page: np.ndarray) -> None:
    blank = clean_page.copy()
    h, w = blank.shape[:2]
    proposal = propose_lead_regions(w, h)
    lead_ii = next(r for r in proposal.regions if r.lead_id == "II")
    x0 = int(lead_ii.rect.x)
    y0 = int(lead_ii.rect.y)
    x1 = int(lead_ii.rect.x + lead_ii.rect.width)
    y1 = int(lead_ii.rect.y + lead_ii.rect.height)
    blank[y0:y1, x0:x1] = (245, 245, 245)
    result = extract_lead_trace(blank, lead_ii, include_debug=True)
    assert result.status == TraceStatus.failed
    assert result.failure_reason
    assert result.samples == []
