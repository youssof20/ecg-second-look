import type { PatternRuleResult } from '../lib/secondLookTypes'
import styles from './PatternFlagsPanel.module.css'

interface PatternFlagsPanelProps {
  flags: PatternRuleResult[]
}

export function PatternFlagsPanel({ flags }: PatternFlagsPanelProps) {
  return (
    <section className={styles.section} aria-labelledby="flags-heading">
      <h2 id="flags-heading" className={styles.title}>
        Prototype pattern flags
      </h2>
      <p className={styles.banner}>
        These are prototype pattern flags, not diagnoses. A missing flag is not
        reassurance.
      </p>
      <ul className={styles.list}>
        {flags.map((flag) => (
          <li
            key={flag.id}
            className={
              flag.status === 'triggered'
                ? `${styles.item} ${styles.itemTriggered}`
                : styles.item
            }
          >
            <div className={styles.row}>
              <strong>{flag.display_name}</strong>
              <span className={styles[`status_${flag.status}`]}>{flag.status}</span>
            </div>
            <p className={styles.purpose}>{flag.purpose}</p>
            <p className={styles.explanation}>{flag.explanation}</p>
            <p className={styles.meta}>
              Leads: {flag.affected_leads.join(', ') || 'none'}. Thresholds:{' '}
              {flag.threshold_summary}. Features: {flag.evidence_features.join(', ')}.
            </p>
            <ul className={styles.limits}>
              {flag.limitations.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
            <p className={styles.source}>{flag.source_note}</p>
          </li>
        ))}
      </ul>
    </section>
  )
}
