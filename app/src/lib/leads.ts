/** Frontal-plane limb lead axes in degrees (Einthoven / Goldberger convention). */
export type FrontalLeadId = 'I' | 'II' | 'III' | 'aVR' | 'aVL' | 'aVF'

export type PrecordialLeadId = 'V1' | 'V2' | 'V3' | 'V4' | 'V5' | 'V6'

export type LeadId = FrontalLeadId | PrecordialLeadId

export type Polarity = 'positive' | 'negative' | 'isoelectric'

export interface LeadAxis {
  id: LeadId
  /** Degrees from lead I; positive counterclockwise when viewing the patient from the front. */
  angleDeg: number
  plane: 'frontal' | 'horizontal'
}

/**
 * Teaching axes only. These are the standard textbook angles for the hexaxial
 * reference system; they are not patient-specific measured axes.
 */
export const FRONTAL_LEADS: readonly LeadAxis[] = [
  { id: 'I', angleDeg: 0, plane: 'frontal' },
  { id: 'II', angleDeg: 60, plane: 'frontal' },
  { id: 'III', angleDeg: 120, plane: 'frontal' },
  { id: 'aVR', angleDeg: -150, plane: 'frontal' },
  { id: 'aVL', angleDeg: -30, plane: 'frontal' },
  { id: 'aVF', angleDeg: 90, plane: 'frontal' },
] as const

/**
 * Simplified horizontal-plane angles for V1–V6 used in this lesson.
 * Real precordial morphology depends on heart position, lead placement, and
 * torso geometry; this model only illustrates leftward vs rightward projection.
 */
export const PRECORDIAL_LEADS: readonly LeadAxis[] = [
  { id: 'V1', angleDeg: 120, plane: 'horizontal' },
  { id: 'V2', angleDeg: 90, plane: 'horizontal' },
  { id: 'V3', angleDeg: 75, plane: 'horizontal' },
  { id: 'V4', angleDeg: 60, plane: 'horizontal' },
  { id: 'V5', angleDeg: 30, plane: 'horizontal' },
  { id: 'V6', angleDeg: 0, plane: 'horizontal' },
] as const

export const ALL_LEADS: readonly LeadAxis[] = [...FRONTAL_LEADS, ...PRECORDIAL_LEADS]

/** Near-zero projections are treated as isoelectric for teaching clarity. */
export const ISOELECTRIC_THRESHOLD = 0.12
