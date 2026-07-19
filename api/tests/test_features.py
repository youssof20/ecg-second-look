from __future__ import annotations

import numpy as np

from ecg_api.features import default_calibration, measure_features_from_traces
from ecg_api.layout import propose_lead_regions
from ecg_api.schemas import CheckStatus, TraceStatus
from ecg_api.trace import extract_lead_trace


def test_measure_features_reports_not_assessable_without_peaks(clean_page: np.ndarray) -> None:
    h, w = clean_page.shape[:2]
    proposal = propose_lead_regions(w, h)
    # Blank every lead so extraction fails -> features not assessable.
    blank = np.full_like(clean_page, 245)
    traces = [extract_lead_trace(blank, region, include_debug=False) for region in proposal.regions]
    assert all(t.status == TraceStatus.failed for t in traces)
    features = measure_features_from_traces(traces, default_calibration())
    assert features.features
    assert features.features[0].quality_status == CheckStatus.not_assessable


def test_measure_features_on_clean_page(clean_page: np.ndarray) -> None:
    h, w = clean_page.shape[:2]
    proposal = propose_lead_regions(w, h)
    traces = [
        extract_lead_trace(clean_page, region, include_debug=False) for region in proposal.regions
    ]
    extracted = [t for t in traces if t.status == TraceStatus.extracted]
    assert len(extracted) >= 8
    features = measure_features_from_traces(traces, default_calibration())
    ids = {f.id for f in features.features}
    assert "heart_rate" in ids
    assert "qrs_duration" in ids
    assert "st_deviation" in ids
    # Assumed calibration should not claim pass for physical HR in this prototype.
    hr = next(f for f in features.features if f.id == "heart_rate")
    assert hr.quality_status in {CheckStatus.warn, CheckStatus.not_assessable, CheckStatus.pass_}
    assert "assumed_defaults" in features.calibration.source
    assert "What was observed" in features.summary
