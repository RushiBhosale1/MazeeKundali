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
    # Outer planets (modern, used by some Maharashtrian astrologers)
    "Pluto":   "प्लु",
    "Neptune": "नेप",
    "Uranus":  "हर्ष",
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
    "Pluto":   "Plu",
    "Neptune": "Nep",
    "Uranus":  "Ura",
}

# Planet color coding (used only in dark/light theme)
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
    # Outer planets — muted gray (less prominent than classical 9)
    "Pluto":   "#8b5cf6",
    "Neptune": "#06b6d4",
    "Uranus":  "#10b981",
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
    planet_degrees: Optional[dict[str, float]] = None,  # planet -> degree within rashi
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

    # ── House center positions and rashi number positions ─────────────────────
    # Rashi numbers go in the CORNER of each house cell (matching expert format)
    HOUSE_POS = {
        # house: center for planets, rashi_pos for the house number
        1:  {"cx": M,             "cy": M * 0.48,        "rx": M,             "ry": 18.0 * scale,  "lagna": True},
        2:  {"cx": M * 0.38,      "cy": M * 0.22,        "rx": M * 0.58,      "ry": M * 0.28},
        3:  {"cx": M * 0.22,      "cy": M * 0.50,        "rx": M * 0.28,      "ry": M * 0.60},
        4:  {"cx": M * 0.48,      "cy": M,               "rx": M * 0.36,      "ry": M * 0.68},
        5:  {"cx": M * 0.22,      "cy": M * 1.50,        "rx": M * 0.28,      "ry": M * 1.40},
        6:  {"cx": M * 0.38,      "cy": M * 1.78,        "rx": M * 0.58,      "ry": M * 1.72},
        7:  {"cx": M,             "cy": M * 1.52,        "rx": M,             "ry": M * 1.92},
        8:  {"cx": M * 1.62,      "cy": M * 1.78,        "rx": M * 1.42,      "ry": M * 1.72},
        9:  {"cx": M * 1.78,      "cy": M * 1.50,        "rx": M * 1.72,      "ry": M * 1.40},
        10: {"cx": M * 1.52,      "cy": M,               "rx": M * 1.64,      "ry": M * 0.68},
        11: {"cx": M * 1.78,      "cy": M * 0.50,        "rx": M * 1.72,      "ry": M * 0.60},
        12: {"cx": M * 1.62,      "cy": M * 0.22,        "rx": M * 1.42,      "ry": M * 0.28},
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

    # ── Theme colors ──────────────────────────────────────────────────────────
    if theme == "dark":
        bg_color = "#0d1b2a"
        border_color = "#f07c00"
        grid_color = "#1a3050"
        rashi_text_color = "#64748b"
        lagna_color = "#f07c00"
        default_planet_color = "#e2e8f0"
        retrograde_color = "#94a3b8"
        degree_color = "#64748b"
    elif theme == "light":
        bg_color = "#ffffff"
        border_color = "#c47300"
        grid_color = "#d1d5db"
        rashi_text_color = "#9ca3af"
        lagna_color = "#c47300"
        default_planet_color = "#1e293b"
        retrograde_color = "#6b7280"
        degree_color = "#9ca3af"
    else:  # "bw" / print theme
        bg_color = "#ffffff"
        border_color = "#000000"
        grid_color = "#000000"
        rashi_text_color = "#999999"
        lagna_color = "#000000"
        default_planet_color = "#000000"
        retrograde_color = "#000000"
        degree_color = "#999999"

    # Background
    lines.append(f'<rect width="{width}" height="{width}" fill="{bg_color}" rx="6"/>')

    # Outer border
    lines.append(
        f'<rect x="1" y="1" width="{width-2}" height="{width-2}" fill="none" '
        f'stroke="{border_color}" stroke-width="1.5" rx="5"/>'
    )

    # Outer Diagonals (corner-to-corner)
    lines.append(f'<line x1="0" y1="0" x2="{width}" y2="{width}" stroke="{grid_color}" stroke-width="1"/>')
    lines.append(f'<line x1="{width}" y1="0" x2="0" y2="{width}" stroke="{grid_color}" stroke-width="1"/>')

    # Inner Rhombus (Diamond)
    lines.append(
        f'<polygon points="{round(M,1)},0 {width},{round(M,1)} {round(M,1)},{width} 0,{round(M,1)}" '
        f'fill="none" stroke="{border_color}" stroke-width="1.5"/>'
    )

    # Center Om symbol
    lines.append(
        f'<text x="{round(M,1)}" y="{round(M + 8*scale,1)}" '
        f'font-size="{round(24*scale,1)}" fill="{lagna_color}" opacity="0.25" '
        f'text-anchor="middle" font-weight="400">ॐ</text>'
    )

    # ── Render 12 Houses ─────────────────────────────────────────────────────
    for house_num in range(1, 13):
        pos = HOUSE_POS[house_num]
        rashi_idx = (lagna_rashi + house_num - 1) % 12
        rashi_num = rashi_idx + 1  # 1-12 display number

        rx, ry = pos["rx"], pos["ry"]
        cx, cy = pos["cx"], pos["cy"]

        # Rashi number (smaller, muted — corner of house)
        lines.append(
            f'<text x="{round(rx,1)}" y="{round(ry,1)}" '
            f'font-size="{round(10*scale,1)}" fill="{rashi_text_color}" '
            f'font-weight="600" text-anchor="middle">{rashi_num}</text>'
        )

        # House 1: "लग्न" label prominently
        if house_num == 1:
            lagna_label = "लग्न" if lang == "mr" else "Lagna"
            lines.append(
                f'<text x="{round(M,1)}" y="{round(36*scale,1)}" '
                f'font-size="{round(11*scale,1)}" fill="{lagna_color}" '
                f'font-weight="700" text-anchor="middle">{lagna_label}</text>'
            )

        # Planets in this house
        planets = house_planets[house_num]
        if planets:
            total = len(planets)
            line_h = min(14.0 * scale, (52.0 * scale) / max(total, 1))
            start_y = cy - ((total - 1) * line_h / 2.0)

            for pi, planet in enumerate(planets):
                py = start_y + pi * line_h
                glyph = planet_labels.get(planet, planet[:3])

                # Status mark: retrograde (ᵛ) > exaltation (↑) > debilitation (↓)
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
                    f'<text x="{round(cx,1)}" y="{round(py,1)}" '
                    f'font-size="{round(11.5*scale,1)}" fill="{pcolor}" '
                    f'font-weight="600" text-anchor="middle">{glyph}{mark}</text>'
                )

                # Show degree within rashi if provided
                if planet_degrees and planet in planet_degrees:
                    deg = planet_degrees[planet]
                    deg_str = f"{deg:.0f}°"
                    lines.append(
                        f'<text x="{round(cx,1)}" y="{round(py + 9*scale,1)}" '
                        f'font-size="{round(7.5*scale,1)}" fill="{degree_color}" '
                        f'text-anchor="middle">{deg_str}</text>'
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
    planet_degrees: Optional[dict[str, float]] = None,
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
        planet_degrees=planet_degrees,
    )
