# Accessibility notes

Checked against the prototype goals for a clinician on a small screen.

## Supported in this build

- Skip link to main content
- Visible `:focus-visible` outlines
- Primary nav keyboard reachable
- Training angle/magnitude sliders for keyboard control of the vector
- Large tap targets on primary actions
- Status/alert roles for busy, error, offline, and refusal messages
- `prefers-reduced-motion` respected
- Higher-contrast variable tweaks under `prefers-contrast: more`
- No required WebGL for core flows

## Manual check list

1. Keyboard only: Tab through Home → Training → Second Look → About
2. Zoom to 200%: no clipped primary controls
3. Narrow phone width (~390px): no horizontal scroll in primary workflow
4. Screen reader: Training lead buttons announce polarity; Second Look quality statuses are readable

## Known limits

- Lead-region boxes are nudge buttons, not full drag handles for every corner of every lead
- Pattern-flag lists are dense; triggered items are visually emphasized but still text-heavy
