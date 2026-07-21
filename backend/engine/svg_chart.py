"""
engine/svg_chart.py
SVG North Indian Kundali chart renderer.

North Indian style: diamond/square layout, fixed house positions, sign numbers rotate.
The 12 houses are fixed position cells; what changes is which Rashi occupies each house.

House cell layout (North Indian — fixed):
     ┌────┬────┬────┐
     │ 12 │  1 │  2 │
     ├────┼────┼────┤
     │ 11 │    │  3 │
     ├────┼────┼────┤
     │ 10 │  9 │  8 │  ← wait, North Indian uses diagonal diamond
     └────┴────┴────┘

Actual North Indian square grid — 4x4 with 4 corner triangles:
  ┌──────┬──────┬──────┐
  │  12  │  1   │  2   │  (top row)
  ├──────┼──────┼──────┤
  │  11  │ LAGNA│  3   │  (middle row — lagna is center)
  ├──────┼──────┼──────┤
  │  10  │  9   │  8   │  (alternative: 4,5,6,7 in corners)
  └──────┴──────┴──────┘

Standard North Indian 3x3 grid with 4 triangular corners:
  ┌─────┬───────┬─────┐
  │ H12 │  H1   │ H2  │
  │     │(Lagna)│     │
  ├─────┤       ├─────┤
  │ H11 │ (mid) │ H3  │
  ├─────┤       ├─────┤
  │ H10 │  H9   │ H4  │  ← H4 is actually diagonally placed
  └─────┴───────┴─────┘
  with H5,6,7,8 in the corners

Corrected: Standard North Indian is 4 rows, 4 cols with diamonds:
  Positions (house numbers):
   ┌──┬──┬──┬──┐
   │12│ 1│ 2│ 3│
   ├──┼──┼──┼──┤
   │11│  │  │ 4│
   ├──┼──┼──┼──┤
   │10│  │  │ 5│
   ├──┼──┼──┼──┤
   │ 9│ 8│ 7│ 6│
   └──┴──┴──┴──┘
(center 2x2 is empty — house labels surround it)
"""
from __future__ import annotations
from typing import Optional
from engine.models import Rashi

# ── Chart dimensions ──────────────────────────────────────────────────────────
W = 360   # total SVG width
H = 360   # total SVG height
CELL = W // 4  # 90px per cell

# ── House positions in 4x4 grid (col, row) — 0-indexed ───────────────────────
# North Indian: H1 = top-center, going clockwise
HOUSE_GRID: dict[int, tuple[int, int]] = {
    1:  (1, 0),
    2:  (2, 0),
    3:  (3, 0),
    4:  (3, 1),
    5:  (3, 2),
    6:  (3, 3),
    7:  (2, 3),
    8:  (1, 3),
    9:  (0, 3),
    10: (0, 2),
    11: (0, 1),
    12: (0, 0),
}

# ── Rashi short names ─────────────────────────────────────────────────────────
RASHI_SHORT_MR: dict[int, str] = {
    0:  "मेष",
    1:  "वृष",
    2:  "मिथ",
    3:  "कर्क",
    4:  "सिंह",
    5:  "कन्या",
    6:  "तुळ",
    7:  "वृश्चि",
    8:  "धनु",
    9:  "मकर",
    10: "कुंभ",
    11: "मीन",
}

RASHI_SHORT_EN: dict[int, str] = {
    0: "Ari", 1: "Tau", 2: "Gem", 3: "Can",
    4: "Leo", 5: "Vir", 6: "Lib", 7: "Sco",
    8: "Sag", 9: "Cap", 10: "Aqr", 11: "Pis",
}

# ── Planet glyphs (short Marathi labels) ─────────────────────────────────────
PLANET_MR: dict[str, str] = {
    "Sun":     "सू",
    "Moon":    "च",
    "Mars":    "म",
    "Mercury": "बु",
    "Jupiter": "गु",
    "Venus":   "शु",
    "Saturn":  "श",
    "Rahu":    "रा",
    "Ketu":    "के",
}

PLANET_COLOR: dict[str, str] = {
    "Sun":     "#f97316",
    "Moon":    "#a78bfa",
    "Mars":    "#ef4444",
    "Mercury": "#22c55e",
    "Jupiter": "#eab308",
    "Venus":   "#ec4899",
    "Saturn":  "#64748b",
    "Rahu":    "#94a3b8",
    "Ketu":    "#78716c",
}


def _house_for_rashi(lagna_rashi: int, planet_rashi: int) -> int:
    """Whole-sign house: distance from lagna rashi."""
    return (planet_rashi - lagna_rashi) % 12 + 1


def render_north_indian_svg(
    lagna_rashi: int,
    planet_rashis: dict[str, int],  # {"Sun": 3, "Moon": 7, ...}
    retrogrades: Optional[set[str]] = None,
    width: int = 360,
    lang: str = "mr",
    theme: str = "dark",
) -> str:
    """
    Render a North Indian style kundali chart as SVG string.

    Args:
        lagna_rashi: 0-11 (Aries=0 ... Pisces=11)
        planet_rashis: planet name -> rashi index (0-11)
        retrogrades: set of planet names that are retrograde
        width: SVG width (height = width)
        lang: 'mr' for Marathi labels, 'en' for English
    Returns:
        SVG string
    """
    if retrogrades is None:
        retrogrades = set()

    scale = width / W
    h = width
    cell = int(CELL * scale)
    rashi_labels = RASHI_SHORT_MR if lang == "mr" else RASHI_SHORT_EN

    # ── Group planets by house ────────────────────────────────────────────────
    house_planets: dict[int, list[str]] = {i: [] for i in range(1, 13)}
    for planet, planet_rashi in planet_rashis.items():
        house_num = _house_for_rashi(lagna_rashi, planet_rashi)
        house_planets[house_num].append(planet)

    # ── Which rashi occupies each house ──────────────────────────────────────
    house_rashi: dict[int, int] = {
        house: (lagna_rashi + house - 1) % 12
        for house in range(1, 13)
    }

    # ── SVG builder ──────────────────────────────────────────────────────────
    lines: list[str] = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{h}" viewBox="0 0 {width} {h}" font-family="Noto Sans Devanagari,Inter,sans-serif">')

    if theme == "dark":
        bg_color = "#0d1b2a"
        border_color = "#f07c00"
    elif theme == "light":
        bg_color = "#ffffff"
        border_color = "#f07c00"
    else: # "bw"
        bg_color = "#ffffff"
        border_color = "#000000"
    
    # Background
    lines.append(f'<rect width="{width}" height="{h}" fill="{bg_color}" rx="8"/>')

    # Outer border
    lines.append(f'<rect x="1" y="1" width="{width-2}" height="{h-2}" fill="none" stroke="{border_color}" stroke-width="1.5" rx="7"/>')

    # ── Draw 4x4 grid (outer 12 cells) ───────────────────────────────────────
    if theme == "dark":
        STROKE = "#1a3050"
        STROKE_LAGNA = "#f07c00"
    elif theme == "light":
        STROKE = "#e5e7eb"
        STROKE_LAGNA = "#f07c00"
    else: # "bw"
        STROKE = "#000000"
        STROKE_LAGNA = "#000000"

    for house_num, (col, row) in HOUSE_GRID.items():
        x = int(col * cell * scale)
        y = int(row * cell * scale)
        rashi_idx = house_rashi[house_num]
        is_lagna = house_num == 1

        # Cell background
        if theme == "dark":
            bg = "rgba(240,124,0,0.08)" if is_lagna else "rgba(255,255,255,0.02)"
        elif theme == "light":
            bg = "rgba(240,124,0,0.08)" if is_lagna else "#ffffff"
        else: # "bw"
            bg = "#ffffff"
        stroke_color = STROKE_LAGNA if is_lagna else STROKE
        stroke_w = "1.5" if is_lagna else "0.8"

        lines.append(
            f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" '
            f'fill="{bg}" stroke="{stroke_color}" stroke-width="{stroke_w}"/>'
        )

        # Rashi number + short name (top-left of cell)
        rashi_label = rashi_labels.get(rashi_idx, "")
        rashi_num = rashi_idx + 1  # 1-12 for display
        text_color = "#7a7268" if theme == "dark" else ("#9ca3af" if theme == "light" else "#000000")

        lines.append(
            f'<text x="{x + int(4*scale)}" y="{y + int(13*scale)}" '
            f'font-size="{int(9*scale)}" fill="{text_color}" font-weight="400">'
            f'{rashi_num} {rashi_label}</text>'
        )

        # Lagna marker
        if is_lagna:
            lagna_color = "#f07c00" if theme in ["dark", "light"] else "#000000"
            lines.append(
                f'<text x="{x + cell - int(4*scale)}" y="{y + int(13*scale)}" '
                f'font-size="{int(9*scale)}" fill="{lagna_color}" text-anchor="end" font-weight="700">ल</text>'
            )

        # ── Planet labels in this house ───────────────────────────────────────
        planets = house_planets.get(house_num, [])
        # Layout: stack vertically, centered in cell
        total_planets = len(planets)
        start_y = y + int(cell * 0.38)
        if total_planets > 0:
            step = min(int(14 * scale), int((cell * 0.55) / total_planets))
            for pi, planet in enumerate(planets):
                py = start_y + pi * step
                px = x + cell // 2
                is_retro = planet in retrogrades
                glyph = PLANET_MR.get(planet, planet[:2])
                if theme == "bw":
                    color = "#000000"
                else:
                    color = PLANET_COLOR.get(planet, "#b8b0a0")
                # Retrograde indicator
                retro_mark = "ᵛ" if is_retro else ""
                lines.append(
                    f'<text x="{px}" y="{py}" '
                    f'font-size="{int(11*scale)}" fill="{color}" '
                    f'text-anchor="middle" font-weight="600">'
                    f'{glyph}{retro_mark}</text>'
                )

    # ── Inner square (center) ─────────────────────────────────────────────────
    cx = cell
    cy = cell
    inner_w = cell * 2
    inner_bg = "rgba(255,255,255,0.01)" if theme == "dark" else "transparent"
    lines.append(
        f'<rect x="{cx}" y="{cy}" width="{inner_w}" height="{inner_w}" '
        f'fill="{inner_bg}" stroke="{STROKE}" stroke-width="0.8"/>'
    )
    # Diagonals of inner square
    lines.append(
        f'<line x1="{cx}" y1="{cy}" x2="{cx+inner_w}" y2="{cy+inner_w}" '
        f'stroke="{STROKE}" stroke-width="0.6"/>'
    )
    lines.append(
        f'<line x1="{cx+inner_w}" y1="{cy}" x2="{cx}" y2="{cy+inner_w}" '
        f'stroke="#1a3050" stroke-width="0.6"/>'
    )
    # Om symbol in center
    center_x = cx + inner_w // 2
    center_y = cy + inner_w // 2
    lines.append(
        f'<text x="{center_x}" y="{center_y + int(8*scale)}" '
        f'font-size="{int(22*scale)}" fill="rgba(240,124,0,0.3)" '
        f'text-anchor="middle" font-weight="400">ॐ</text>'
    )

    lines.append('</svg>')
    return "\n".join(lines)


def compute_chart_svg(
    lagna_rashi: int,
    planet_positions: list[dict],
    width: int = 360,
    lang: str = "mr",
) -> str:
    """
    Convenience wrapper: takes list of planet_position dicts
    (as stored in DB JSONB) and renders SVG.
    """
    planet_rashis: dict[str, int] = {}
    retrogrades: set[str] = set()

    for pp in planet_positions:
        name = pp.get("planet_en", "")
        rashi_val = pp.get("rashi", {}).get("value", 0)
        planet_rashis[name] = rashi_val
        if pp.get("retrograde", False):
            retrogrades.add(name)

    return render_north_indian_svg(lagna_rashi, planet_rashis, retrogrades, width, lang)
