from __future__ import annotations

from ecg_api.features import default_calibration
from ecg_api.rules import evaluate_pattern_rules
from ecg_api.schemas import (
    CheckStatus,
    FeatureMeasurement,
    FeatureSet,
    RuleStatus,
)


def _feature_set(items: list[FeatureMeasurement]) -> FeatureSet:
    return FeatureSet(
        calibration=default_calibration(),
        features=items,
        summary="test",
    )


def test_st_rule_triggers_on_high_inferior_st() -> None:
    features = _feature_set(
        [
            FeatureMeasurement(
                id="st_deviation_inferior_group",
                display_name="ST deviation (II/III/aVF)",
                value=0.25,
                units="mV",
                source_leads=["II", "III", "aVF"],
                method="test",
                quality_status=CheckStatus.warn,
                evidence="test",
                next_action="test",
            )
        ]
    )
    results = {item.id: item for item in evaluate_pattern_rules(features)}
    assert results["possible_contiguous_st_elevation"].status == RuleStatus.triggered


def test_bradycardia_not_assessable_without_hr() -> None:
    features = _feature_set(
        [
            FeatureMeasurement(
                id="heart_rate",
                display_name="Heart rate",
                value=None,
                units="bpm",
                source_leads=["II"],
                method="test",
                quality_status=CheckStatus.not_assessable,
                failure_reason="Fewer than two QRS peaks detected.",
                evidence="test",
                next_action="test",
            )
        ]
    )
    results = {item.id: item for item in evaluate_pattern_rules(features)}
    assert results["possible_marked_bradycardia"].status == RuleStatus.not_assessable
    assert "could not be assessed reliably" in results["possible_marked_bradycardia"].explanation


def test_irregular_tachy_not_triggered_when_regular() -> None:
    features = _feature_set(
        [
            FeatureMeasurement(
                id="heart_rate",
                display_name="Heart rate",
                value=130,
                units="bpm",
                source_leads=["II"],
                method="test",
                quality_status=CheckStatus.warn,
                evidence="test",
                next_action="test",
            ),
            FeatureMeasurement(
                id="rr_variability",
                display_name="R–R variability",
                value=10,
                units="ms",
                source_leads=["II"],
                method="test",
                quality_status=CheckStatus.warn,
                evidence="test",
                next_action="test",
            ),
        ]
    )
    results = {item.id: item for item in evaluate_pattern_rules(features)}
    assert results["possible_irregular_tachyarrhythmia"].status == RuleStatus.not_triggered
