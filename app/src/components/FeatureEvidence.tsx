import type { FeatureSet } from '../lib/secondLookTypes'
import styles from './FeatureEvidence.module.css'

interface FeatureEvidenceProps {
  features: FeatureSet
  extractedCount: number
  failedCount: number
}

export function FeatureEvidence({
  features,
  extractedCount,
  failedCount,
}: FeatureEvidenceProps) {
  return (
    <section className={styles.section} aria-labelledby="evidence-heading">
      <h2 id="evidence-heading" className={styles.title}>
        Feature evidence
      </h2>
      <p className={styles.summary}>{features.summary}</p>
      <p className={styles.meta}>
        Traces extracted {extractedCount}, failed {failedCount}. Calibration:{' '}
        {features.calibration.source} ({features.calibration.paper_speed_mm_s} mm/s,{' '}
        {features.calibration.voltage_gain_mm_mv} mm/mV).
      </p>
      <p className={styles.calNote}>{features.calibration.note}</p>

      <ul className={styles.list}>
        {features.features.map((feature) => (
          <li key={feature.id} className={styles.item}>
            <div className={styles.row}>
              <strong>{feature.display_name}</strong>
              <span className={styles[feature.quality_status]}>
                {feature.quality_status}
              </span>
            </div>
            <p className={styles.value}>
              {feature.value === null
                ? 'Unable to assess'
                : `${feature.value} ${feature.units}`}
              {' · '}
              leads {feature.source_leads.join(', ') || 'none'}
              {' · '}
              {feature.method}
            </p>
            <p className={styles.evidence}>
              <span className={styles.label}>Observed:</span> {feature.evidence}
            </p>
            {feature.failure_reason ? (
              <p className={styles.failure}>
                <span className={styles.label}>Why unreliable:</span>{' '}
                {feature.failure_reason}
              </p>
            ) : null}
            <p className={styles.next}>
              <span className={styles.label}>Next action:</span> {feature.next_action}
            </p>
          </li>
        ))}
      </ul>
    </section>
  )
}
