"""
engine/svg_chart.py
SVG North Indian Diamond Kundali chart renderer (उत्तर भारतीय हिरा पद्धती).

Classical Vedic Astrology / Maharashtrian Diamond Chart Format:
  - Outer square with corner diagonals and central rhombus (diamond).
  - House 1 (Lagna) is ALWAYS fixed at the Top-Center Rhombus.
  - Houses 1 to 12 progress counter-clockwise.
  - Displays full Marathi planet names with exaltation (↑), debilitation (↓), and retrograde (ᵛ) indicators.
"""
from __future__ import annotations
import logging
from typing import Optional
from engine.models import Rashi

logger = logging.getLogger(__name__)

# Default canvas size
W = 360

# Planet full Marathi names (matches astrological tradition in Maharashtra)
PLANET_FULL_MR: dict[str, str] = {
    "Sun":     "रवि",
    "Moon":    "चंद्र",
    "Mars":    "मंगळ",
    "Mercury": "बुध",
    "Jupiter": "गुरु",
    "Venus":   "शुक्र",
    "Saturn":  "शनि",
    "Rahu":    "राहू",
    "Ketu":    "केतु",
}

# Planet English short names
PLANET_FULL_EN: dict[str, str] = {
    "Sun":     "Sun",
    "Moon":    "Mon",
    "Mars":    "Mar",
    "Mercury": "Mer",
    "Jupiter": "Jup",
    "Venus":   "Ven",
    "Saturn":  "Sat",
    "Rahu":    "Rah",
    "Ketu":    "Ket",
}

# Planet color coding
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
    """Whole-sign house: distance from lagna rashi (1-12)."""
    return (planet_rashi - lagna_rashi) % 12 + 1


def render_north_indian_svg(
    lagna_rashi: int,
    planet_rashis: dict[str, int],  # planet -> rashi index (0-11)
    retrogrades: Optional[set[str]] = None,
    exaltations: Optional[set[str]] = None,
    debilitations: Optional[set[str]] = None,
    width: int = 360,
    lang: str = "mr",
    theme: str = "dark",
    is_bhava_chalit: bool = False,
    planet_houses: Optional[dict[str, int]] = None,
) -> str:
    """
    Render authentic North Indian Diamond style Kundali chart as SVG.

    Layout (12 Diamond/Triangular Houses):
      H1  = Top Center Diamond (Lagna)
      H2  = Top-Left Triangle
      H3  = Left-Top Triangle
      H4  = Center-Left Diamond
      H5  = Left-Bottom Triangle
      H6  = Bottom-Left Triangle
      H7  = Bottom Center Diamond
      H8  = Bottom-Right Triangle
      H9  = Right-Bottom Triangle
      H10 = Center-Right Diamond
      H11 = Right-Top Triangle
      H12 = Top-Right Triangle
    """
    if retrogrades is None:
        retrogrades = set()
    if exaltations is None:
        exaltations = set()
    if debilitations is None:
        debilitations = set()

    W_float = float(width)
    scale = W_float / 360.0
    M = W_float / 2.0

    # Positions for house text, rashi numbers, and planet text
    HOUSE_POS = {
        1:  {"center": (M, M * 0.52),         "rashi_pos": (M, 24.0 * scale),      "lagna_pos": (M, 42.0 * scale)},
        2:  {"center": (M * 0.45, M * 0.22), "rashi_pos": (M * 0.62, M * 0.30)},
        3:  {"center": (M * 0.22, M * 0.45), "rashi_pos": (M * 0.30, M * 0.62)},
        4:  {"center": (M * 0.52, M),         "rashi_pos": (M * 0.42, M * 0.70)},
        5:  {"center": (M * 0.22, M * 1.55), "rashi_pos": (M * 0.30, M * 1.38)},
        6:  {"center": (M * 0.45, M * 1.78), "rashi_pos": (M * 0.62, M * 1.70)},
        7:  {"center": (M, M * 1.48),         "rashi_pos": (M, M * 1.88)},
        8:  {"center": (M * 1.55, M * 1.78), "rashi_pos": (M * 1.38, M * 1.70)},
        9:  {"center": (M * 1.78, M * 1.55), "rashi_pos": (M * 1.70, M * 1.38)},
        10: {"center": (M * 1.48, M),         "rashi_pos": (M * 1.58, M * 0.70)},
        11: {"center": (M * 1.78, M * 0.45), "rashi_pos": (M * 1.70, M * 0.62)},
        12: {"center": (M * 1.55, M * 0.22), "rashi_pos": (M * 1.38, M * 0.30)},
    }

    planet_labels = PLANET_FULL_MR if lang == "mr" else PLANET_FULL_EN

    # Group planets by house (1-12)
    house_planets: dict[int, list[str]] = {i: [] for i in range(1, 13)}
    if is_bhava_chalit and planet_houses:
        for p, h in planet_houses.items():
            if 1 <= h <= 12:
                house_planets[h].append(p)
    else:
        for p, pr in planet_rashis.items():
            h = (pr - lagna_rashi) % 12 + 1
            house_planets[h].append(p)

    lines: list[str] = []
    lines.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{width}" '
        f'viewBox="0 0 {width} {width}" font-family="Noto Sans Devanagari,Inter,sans-serif">'
    )

    if theme == "dark":
        bg_color = "#0d1b2a"
        border_color = "#f07c00"
        grid_color = "#1a3050"
        rashi_text_color = "#7a7268"
        lagna_color = "#f07c00"
        default_planet_color = "#e2e8f0"
    elif theme == "light":
        bg_color = "#ffffff"
        border_color = "#f07c00"
        grid_color = "#e5e7eb"
        rashi_text_color = "#6b7280"
        lagna_color = "#f07c00"
        default_planet_color = "#1e293b"
    else:  # "bw" / print theme
        bg_color = "#ffffff"
        border_color = "#000000"
        grid_color = "#000000"
        rashi_text_color = "#000000"
        lagna_color = "#000000"
        default_planet_color = "#000000"

    # Background
    lines.append(f'<rect width="{width}" height="{width}" fill="{bg_color}" rx="8"/>')

    # Outer border
    lines.append(
        f'<rect x="1" y="1" width="{width-2}" height="{width-2}" fill="none" '
        f'stroke="{border_color}" stroke-width="1.5" rx="7"/>'
    )

    # Outer Diagonals
    lines.append(
        f'<line x1="0" y1="0" x2="{width}" y2="{width}" stroke="{grid_color}" stroke-width="1"/>'
    )
    lines.append(
        f'<line x1="{width}" y1="0" x2="0" y2="{width}" stroke="{grid_color}" stroke-width="1"/>'
    )

    # Inner Rhombus (Diamond)
    lines.append(
        f'<polygon points="{round(M, 1)},0 {width},{round(M, 1)} {round(M, 1)},{width} 0,{round(M, 1)}" '
        f'fill="none" stroke="{border_color}" stroke-width="1.5"/>'
    )

    # Center Om symbol
    lines.append(
        f'<text x="{round(M, 1)}" y="{round(M + 7*scale, 1)}" '
        f'font-size="{round(22*scale, 1)}" fill="{lagna_color}" opacity="0.3" '
        f'text-anchor="middle" font-weight="400">ॐ</text>'
    )

    # Render 12 Houses
    for house_num in range(1, 13):
        pos = HOUSE_POS[house_num]
        rashi_idx = (lagna_rashi + house_num - 1) % 12
        rashi_num = rashi_idx + 1  # 1-12 for display

        # Rashi number
        rx, ry = pos["rashi_pos"]
        lines.append(
            f'<text x="{round(rx, 1)}" y="{round(ry, 1)}" '
            f'font-size="{round(10.5*scale, 1)}" fill="{rashi_text_color}" '
            f'font-weight="600" text-anchor="middle">{rashi_num}</text>'
        )

        # Lagna marker in House 1
        if house_num == 1:
            lx, ly = pos["lagna_pos"]
            lagna_label = "लग्न" if lang == "mr" else "Lagna"
            lines.append(
                f'<text x="{round(lx, 1)}" y="{round(ly, 1)}" '
                f'font-size="{round(11*scale, 1)}" fill="{lagna_color}" '
                f'font-weight="700" text-anchor="middle">{lagna_label}</text>'
            )

        # Planets in this house
        planets = house_planets[house_num]
        if planets:
            cx, cy = pos["center"]
            total = len(planets)
            step = min(15.0 * scale, (60.0 * scale) / max(total, 1))
            start_y = cy - ((total - 1) * step / 2.0)

            for pi, planet in enumerate(planets):
                py = start_y + pi * step
                glyph = planet_labels.get(planet, planet[:2])

                # Status mark (retrograde / exaltation / debilitation)
                mark = ""
                if planet in retrogrades:
                    mark = "ᵛ"
                elif planet in exaltations:
                    mark = "↑"
                elif planet in debilitations:
                    mark = "↓"

                if theme == "bw":
                    pcolor = "#000000"
                else:
                    pcolor = PLANET_COLOR.get(planet, default_planet_color)

                lines.append(
                    f'<text x="{round(cx, 1)}" y="{round(py, 1)}" '
                    f'font-size="{round(11.5*scale, 1)}" fill="{pcolor}" '
                    f'font-weight="600" text-anchor="middle">{glyph}{mark}</text>'
                )

    lines.append('</svg>')
    return "\n".join(lines)


def compute_chart_svg(
    lagna_rashi: int,
    planet_rashis: dict[str, int],
    retrogrades: Optional[set[str]] = None,
    exaltations: Optional[set[str]] = None,
    debilitations: Optional[set[str]] = None,
    width: int = 360,
    lang: str = "mr",
    theme: str = "dark",
    is_bhava_chalit: bool = False,
    planet_houses: Optional[dict[str, int]] = None,
) -> str:
    """Wrapper function returning chart SVG."""
    return render_north_indian_svg(
        lagna_rashi=lagna_rashi,
        planet_rashis=planet_rashis,
        retrogrades=retrogrades,
        exaltations=exaltations,
        debilitations=debilitations,
        width=width,
        lang=lang,
        theme=theme,
        is_bhava_chalit=is_bhava_chalit,
        planet_houses=planet_houses,
    )
