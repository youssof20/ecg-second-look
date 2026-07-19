"""Deterministic explanation templates for prototype pattern flags."""

from __future__ import annotations

from ecg_api.schemas import PatternRuleResult, RuleStatus


def format_rule_explanation(result: PatternRuleResult) -> str:
    if result.status == RuleStatus.not_assessable:
        return (
            f"The finding could not be assessed reliably because {result.reason}. "
            f"Review the highlighted leads ({', '.join(result.affected_leads) or 'none'}) "
            "and interpret them in the clinical context. "
            "Obtain urgent senior or specialist review when clinically indicated."
        )
    if result.status == RuleStatus.triggered:
        return (
            f"The prototype measured values that may be compatible with "
            f"'{result.display_name}'. {result.reason} "
            f"Affected leads: {', '.join(result.affected_leads) or 'none'}. "
            "Review the highlighted waveform regions on the original ECG. "
            "This is a prototype pattern flag, not a diagnosis. "
            "Obtain urgent senior or specialist review when clinically indicated."
        )
    return (
        f"The prototype did not trigger '{result.display_name}'. {result.reason} "
        "Absence of a prototype flag is not reassurance and does not exclude disease."
    )
