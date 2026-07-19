# Offline behavior

## Training

After `npm.cmd run build` and a first visit (or install as a PWA), Training works without a network connection. The service worker caches the app shell and training assets.

## Second Look

Second Look needs the local Python API on the same machine:

```powershell
.\.venv\Scripts\python.exe -m uvicorn ecg_api.main:app --app-dir api --reload --port 8000
```

That is local processing, not cloud upload storage. It is not the same as fully offline inference on a phone.

If the browser is offline, the app shows a banner: Training still works; Second Look needs the local service.

## How to check

1. `cd app` then `npm.cmd run build` and `npm.cmd run preview`
2. Open the preview URL once while online
3. Turn off network in DevTools
4. Reload: Home / Training / About should still load
5. Second Look should still open, but analysis calls fail until the API is reachable
