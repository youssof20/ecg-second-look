/**
 * Builds a single-beat teaching QRS path from a signed lead projection.
 * Shape is intentionally schematic (P-ish bump, QRS, T-ish bump), not a
 * physiologic action-potential model.
 */
export function buildTeachingWaveform(
  projection: number,
  sampleCount = 160,
): Float32Array {
  const samples = new Float32Array(sampleCount)
  const qrsPeak = 0.42
  const tPeak = 0.68

  for (let i = 0; i < sampleCount; i += 1) {
    const t = i / (sampleCount - 1)
    let y = 0

    // Small atrial-like bump; keeps polarity with the QRS for visual clarity.
    y += 0.12 * projection * gaussian(t, 0.22, 0.03)

    // QRS: narrow triangular spike scaled by projection.
    y += projection * triangular(t, qrsPeak, 0.035)

    // T-ish wave: broader, same sign as QRS in this simplified model.
    y += 0.35 * projection * gaussian(t, tPeak, 0.055)

    samples[i] = y
  }

  return samples
}

function gaussian(t: number, center: number, width: number): number {
  const z = (t - center) / width
  return Math.exp(-0.5 * z * z)
}

function triangular(t: number, center: number, halfWidth: number): number {
  const d = Math.abs(t - center)
  if (d >= halfWidth) return 0
  return 1 - d / halfWidth
}

/** SVG polyline points for a waveform drawn in a viewBox of width×height. */
export function waveformToPolyline(
  samples: Float32Array,
  width: number,
  height: number,
  /** Vertical scale relative to full magnitude = 1. */
  gain = 0.38,
): string {
  const mid = height / 2
  const points: string[] = []

  for (let i = 0; i < samples.length; i += 1) {
    const x = (i / (samples.length - 1)) * width
    const y = mid - samples[i]! * height * gain
    points.push(`${x.toFixed(2)},${y.toFixed(2)}`)
  }

  return points.join(' ')
}
