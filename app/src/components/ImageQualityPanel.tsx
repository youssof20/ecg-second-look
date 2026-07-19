import type { QualityReport } from '../lib/secondLookTypes'
import styles from './ImageQualityPanel.module.css'

interface ImageQualityPanelProps {
  report: QualityReport
}

export function ImageQualityPanel({ report }: ImageQualityPanelProps) {
  return (
    <section className={styles.panel} aria-labelledby="quality-heading">
      <h2 id="quality-heading" className={styles.title}>
        Image quality
      </h2>
      <p className={styles.meta}>
        {report.width_px}×{report.height_px}px · overall{' '}
        <span className={styles[report.overall_status]}>{report.overall_status}</span>
      </p>

      {report.identifier_warning ? (
        <p className={styles.warning} role="status">
          {report.identifier_warning}
        </p>
      ) : null}

      {!report.analysis_allowed && report.refusal_reason ? (
        <p className={styles.refusal} role="alert">
          {report.refusal_reason}
        </p>
      ) : null}

      <ul className={styles.list}>
        {report.checks.map((check) => (
          <li key={check.id} className={styles.item}>
            <div className={styles.row}>
              <strong>{check.label}</strong>
              <span className={styles[check.status]}>{check.status}</span>
            </div>
            <p className={styles.detail}>{check.detail}</p>
            {check.guidance ? <p className={styles.guidance}>{check.guidance}</p> : null}
          </li>
        ))}
      </ul>
    </section>
  )
}
