"""Decode uploaded bytes into a BGR image without trusting browser MIME types."""

from __future__ import annotations

import numpy as np
import cv2

from ecg_api.config import MAX_UPLOAD_BYTES


class ImageDecodeError(ValueError):
    """Raised when bytes cannot be decoded as an image."""


def decode_image_bytes(data: bytes) -> np.ndarray:
    if not data:
        raise ImageDecodeError("Empty upload.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise ImageDecodeError(
            f"Upload exceeds the {MAX_UPLOAD_BYTES // (1024 * 1024)} MB limit."
        )

    buffer = np.frombuffer(data, dtype=np.uint8)
    image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    if image is None or image.size == 0:
        raise ImageDecodeError(
            "Could not decode image bytes. Use PNG or JPEG of a printed ECG page."
        )
    if image.ndim != 3 or image.shape[2] != 3:
        raise ImageDecodeError("Decoded image must be a 3-channel color image.")
    return image


def encode_png_base64(image: np.ndarray) -> str:
    import base64

    ok, encoded = cv2.imencode(".png", image)
    if not ok:
        raise ImageDecodeError("Failed to encode corrected image as PNG.")
    return base64.b64encode(encoded.tobytes()).decode("ascii")
