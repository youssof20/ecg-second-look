from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from ecg_api.main import app

SAMPLES = Path(__file__).resolve().parents[2] / "samples" / "synthetic"
client = TestClient(app)


def test_propose_layout_endpoint() -> None:
    path = SAMPLES / "clean_12lead.png"
    with path.open("rb") as handle:
        response = client.post(
            "/api/v1/propose-layout",
            files={"file": ("clean_12lead.png", handle, "image/png")},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["layout_id"] == "grid_3x4_standard"
    assert len(body["regions"]) == 12


def test_extract_trace_endpoint_success() -> None:
    path = SAMPLES / "clean_12lead.png"
    with path.open("rb") as handle:
        layout = client.post(
            "/api/v1/propose-layout",
            files={"file": ("clean_12lead.png", handle, "image/png")},
        ).json()
    region = next(item for item in layout["regions"] if item["lead_id"] == "II")
    with path.open("rb") as handle:
        response = client.post(
            "/api/v1/extract-trace",
            data={"region_json": json.dumps(region), "include_debug": "true"},
            files={"file": ("clean_12lead.png", handle, "image/png")},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "extracted"
    assert body["lead_id"] == "II"
    assert len(body["samples"]) > 20
