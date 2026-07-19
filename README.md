# ECG Second Look

Offline-first ECG interpretation trainer and transparent second-reader prototype for non-cardiologist clinicians in low-resource settings.

Training works offline after install. Second Look uses a local Python service on the same machine.

**Not a medical device. Not for patient-care decisions.**

## What currently works

- Offline Training mode (vector lesson)
- Second Look: quality checks, page corners, 3x4 leads, multi-lead traces, features, prototype pattern flags
- PWA packaging for the app shell
- Synthetic fixtures, tests, and benchmark script
- Accessibility basics: skip link, focus outlines, offline banner, reduced-motion support

## What does not work

- Clinical validation
- Fully offline Second Look on a phone without the local API
- Reliable detection of STEMI, hyperkalemia, VT, AF, or other conditions

## Local setup

On Windows PowerShell, use `npm.cmd`:

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

## Docs

- `docs/offline.md`
- `docs/accessibility.md`
- `docs/demo-walkthrough.md`
- `docs/validation-roadmap.md`
- `docs/engineering-notes.md`

## Testing

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

## Sample workflow

See `docs/demo-walkthrough.md`.

## Safety

Educational and research prototype only. Pattern flags are not diagnoses. Do not upload identifiable clinical material.

## License

MIT. See `LICENSE`.
