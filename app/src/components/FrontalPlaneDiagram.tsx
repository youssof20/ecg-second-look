import type { PointerEvent } from 'react'
import type { CardiacVector } from '../lib/projection'
import { FRONTAL_LEADS } from '../lib/leads'
import styles from './FrontalPlaneDiagram.module.css'

interface FrontalPlaneDiagramProps {
  vector: CardiacVector
  onAngleChange: (angleDeg: number) => void
}

const SIZE = 280
const CENTER = SIZE / 2
const AXIS_RADIUS = 108
const VECTOR_MAX = 96

function polarToCartesian(angleDeg: number, radius: number): { x: number; y: number } {
  // Screen y grows downward; ECG angles increase counterclockwise from +x (lead I).
  const radians = (angleDeg * Math.PI) / 180
  return {
    x: CENTER + radius * Math.cos(radians),
    y: CENTER - radius * Math.sin(radians),
  }
}

function angleFromPointer(clientX: number, clientY: number, svg: SVGSVGElement): number {
  const rect = svg.getBoundingClientRect()
  const x = ((clientX - rect.left) / rect.width) * SIZE - CENTER
  const y = CENTER - ((clientY - rect.top) / rect.height) * SIZE
  const degrees = (Math.atan2(y, x) * 180) / Math.PI
  return Math.round(degrees)
}

export function FrontalPlaneDiagram({ vector, onAngleChange }: FrontalPlaneDiagramProps) {
  const tip = polarToCartesian(vector.angleDeg, VECTOR_MAX * vector.magnitude)

  function handlePointer(event: PointerEvent<SVGSVGElement>) {
    if (event.buttons === 0 && event.type === 'pointermove') return
    const svg = event.currentTarget
    onAngleChange(angleFromPointer(event.clientX, event.clientY, svg))
  }

  return (
    <figure className={styles.figure}>
      <svg
        className={styles.svg}
        viewBox={`0 0 ${SIZE} ${SIZE}`}
        role="img"
        aria-label={`Frontal-plane cardiac vector at ${vector.angleDeg} degrees, magnitude ${vector.magnitude.toFixed(2)}`}
        onPointerDown={handlePointer}
        onPointerMove={handlePointer}
      >
        <circle className={styles.disc} cx={CENTER} cy={CENTER} r={AXIS_RADIUS + 8} />

        {FRONTAL_LEADS.map((lead) => {
          const end = polarToCartesian(lead.angleDeg, AXIS_RADIUS)
          const label = polarToCartesian(lead.angleDeg, AXIS_RADIUS + 18)
          return (
            <g key={lead.id}>
              <line
                className={styles.axis}
                x1={CENTER}
                y1={CENTER}
                x2={end.x}
                y2={end.y}
              />
              <text className={styles.axisLabel} x={label.x} y={label.y} textAnchor="middle" dominantBaseline="middle">
                {lead.id}
              </text>
            </g>
          )
        })}

        <line
          className={styles.vector}
          x1={CENTER}
          y1={CENTER}
          x2={tip.x}
          y2={tip.y}
          markerEnd="url(#vectorArrow)"
        />
        <circle className={styles.tip} cx={tip.x} cy={tip.y} r={7} />

        <defs>
          <marker
            id="vectorArrow"
            markerWidth="8"
            markerHeight="8"
            refX="6"
            refY="3"
            orient="auto"
          >
            <path d="M0,0 L6,3 L0,6 Z" className={styles.arrowHead} />
          </marker>
        </defs>
      </svg>
      <figcaption className={styles.caption}>
        Drag on the diagram to set the mean QRS vector angle. Lead axes use the
        hexaxial reference system.
      </figcaption>
    </figure>
  )
}
