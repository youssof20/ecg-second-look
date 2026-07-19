from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from ecg_api.main import app

SAMPLES = Path(__file__).resolve().parents[2] / "samples" / "synthetic"
client = TestClient(app)


def test_analyze_leads_endpoint() -> None:
    path = SAMPLES / "clean_12lead.png"
    with path.open("rb") as handle:
        layout = client.post(
            "/api/v1/propose-layout",
            files={"file": ("clean_12lead.png", handle, "image/png")},
        ).json()
    with path.open("rb") as handle:
        response = client.post(
            "/api/v1/analyze-leads",
            data={
                "regions_json": json.dumps(layout["regions"]),
                "include_debug": "false",
            },
            files={"file": ("clean_12lead.png", handle, "image/png")},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["extracted_count"] >= 8
    assert len(body["features"]["features"]) >= 3
    assert "summary" in body["features"]
