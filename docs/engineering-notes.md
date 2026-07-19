# Engineering notes

## Slice 1 — training shell

- Precordial leads reuse the frontal angle slider on approximate horizontal-plane axes so learners can compare leftward vs rightward polarity without a second control. This is a teaching shortcut, not a claim that frontal and horizontal axes are identical.
- Waveforms are schematic (Gaussian/triangular bumps) scaled by signed projection. They exist so polarity changes are visible at a glance; they are not digitized signals.
- Isoelectric threshold is `|projection| ≤ 0.12` so perpendicular vectors read as flat rather than flickering sign with floating-point noise.
- Service worker registration is production-oriented (`vite-plugin-pwa`). Dev server leaves the SW disabled to avoid stale-module confusion while editing.
- System font stack (Palatino / Segoe UI) keeps the first paint offline without shipping webfonts.
