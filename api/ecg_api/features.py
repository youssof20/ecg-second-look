"""Limited feature measurements from extracted lead centerlines.

Physical units use explicit calibration. When calibration is assumed rather than
confirmed, quality status is capped at warn / not_assessable as documented.
"""

from __future__ import annotations

import numpy as np
from scipy.signal import find_peaks

from ecg_api.schemas import (
    Calibration,
    CheckStatus,
    FeatureMeasurement,
    FeatureSet,
    TraceExtractionResult,
    TraceStatus,
)

# Assumed strip duration for one lead cell when deriving px/mm from ROI width.
ASSUMED_STRIP_SECONDS = 2.5
# Assumed vertical span (mm) of the lead ROI for crude voltage scaling.
ASSUMED_ROI_HEIGHT_MM = 15.0


def default_calibration() -> Calibration:
    return Calibration(
        paper_speed_mm_s=25.0,
        voltage_gain_mm_mv=10.0,
        source="assumed_defaults",
        note=(
            "FOR EDUCATIONAL PROTOTYPE USE ONLY - REQUIRES CLINICAL REVIEW AND VALIDATION. "
            "Defaults are 25 mm/s and 10 mm/mV with ROI-based px/mm estimates."
        ),
    )


def measure_features_from_traces(
    traces: list[TraceExtractionResult],
    calibration: Calibration | None = None,
) -> FeatureSet:
    cal = calibration or default_calibration()
    features: list[FeatureMeasurement] = []

    usable = [t for t in traces if t.status == TraceStatus.extracted and len(t.samples) >= 20]
    if not usable:
        return FeatureSet(
            calibration=cal,
            features=[
                FeatureMeasurement(
                    id="heart_rate",
                    display_name="Heart rate",
                    value=None,
                    units="bpm",
                    source_leads=[],
                    method="rr_intervals_v1",
                    quality_status=CheckStatus.not_assessable,
                    failure_reason="No usable extracted traces.",
                    evidence="No lead centerlines met the extraction quality gate.",
                    next_action="Adjust lead regions or retake the photo, then extract again.",
                )
            ],
            summary=(
                "What was observed: no usable traces. "
                "Where: none. "
                "How reliable: not assessable. "
                "What to do: fix extraction before interpreting measurements."
            ),
        )

    # Prefer lead II for rhythm timing when available.
    rhythm_trace = next((t for t in usable if t.lead_id == "II"), usable[0])
    features.extend(_measure_rhythm(rhythm_trace, cal))
    features.extend(_measure_morphology(rhythm_trace, cal))

    # Contiguous ST screen across inferior leads when present.
    st_leads = [t for t in usable if t.lead_id in {"II", "III", "aVF"}]
    if st_leads:
        features.append(_measure_st_group(st_leads, cal))

    return FeatureSet(
        calibration=cal,
        features=features,
        summary=_summarize(features, cal),
    )


def _px_scales(trace: TraceExtractionResult, cal: Calibration) -> tuple[float, float]:
    """Return (px_per_mm_time, px_per_mm_volt) from ROI size and assumed strip geometry."""
    width = max(trace.region.rect.width, 1.0)
    height = max(trace.region.rect.height, 1.0)
    strip_mm = cal.paper_speed_mm_s * ASSUMED_STRIP_SECONDS
    px_per_mm_time = width / strip_mm
    px_per_mm_volt = height / ASSUMED_ROI_HEIGHT_MM
    return px_per_mm_time, px_per_mm_volt


def _signal_from_trace(trace: TraceExtractionResult) -> tuple[np.ndarray, np.ndarray]:
    xs = np.array([s.x for s in trace.samples], dtype=np.float64)
    ys = np.array([s.y for s in trace.samples], dtype=np.float64)
    # Image y grows downward; invert so upright QRS becomes positive peaks.
    baseline = float(np.median(ys))
    signal = -(ys - baseline)
    return xs, signal


def _measure_rhythm(trace: TraceExtractionResult, cal: Calibration) -> list[FeatureMeasurement]:
    xs, signal = _signal_from_trace(trace)
    px_t, _ = _px_scales(trace, cal)
    # Sample index spacing in mm: x is normalized 0..1 across ROI width.
    width_px = trace.region.rect.width
    if len(signal) < 30:
        return [
            FeatureMeasurement(
                id="heart_rate",
                display_name="Heart rate",
                value=None,
                units="bpm",
                source_leads=[trace.lead_id],
                method="rr_intervals_v1",
                quality_status=CheckStatus.not_assessable,
                failure_reason="Trace too short for peak detection.",
                evidence=f"Lead {trace.lead_id} had fewer than 30 samples.",
                next_action="Widen the lead box or use a longer strip segment.",
            )
        ]

    prominence = max(2.0, 0.35 * float(np.max(signal) - np.min(signal)))
    distance = max(5, len(signal) // 12)
    peaks, _ = find_peaks(signal, prominence=prominence, distance=distance)

    cal_cap = (
        CheckStatus.warn
        if cal.source == "assumed_defaults"
        else CheckStatus.pass_
    )

    if len(peaks) < 2:
        return [
            FeatureMeasurement(
                id="heart_rate",
                display_name="Heart rate",
                value=None,
                units="bpm",
                source_leads=[trace.lead_id],
                method="rr_intervals_v1",
                quality_status=CheckStatus.not_assessable,
                failure_reason="Fewer than two QRS peaks detected.",
                evidence=(
                    f"The prototype measured {len(peaks)} candidate peak(s) in lead "
                    f"{trace.lead_id}."
                ),
                next_action="Review the highlighted trace; HR needs at least two QRS complexes.",
            ),
            FeatureMeasurement(
                id="rr_variability",
                display_name="R–R variability",
                value=None,
                units="ms",
                source_leads=[trace.lead_id],
                method="rr_std_v1",
                quality_status=CheckStatus.not_assessable,
                failure_reason="Fewer than two QRS peaks detected.",
                evidence=f"Insufficient peaks in lead {trace.lead_id}.",
                next_action="Do not infer regularity from this capture.",
            ),
        ]

    # Convert peak index differences to time using normalized x positions.
    peak_x = xs[peaks]
    dx = np.diff(peak_x) * width_px
    rr_mm = dx / px_t
    rr_s = rr_mm / cal.paper_speed_mm_s
    rr_ms = rr_s * 1000.0
    hr = 60.0 / float(np.mean(rr_s))

    quality = cal_cap
    if trace.quality_status == CheckStatus.warn:
        quality = CheckStatus.warn
    if cal.source == "assumed_defaults":
        failure = None
        note_next = (
            "Confirm paper speed (25 or 50 mm/s) before using this rate clinically. "
            "Review the lead II trace in context."
        )
    else:
        failure = None
        note_next = "Review the measured intervals on the source ECG."

    return [
        FeatureMeasurement(
            id="heart_rate",
            display_name="Heart rate",
            value=round(hr, 1),
            units="bpm",
            source_leads=[trace.lead_id],
            method="rr_intervals_v1",
            quality_status=quality,
            failure_reason=failure,
            evidence=(
                f"The prototype measured mean R–R {float(np.mean(rr_ms)):.0f} ms "
                f"from {len(peaks)} peaks in lead {trace.lead_id} "
                f"(calibration: {cal.source})."
            ),
            next_action=note_next,
        ),
        FeatureMeasurement(
            id="rr_variability",
            display_name="R–R variability",
            value=round(float(np.std(rr_ms)), 1),
            units="ms",
            source_leads=[trace.lead_id],
            method="rr_std_v1",
            quality_status=quality,
            failure_reason=None,
            evidence=(
                f"Std-dev of R–R intervals in lead {trace.lead_id} was "
                f"{float(np.std(rr_ms)):.1f} ms across {len(rr_ms)} interval(s)."
            ),
            next_action="Interpret regularity only after inspecting the original tracing.",
        ),
    ]


def _measure_morphology(trace: TraceExtractionResult, cal: Calibration) -> list[FeatureMeasurement]:
    xs, signal = _signal_from_trace(trace)
    px_t, px_v = _px_scales(trace, cal)
    width_px = trace.region.rect.width
    cal_cap = CheckStatus.warn if cal.source == "assumed_defaults" else CheckStatus.pass_

    prominence = max(2.0, 0.35 * float(np.max(signal) - np.min(signal)))
    peaks, _ = find_peaks(signal, prominence=prominence, distance=max(5, len(signal) // 12))
    if len(peaks) == 0:
        return [
            FeatureMeasurement(
                id="qrs_duration",
                display_name="QRS duration",
                value=None,
                units="ms",
                source_leads=[trace.lead_id],
                method="peak_width_v1",
                quality_status=CheckStatus.not_assessable,
                failure_reason="No QRS peak detected.",
                evidence=f"Lead {trace.lead_id} had no peak above prominence threshold.",
                next_action="Adjust the lead box and re-extract before estimating QRS width.",
            )
        ]

    peak = int(peaks[len(peaks) // 2])
    half = max(prominence * 0.2, 1.0)
    left = peak
    while left > 0 and signal[left] > half:
        left -= 1
    right = peak
    while right < len(signal) - 1 and signal[right] > half:
        right += 1

    width_norm = xs[right] - xs[left]
    width_px_span = width_norm * width_px
    width_mm = width_px_span / px_t
    width_ms = (width_mm / cal.paper_speed_mm_s) * 1000.0

    # J point approx at right edge of QRS; ST sample a short fixed delay later.
    j = right
    st_offset = max(2, int(0.04 * len(signal)))  # ~crude 40–80 ms region in index space
    st_idx = min(len(signal) - 1, j + st_offset)
    st_amp_px = float(signal[st_idx])
    st_mm = st_amp_px / px_v
    st_mv = st_mm / cal.voltage_gain_mm_mv

    # T-wave: max abs in a window after ST.
    t_start = st_idx
    t_end = min(len(signal), st_idx + max(8, len(signal) // 5))
    if t_end - t_start >= 3:
        window = signal[t_start:t_end]
        t_local = int(np.argmax(np.abs(window)))
        t_amp_px = float(window[t_local])
        t_mv = (t_amp_px / px_v) / cal.voltage_gain_mm_mv
        t_orient = "upright" if t_amp_px >= 0 else "inverted"
        t_feature = FeatureMeasurement(
            id="t_wave",
            display_name="T-wave amplitude",
            value=round(t_mv, 3),
            units="mV",
            source_leads=[trace.lead_id],
            method="post_st_extremum_v1",
            quality_status=cal_cap,
            failure_reason=None,
            evidence=(
                f"The prototype measured a {t_orient} T-wave extremum of {t_mv:.3f} mV "
                f"in lead {trace.lead_id} (calibration: {cal.source})."
            ),
            next_action="Compare the marked morphology with the original ECG paper.",
        )
    else:
        t_feature = FeatureMeasurement(
            id="t_wave",
            display_name="T-wave amplitude",
            value=None,
            units="mV",
            source_leads=[trace.lead_id],
            method="post_st_extremum_v1",
            quality_status=CheckStatus.not_assessable,
            failure_reason="Insufficient samples after the QRS for a T-wave window.",
            evidence=f"Lead {trace.lead_id} trace ended too soon after the QRS.",
            next_action="Use a wider lead region if the T wave is cut off.",
        )

    return [
        FeatureMeasurement(
            id="qrs_duration",
            display_name="QRS duration",
            value=round(width_ms, 1),
            units="ms",
            source_leads=[trace.lead_id],
            method="peak_width_v1",
            quality_status=cal_cap,
            failure_reason=None,
            evidence=(
                f"The prototype measured approximate QRS width {width_ms:.1f} ms "
                f"in lead {trace.lead_id} using half-prominence bounds."
            ),
            next_action="Treat this as a coarse width estimate; confirm on the paper grid.",
        ),
        FeatureMeasurement(
            id="st_deviation",
            display_name="ST deviation",
            value=round(st_mv, 3),
            units="mV",
            source_leads=[trace.lead_id],
            method="j_plus_offset_v1",
            quality_status=cal_cap,
            failure_reason=None,
            evidence=(
                f"The prototype measured ST amplitude {st_mv:.3f} mV in lead "
                f"{trace.lead_id} shortly after the estimated J point."
            ),
            next_action="Review the ST segment on the original ECG before any triage decision.",
        ),
        t_feature,
    ]


def _measure_st_group(
    traces: list[TraceExtractionResult],
    cal: Calibration,
) -> FeatureMeasurement:
    values: list[tuple[str, float]] = []
    for trace in traces:
        morph = _measure_morphology(trace, cal)
        st = next((f for f in morph if f.id == "st_deviation"), None)
        if st and st.value is not None:
            values.append((trace.lead_id, float(st.value)))

    if not values:
        return FeatureMeasurement(
            id="st_deviation_inferior_group",
            display_name="ST deviation (II/III/aVF)",
            value=None,
            units="mV",
            source_leads=[t.lead_id for t in traces],
            method="j_plus_offset_v1",
            quality_status=CheckStatus.not_assessable,
            failure_reason="ST could not be measured in the inferior leads.",
            evidence="No ST values were available from leads II, III, or aVF.",
            next_action="Inspect those lead boxes and re-extract before assessing ST.",
        )

    mean_st = float(np.mean([v for _, v in values]))
    leads = [lead for lead, _ in values]
    return FeatureMeasurement(
        id="st_deviation_inferior_group",
        display_name="ST deviation (II/III/aVF)",
        value=round(mean_st, 3),
        units="mV",
        source_leads=leads,
        method="j_plus_offset_v1",
        quality_status=CheckStatus.warn if cal.source == "assumed_defaults" else CheckStatus.pass_,
        failure_reason=None,
        evidence=(
            "The prototype measured ST values "
            + ", ".join(f"{lead}={val:.3f} mV" for lead, val in values)
            + f" (mean {mean_st:.3f} mV)."
        ),
        next_action=(
            "Review the highlighted inferior leads on the original ECG and seek senior "
            "clinical review when an acute coronary syndrome is suspected."
        ),
    )


def _summarize(features: list[FeatureMeasurement], cal: Calibration) -> str:
    observed = []
    for feature in features:
        if feature.value is None:
            observed.append(f"{feature.display_name}: unable to assess")
        else:
            observed.append(f"{feature.display_name}: {feature.value} {feature.units}")
    leads = sorted({lead for f in features for lead in f.source_leads})
    reliabilities = sorted({f.quality_status.value for f in features})
    return (
        f"What was observed: {'; '.join(observed)}. "
        f"Where: leads {', '.join(leads) if leads else 'none'}. "
        f"How reliable: {', '.join(reliabilities)} "
        f"(calibration {cal.source}). "
        "What to do: inspect the source ECG and treat these as prototype measurements only."
    )
