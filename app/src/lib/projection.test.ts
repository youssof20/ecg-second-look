import { describe, expect, it } from 'vitest'
import { FRONTAL_LEADS, ISOELECTRIC_THRESHOLD } from './leads'
import {
  polarityFromProjection,
  projectFrontalLeads,
  projectOntoLead,
} from './projection'

describe('projectOntoLead', () => {
  it('gives full positive projection when vector aligns with lead I', () => {
    const leadI = FRONTAL_LEADS[0]!
    const value = projectOntoLead({ angleDeg: 0, magnitude: 1 }, leadI)
    expect(value).toBeCloseTo(1, 5)
  })

  it('gives near-zero projection when vector is perpendicular to lead I', () => {
    const leadI = FRONTAL_LEADS[0]!
    const value = projectOntoLead({ angleDeg: 90, magnitude: 1 }, leadI)
    expect(Math.abs(value)).toBeLessThan(ISOELECTRIC_THRESHOLD)
  })

  it('makes aVR negative for a normal leftward/inferior mean axis', () => {
    const aVR = FRONTAL_LEADS.find((lead) => lead.id === 'aVR')!
    const value = projectOntoLead({ angleDeg: 60, magnitude: 1 }, aVR)
    expect(value).toBeLessThan(-0.5)
  })

  it('scales with magnitude', () => {
    const leadII = FRONTAL_LEADS.find((lead) => lead.id === 'II')!
    const full = projectOntoLead({ angleDeg: 60, magnitude: 1 }, leadII)
    const half = projectOntoLead({ angleDeg: 60, magnitude: 0.5 }, leadII)
    expect(half).toBeCloseTo(full * 0.5, 5)
  })
})

describe('polarityFromProjection', () => {
  it('labels small values as isoelectric', () => {
    expect(polarityFromProjection(0)).toBe('isoelectric')
    expect(polarityFromProjection(ISOELECTRIC_THRESHOLD / 2)).toBe('isoelectric')
  })

  it('labels signed deflections', () => {
    expect(polarityFromProjection(0.5)).toBe('positive')
    expect(polarityFromProjection(-0.5)).toBe('negative')
  })
})

describe('projectFrontalLeads', () => {
  it('returns six limb-lead projections', () => {
    const result = projectFrontalLeads({ angleDeg: 45, magnitude: 0.8 })
    expect(result).toHaveLength(6)
    expect(result.map((item) => item.lead.id)).toEqual([
      'I',
      'II',
      'III',
      'aVR',
      'aVL',
      'aVF',
    ])
  })
})
