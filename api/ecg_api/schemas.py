from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class CheckStatus(str, Enum):
    pass_ = "pass"
    warn = "warn"
    fail = "fail"
    not_assessable = "not_assessable"


class QualityCheck(BaseModel):
    id: str
    label: str
    status: CheckStatus
    detail: str
    guidance: str | None = None


class QualityReport(BaseModel):
    width_px: int
    height_px: int
    overall_status: CheckStatus
    checks: list[QualityCheck]
    may_contain_identifier_text: bool
    identifier_warning: str | None = None
    analysis_allowed: bool
    refusal_reason: str | None = None


class Point(BaseModel):
    x: float = Field(ge=0)
    y: float = Field(ge=0)


class CornerSet(BaseModel):
    """Page corners in image coordinates: top-left, top-right, bottom-right, bottom-left."""

    top_left: Point
    top_right: Point
    bottom_right: Point
    bottom_left: Point

    def as_array(self) -> list[list[float]]:
        return [
            [self.top_left.x, self.top_left.y],
            [self.top_right.x, self.top_right.y],
            [self.bottom_right.x, self.bottom_right.y],
            [self.bottom_left.x, self.bottom_left.y],
        ]


class DetectionStatus(str, Enum):
    detected = "detected"
    fallback_full_frame = "fallback_full_frame"
    not_assessable = "not_assessable"


class PageDetectionResult(BaseModel):
    status: DetectionStatus
    corners: CornerSet
    page_area_fraction: float | None = None
    detail: str


class RectifyRequest(BaseModel):
    corners: CornerSet
    output_width: int | None = Field(default=None, ge=200, le=4000)
    output_height: int | None = Field(default=None, ge=200, le=4000)


class RectifyResponse(BaseModel):
    corrected_image_base64: str
    media_type: str = "image/png"
    output_width: int
    output_height: int
    used_corners: CornerSet
    note: str


LeadId = str


class Rect(BaseModel):
    x: float = Field(ge=0)
    y: float = Field(ge=0)
    width: float = Field(gt=0)
    height: float = Field(gt=0)


class LeadRegion(BaseModel):
    lead_id: LeadId
    rect: Rect
    row: int = Field(ge=0, le=2)
    col: int = Field(ge=0, le=3)


class LayoutProposal(BaseModel):
    layout_id: str
    layout_version: str
    image_width: int
    image_height: int
    regions: list[LeadRegion]
    assumptions: list[str]


class TraceStatus(str, Enum):
    extracted = "extracted"
    failed = "failed"


class TraceSample(BaseModel):
    """Normalized sample: x in [0,1] across the ROI, y in image-down pixels within the ROI."""

    x: float
    y: float


class TraceExtractionResult(BaseModel):
    status: TraceStatus
    lead_id: LeadId
    region: LeadRegion
    samples: list[TraceSample]
    ink_fraction: float
    gap_count: int
    quality_status: CheckStatus
    failure_reason: str | None = None
    method: str
    source_crop_base64: str | None = None
    debug_overlay_base64: str | None = None
    note: str


class Calibration(BaseModel):
    paper_speed_mm_s: float = Field(default=25.0, description="25 or 50 typical")
    voltage_gain_mm_mv: float = Field(default=10.0, description="10 or 5 typical")
    source: str = Field(description="assumed_defaults or user_confirmed")
    note: str


class FeatureMeasurement(BaseModel):
    id: str
    display_name: str
    value: float | None
    units: str
    source_leads: list[LeadId]
    method: str
    quality_status: CheckStatus
    failure_reason: str | None = None
    evidence: str
    next_action: str


class FeatureSet(BaseModel):
    calibration: Calibration
    features: list[FeatureMeasurement]
    summary: str


class RuleStatus(str, Enum):
    triggered = "triggered"
    not_triggered = "not_triggered"
    not_assessable = "not_assessable"


class PatternRuleResult(BaseModel):
    id: str
    display_name: str
    status: RuleStatus
    purpose: str
    reason: str
    affected_leads: list[LeadId]
    evidence_features: list[str]
    threshold_summary: str
    limitations: list[str]
    source_note: str
    version: str
    explanation: str


class MultiLeadAnalysis(BaseModel):
    traces: list[TraceExtractionResult]
    features: FeatureSet
    pattern_flags: list[PatternRuleResult] = []
    extracted_count: int
    failed_count: int
    note: str
