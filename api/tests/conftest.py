from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

API_ROOT = Path(__file__).resolve().parents[1]
ROOT = API_ROOT.parent
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

SAMPLES = ROOT / "samples" / "synthetic"


@pytest.fixture
def clean_page() -> np.ndarray:
    path = SAMPLES / "clean_12lead.png"
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    assert image is not None
    return image


@pytest.fixture
def skewed_photo() -> np.ndarray:
    path = SAMPLES / "photo_skewed.png"
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    assert image is not None
    return image
