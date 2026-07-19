import { useMemo } from 'react'
import type { LeadProjection } from '../lib/projection'
import { buildTeachingWaveform, waveformToPolyline } from '../lib/waveform'
import styles from './LeadWaveformStrip.module.css'

interface LeadWaveformStripProps {
  projections: LeadProjection[]
  selectedLeadId?: string
  onSelectLead?: (leadId: string) => void
}

const WIDTH = 220
const HEIGHT = 48

export function LeadWaveformStrip({
  projections,
  selectedLeadId,
  onSelectLead,
}: LeadWaveformStripProps) {
  return (
    <ul className={styles.list} aria-label="Lead projections and teaching waveforms">
      {projections.map((item) => (
        <LeadRow
          key={item.lead.id}
          item={item}
          selected={selectedLeadId === item.lead.id}
          onSelect={onSelectLead}
        />
      ))}
    </ul>
  )
}

function LeadRow({
  item,
  selected,
  onSelect,
}: {
  item: LeadProjection
  selected: boolean
  onSelect?: (leadId: string) => void
}) {
  const points = useMemo(() => {
    const samples = buildTeachingWaveform(item.projection)
    return waveformToPolyline(samples, WIDTH, HEIGHT)
  }, [item.projection])

  return (
    <li>
      <button
        type="button"
        className={selected ? `${styles.row} ${styles.rowSelected}` : styles.row}
        aria-pressed={selected}
        aria-label={`Lead ${item.lead.id}, ${item.polarity}, projection ${item.projection.toFixed(2)}`}
        onClick={() => onSelect?.(item.lead.id)}
      >
        <span className={styles.leadId}>{item.lead.id}</span>
        <span className={`${styles.polarity} ${styles[item.polarity]}`}>
          {item.polarity}
        </span>
        <svg
          className={styles.wave}
          viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
          aria-hidden="true"
        >
          <line
            className={styles.baseline}
            x1={0}
            y1={HEIGHT / 2}
            x2={WIDTH}
            y2={HEIGHT / 2}
          />
          <polyline className={styles.trace} points={points} fill="none" />
        </svg>
        <span className={styles.value}>{item.projection.toFixed(2)}</span>
      </button>
    </li>
  )
}
