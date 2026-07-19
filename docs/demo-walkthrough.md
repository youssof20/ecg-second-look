# Demo walkthrough

Use this script to record a short realistic demo. Keep the tone factual.

## Setup

```powershell
# terminal 1
.\.venv\Scripts\python.exe -m uvicorn ecg_api.main:app --app-dir api --reload --port 8000

# terminal 2
cd app
npm.cmd run dev
```

Open `http://127.0.0.1:5173`.

## Recording order (about 2–3 minutes)

1. **Home** — read the one-line project purpose. Mention it is not a medical device.
2. **Training** — drag the vector (or use sliders). Show lead II positive, aVR negative. Open model assumptions.
3. **Second Look** — load **Clean page (layout)**.
4. Show the quality panel.
5. Propose 3×4 layout. Select lead II. Extract one lead. Toggle debug overlay.
6. Extract all leads + measure features. Scroll the evidence panel.
7. Show pattern flags. Point out `not_assessable` / non-diagnosis wording.
8. Load **Blurry (should refuse)** and show refusal.
9. Optional: **Skewed photo** → corners → original/corrected compare.

## What not to say on camera

- Do not say diagnosis confirmed, STEMI ruled in/out, safe to discharge, AI verified, or cardiologist-level.
- Prefer: “The prototype measured…”, “This pattern may be compatible with…”, “Unable to assess because…”
