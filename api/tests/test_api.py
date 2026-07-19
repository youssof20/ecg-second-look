from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ecg_api.main import app

SAMPLES = Path(__file__).resolve().parents[2] / "samples" / "synthetic"
client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_quality_endpoint_on_clean_sample() -> None:
    path = SAMPLES / "photo_flat.png"
    with path.open("rb") as handle:
        response = client.post(
            "/api/v1/quality",
            files={"file": ("photo_flat.png", handle, "application/octet-stream")},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["analysis_allowed"] is True
    assert body["width_px"] > 0


def test_quality_refuses_tiny_sample() -> None:
    path = SAMPLES / "photo_tiny.png"
    with path.open("rb") as handle:
        response = client.post(
            "/api/v1/quality",
            files={"file": ("photo_tiny.png", handle, "image/png")},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["analysis_allowed"] is False


def test_detect_page_refuses_blurry() -> None:
    path = SAMPLES / "photo_blurry.png"
    with path.open("rb") as handle:
        response = client.post(
            "/api/v1/detect-page",
            files={"file": ("photo_blurry.png", handle, "image/png")},
        )
    assert response.status_code == 422


def test_rectify_round_trip() -> None:
    path = SAMPLES / "photo_flat.png"
    with path.open("rb") as handle:
        detect = client.post(
            "/api/v1/detect-page",
            files={"file": ("photo_flat.png", handle, "image/png")},
        )
    assert detect.status_code == 200
    corners = detect.json()["corners"]
    payload = json.dumps({"corners": corners})
    with path.open("rb") as handle:
        rectify = client.post(
            "/api/v1/rectify",
            data={"corners_json": payload},
            files={"file": ("photo_flat.png", handle, "image/png")},
        )
    assert rectify.status_code == 200
    body = rectify.json()
    assert body["corrected_image_base64"]
    assert body["output_width"] >= 200


def test_rejects_non_image_bytes() -> None:
    response = client.post(
        "/api/v1/quality",
        files={"file": ("notes.txt", b"not an image", "text/plain")},
    )
    assert response.status_code == 400
