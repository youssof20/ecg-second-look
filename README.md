# ECG Second Look

Offline-first ECG interpretation trainer and transparent second-reader prototype for non-cardiologist clinicians in low-resource settings.

Training mode runs in the browser after install. Second Look uses a local Python service on the same machine. That is not on-device mobile offline inference.

**Not a medical device. Not for patient-care decisions.**

## What currently works

- Offline frontal-plane vector training lesson
- Local Second Look pipeline: quality checks, page corners, 3x4 lead regions, multi-lead trace extraction, limited features, prototype pattern flags
- Synthetic fixtures and a small benchmark script

## What does not work

- Clinical validation
- Fully offline Second Look on a phone without the local API
- Reliable diagnosis of STEMI, hyperkalemia, VT, AF, or any other condition

## Local setup

On Windows PowerShell, use `npm.cmd` (avoids the script-permission error):

```powershell
cd app
npm.cmd install
npm.cmd run dev
```

API (needed for Second Look):

```powershell
python -m venv .venv
.\.venv\Scripts\pip.exe install -r api\requirements.txt
.\.venv\Scripts\python.exe -m uvicorn ecg_api.main:app --app-dir api --reload --port 8000
```

Tests:

```powershell
cd app
npm.cmd run test
npm.cmd run lint
npm.cmd run typecheck
npm.cmd run build

# from repo root
.\.venv\Scripts\python.exe -m pytest api\tests -q
.\.venv\Scripts\python.exe scripts\benchmark_pipeline.py
```

## Architecture

| Path | Role |
|------|------|
| `app/` | React PWA |
| `api/` | FastAPI + OpenCV pipeline |
| `samples/synthetic/` | Generated fixtures only |
| `docs/` | Engineering notes and validation roadmap |

Uploads stay in memory and are not stored by default.

## Sample workflow (Second Look)

1. Start the API, then the app.
2. Open Second Look and load **Clean page (layout)** or **Skewed photo**.
3. Complete quality / corners as needed.
4. Propose 3x4 layout, extract all leads, review feature evidence and pattern flags.

## Safety and intended use

Educational and research prototype only. Pattern outputs are prototype flags, not diagnoses. Do not upload identifiable clinical headers.

## Roadmap

Next: accessibility polish, offline packaging review, and a realistic demo recording (Slice 6).

See `docs/validation-roadmap.md`.

## License

MIT. See `LICENSE`.
