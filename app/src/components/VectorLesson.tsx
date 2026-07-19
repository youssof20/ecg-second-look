import { useMemo, useState } from 'react'
import { FrontalPlaneDiagram } from './FrontalPlaneDiagram'
import { LeadWaveformStrip } from './LeadWaveformStrip'
import { PrecordialView } from './PrecordialView'
import {
  explainPolarity,
  projectFrontalLeads,
  projectPrecordialLeads,
  type CardiacVector,
} from '../lib/projection'
import type { LeadId } from '../lib/leads'
import styles from './VectorLesson.module.css'

const DEFAULT_VECTOR: CardiacVector = {
  angleDeg: 60,
  magnitude: 0.85,
}

export function VectorLesson() {
  const [vector, setVector] = useState<CardiacVector>(DEFAULT_VECTOR)
  const [selectedLeadId, setSelectedLeadId] = useState<LeadId>('II')

  const frontal = useMemo(() => projectFrontalLeads(vector), [vector])
  const precordial = useMemo(() => projectPrecordialLeads(vector), [vector])

  const selected =
    frontal.find((item) => item.lead.id === selectedLeadId) ??
    precordial.find((item) => item.lead.id === selectedLeadId) ??
    frontal[1]!

  function setAngle(angleDeg: number) {
    setVector((current) => ({ ...current, angleDeg }))
  }

  function setMagnitude(magnitude: number) {
    setVector((current) => ({ ...current, magnitude }))
  }

  return (
    <div className={styles.lesson}>
      <header className={styles.header}>
        <h2 className={styles.title}>Mean QRS vector on the limb leads</h2>
        <p className={styles.objective}>
          Learning objective: see how one frontal-plane vector becomes a positive,
          negative, or isoelectric deflection in each limb lead.
        </p>
      </header>

      <div className={styles.layout}>
        <section className={styles.controls} aria-labelledby="vector-controls">
          <h3 id="vector-controls" className={styles.sectionTitle}>
            Cardiac vector
          </h3>
          <FrontalPlaneDiagram vector={vector} onAngleChange={setAngle} />

          <label className={styles.sliderLabel} htmlFor="vector-angle">
            Angle: <strong>{vector.angleDeg}&deg;</strong>
          </label>
          <input
            id="vector-angle"
            className={styles.slider}
            type="range"
            min={-180}
            max={180}
            step={1}
            value={vector.angleDeg}
            onChange={(event) => setAngle(Number(event.target.value))}
          />

          <label className={styles.sliderLabel} htmlFor="vector-magnitude">
            Magnitude: <strong>{vector.magnitude.toFixed(2)}</strong>
          </label>
          <input
            id="vector-magnitude"
            className={styles.slider}
            type="range"
            min={0.15}
            max={1}
            step={0.01}
            value={vector.magnitude}
            onChange={(event) => setMagnitude(Number(event.target.value))}
          />

          <aside className={styles.assumptions}>
            <h4 className={styles.asideTitle}>Model assumptions</h4>
            <ul>
              <li>Single mean QRS vector in the frontal plane.</li>
              <li>Lead axes fixed at standard hexaxial angles.</li>
              <li>Waveforms are schematic, not measured ECG samples.</li>
              <li>No torso volume conductor or lead-placement error.</li>
            </ul>
          </aside>
        </section>

        <section className={styles.leads} aria-labelledby="limb-leads">
          <h3 id="limb-leads" className={styles.sectionTitle}>
            Limb-lead projections
          </h3>
          <p className={styles.hint}>
            Select a lead to read why its polarity changed.
          </p>
          <LeadWaveformStrip
            projections={frontal}
            selectedLeadId={selected.lead.id}
            onSelectLead={(id) => setSelectedLeadId(id as LeadId)}
          />

          <div className={styles.explanation} role="status" aria-live="polite">
            <h4 className={styles.asideTitle}>Why this lead looks that way</h4>
            <p>{explainPolarity(selected)}</p>
          </div>

          <PrecordialView projections={precordial} />
        </section>
      </div>
    </div>
  )
}
