# Analysis API

Local FastAPI service for Second Look stages 1–2 (quality + page rectification).

```bash
# from repository root
.\.venv\Scripts\pip.exe install -r api\requirements.txt
.\.venv\Scripts\python.exe -m uvicorn ecg_api.main:app --app-dir api --reload --port 8000
```

Endpoints:

- `GET /api/v1/health`
- `POST /api/v1/quality` (multipart file)
- `POST /api/v1/detect-page` (multipart file; refused when quality hard-fails)
- `POST /api/v1/propose-layout` (multipart file; 3×4 geometric proposal)
- `POST /api/v1/extract-trace` (multipart file + `region_json` form field)
- `POST /api/v1/analyze-leads` (multipart file + `regions_json` + optional `calibration_json`)
- `GET /samples/...` (synthetic fixtures)

Uploads are not written to disk.
