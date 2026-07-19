import { useMemo } from 'react'
import type { TraceExtractionResult } from '../lib/secondLookTypes'
import styles from './TraceComparison.module.css'

interface TraceComparisonProps {
  result: TraceExtractionResult
  showDebug: boolean
  onToggleDebug: (value: boolean) => void
}

export function TraceComparison({ result, showDebug, onToggleDebug }: TraceComparisonProps) {
  const sourceUrl = useMemo(() => {
    if (!result.source_crop_base64) return null
    return `data:image/png;base64,${result.source_crop_base64}`
  }, [result.source_crop_base64])

  const debugUrl = useMemo(() => {
    if (!result.debug_overlay_base64) return null
    return `data:image/png;base64,${result.debug_overlay_base64}`
  }, [result.debug_overlay_base64])

  const polyline = useMemo(() => {
    if (!result.samples.length) return ''
    const width = 320
    const height = 120
    return result.samples
      .map((sample) => {
        const x = sample.x * (width - 1)
        const y = Math.min(height - 1, Math.max(0, sample.y))
        // Samples are in ROI pixel y; scale roughly into the plot height.
        const maxY = Math.max(...result.samples.map((item) => item.y), 1)
        const scaledY = (y / maxY) * (height - 8) + 4
        return `${x.toFixed(1)},${scaledY.toFixed(1)}`
      })
      .join(' ')
  }, [result.samples])

  return (
    <section className={styles.section} aria-labelledby="trace-heading">
      <h2 id="trace-heading" className={styles.title}>
        Trace extraction · lead {result.lead_id}
      </h2>

      <p className={result.status === 'failed' ? styles.fail : styles.ok} role="status">
        Status: <strong>{result.status}</strong>
        {result.failure_reason ? `. ${result.failure_reason}` : null}
      </p>

      <p className={styles.meta}>
        Method {result.method}. Ink {result.ink_fraction.toFixed(4)}. Gaps {result.gap_count}.
        Quality {result.quality_status}.
      </p>
      <p className={styles.note}>{result.note}</p>

      <label className={styles.debugToggle}>
        <input
          type="checkbox"
          checked={showDebug}
          onChange={(event) => onToggleDebug(event.target.checked)}
        />
        Show debug overlay
      </label>

      <div className={styles.grid}>
        <figure className={styles.figure}>
          <figcaption>Source crop</figcaption>
          {sourceUrl ? (
            <img src={sourceUrl} alt={`Source crop for lead ${result.lead_id}`} />
          ) : (
            <p>No crop available.</p>
          )}
        </figure>

        <figure className={styles.figure}>
          <figcaption>Extracted centerline</figcaption>
          {result.samples.length > 0 ? (
            <svg viewBox="0 0 320 120" className={styles.plot} aria-hidden="true">
              <rect x="0" y="0" width="320" height="120" className={styles.plotBg} />
              <polyline points={polyline} className={styles.plotLine} fill="none" />
            </svg>
          ) : (
            <p className={styles.empty}>No samples extracted.</p>
          )}
        </figure>

        {showDebug ? (
          <figure className={styles.figureWide}>
            <figcaption>Debug overlay (ink mask + centerline)</figcaption>
            {debugUrl ? (
              <img src={debugUrl} alt={`Debug overlay for lead ${result.lead_id}`} />
            ) : (
              <p>No debug overlay.</p>
            )}
          </figure>
        ) : null}
      </div>
    </section>
  )
}
