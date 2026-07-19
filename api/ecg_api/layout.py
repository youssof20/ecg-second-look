"""Single supported 12-lead page layout (3 rows × 4 columns)."""

from __future__ import annotations

from ecg_api.schemas import LeadId, LeadRegion, LayoutProposal, Rect

# Matches the synthetic fixture and a common printed 3×4 arrangement.
LAYOUT_ID = "grid_3x4_standard"
LAYOUT_VERSION = "1"

LEAD_ORDER: list[list[LeadId]] = [
    ["I", "aVR", "V1", "V4"],
    ["II", "aVL", "V2", "V5"],
    ["III", "aVF", "V3", "V6"],
]

# Fraction of page height reserved for header / calibration text.
HEADER_FRACTION = 0.09
# Inset inside each cell so labels above the waveform are mostly excluded.
CELL_INSET = 0.08


def propose_lead_regions(width: int, height: int) -> LayoutProposal:
    if width < 200 or height < 200:
        raise ValueError("Image is too small for the 3×4 layout proposal.")

    content_top = int(round(height * HEADER_FRACTION))
    content_height = max(1, height - content_top)
    rows = 3
    cols = 4
    cell_w = width / cols
    cell_h = content_height / rows

    regions: list[LeadRegion] = []
    for r, row in enumerate(LEAD_ORDER):
        for c, lead_id in enumerate(row):
            x0 = c * cell_w
            y0 = content_top + r * cell_h
            inset_x = cell_w * CELL_INSET
            inset_y = cell_h * CELL_INSET
            rect = Rect(
                x=max(0.0, x0 + inset_x),
                y=max(0.0, y0 + inset_y * 1.4),
                width=max(1.0, cell_w - 2 * inset_x),
                height=max(1.0, cell_h - inset_y * 2.2),
            )
            regions.append(
                LeadRegion(
                    lead_id=lead_id,
                    rect=rect,
                    row=r,
                    col=c,
                )
            )

    return LayoutProposal(
        layout_id=LAYOUT_ID,
        layout_version=LAYOUT_VERSION,
        image_width=width,
        image_height=height,
        regions=regions,
        assumptions=[
            "Assumes a 3×4 printed layout: I/aVR/V1/V4, II/aVL/V2/V5, III/aVF/V3/V6.",
            "Header band is excluded by a fixed fraction; adjust boxes if your print differs.",
            "Proposal is geometric only; it does not read lead labels from the image.",
        ],
    )


def clip_region_to_image(region: LeadRegion, width: int, height: int) -> LeadRegion:
    x = min(max(0.0, region.rect.x), width - 1.0)
    y = min(max(0.0, region.rect.y), height - 1.0)
    w = min(region.rect.width, width - x)
    h = min(region.rect.height, height - y)
    if w < 8 or h < 8:
        raise ValueError(f"Lead {region.lead_id} region is too small after clipping.")
    return LeadRegion(
        lead_id=region.lead_id,
        rect=Rect(x=x, y=y, width=w, height=h),
        row=region.row,
        col=region.col,
    )
