import type { LeadProjection } from '../lib/projection'
import { buildTeachingWaveform, waveformToPolyline } from '../lib/waveform'
import styles from './PrecordialView.module.css'

interface PrecordialViewProps {
  projections: LeadProjection[]
}

const WIDTH = 120
const HEIGHT = 40

export function PrecordialView({ projections }: PrecordialViewProps) {
  return (
    <section className={styles.section} aria-labelledby="precordial-heading">
      <h3 id="precordial-heading" className={styles.heading}>
        Precordial leads (simplified)
      </h3>
      <p className={styles.note}>
        Same angle control, mapped onto approximate horizontal-plane axes.
        Placement and torso geometry are not modeled.
      </p>
      <ul className={styles.grid}>
        {projections.map((item) => {
          const points = waveformToPolyline(
            buildTeachingWaveform(item.projection),
            WIDTH,
            HEIGHT,
          )
          return (
            <li key={item.lead.id} className={styles.cell}>
              <div className={styles.meta}>
                <span className={styles.id}>{item.lead.id}</span>
                <span className={`${styles.polarity} ${styles[item.polarity]}`}>
                  {item.polarity}
                </span>
              </div>
              <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} className={styles.wave} aria-hidden="true">
                <line
                  x1={0}
                  y1={HEIGHT / 2}
                  x2={WIDTH}
                  y2={HEIGHT / 2}
                  className={styles.baseline}
                />
                <polyline points={points} className={styles.trace} fill="none" />
              </svg>
            </li>
          )
        })}
      </ul>
    </section>
  )
}
