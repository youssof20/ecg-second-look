"""Prototype rule thresholds.

FOR EDUCATIONAL PROTOTYPE USE ONLY - REQUIRES CLINICAL REVIEW AND VALIDATION

Values are teaching placeholders for a transparent rules engine.
They are not clinically validated cutoffs and must not be treated as diagnoses.
"""

from __future__ import annotations

from typing import Any

RULE_CONFIG_VERSION = "1"

# Each entry feeds PatternRule construction in rules.py.
RULE_THRESHOLDS: dict[str, dict[str, Any]] = {
    "possible_contiguous_st_elevation": {
        "display_name": "Possible contiguous ST-elevation pattern",
        "purpose": "Flag when ST deviation is high in contiguous inferior leads.",
        "status": "prototype_only",
        "required_features": ["st_deviation_inferior_group"],
        "st_threshold_mv": 0.15,
        "min_leads": 2,
        "affected_leads": ["II", "III", "aVF"],
        "limitations": [
            "Uses crude J+offset ST estimates from photographed traces.",
            "Does not implement AHA/ESC STEMI criteria.",
        ],
        "source_note": "Prototype placeholder only. No clinical citation attached.",
    },
    "possible_severe_hyperkalemia_morphology": {
        "display_name": "Possible severe hyperkalemia-associated morphology",
        "purpose": "Flag very broad QRS with tall upright T morphology cues.",
        "status": "prototype_only",
        "required_features": ["qrs_duration", "t_wave"],
        "qrs_threshold_ms": 160.0,
        "t_amplitude_threshold_mv": 0.6,
        "limitations": [
            "Peaked-T detection is a simple amplitude heuristic.",
            "Many non-hyperkalemia conditions broaden the QRS.",
        ],
        "source_note": "Prototype placeholder only. No clinical citation attached.",
    },
    "possible_regular_broad_complex_tachycardia": {
        "display_name": "Possible regular broad-complex tachycardia",
        "purpose": "Flag fast rate with wide QRS and low RR variability.",
        "status": "prototype_only",
        "required_features": ["heart_rate", "qrs_duration", "rr_variability"],
        "hr_threshold_bpm": 120.0,
        "qrs_threshold_ms": 120.0,
        "rr_std_max_ms": 40.0,
        "limitations": [
            "Cannot distinguish VT from SVT with aberrancy.",
            "Needs reliable multi-beat extraction.",
        ],
        "source_note": "Prototype placeholder only. No clinical citation attached.",
    },
    "possible_marked_bradycardia": {
        "display_name": "Possible marked bradycardia",
        "purpose": "Flag a very low measured heart rate when assessable.",
        "status": "prototype_only",
        "required_features": ["heart_rate"],
        "hr_threshold_bpm": 40.0,
        "limitations": [
            "Single-beat teaching strips often cannot assess rate.",
        ],
        "source_note": "Prototype placeholder only. No clinical citation attached.",
    },
    "possible_irregular_tachyarrhythmia": {
        "display_name": "Possible irregular tachyarrhythmia",
        "purpose": "Flag fast rate with high RR variability.",
        "status": "prototype_only",
        "required_features": ["heart_rate", "rr_variability"],
        "hr_threshold_bpm": 100.0,
        "rr_std_min_ms": 80.0,
        "limitations": [
            "Does not diagnose atrial fibrillation.",
            "Artifact and missed peaks inflate RR variability.",
        ],
        "source_note": "Prototype placeholder only. No clinical citation attached.",
    },
}
