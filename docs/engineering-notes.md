# Engineering notes

## Slice 1 — training shell

- Precordial leads reuse the frontal angle slider on approximate horizontal-plane axes so learners can compare leftward vs rightward polarity without a second control. This is a teaching shortcut, not a claim that frontal and horizontal axes are identical.
- Waveforms are schematic (Gaussian/triangular bumps) scaled by signed projection. They exist so polarity changes are visible at a glance; they are not digitized signals.
- Isoelectric threshold is `|projection| ≤ 0.12` so perpendicular vectors read as flat rather than flickering sign with floating-point noise.
- Service worker registration is production-oriented (`vite-plugin-pwa`). Dev server leaves the SW disabled to avoid stale-module confusion while editing.
- System font stack (Palatino / Segoe UI) keeps the first paint offline without shipping webfonts.

## Slice 2 — quality and page correction

- Glare detection uses saturated pixels (`≥252`), not ordinary paper white (`~245`). An earlier threshold of 245 marked every clean synthetic page as glare.
- Hard refusals are limited to resolution and blur. Glare/shadow/coverage warnings still allow corner editing so the user can inspect a salvageable capture.
- When no page quad is found, the API returns full-frame corners with status `fallback_full_frame` instead of inventing a confident detection.
- Rectify returns PNG base64 and never writes the upload or result to disk.
- OpenCV pin is `opencv-python-headless==5.0.0.93` because older 4.12 wheels conflict with NumPy builds available for Python 3.14 on this machine.

## Slice 3 — layout and one-lead trace

- Only one layout is supported: geometric 3×4 (`I/aVR/V1/V4` …). Boxes are proposals, not OCR of lead labels.
- Trace extraction uses HSV grid suppression only when reddish grid coverage exceeds 2%; otherwise faint grayscale traces were being erased in early experiments.
- Gap repair is capped (`MAX_GAP_RUN = 6`). Longer discontinuities stay as failures instead of inventing a continuous waveform.

## Slice 4 — features

- Heart rate / RR / QRS / ST / T measurements use ROI-derived px/mm plus user or default paper speed and voltage gain. Assumed calibration caps quality at `warn` rather than inventing high confidence.
- Synthetic lead strips often contain a single schematic beat, so heart rate commonly returns `not_assessable` (fewer than two peaks). That is preferred over fabricating a rate.
- Feature evidence copy is template-filled from measured fields only; no free-form clinical narrative generator.
