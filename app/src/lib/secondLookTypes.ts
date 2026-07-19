export type CheckStatus = 'pass' | 'warn' | 'fail' | 'not_assessable'

export interface QualityCheck {
  id: string
  label: string
  status: CheckStatus
  detail: string
  guidance: string | null
}

export interface QualityReport {
  width_px: number
  height_px: number
  overall_status: CheckStatus
  checks: QualityCheck[]
  may_contain_identifier_text: boolean
  identifier_warning: string | null
  analysis_allowed: boolean
  refusal_reason: string | null
}

export interface Point {
  x: number
  y: number
}

export interface CornerSet {
  top_left: Point
  top_right: Point
  bottom_right: Point
  bottom_left: Point
}

export type DetectionStatus = 'detected' | 'fallback_full_frame' | 'not_assessable'

export interface PageDetectionResult {
  status: DetectionStatus
  corners: CornerSet
  page_area_fraction: number | null
  detail: string
}

export interface RectifyResponse {
  corrected_image_base64: string
  media_type: string
  output_width: number
  output_height: number
  used_corners: CornerSet
  note: string
}

export interface Rect {
  x: number
  y: number
  width: number
  height: number
}

export interface LeadRegion {
  lead_id: string
  rect: Rect
  row: number
  col: number
}

export interface LayoutProposal {
  layout_id: string
  layout_version: string
  image_width: number
  image_height: number
  regions: LeadRegion[]
  assumptions: string[]
}

export type TraceStatus = 'extracted' | 'failed'

export interface TraceSample {
  x: number
  y: number
}

export interface TraceExtractionResult {
  status: TraceStatus
  lead_id: string
  region: LeadRegion
  samples: TraceSample[]
  ink_fraction: number
  gap_count: number
  quality_status: CheckStatus
  failure_reason: string | null
  method: string
  source_crop_base64: string | null
  debug_overlay_base64: string | null
  note: string
}

export const SAMPLE_FILES = [
  { id: 'clean_page', label: 'Clean page (layout)', path: '/samples/synthetic/clean_12lead.png' },
  { id: 'photo_skewed', label: 'Skewed photo', path: '/samples/synthetic/photo_skewed.png' },
  { id: 'photo_flat', label: 'Flat photo', path: '/samples/synthetic/photo_flat.png' },
  { id: 'photo_blurry', label: 'Blurry (should refuse)', path: '/samples/synthetic/photo_blurry.png' },
  { id: 'photo_tiny', label: 'Too small (should refuse)', path: '/samples/synthetic/photo_tiny.png' },
] as const
