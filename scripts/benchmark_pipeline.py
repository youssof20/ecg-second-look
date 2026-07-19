"""Small reproducible synthetic-pipeline benchmark.

Reports stage metrics separately. Synthetic success is not clinical validity.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "api"))

from ecg_api.features import default_calibration, measure_features_from_traces
from ecg_api.layout import propose_lead_regions
from ecg_api.perspective import detect_page_corners
from ecg_api.quality import assess_image_quality
from ecg_api.rules import evaluate_pattern_rules
from ecg_api.schemas import DetectionStatus, TraceStatus
from ecg_api.trace import extract_lead_trace

SAMPLES = ROOT / "samples" / "synthetic"


def _load(name: str):
    path = SAMPLES / name
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(path)
    return image


def main() -> None:
    report: dict = {
        "dataset": "samples/synthetic",
        "sample_size": 0,
        "note": (
            "Synthetic benchmark only. Success here does not establish clinical validity."
        ),
        "stages": {},
    }

    # Quality rejection
    tiny = assess_image_quality(_load("photo_tiny.png"))
    blurry = assess_image_quality(_load("photo_blurry.png"))
    clean = assess_image_quality(_load("clean_12lead.png"))
    report["stages"]["quality_rejection"] = {
        "metric": "hard_refusal_rate_on_known_bad_inputs",
        "tiny_refused": not tiny.analysis_allowed,
        "blurry_refused": not blurry.analysis_allowed,
        "clean_allowed": clean.analysis_allowed,
    }

    # Page detection on skewed photo
    skewed = _load("photo_skewed.png")
    detection = detect_page_corners(skewed)
    report["stages"]["page_detection"] = {
        "metric": "detection_status_on_photo_skewed",
        "status": detection.status.value,
        "detected_or_fallback": detection.status
        in {DetectionStatus.detected, DetectionStatus.fallback_full_frame},
    }

    # Lead regions + waveform reconstruction on clean page
    page = _load("clean_12lead.png")
    h, w = page.shape[:2]
    layout = propose_lead_regions(w, h)
    traces = [extract_lead_trace(page, region, include_debug=False) for region in layout.regions]
    extracted = sum(1 for t in traces if t.status == TraceStatus.extracted)
    report["stages"]["lead_region_detection"] = {
        "metric": "proposed_region_count",
        "regions": len(layout.regions),
        "expected": 12,
    }
    report["stages"]["waveform_reconstruction"] = {
        "metric": "leads_extracted_over_12",
        "extracted": extracted,
        "total": 12,
        "fraction": round(extracted / 12, 3),
    }

    features = measure_features_from_traces(traces, default_calibration())
    hr = next(f for f in features.features if f.id == "heart_rate")
    qrs = next(f for f in features.features if f.id == "qrs_duration")
    st = next(f for f in features.features if f.id == "st_deviation")
    report["stages"]["heart_rate_estimation"] = {
        "metric": "quality_status",
        "status": hr.quality_status.value,
        "value": hr.value,
        "units": hr.units,
    }
    report["stages"]["qrs_duration_estimation"] = {
        "metric": "quality_status",
        "status": qrs.quality_status.value,
        "value": qrs.value,
        "units": qrs.units,
    }
    report["stages"]["st_deviation_estimation"] = {
        "metric": "quality_status",
        "status": st.quality_status.value,
        "value": st.value,
        "units": st.units,
    }

    flags = evaluate_pattern_rules(features)
    report["stages"]["rule_sensitivity_on_synthetic"] = {
        "metric": "status_counts",
        "triggered": sum(1 for f in flags if f.status.value == "triggered"),
        "not_triggered": sum(1 for f in flags if f.status.value == "not_triggered"),
        "not_assessable": sum(1 for f in flags if f.status.value == "not_assessable"),
        "known_limitation": (
            "Single-beat synthetic strips often force rhythm rules to not_assessable."
        ),
    }
    report["stages"]["rejection_of_poor_quality_inputs"] = report["stages"]["quality_rejection"]
    report["sample_size"] = 4
    report["exclusions"] = ["No real clinical ECGs included."]
    report["ground_truth"] = (
        "Fixture labels only (tiny/blurry should refuse; clean page should extract)."
    )

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
