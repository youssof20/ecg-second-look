import { useMemo, useRef, useState } from 'react'
import type { PointerEvent as ReactPointerEvent } from 'react'
import type { CornerSet, Point } from '../lib/secondLookTypes'
import styles from './PageCornerEditor.module.css'

type CornerKey = keyof CornerSet

interface PageCornerEditorProps {
  imageUrl: string
  imageWidth: number
  imageHeight: number
  corners: CornerSet
  onChange: (corners: CornerSet) => void
}

const CORNER_KEYS: CornerKey[] = [
  'top_left',
  'top_right',
  'bottom_right',
  'bottom_left',
]

const LABELS: Record<CornerKey, string> = {
  top_left: 'TL',
  top_right: 'TR',
  bottom_right: 'BR',
  bottom_left: 'BL',
}

export function PageCornerEditor({
  imageUrl,
  imageWidth,
  imageHeight,
  corners,
  onChange,
}: PageCornerEditorProps) {
  const svgRef = useRef<SVGSVGElement>(null)
  const [active, setActive] = useState<CornerKey | null>(null)

  const polygon = useMemo(
    () =>
      CORNER_KEYS.map((key) => `${corners[key].x},${corners[key].y}`).join(' '),
    [corners],
  )

  function clientToImage(event: ReactPointerEvent<SVGSVGElement>): Point {
    const svg = svgRef.current
    if (!svg) return { x: 0, y: 0 }
    const rect = svg.getBoundingClientRect()
    const x = ((event.clientX - rect.left) / rect.width) * imageWidth
    const y = ((event.clientY - rect.top) / rect.height) * imageHeight
    return {
      x: Math.min(imageWidth - 1, Math.max(0, x)),
      y: Math.min(imageHeight - 1, Math.max(0, y)),
    }
  }

  function moveCorner(key: CornerKey, point: Point) {
    onChange({ ...corners, [key]: point })
  }

  function onPointerDown(key: CornerKey, event: ReactPointerEvent<SVGCircleElement>) {
    event.preventDefault()
    event.stopPropagation()
    setActive(key)
    event.currentTarget.setPointerCapture(event.pointerId)
  }

  function onPointerMove(event: ReactPointerEvent<SVGSVGElement>) {
    if (!active) return
    moveCorner(active, clientToImage(event))
  }

  function onPointerUp() {
    setActive(null)
  }

  return (
    <section className={styles.section} aria-labelledby="corner-heading">
      <h2 id="corner-heading" className={styles.title}>
        Page corners
      </h2>
      <p className={styles.help}>
        Drag the four handles so they sit on the paper corners. Correction will not
        run silently; you confirm before the warped image is shown.
      </p>
      <svg
        ref={svgRef}
        className={styles.svg}
        viewBox={`0 0 ${imageWidth} ${imageHeight}`}
        role="img"
        aria-label="ECG photo with adjustable page corners"
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        onPointerLeave={onPointerUp}
      >
        <image href={imageUrl} width={imageWidth} height={imageHeight} />
        <polygon className={styles.quad} points={polygon} />
        {CORNER_KEYS.map((key) => (
          <g key={key}>
            <circle
              className={styles.handle}
              cx={corners[key].x}
              cy={corners[key].y}
              r={Math.max(imageWidth, imageHeight) * 0.015}
              onPointerDown={(event) => onPointerDown(key, event)}
            />
            <text
              className={styles.label}
              x={corners[key].x}
              y={corners[key].y - Math.max(imageWidth, imageHeight) * 0.02}
              textAnchor="middle"
            >
              {LABELS[key]}
            </text>
          </g>
        ))}
      </svg>
    </section>
  )
}
