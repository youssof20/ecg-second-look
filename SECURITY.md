# Security

## Reporting vulnerabilities

Use GitHub Security Advisories for this repository when available. Include steps to reproduce and impact.

Do not file public issues for exploitable upload, path, or dependency bugs until a fix is ready.

## Clinical behavior

Unsafe clinical presentation (diagnostic wording, suppressed uncertainty, implied clearance) is a product defect. Report with label `clinical-safety` or through the same private channel.

## Upload handling (implemented)

- Max upload size: 8 MB (`api/ecg_api/config.py`)
- Images are decoded with OpenCV from raw bytes; browser MIME type and filename are not trusted
- Rejects undecodable payloads
- Uploads are processed in memory and not written to disk by default
- CORS limited to local Vite origins

## Client

- No API secrets in the browser bundle
- Analysis calls go to the local service via `/api`

## Dependencies

- App and API dependencies are pinned in `app/package-lock.json` and `api/requirements.txt`
- GitHub Actions run lint/typecheck/tests on app and API changes
- Dependabot config watches npm and pip ecosystems
