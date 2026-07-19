import {
  ALL_LEADS,
  FRONTAL_LEADS,
  ISOELECTRIC_THRESHOLD,
  PRECORDIAL_LEADS,
  type LeadAxis,
  type LeadId,
  type Polarity,
} from './leads'

export interface CardiacVector {
  /** Mean QRS axis angle in degrees (frontal plane for limb leads). */
  angleDeg: number
  /** Relative magnitude in arbitrary teaching units (0–1). */
  magnitude: number
}

export interface LeadProjection {
  lead: LeadAxis
  /** Signed scalar projection onto the lead axis, scaled by magnitude. */
  projection: number
  polarity: Polarity
}

function toRadians(degrees: number): number {
  return (degrees * Math.PI) / 180
}

/**
 * Scalar projection of the cardiac vector onto a lead axis.
 * Uses cos(θ_vector − θ_lead) × magnitude.
 */
export function projectOntoLead(vector: CardiacVector, lead: LeadAxis): number {
  const delta = toRadians(vector.angleDeg - lead.angleDeg)
  return vector.magnitude * Math.cos(delta)
}

export function polarityFromProjection(projection: number): Polarity {
  if (projection > ISOELECTRIC_THRESHOLD) return 'positive'
  if (projection < -ISOELECTRIC_THRESHOLD) return 'negative'
  return 'isoelectric'
}

export function projectLead(vector: CardiacVector, lead: LeadAxis): LeadProjection {
  const projection = projectOntoLead(vector, lead)
  return {
    lead,
    projection,
    polarity: polarityFromProjection(projection),
  }
}

export function projectFrontalLeads(vector: CardiacVector): LeadProjection[] {
  return FRONTAL_LEADS.map((lead) => projectLead(vector, lead))
}

/**
 * Horizontal-plane teaching view. Uses the same angle control as the frontal
 * lesson so learners can see how a leftward vs rightward mean vector changes
 * V1–V6 polarity. This is not a separate measured horizontal-plane axis.
 */
export function projectPrecordialLeads(vector: CardiacVector): LeadProjection[] {
  return PRECORDIAL_LEADS.map((lead) => projectLead(vector, lead))
}

export function projectAllLeads(vector: CardiacVector): LeadProjection[] {
  return ALL_LEADS.map((lead) => projectLead(vector, lead))
}

export function findProjection(
  projections: LeadProjection[],
  id: LeadId,
): LeadProjection | undefined {
  return projections.find((item) => item.lead.id === id)
}

export function explainPolarity(projection: LeadProjection): string {
  const lead = projection.lead.id
  const abs = Math.abs(projection.projection)

  if (projection.polarity === 'isoelectric') {
    return `Lead ${lead} is nearly isoelectric because the vector is almost perpendicular to the lead axis (projection ≈ ${projection.projection.toFixed(2)}).`
  }

  if (projection.polarity === 'positive') {
    return `Lead ${lead} is positive because the vector points toward the positive electrode (projection ${projection.projection.toFixed(2)}). Larger positive values produce a taller upright deflection.`
  }

  return `Lead ${lead} is negative because the vector points away from the positive electrode (projection ${projection.projection.toFixed(2)}; |p| = ${abs.toFixed(2)}). The QRS appears predominantly downward.`
}
