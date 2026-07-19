import type { LeadRegion, LayoutProposal } from '../lib/secondLookTypes'
import styles from './LeadRegionEditor.module.css'

interface LeadRegionEditorProps {
  imageUrl: string
  proposal: LayoutProposal
  regions: LeadRegion[]
  selectedLeadId: string
  onSelectLead: (leadId: string) => void
  onChangeRegion: (region: LeadRegion) => void
}

export function LeadRegionEditor({
  imageUrl,
  proposal,
  regions,
  selectedLeadId,
  onSelectLead,
  onChangeRegion,
}: LeadRegionEditorProps) {
  const selected = regions.find((item) => item.lead_id === selectedLeadId) ?? regions[0]

  function updateSelected(patch: Partial<LeadRegion['rect']>) {
    if (!selected) return
    onChangeRegion({
      ...selected,
      rect: {
        ...selected.rect,
        ...patch,
      },
    })
  }

  return (
    <section className={styles.section} aria-labelledby="leads-heading">
      <h2 id="leads-heading" className={styles.title}>
        Lead regions ({proposal.layout_id})
      </h2>
      <p className={styles.help}>
        One supported layout: 3×4. Select a lead, then nudge its box. Segmentation
        errors stay visible on purpose.
      </p>
      <ul className={styles.assumptions}>
        {proposal.assumptions.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>

      <div className={styles.leadRow} role="list" aria-label="Leads">
        {regions.map((region) => (
          <button
            key={region.lead_id}
            type="button"
            role="listitem"
            className={
              region.lead_id === selectedLeadId
                ? `${styles.leadChip} ${styles.leadChipActive}`
                : styles.leadChip
            }
            aria-pressed={region.lead_id === selectedLeadId}
            onClick={() => onSelectLead(region.lead_id)}
          >
            {region.lead_id}
          </button>
        ))}
      </div>

      <svg
        className={styles.svg}
        viewBox={`0 0 ${proposal.image_width} ${proposal.image_height}`}
        role="img"
        aria-label="Page image with proposed lead regions"
      >
        <image href={imageUrl} width={proposal.image_width} height={proposal.image_height} />
        {regions.map((region) => (
          <g key={region.lead_id}>
            <rect
              className={
                region.lead_id === selectedLeadId ? styles.boxSelected : styles.box
              }
              x={region.rect.x}
              y={region.rect.y}
              width={region.rect.width}
              height={region.rect.height}
            />
            <text
              className={styles.boxLabel}
              x={region.rect.x + 6}
              y={region.rect.y + 18}
            >
              {region.lead_id}
            </text>
          </g>
        ))}
      </svg>

      {selected ? (
        <div className={styles.nudge} aria-label={`Adjust lead ${selected.lead_id}`}>
          <p className={styles.nudgeTitle}>
            Adjust <strong>{selected.lead_id}</strong>
          </p>
          <div className={styles.nudgeRow}>
            <button type="button" onClick={() => updateSelected({ x: selected.rect.x - 8 })}>
              Left
            </button>
            <button type="button" onClick={() => updateSelected({ x: selected.rect.x + 8 })}>
              Right
            </button>
            <button type="button" onClick={() => updateSelected({ y: selected.rect.y - 8 })}>
              Up
            </button>
            <button type="button" onClick={() => updateSelected({ y: selected.rect.y + 8 })}>
              Down
            </button>
            <button
              type="button"
              onClick={() =>
                updateSelected({
                  width: Math.max(20, selected.rect.width - 12),
                  height: Math.max(20, selected.rect.height - 12),
                })
              }
            >
              Shrink
            </button>
            <button
              type="button"
              onClick={() =>
                updateSelected({
                  width: selected.rect.width + 12,
                  height: selected.rect.height + 12,
                })
              }
            >
              Grow
            </button>
          </div>
        </div>
      ) : null}
    </section>
  )
}
