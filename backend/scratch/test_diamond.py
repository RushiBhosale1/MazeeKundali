import os
from engine.models import Rashi

def render_north_indian_diamond_svg(
    lagna_rashi: int,
    planet_rashis: dict[str, int],
    retrogrades: set[str] = None,
    exaltations: set[str] = None,
    debilitations: set[str] = None,
    width: int = 360,
    lang: str = "mr",
    theme: str = "dark",
    is_bhava_chalit: bool = False,
    planet_houses: dict[str, int] = None,
) -> str:
    if retrogrades is None:
        retrogrades = set()
    if exaltations is None:
        exaltations = set()
    if debilitations is None:
        debilitations = set()

    W = float(width)
    scale = W / 360.0
    M = W / 2.0

    # House centers & text positions in North Indian Diamond Chart
    # House 1 = Top Center Rhombus
    # House 2 = Top-Left Triangle, etc. (counter-clockwise)
    HOUSE_POS = {
        1:  {"center": (M, M * 0.5),      "rashi_pos": (M, 24 * scale),      "lagna_pos": (M, 42 * scale)},
        2:  {"center": (M * 0.45, M * 0.22), "rashi_pos": (M * 0.58, M * 0.30)},
        3:  {"center": (M * 0.22, M * 0.45), "rashi_pos": (M * 0.30, M * 0.58)},
        4:  {"center": (M * 0.5, M),      "rashi_pos": (M * 0.42, M * 0.70)},
        5:  {"center": (M * 0.22, M * 1.55), "rashi_pos": (M * 0.30, M * 1.42)},
        6:  {"center": (M * 0.45, M * 1.78), "rashi_pos": (M * 0.58, M * 1.70)},
        7:  {"center": (M, M * 1.5),      "rashi_pos": (M, M * 1.88)},
        8:  {"center": (M * 1.55, M * 1.78), "rashi_pos": (M * 1.42, M * 1.70)},
        9:  {"center": (M * 1.78, M * 1.55), "rashi_pos": (M * 1.70, M * 1.42)},
        10: {"center": (M * 1.5, M),      "rashi_pos": (M * 1.58, M * 0.70)},
        11: {"center": (M * 1.78, M * 0.45), "rashi_pos": (M * 1.70, M * 0.58)},
        12: {"center": (M * 1.55, M * 0.22), "rashi_pos": (M * 1.42, M * 0.30)},
    }

    PLANET_MR = {
        "Sun": "रवि", "Moon": "चंद्र", "Mars": "मंगळ",
        "Mercury": "बुध", "Jupiter": "गुरु", "Venus": "शुक्र",
        "Saturn": "शनि", "Rahu": "राहू", "Ketu": "केतु",
    }

    # Group planets by house (1-12)
    house_planets = {i: [] for i in range(1, 13)}
    if is_bhava_chalit and planet_houses:
        for p, h in planet_houses.items():
            if 1 <= h <= 12:
                house_planets[h].append(p)
    else:
        for p, pr in planet_rashis.items():
            h = (pr - lagna_rashi) % 12 + 1
            house_planets[h].append(p)

    lines = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{int(W)}" height="{int(W)}" viewBox="0 0 {int(W)} {int(W)}" font-family="Noto Sans Devanagari,Inter,sans-serif">')

    bg_color = "#0d1b2a" if theme == "dark" else "#ffffff"
    border_color = "#f07c00" if theme in ["dark", "light"] else "#000000"
    grid_color = "#1a3050" if theme == "dark" else ("#e5e7eb" if theme == "light" else "#000000")

    lines.append(f'<rect width="{int(W)}" height="{int(W)}" fill="{bg_color}" rx="8"/>')
    lines.append(f'<rect x="1" y="1" width="{int(W-2)}" height="{int(W-2)}" fill="none" stroke="{border_color}" stroke-width="1.5" rx="7"/>')

    # Diagonals
    lines.append(f'<line x1="0" y1="0" x2="{int(W)}" y2="{int(W)}" stroke="{grid_color}" stroke-width="1"/>')
    lines.append(f'<line x1="{int(W)}" y1="0" x2="0" y2="{int(W)}" stroke="{grid_color}" stroke-width="1"/>')

    # Rhombus
    lines.append(f'<polygon points="{int(M)},0 {int(W)},{int(M)} {int(M)},{int(W)} 0,{int(M)}" fill="none" stroke="{border_color}" stroke-width="1.5"/>')

    # Om symbol in center
    om_color = "#f07c00" if theme in ["dark", "light"] else "#000000"
    lines.append(f'<text x="{int(M)}" y="{int(M+8*scale)}" font-size="{int(22*scale)}" fill="{om_color}" opacity="0.35" text-anchor="middle" font-weight="400">ॐ</text>')

    # Render Houses
    for house_num in range(1, 13):
        pos = HOUSE_POS[house_num]
        rashi_idx = (lagna_rashi + house_num - 1) % 12
        rashi_num = rashi_idx + 1

        rx, ry = pos["rashi_pos"]
        txt_color = "#7a7268" if theme == "dark" else "#6b7280"
        lines.append(f'<text x="{round(rx, 1)}" y="{round(ry, 1)}" font-size="{round(11*scale, 1)}" fill="{txt_color}" font-weight="600" text-anchor="middle">{rashi_num}</text>')

        if house_num == 1:
            lx, ly = pos["lagna_pos"]
            lines.append(f'<text x="{round(lx, 1)}" y="{round(ly, 1)}" font-size="{round(11*scale, 1)}" fill="{border_color}" font-weight="700" text-anchor="middle">लग्न</text>')

        # Planets in this house
        planets = house_planets[house_num]
        if planets:
            cx, cy = pos["center"]
            total = len(planets)
            start_y = cy - ((total - 1) * 8 * scale)
            for pi, planet in enumerate(planets):
                py = start_y + pi * 16 * scale
                glyph = PLANET_MR.get(planet, planet[:2])
                mark = ""
                if planet in retrogrades:
                    mark = "ᵛ"
                elif planet in exaltations:
                    mark = "↑"
                elif planet in debilitations:
                    mark = "↓"
                
                pcolor = "#f07c00" if theme in ["dark", "light"] else "#000000"
                lines.append(f'<text x="{round(cx, 1)}" y="{round(py, 1)}" font-size="{round(11.5*scale, 1)}" fill="{pcolor}" font-weight="600" text-anchor="middle">{glyph}{mark}</text>')

    lines.append('</svg>')
    return "\n".join(lines)

svg = render_north_indian_diamond_svg(0, {"Sun": 0, "Moon": 1, "Mars": 2})
print("SVG Generated successfully, length:", len(svg))
