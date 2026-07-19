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

export const SAMPLE_FILES = [
  { id: 'photo_skewed', label: 'Skewed photo', path: '/samples/synthetic/photo_skewed.png' },
  { id: 'photo_flat', label: 'Flat photo', path: '/samples/synthetic/photo_flat.png' },
  { id: 'photo_blurry', label: 'Blurry (should refuse)', path: '/samples/synthetic/photo_blurry.png' },
  { id: 'photo_tiny', label: 'Too small (should refuse)', path: '/samples/synthetic/photo_tiny.png' },
] as const
