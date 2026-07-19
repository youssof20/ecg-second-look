"""Upload and decoding limits for the local analysis service."""

# Keep phone camera JPEGs workable without accepting arbitrary large dumps.
MAX_UPLOAD_BYTES = 8 * 1024 * 1024

# Below this short side, printed ECG grid structure is usually unusable.
MIN_SHORT_SIDE_PX = 400

# Laplacian variance below this usually means motion blur or soft focus.
BLUR_VARIANCE_THRESHOLD = 40.0

# Fraction of pixels near white that suggests flash glare / overexposure.
GLARE_FRACTION_THRESHOLD = 0.08

# Fraction of very dark pixels that suggests severe shadowing.
SHADOW_FRACTION_THRESHOLD = 0.18

# Contour area relative to image area required to treat a quad as the page.
MIN_PAGE_AREA_FRACTION = 0.20
