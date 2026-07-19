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
