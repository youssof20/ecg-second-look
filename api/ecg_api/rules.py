"""Inspectable prototype pattern rules. Not a diagnostic engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from ecg_api.explanations import format_rule_explanation
from ecg_api.rule_config import RULE_CONFIG_VERSION, RULE_THRESHOLDS
from ecg_api.schemas import (
    CheckStatus,
    FeatureMeasurement,
    FeatureSet,
    PatternRuleResult,
    RuleStatus,
)


def _feature_map(features: FeatureSet) -> dict[str, FeatureMeasurement]:
    return {item.id: item for item in features.features}


def _usable(feature: FeatureMeasurement | None) -> bool:
    return (
        feature is not None
        and feature.value is not None
        and feature.quality_status
        in {CheckStatus.pass_, CheckStatus.warn}
    )


@dataclass(frozen=True)
class PatternRule:
    id: str
    display_name: str
    purpose: str
    required_features: tuple[str, ...]
    status: str
    limitations: tuple[str, ...]
    source_note: str
    version: str
    evaluate: Callable[[FeatureSet, dict[str, Any]], PatternRuleResult]


def _base_result(
    rule: PatternRule,
    *,
    status: RuleStatus,
    reason: str,
    affected_leads: list[str],
    evidence_features: list[str],
    threshold_summary: str,
) -> PatternRuleResult:
    draft = PatternRuleResult(
        id=rule.id,
        display_name=rule.display_name,
        status=status,
        purpose=rule.purpose,
        reason=reason,
        affected_leads=affected_leads,
        evidence_features=evidence_features,
        threshold_summary=threshold_summary,
        limitations=list(rule.limitations),
        source_note=rule.source_note,
        version=rule.version,
        explanation="",
    )
    return draft.model_copy(update={"explanation": format_rule_explanation(draft)})


def _not_assessable(rule: PatternRule, reason: str, cfg: dict[str, Any]) -> PatternRuleResult:
    return _base_result(
        rule,
        status=RuleStatus.not_assessable,
        reason=reason,
        affected_leads=list(cfg.get("affected_leads", [])),
        evidence_features=list(rule.required_features),
        threshold_summary="required measurements unavailable or unreliable",
    )


def _eval_st_elevation(features: FeatureSet, cfg: dict[str, Any]) -> PatternRuleResult:
    rule = RULES_BY_ID["possible_contiguous_st_elevation"]
    fmap = _feature_map(features)
    st = fmap.get("st_deviation_inferior_group")
    if not _usable(st):
        return _not_assessable(
            rule,
            st.failure_reason if st and st.failure_reason else "inferior ST was not assessable",
            cfg,
        )
    assert st is not None and st.value is not None
    threshold = float(cfg["st_threshold_mv"])
    leads = st.source_leads
    if len(leads) < int(cfg["min_leads"]):
        return _not_assessable(
            rule,
            f"only {len(leads)} inferior lead(s) had usable ST values",
            cfg,
        )
    if st.value >= threshold:
        return _base_result(
            rule,
            status=RuleStatus.triggered,
            reason=(
                f"ST deviation above the prototype threshold ({threshold} mV) was measured "
                f"in leads {', '.join(leads)} (mean {st.value:.3f} mV)."
            ),
            affected_leads=leads,
            evidence_features=["st_deviation_inferior_group"],
            threshold_summary=f"st_threshold_mv={threshold}",
        )
    return _base_result(
        rule,
        status=RuleStatus.not_triggered,
        reason=(
            f"Mean inferior ST {st.value:.3f} mV did not meet the prototype threshold "
            f"of {threshold} mV."
        ),
        affected_leads=leads,
        evidence_features=["st_deviation_inferior_group"],
        threshold_summary=f"st_threshold_mv={threshold}",
    )


def _eval_hyperkalemia(features: FeatureSet, cfg: dict[str, Any]) -> PatternRuleResult:
    rule = RULES_BY_ID["possible_severe_hyperkalemia_morphology"]
    fmap = _feature_map(features)
    qrs = fmap.get("qrs_duration")
    t_wave = fmap.get("t_wave")
    if not _usable(qrs) or not _usable(t_wave):
        return _not_assessable(
            rule,
            "QRS duration and/or T-wave amplitude could not be assessed reliably",
            cfg,
        )
    assert qrs is not None and qrs.value is not None
    assert t_wave is not None and t_wave.value is not None
    qrs_thr = float(cfg["qrs_threshold_ms"])
    t_thr = float(cfg["t_amplitude_threshold_mv"])
    leads = sorted(set(qrs.source_leads + t_wave.source_leads))
    if qrs.value >= qrs_thr and t_wave.value >= t_thr:
        return _base_result(
            rule,
            status=RuleStatus.triggered,
            reason=(
                f"QRS width {qrs.value:.1f} ms and T amplitude {t_wave.value:.3f} mV "
                f"met prototype thresholds ({qrs_thr} ms, {t_thr} mV)."
            ),
            affected_leads=leads,
            evidence_features=["qrs_duration", "t_wave"],
            threshold_summary=f"qrs_threshold_ms={qrs_thr}; t_amplitude_threshold_mv={t_thr}",
        )
    return _base_result(
        rule,
        status=RuleStatus.not_triggered,
        reason=(
            f"QRS {qrs.value:.1f} ms and T {t_wave.value:.3f} mV did not jointly meet "
            f"prototype thresholds."
        ),
        affected_leads=leads,
        evidence_features=["qrs_duration", "t_wave"],
        threshold_summary=f"qrs_threshold_ms={qrs_thr}; t_amplitude_threshold_mv={t_thr}",
    )


def _eval_broad_complex_tachycardia(features: FeatureSet, cfg: dict[str, Any]) -> PatternRuleResult:
    rule = RULES_BY_ID["possible_regular_broad_complex_tachycardia"]
    fmap = _feature_map(features)
    hr = fmap.get("heart_rate")
    qrs = fmap.get("qrs_duration")
    rr = fmap.get("rr_variability")
    if not _usable(hr) or not _usable(qrs) or not _usable(rr):
        return _not_assessable(
            rule,
            "heart rate, QRS duration, and/or RR variability were not assessable",
            cfg,
        )
    assert hr is not None and hr.value is not None
    assert qrs is not None and qrs.value is not None
    assert rr is not None and rr.value is not None
    hr_thr = float(cfg["hr_threshold_bpm"])
    qrs_thr = float(cfg["qrs_threshold_ms"])
    rr_max = float(cfg["rr_std_max_ms"])
    leads = sorted(set(hr.source_leads + qrs.source_leads + rr.source_leads))
    if hr.value >= hr_thr and qrs.value >= qrs_thr and rr.value <= rr_max:
        return _base_result(
            rule,
            status=RuleStatus.triggered,
            reason=(
                f"Rate {hr.value:.1f} bpm, QRS {qrs.value:.1f} ms, and RR std {rr.value:.1f} ms "
                "met the prototype regular broad-complex pattern thresholds."
            ),
            affected_leads=leads,
            evidence_features=["heart_rate", "qrs_duration", "rr_variability"],
            threshold_summary=(
                f"hr_threshold_bpm={hr_thr}; qrs_threshold_ms={qrs_thr}; "
                f"rr_std_max_ms={rr_max}"
            ),
        )
    return _base_result(
        rule,
        status=RuleStatus.not_triggered,
        reason="Measured rate/QRS/RR values did not meet the prototype pattern thresholds.",
        affected_leads=leads,
        evidence_features=["heart_rate", "qrs_duration", "rr_variability"],
        threshold_summary=(
            f"hr_threshold_bpm={hr_thr}; qrs_threshold_ms={qrs_thr}; rr_std_max_ms={rr_max}"
        ),
    )


def _eval_bradycardia(features: FeatureSet, cfg: dict[str, Any]) -> PatternRuleResult:
    rule = RULES_BY_ID["possible_marked_bradycardia"]
    fmap = _feature_map(features)
    hr = fmap.get("heart_rate")
    if not _usable(hr):
        return _not_assessable(
            rule,
            hr.failure_reason if hr and hr.failure_reason else "heart rate was not assessable",
            cfg,
        )
    assert hr is not None and hr.value is not None
    thr = float(cfg["hr_threshold_bpm"])
    if hr.value <= thr:
        return _base_result(
            rule,
            status=RuleStatus.triggered,
            reason=f"Measured heart rate {hr.value:.1f} bpm was at or below {thr} bpm.",
            affected_leads=hr.source_leads,
            evidence_features=["heart_rate"],
            threshold_summary=f"hr_threshold_bpm={thr}",
        )
    return _base_result(
        rule,
        status=RuleStatus.not_triggered,
        reason=f"Measured heart rate {hr.value:.1f} bpm was above {thr} bpm.",
        affected_leads=hr.source_leads,
        evidence_features=["heart_rate"],
        threshold_summary=f"hr_threshold_bpm={thr}",
    )


def _eval_irregular_tachy(features: FeatureSet, cfg: dict[str, Any]) -> PatternRuleResult:
    rule = RULES_BY_ID["possible_irregular_tachyarrhythmia"]
    fmap = _feature_map(features)
    hr = fmap.get("heart_rate")
    rr = fmap.get("rr_variability")
    if not _usable(hr) or not _usable(rr):
        return _not_assessable(
            rule,
            "heart rate and/or RR variability were not assessable",
            cfg,
        )
    assert hr is not None and hr.value is not None
    assert rr is not None and rr.value is not None
    hr_thr = float(cfg["hr_threshold_bpm"])
    rr_min = float(cfg["rr_std_min_ms"])
    leads = sorted(set(hr.source_leads + rr.source_leads))
    if hr.value >= hr_thr and rr.value >= rr_min:
        return _base_result(
            rule,
            status=RuleStatus.triggered,
            reason=(
                f"Rate {hr.value:.1f} bpm with RR std {rr.value:.1f} ms met the prototype "
                "irregular tachyarrhythmia thresholds."
            ),
            affected_leads=leads,
            evidence_features=["heart_rate", "rr_variability"],
            threshold_summary=f"hr_threshold_bpm={hr_thr}; rr_std_min_ms={rr_min}",
        )
    return _base_result(
        rule,
        status=RuleStatus.not_triggered,
        reason="Measured rate/RR variability did not meet the prototype pattern thresholds.",
        affected_leads=leads,
        evidence_features=["heart_rate", "rr_variability"],
        threshold_summary=f"hr_threshold_bpm={hr_thr}; rr_std_min_ms={rr_min}",
    )


def _build_rules() -> list[PatternRule]:
    builders: dict[str, Callable[[FeatureSet, dict[str, Any]], PatternRuleResult]] = {
        "possible_contiguous_st_elevation": _eval_st_elevation,
        "possible_severe_hyperkalemia_morphology": _eval_hyperkalemia,
        "possible_regular_broad_complex_tachycardia": _eval_broad_complex_tachycardia,
        "possible_marked_bradycardia": _eval_bradycardia,
        "possible_irregular_tachyarrhythmia": _eval_irregular_tachy,
    }
    rules: list[PatternRule] = []
    for rule_id, cfg in RULE_THRESHOLDS.items():
        rules.append(
            PatternRule(
                id=rule_id,
                display_name=str(cfg["display_name"]),
                purpose=str(cfg["purpose"]),
                required_features=tuple(cfg["required_features"]),
                status=str(cfg["status"]),
                limitations=tuple(cfg["limitations"]),
                source_note=str(cfg["source_note"]),
                version=RULE_CONFIG_VERSION,
                evaluate=builders[rule_id],
            )
        )
    return rules


RULES: list[PatternRule] = _build_rules()
RULES_BY_ID = {rule.id: rule for rule in RULES}


def evaluate_pattern_rules(features: FeatureSet) -> list[PatternRuleResult]:
    results: list[PatternRuleResult] = []
    for rule in RULES:
        cfg = RULE_THRESHOLDS[rule.id]
        results.append(rule.evaluate(features, cfg))
    return results
