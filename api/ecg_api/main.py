"""Local FastAPI service for Second Look image quality and page correction."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from ecg_api.config import MAX_UPLOAD_BYTES
from ecg_api.decode import ImageDecodeError, decode_image_bytes, encode_png_base64
from ecg_api.perspective import detect_page_corners, rectify_page
from ecg_api.quality import assess_image_quality
from ecg_api.schemas import PageDetectionResult, QualityReport, RectifyRequest, RectifyResponse

SAMPLES_DIR = Path(__file__).resolve().parents[2] / "samples"

app = FastAPI(
    title="ECG Second Look API",
    version="0.2.0",
    description=(
        "Local prototype endpoints for image-quality checks and page rectification. "
        "Not a medical device. Uploads are processed in memory and not stored."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

if SAMPLES_DIR.is_dir():
    app.mount("/samples", StaticFiles(directory=str(SAMPLES_DIR)), name="samples")



@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ecg-second-look-api"}


@app.post("/api/v1/quality", response_model=QualityReport)
async def quality(file: UploadFile = File(...)) -> QualityReport:
    data = await _read_upload(file)
    image = _decode_or_400(data)
    return assess_image_quality(image)


@app.post("/api/v1/detect-page", response_model=PageDetectionResult)
async def detect_page(file: UploadFile = File(...)) -> PageDetectionResult:
    data = await _read_upload(file)
    image = _decode_or_400(data)
    report = assess_image_quality(image)
    if not report.analysis_allowed:
        raise HTTPException(
            status_code=422,
            detail={
                "message": report.refusal_reason or "Quality checks refused analysis.",
                "quality": report.model_dump(),
            },
        )
    return detect_page_corners(image)


@app.post("/api/v1/rectify", response_model=RectifyResponse)
async def rectify(
    file: UploadFile = File(...),
    corners_json: str = Form(...),
) -> RectifyResponse:
    """
    Multipart form: `file` plus `corners_json` (RectifyRequest JSON string).

    The corrected image is returned as base64 so the client can compare it with
    the original without the server storing either image.
    """
    try:
        request = RectifyRequest.model_validate_json(corners_json)
    except Exception as exc:  # noqa: BLE001 - return validation detail to client
        raise HTTPException(status_code=400, detail=f"Invalid corners JSON: {exc}") from exc

    data = await _read_upload(file)
    image = _decode_or_400(data)

    try:
        warped, out_w, out_h = rectify_page(
            image,
            request.corners,
            output_width=request.output_width,
            output_height=request.output_height,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return RectifyResponse(
        corrected_image_base64=encode_png_base64(warped),
        output_width=out_w,
        output_height=out_h,
        used_corners=request.corners,
        note=(
            "Compare the corrected page with the original before trusting later steps. "
            "Transformation is deterministic from the corners you confirmed."
        ),
    )


async def _read_upload(file: UploadFile) -> bytes:
    data = await file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Upload exceeds the {MAX_UPLOAD_BYTES // (1024 * 1024)} MB limit.",
        )
    return data


def _decode_or_400(data: bytes):
    try:
        return decode_image_bytes(data)
    except ImageDecodeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
