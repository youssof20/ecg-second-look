"""Generate synthetic 12-lead ECG page images and distorted regression fixtures."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "samples" / "synthetic"


def draw_grid(canvas: np.ndarray, small: int = 10, large: int = 50) -> None:
    h, w = canvas.shape[:2]
    # Pink/red teaching grid (common printed ECG paper look).
    for x in range(0, w, small):
        color = (180, 180, 220) if x % large else (140, 140, 200)
        cv2.line(canvas, (x, 0), (x, h - 1), color, 1)
    for y in range(0, h, small):
        color = (180, 180, 220) if y % large else (140, 140, 200)
        cv2.line(canvas, (0, y), (w - 1, y), color, 1)


def synthetic_qrs(x0: int, y0: int, width: int, amplitude: int, invert: bool = False) -> np.ndarray:
    """Return polyline points for one schematic QRS + T in image coordinates."""
    sign = -1 if invert else 1
    xs = np.linspace(0, width, 80)
    ys = np.zeros_like(xs)
    for i, t in enumerate(xs / width):
        # P
        ys[i] += 0.15 * amplitude * np.exp(-0.5 * ((t - 0.18) / 0.03) ** 2)
        # QRS triangle
        d = abs(t - 0.42)
        if d < 0.04:
            ys[i] += amplitude * (1 - d / 0.04)
        # T
        ys[i] += 0.35 * amplitude * np.exp(-0.5 * ((t - 0.68) / 0.05) ** 2)
    pts = np.column_stack([x0 + xs, y0 - sign * ys]).astype(np.int32)
    return pts


def render_clean_page(width: int = 1400, height: int = 1000) -> np.ndarray:
    canvas = np.full((height, width, 3), 245, dtype=np.uint8)
    draw_grid(canvas)

    # Banner that is clearly non-PHI.
    cv2.rectangle(canvas, (0, 0), (width - 1, 70), (235, 235, 235), -1)
    cv2.putText(
        canvas,
        "SYNTHETIC ECG FIXTURE — NO PATIENT DATA",
        (24, 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (40, 40, 40),
        2,
        cv2.LINE_AA,
    )

    leads = [
        ["I", "aVR", "V1", "V4"],
        ["II", "aVL", "V2", "V5"],
        ["III", "aVF", "V3", "V6"],
    ]
    cell_w = width // 4
    cell_h = (height - 90) // 3
    amplitudes = {
        "I": 28,
        "II": 42,
        "III": 22,
        "aVR": -30,
        "aVL": 8,
        "aVF": 34,
        "V1": -24,
        "V2": -18,
        "V3": 20,
        "V4": 36,
        "V5": 40,
        "V6": 32,
    }

    for r, row in enumerate(leads):
        for c, lead in enumerate(row):
            x = c * cell_w + 30
            y = 90 + r * cell_h + cell_h // 2
            cv2.putText(
                canvas,
                lead,
                (x, y - 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (20, 20, 20),
                2,
                cv2.LINE_AA,
            )
            amp = amplitudes[lead]
            invert = amp < 0
            pts = synthetic_qrs(x, y, cell_w - 70, abs(amp), invert=invert)
            cv2.polylines(canvas, [pts], False, (10, 10, 10), 2, cv2.LINE_AA)

    # Calibration pulse
    cv2.rectangle(canvas, (40, height - 80), (60, height - 40), (10, 10, 10), 2)
    return canvas


def place_on_desk(page: np.ndarray, canvas_size: tuple[int, int], skew: bool) -> np.ndarray:
    ch, cw = canvas_size
    desk = np.full((ch, cw, 3), 48, dtype=np.uint8)
    ph, pw = page.shape[:2]

    if skew:
        src = np.float32([[0, 0], [pw - 1, 0], [pw - 1, ph - 1], [0, ph - 1]])
        margin_x = int(cw * 0.08)
        margin_y = int(ch * 0.1)
        dst = np.float32(
            [
                [margin_x + 40, margin_y + 30],
                [cw - margin_x - 10, margin_y - 10],
                [cw - margin_x - 60, ch - margin_y - 20],
                [margin_x - 20, ch - margin_y + 40],
            ]
        )
        matrix = cv2.getPerspectiveTransform(src, dst)
        warped = cv2.warpPerspective(page, matrix, (cw, ch), borderValue=(48, 48, 48))
        mask = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY) > 60
        desk[mask] = warped[mask]
        return desk

    scale = min((cw - 80) / pw, (ch - 80) / ph)
    resized = cv2.resize(page, (int(pw * scale), int(ph * scale)))
    rh, rw = resized.shape[:2]
    x0 = (cw - rw) // 2
    y0 = (ch - rh) // 2
    desk[y0 : y0 + rh, x0 : x0 + rw] = resized
    return desk


def add_blur(image: np.ndarray, ksize: int = 21) -> np.ndarray:
    return cv2.GaussianBlur(image, (ksize, ksize), 0)


def add_glare(image: np.ndarray) -> np.ndarray:
    out = image.copy()
    h, w = out.shape[:2]
    overlay = np.zeros_like(out)
    cv2.circle(overlay, (w // 2, h // 3), min(w, h) // 5, (255, 255, 255), -1)
    overlay = cv2.GaussianBlur(overlay, (81, 81), 0)
    mixed = cv2.addWeighted(out, 0.55, overlay, 0.7, 0)
    # Force a saturated hotspot so quality checks can distinguish glare from paper white.
    cv2.circle(mixed, (w // 2, h // 3), min(w, h) // 12, (255, 255, 255), -1)
    return mixed


def add_shadow(image: np.ndarray) -> np.ndarray:
    out = image.astype(np.float32)
    h, w = out.shape[:2]
    ramp = np.linspace(0.35, 1.0, w, dtype=np.float32)
    out *= ramp[np.newaxis, :, np.newaxis]
    return np.clip(out, 0, 255).astype(np.uint8)


def tiny_image(page: np.ndarray) -> np.ndarray:
    return cv2.resize(page, (220, 160))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    page = render_clean_page()
    cv2.imwrite(str(OUT / "clean_12lead.png"), page)

    desk = place_on_desk(page, (1100, 1500), skew=False)
    cv2.imwrite(str(OUT / "photo_flat.png"), desk)

    skewed = place_on_desk(page, (1100, 1500), skew=True)
    cv2.imwrite(str(OUT / "photo_skewed.png"), skewed)

    cv2.imwrite(str(OUT / "photo_blurry.png"), add_blur(desk))
    cv2.imwrite(str(OUT / "photo_glare.png"), add_glare(desk))
    cv2.imwrite(str(OUT / "photo_shadow.png"), add_shadow(desk))
    cv2.imwrite(str(OUT / "photo_tiny.png"), tiny_image(desk))

    print(f"Wrote fixtures to {OUT}")


if __name__ == "__main__":
    main()
