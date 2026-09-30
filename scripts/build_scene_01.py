#!/usr/bin/env python3
"""Build one modular night-desk validation scene from independent SVG assets."""

from __future__ import annotations

import io
import json
import sys
from dataclasses import dataclass, replace
from pathlib import Path
from xml.sax.saxutils import escape

import cairosvg
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_motif_bot import DEFS as BOT_DEFS, assemble_pose  # noqa: E402

ASSETS = ROOT / "assets/scenes/scene-01"
SCENE = ROOT / "scenes/scene-01"
PREVIEWS = ROOT / "previews/scene-01"
W, H = 1080, 1920

P = {
    "paper": "#F4EBD8", "edge": "#DCCDB3", "ink": "#202C32",
    "teal": "#56BFB1", "tealDark": "#318E85", "mint": "#A6E5D6",
    "coral": "#DF806B", "gold": "#EBC46B", "plum": "#554565",
    "night": "#172C3E", "night2": "#254D50", "wood": "#9A735D",
    "woodEdge": "#725343", "wall": "#62546A", "wallDark": "#4A3E57",
    "shadow": "#252A32", "mist": "#CBD7D0",
}

DEFS = f"""<defs>
<pattern id="sceneGrain" width="43" height="39" patternUnits="userSpaceOnUse">
 <circle cx="7" cy="9" r="1.1" fill="{P['paper']}" opacity=".13"/>
 <circle cx="30" cy="20" r=".8" fill="{P['paper']}" opacity=".12"/>
 <circle cx="17" cy="33" r="1" fill="{P['ink']}" opacity=".11"/>
 <path d="M25 5 l3 .5 M4 28 l2 -.5" stroke="{P['paper']}" stroke-width=".8" opacity=".16"/>
 <ellipse cx="38" cy="31" rx="2.4" ry=".8" fill="{P['paper']}" opacity=".11"/>
 <path d="M14 19 l4 -.7 M34 8 l-2 1.4" stroke="{P['ink']}" stroke-width=".7" opacity=".13"/>
</pattern>
<pattern id="paperSpeckle" width="29" height="31" patternUnits="userSpaceOnUse">
 <circle cx="5" cy="7" r=".8" fill="{P['woodEdge']}" opacity=".18"/>
 <circle cx="19" cy="17" r="1.1" fill="{P['woodEdge']}" opacity=".13"/>
 <path d="M10 26 l3 -.5" stroke="{P['woodEdge']}" stroke-width=".7" opacity=".13"/>
 <ellipse cx="24" cy="5" rx="1.9" ry=".7" fill="{P['woodEdge']}" opacity=".13"/>
 <path d="M3 19 l2 .8 M20 28 l2 -1" stroke="{P['woodEdge']}" stroke-width=".6" opacity=".14"/>
</pattern>
<pattern id="woodFiber" width="59" height="41" patternUnits="userSpaceOnUse">
 <path d="M5 12 q13 -3 26 0 M34 29 q10 2 19 -1 M16 34 l8 -1" fill="none" stroke="{P['woodEdge']}" stroke-width="1.3" opacity=".18"/>
 <circle cx="47" cy="10" r="1" fill="{P['paper']}" opacity=".18"/>
 <circle cx="9" cy="28" r=".8" fill="{P['ink']}" opacity=".12"/>
</pattern>
</defs>"""


def svg(w: int, h: int, body: str, title: str, defs: str = DEFS) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">\n'
            f'<title>{escape(title)}</title>\n{defs}\n{body}\n</svg>\n')


def txt(x: int, y: int, value: str, size: int = 22, fill: str = P["ink"],
        weight: int = 700, spacing: int | None = None) -> str:
    extra = f' letter-spacing="{spacing}"' if spacing is not None else ""
    return (f'<text x="{x}" y="{y}" font-family="DejaVu Sans, Arial, sans-serif" '
            f'font-size="{size}" font-weight="{weight}" fill="{fill}"{extra}>'
            f'{escape(value)}</text>')


def paper_path(d: str, fill: str = P["paper"], grain: str = "paperSpeckle",
               shadow: bool = True) -> str:
    under = (f'<path d="{d}" transform="translate(6 8)" fill="{P["shadow"]}" opacity=".19"/>'
             f'<path d="{d}" transform="translate(2 4)" fill="{P["edge"]}" opacity=".6"/>') if shadow else ""
    return (under + f'<path d="{d}" fill="{fill}"/>'
            f'<path d="{d}" fill="url(#{grain})" opacity=".72"/>'
            f'<path d="{d}" fill="none" stroke="{P["edge"]}" stroke-width="2" opacity=".38"/>')


def card(x: int, y: int, w: int, h: int, r: int, fill: str = P["paper"],
         grain: str = "paperSpeckle", shadow: bool = True) -> str:
    # Small deterministic edge drift, kept below what would hurt phone-size read.
    d = (f'M{x+r} {y+1} Q{x+w*.47:.1f} {y-2} {x+w-r} {y+1} '
         f'Q{x+w+1} {y+2} {x+w} {y+r} '
         f'Q{x+w+2} {y+h*.47:.1f} {x+w-1} {y+h-r} '
         f'Q{x+w-2} {y+h+1} {x+w-r} {y+h} '
         f'Q{x+w*.54:.1f} {y+h+2} {x+r} {y+h-1} '
         f'Q{x-1} {y+h-2} {x} {y+h-r} '
         f'Q{x-2} {y+h*.43:.1f} {x+1} {y+r} '
         f'Q{x+2} {y+2} {x+r} {y+1} Z')
    return paper_path(d, fill, grain, shadow)


def line(d: str, color: str, width: int, opacity: float = 1,
         dash: str | None = None) -> str:
    a = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" '
            f'opacity="{opacity}" stroke-linecap="round" stroke-linejoin="round"{a}/>')


@dataclass(frozen=True)
class Asset:
    slug: str
    category: str
    name: str
    w: int
    h: int
    x: int
    y: int
    layer: str
    body: str
    anchors: dict[str, tuple[float, float]]
    concepts: tuple[str, ...]

    @property
    def file(self) -> Path:
        return ASSETS / self.category / f"{self.slug}.svg"

    def placed(self) -> str:
        # Read the exported SVG so the composite is built from the independent
        # asset files, not merely the in-memory drawing definitions.
        exported = self.file.read_text()
        body = exported.split("</defs>", 1)[1].rsplit("</svg>", 1)[0].strip()
        return (f'<g id="{self.slug}" data-asset="{self.file.relative_to(ROOT)}" '
                f'transform="translate({self.x} {self.y})">{body}</g>')


def environment() -> list[Asset]:
    wall = (
        f'<path d="M0 0 H1080 V1472 Q735 1462 520 1473 Q290 1465 0 1472 Z" fill="{P["wall"]}"/>'
        f'<path d="M0 0 H1080 V1472 Q735 1462 520 1473 Q290 1465 0 1472 Z" fill="url(#sceneGrain)" opacity=".7"/>'
        f'<path d="M81 272 Q376 263 675 275 Q891 267 1020 278 L1020 1013 Q719 1003 477 1017 Q283 1006 81 1014 Z" fill="{P["paper"]}" opacity=".025"/>'
        f'<path d="M82 277 Q392 269 652 280 M88 1011 Q462 1004 824 1010" fill="none" stroke="{P["paper"]}" stroke-width="3" opacity=".075"/>'
        f'<path d="M0 0 H81 V1460 H0 Z" fill="{P["wallDark"]}" opacity=".28"/>'
        f'<path d="M1020 0 H1080 V1466 H1020 Z" fill="{P["wallDark"]}" opacity=".19"/>'
        f'{line("M0 1453 Q535 1445 1080 1454", P["paper"], 4, .12)}'
        f'<path d="M0 0 H1080 V262 Q741 255 531 268 Q264 259 0 266 Z" fill="{P["wallDark"]}" opacity=".14"/>'
    )
    floor = (
        f'<path d="M0 1 Q243 -3 479 2 Q798 -5 1080 1 V520 H0 Z" fill="{P["wood"]}"/>'
        f'<path d="M0 1 Q243 -3 479 2 Q798 -5 1080 1 V520 H0 Z" fill="url(#woodFiber)" opacity=".85"/>'
        f'<path d="M0 1 Q243 -3 479 2 Q798 -5 1080 1 V25 Q531 17 0 26 Z" fill="{P["woodEdge"]}"/>'
        f'{line("M0 220 Q282 215 551 219 Q833 213 1080 223", P["woodEdge"], 3, .32)}'
        f'{line("M315 218 Q299 365 278 520 M789 218 Q815 350 840 520", P["woodEdge"], 3, .21)}'
        f'<ellipse cx="530" cy="198" rx="470" ry="80" fill="{P["shadow"]}" opacity=".13"/>'
        f'<path d="M0 372 Q298 366 519 373 Q844 363 1080 373 V520 H0 Z" fill="{P["woodEdge"]}" opacity=".12"/>'
    )
    sky = (
        f'{card(0, 0, 290, 342, 18, P["night"], "sceneGrain", False)}'
        f'<path d="M0 242 Q80 211 153 242 Q235 217 290 237 V342 H0 Z" fill="{P["night2"]}"/>'
        f'<circle cx="184" cy="80" r="45" fill="{P["gold"]}" opacity=".18"/>'
        f'<path d="M163 42 Q199 30 217 66 Q226 100 194 119 Q157 126 142 94 Q135 64 163 42 Z" fill="{P["paper"]}"/>'
        f'<path d="M163 42 Q199 30 217 66 Q226 100 194 119 Q157 126 142 94 Q135 64 163 42 Z" fill="url(#paperSpeckle)" opacity=".55"/>'
        f'<circle cx="59" cy="70" r="3" fill="{P["mint"]}"/><circle cx="88" cy="124" r="2" fill="{P["paper"]}"/>'
        f'<circle cx="254" cy="151" r="2.5" fill="{P["mint"]}"/>'
        f'<path d="M0 275 L23 275 V251 H53 V271 H75 V234 H109 V271 H131 V251 H165 V273 H198 V239 H227 V268 H290 V342 H0 Z" fill="{P["night"]}"/>'
        f'<path d="M23 287 h4 m20 -3 h4 m42 6 h4 m106 -3 h4 m23 14 h4" stroke="{P["gold"]}" stroke-width="3" opacity=".63"/>'
    )
    window = (
        f'<path d="M22 12 Q158 -1 304 10 L319 22 V356 Q164 370 14 357 L10 23 Z" '
        f'fill="{P["shadow"]}" opacity=".2" transform="translate(6 9)"/>'
        f'<path d="M22 12 Q158 -1 304 10 L319 22 V356 Q164 370 14 357 L10 23 Z '
        f'M43 35 L43 328 Q160 335 286 328 V35 Q165 27 43 35 Z" fill="{P["paper"]}" fill-rule="evenodd"/>'
        f'<path d="M22 12 Q158 -1 304 10 L319 22 V356 Q164 370 14 357 L10 23 Z '
        f'M43 35 L43 328 Q160 335 286 328 V35 Q165 27 43 35 Z" fill="url(#paperSpeckle)" fill-rule="evenodd" opacity=".63"/>'
        f'<path d="M165 31 Q161 174 164 330" stroke="{P["edge"]}" stroke-width="18" fill="none"/>'
        f'<path d="M40 184 Q163 180 288 184" stroke="{P["edge"]}" stroke-width="16" fill="none"/>'
        f'<path d="M164 35 Q163 169 164 327 M43 186 Q157 182 282 185" stroke="{P["paper"]}" stroke-width="9" fill="none" opacity=".82"/>'
        f'<path d="M-8 349 Q169 356 336 348 L326 373 Q161 381 -13 373 Z" fill="{P["paper"]}"/>'
        f'<path d="M-8 349 Q169 356 336 348 L326 373 Q161 381 -13 373 Z" fill="url(#paperSpeckle)" opacity=".56"/>'
        f'<path d="M-8 349 Q169 356 336 348 L326 373 Q161 381 -13 373 Z" fill="none" stroke="{P["edge"]}" stroke-width="2" opacity=".5"/>'
        f'{line("M-9 373 Q153 381 327 373", P["edge"], 7, .67)}'
    )
    return [
        Asset("wall-background", "environment", "Textured night wall", 1080, 1475, 0, 0, "background", wall, {}, ("room", "night", "paper")),
        Asset("floor", "environment", "Cut-paper floor", 1080, 520, 0, 1450, "background", floor, {}, ("floor", "stage")),
        Asset("night-sky-moon", "environment", "Night sky, moon and city", 290, 342, 132, 398, "background", sky, {}, ("night", "moon", "city")),
        Asset("window", "environment", "Paper window frame", 336, 380, 112, 385, "midground", window, {}, ("window", "room")),
    ]


def furniture() -> list[Asset]:
    chair = (
        f'{card(41, 7, 190, 235, 35, P["night2"], "sceneGrain")}'
        f'<path d="M68 35 Q142 26 203 35 L202 194 Q143 205 66 193 Z" fill="{P["wallDark"]}" opacity=".22"/>'
        f'<path d="M70 214 Q146 201 224 214 L235 254 Q142 269 53 252 Z" fill="{P["tealDark"]}"/>'
        f'<path d="M141 254 L143 329 M83 329 H207" stroke="{P["ink"]}" stroke-width="13" fill="none" stroke-linecap="round"/>'
        f'<ellipse cx="141" cy="335" rx="85" ry="10" fill="{P["shadow"]}" opacity=".13"/>'
    )
    desk = (
        f'<ellipse cx="463" cy="360" rx="447" ry="32" fill="{P["shadow"]}" opacity=".19"/>'
        f'<path d="M65 122 L112 123 L121 384 L81 384 Z M805 120 L856 122 L862 384 L820 383 Z" fill="{P["woodEdge"]}"/>'
        f'<path d="M38 73 Q440 54 901 75 L924 117 Q471 136 20 116 Z" fill="{P["shadow"]}" opacity=".19" transform="translate(7 10)"/>'
        f'<path d="M38 73 Q440 54 901 75 L924 117 Q471 136 20 116 Z" fill="{P["wood"]}"/>'
        f'<path d="M38 73 Q440 54 901 75 L924 117 Q471 136 20 116 Z" fill="url(#woodFiber)" opacity=".88"/>'
        f'<path d="M20 116 Q245 127 476 133 Q708 131 924 117 L917 177 Q697 190 468 189 Q236 187 29 176 Z" fill="{P["woodEdge"]}"/>'
        f'<path d="M20 116 Q245 127 476 133 Q708 131 924 117 L917 177 Q697 190 468 189 Q236 187 29 176 Z" fill="url(#woodFiber)" opacity=".6"/>'
        f'{line("M49 166 Q259 180 481 179 Q702 183 895 164", P["paper"], 3, .2)}'
        f'{line("M44 80 Q364 64 703 75", P["paper"], 3, .16)}'
    )
    return [
        Asset("chair", "furniture", "Simple desk chair", 275, 345, 320, 1040, "midground", chair,
              {"seat": (.51, .70)}, ("chair", "seat")),
        Asset("desk", "furniture", "Wide paper and wood desk", 945, 390, 68, 1215, "foreground", desk,
              {"surface": (.50, .21)}, ("desk", "workstation")),
    ]


def computing() -> list[Asset]:
    laptop = (
        f'<path d="M28 8 Q147 0 267 11 L270 176 Q143 181 23 177 Z" fill="{P["shadow"]}" opacity=".18" transform="translate(5 6)"/>'
        f'{paper_path("M40 8 Q149 3 253 10 Q268 12 269 27 L270 166 Q268 179 254 181 Q144 184 37 178 Q24 176 23 164 L24 25 Q26 10 40 8 Z", P["edge"])}'
        f'{card(37, 20, 220, 144, 8, P["ink"], "sceneGrain", False)}'
        f'<circle cx="48" cy="34" r="4" fill="{P["coral"]}"/><circle cx="62" cy="34" r="4" fill="{P["gold"]}"/>'
        f'<circle cx="76" cy="34" r="4" fill="{P["teal"]}"/>'
        f'{line("M55 66 H162 M55 89 H207 M55 112 H182", P["teal"], 6, .72)}'
        f'{line("M55 76 H119 M55 99 H162 M55 122 H144", P["paper"], 4, .53)}'
        f'<path d="M12 178 L279 178 L295 214 Q148 228 0 215 Z" fill="{P["paper"]}"/>'
        f'<path d="M12 178 L279 178 L295 214 Q148 228 0 215 Z" fill="url(#paperSpeckle)" opacity=".75"/>'
        f'{line("M0 215 Q142 229 295 214", P["edge"], 3, .68)}'
        f'{line("M45 193 H247", P["edge"], 5, .85)}'
        f'<rect x="118" y="207" width="60" height="9" rx="4" fill="{P["edge"]}"/>'
    )
    monitor = (
        f'<path d="M22 10 Q178 -1 326 11 L337 27 V254 Q166 269 7 252 V27 Z" fill="{P["shadow"]}" opacity=".19" transform="translate(7 8)"/>'
        f'{paper_path("M31 7 Q173 1 317 9 Q334 11 338 28 L338 242 Q335 261 317 266 Q170 274 25 264 Q8 260 7 244 L9 28 Q10 12 31 7 Z")}'
        f'{card(22, 21, 300, 226, 11, P["ink"], "sceneGrain", False)}'
        f'<circle cx="171" cy="256" r="4" fill="{P["tealDark"]}"/>'
        f'<path d="M148 269 L195 269 L202 313 H140 Z" fill="{P["edge"]}"/>'
        f'<path d="M91 316 Q171 308 251 316 L263 334 Q175 345 80 334 Z" fill="{P["paper"]}"/>'
        f'<path d="M91 316 Q171 308 251 316 L263 334 Q175 345 80 334 Z" fill="url(#paperSpeckle)" opacity=".72"/>'
    )
    keyboard = (
        f'<path d="M13 11 Q153 -1 303 11 L319 49 Q168 62 0 51 Z" fill="{P["shadow"]}" opacity=".17" transform="translate(3 5)"/>'
        f'{paper_path("M13 11 Q154 1 303 10 L319 49 Q161 62 0 51 Z")}'
        + "".join(
            f'<rect x="{21+c*27+((c*7+r*3)%5)-2}" y="{18+r*13+((c*3+r)%3)-1}" '
            f'width="{20+(c+r)%3}" height="{8+(c*2+r)%2}" rx="2" '
            f'transform="rotate({(-1,0,1)[(c+r)%3]} {31+c*27} {23+r*13})" fill="{P["edge"]}"/>'
            for r in range(2) for c in range(11)
        )
        + f'<rect x="96" y="46" width="126" height="5" rx="2" fill="{P["edge"]}"/>'
    )
    mouse = (
        f'<ellipse cx="35" cy="49" rx="30" ry="12" fill="{P["shadow"]}" opacity=".16"/>'
        f'<path d="M35 5 Q66 7 66 37 Q64 60 34 60 Q6 59 5 38 Q4 9 35 5 Z" fill="{P["paper"]}"/>'
        f'<path d="M35 5 Q66 7 66 37 Q64 60 34 60 Q6 59 5 38 Q4 9 35 5 Z" fill="url(#paperSpeckle)" opacity=".56"/>'
        f'{line("M35 9 V28", P["edge"], 3, .8)}'
        f'<path d="M30 20 Q36 16 41 20" stroke="{P["tealDark"]}" stroke-width="4" fill="none"/>'
    )
    return [
        Asset("laptop", "computing", "Open coding laptop", 295, 225, 150, 1070, "midground", laptop,
              {"screenContent": (.50, .40), "keyboard": (.50, .85)}, ("laptop", "coding")),
        Asset("desktop-monitor", "computing", "Desktop monitor shell", 345, 345, 610, 925, "midground", monitor,
              {"screenContent": (.50, .39), "surface": (.50, .96)}, ("monitor", "screen")),
        Asset("keyboard", "computing", "Paper key keyboard", 320, 65, 570, 1257, "foreground", keyboard,
              {"surface": (.50, .50)}, ("keyboard", "typing")),
        Asset("mouse", "computing", "Simple desk mouse", 72, 65, 892, 1255, "foreground", mouse,
              {"surface": (.50, .50)}, ("mouse", "computer")),
    ]


def desk_props() -> list[Asset]:
    lamp = (
        f'<path d="M47 317 Q76 307 107 315 L127 335 Q80 349 29 335 Z" fill="{P["shadow"]}" opacity=".16"/>'
        f'<path d="M78 311 L111 179 L54 126" stroke="{P["edge"]}" stroke-width="15" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<circle cx="111" cy="180" r="15" fill="{P["tealDark"]}"/>'
        f'<path d="M25 89 Q51 59 97 82 L128 143 Q100 161 48 149 Z" fill="{P["paper"]}"/>'
        f'<path d="M25 89 Q51 59 97 82 L128 143 Q100 161 48 149 Z" fill="url(#paperSpeckle)" opacity=".6"/>'
        f'<path d="M48 149 Q90 158 128 143" stroke="{P["gold"]}" stroke-width="8" fill="none"/>'
        f'<path d="M56 159 L8 309 L154 309 L119 160 Z" fill="{P["gold"]}" opacity=".075"/>'
        f'<ellipse cx="76" cy="331" rx="55" ry="11" fill="{P["tealDark"]}"/>'
        f'<ellipse cx="76" cy="326" rx="55" ry="11" fill="{P["paper"]}"/>'
        f'<circle cx="81" cy="93" r="6" fill="{P["tealDark"]}"/>'
    )
    mug = (
        f'<ellipse cx="51" cy="100" rx="49" ry="11" fill="{P["shadow"]}" opacity=".15"/>'
        f'<path d="M15 21 Q51 16 89 22 L83 91 Q50 103 19 89 Z" fill="{P["paper"]}"/>'
        f'<path d="M15 21 Q51 16 89 22 L83 91 Q50 103 19 89 Z" fill="url(#paperSpeckle)" opacity=".6"/>'
        f'<path d="M83 32 Q121 28 111 61 Q105 82 84 74" fill="none" stroke="{P["paper"]}" stroke-width="13"/>'
        f'<ellipse cx="51" cy="23" rx="37" ry="10" fill="{P["edge"]}"/>'
        f'<ellipse cx="51" cy="21" rx="29" ry="6" fill="{P["woodEdge"]}"/>'
        f'<path d="M31 53 H69" stroke="{P["tealDark"]}" stroke-width="6" stroke-linecap="round"/>'
    )
    clock = (
        f'{paper_path("M70 5 Q115 3 134 43 Q150 82 124 115 Q98 142 62 135 Q22 132 7 98 Q-7 62 20 25 Q39 5 70 5 Z")}'
        f'<path d="M69 18 Q110 17 122 53 Q133 90 105 113 Q74 134 43 113 Q16 93 19 63 Q22 28 69 18 Z" fill="none" stroke="{P["edge"]}" stroke-width="3" opacity=".86"/>'
        f'<circle cx="70" cy="70" r="5" fill="{P["tealDark"]}"/>'
        f'{line("M70 70 L104 65 M70 70 L88 51", P["ink"], 6)}'
        + "".join(f'<circle cx="{x}" cy="{y}" r="3.3" fill="{P["tealDark"]}"/>' for x,y in [(70,25),(115,70),(70,115),(25,70)])
        + card(28, 132, 84, 27, 5, P["paper"])
        + txt(35, 153, "02:14", 20, P["ink"], 700)
    )
    document = (
        f'<path d="M10 5 Q67 -2 128 8 L139 97 Q70 106 4 94 Z" fill="{P["shadow"]}" opacity=".17" transform="translate(4 5)"/>'
        f'<path d="M10 5 Q67 -2 128 8 L139 97 Q70 106 4 94 Z" fill="{P["paper"]}"/>'
        f'<path d="M10 5 Q67 -2 128 8 L139 97 Q70 106 4 94 Z" fill="url(#paperSpeckle)" opacity=".6"/>'
        + txt(21, 31, "NOTES", 16, P["ink"], 700)
        + f'<path d="M22 46 l6 6 9 -12 M22 69 l6 6 9 -12" fill="none" stroke="{P["tealDark"]}" stroke-width="4" stroke-linecap="round"/>'
        + f'{line("M47 48 H108 M47 70 H95", P["edge"], 5, .9)}'
    )
    plant = (
        f'<ellipse cx="58" cy="123" rx="53" ry="12" fill="{P["shadow"]}" opacity=".13"/>'
        f'<path d="M27 67 Q61 76 93 67 L84 116 Q61 126 34 116 Z" fill="{P["paper"]}"/>'
        f'<path d="M27 67 Q61 76 93 67 L84 116 Q61 126 34 116 Z" fill="url(#paperSpeckle)" opacity=".62"/>'
        f'<path d="M21 65 Q61 77 99 65" fill="none" stroke="{P["edge"]}" stroke-width="10"/>'
        f'{line("M59 72 Q54 25 59 13 M60 57 Q27 43 20 22 M60 47 Q94 34 99 7", P["tealDark"], 5)}'
        f'<path d="M57 19 Q38 13 44 0 Q64 1 67 16 Z M26 29 Q2 27 3 12 Q25 12 33 27 Z M91 22 Q102 -1 116 7 Q111 30 92 31 Z" fill="{P["teal"]}"/>'
        f'<path d="M57 19 Q38 13 44 0 Q64 1 67 16 Z M26 29 Q2 27 3 12 Q25 12 33 27 Z M91 22 Q102 -1 116 7 Q111 30 92 31 Z" fill="url(#sceneGrain)" opacity=".44"/>'
    )
    return [
        Asset("desk-lamp", "desk-props", "Warm paper desk lamp", 160, 346, 80, 985, "midground", lamp,
              {"surface": (.48, .96)}, ("lamp", "light")),
        Asset("coffee-mug", "desk-props", "Cream coffee mug", 120, 110, 82, 1218, "foreground", mug,
              {"grip": (.89, .50), "surface": (.43, .92)}, ("mug", "coffee")),
        Asset("late-night-clock", "desk-props", "Late night wall clock", 140, 160, 820, 502, "midground", clock,
              {}, ("clock", "night")),
        Asset("document", "desk-props", "Checked work notes", 145, 107, 426, 1225, "foreground", document,
              {"surface": (.50, .50)}, ("paper", "tasks")),
        Asset("small-plant", "desk-props", "Small desk plant", 120, 132, 950, 1195, "foreground", plant,
              {"surface": (.50, .89)}, ("plant", "desk")),
    ]


def ui() -> list[Asset]:
    panel = (
        f'{paper_path("M11 3 Q136 -3 266 4 L274 13 L273 180 Q266 191 257 191 Q133 196 9 190 L3 181 L4 14 Z", P["edge"])}'
        f'<path d="M14 14 Q137 9 262 15 L264 176 Q142 183 13 177 Z" fill="{P["night2"]}"/>'
        f'<path d="M14 14 Q137 9 262 15 L264 176 Q142 183 13 177 Z" fill="url(#sceneGrain)" opacity=".75"/>'
        f'<path d="M32 3 L75 1 L74 16 L31 17 Z M202 3 L245 5 L244 18 L201 16 Z" fill="{P["paper"]}" opacity=".72"/>'
        + txt(19, 36, "AGENT RUNNING", 19, P["mint"], 700, 1)
        + f'<circle cx="246" cy="29" r="8" fill="{P["teal"]}"/>'
        + f'{line("M20 48 Q134 46 254 49", P["paper"], 2, .28)}'
        + f'<path d="M18 61 Q131 58 254 62 L254 94 Q136 97 18 94 Z" fill="{P["paper"]}" opacity=".09"/>'
        + f'<path d="M18 98 Q133 96 254 99 L254 131 Q138 133 18 131 Z" fill="{P["paper"]}" opacity=".08"/>'
        + f'<path d="M18 136 Q135 133 254 137 L254 168 Q136 171 18 168 Z" fill="{P["paper"]}" opacity=".08"/>'
        + f'<circle cx="31" cy="77" r="12" fill="{P["tealDark"]}"/>'
        + f'{line("M24 76 l6 6 9 -12", P["paper"], 3)}'
        + txt(54, 84, "Plan", 19, P["paper"], 600)
        + f'<circle cx="31" cy="114" r="12" fill="{P["tealDark"]}"/>'
        + f'{line("M24 113 l6 6 9 -12", P["paper"], 3)}'
        + txt(54, 121, "Code", 19, P["paper"], 600)
        + f'<circle cx="31" cy="151" r="12" fill="none" stroke="{P["gold"]}" stroke-width="4"/>'
        + f'<circle cx="31" cy="151" r="3" fill="{P["gold"]}"/>'
        + txt(54, 158, "Verify", 19, P["paper"], 600)
        + f'<path d="M130 179 Q190 176 251 179" stroke="{P["teal"]}" stroke-width="5" fill="none" opacity=".95"/>'
    )
    notification = (
        f'<path d="M196 108 L228 108 L222 157 L201 152 Z" fill="{P["edge"]}" opacity=".72"/>'
        f'<path d="M201 112 L222 112 L218 148 L205 145 Z" fill="{P["paper"]}" opacity=".9"/>'
        f'{paper_path("M17 12 Q119 6 270 13 L282 24 L279 109 Q151 119 15 113 L7 103 L8 23 Z")}'
        f'<path d="M241 13 L282 24 L279 55 Q262 40 241 13 Z" fill="{P["edge"]}" opacity=".7"/>'
        f'<path d="M22 7 L69 5 L70 22 L22 24 Z M203 8 L252 10 L249 25 L204 24 Z" fill="{P["edge"]}" opacity=".81"/>'
        f'<circle cx="45" cy="64" r="23" fill="{P["tealDark"]}"/>'
        f'{line("M32 63 l10 10 17 -22", P["paper"], 6)}'
        + txt(81, 47, "TASK 03", 17, P["ink"], 700, 1)
        + f'<g transform="rotate(-7 169 81)">'
        + f'<path d="M83 57 Q169 52 258 58 L256 102 Q170 109 82 102 Z" fill="none" stroke="{P["coral"]}" stroke-width="5" opacity=".92"/>'
        + txt(102, 91, "DONE", 40, P["coral"], 700, 2)
        + '</g>'
    )
    return [
        Asset("task-progress-panel", "ui", "Replaceable task progress panel", 276, 194, 648, 958, "ui", panel,
              {"screenContent": (.50, .50)}, ("task", "progress", "agent")),
        Asset("notification-card", "ui", "Stamped paper task ticket", 286, 160, 670, 765, "ui", notification,
              {}, ("notification", "task", "complete")),
    ]


def all_assets() -> list[Asset]:
    items = environment() + furniture() + computing() + desk_props() + ui()
    workstation = {
        "chair", "desk-lamp", "desktop-monitor", "laptop", "desk",
        "document", "keyboard", "mouse", "coffee-mug", "small-plant",
        "task-progress-panel", "notification-card",
    }
    items = [replace(a, y=a.y-64) if a.slug in workstation else a for a in items]
    order = [
        "wall-background", "floor", "night-sky-moon", "window",
        "late-night-clock", "chair", "desk-lamp", "desktop-monitor", "laptop",
        "desk", "document", "keyboard", "mouse", "coffee-mug", "small-plant",
        "task-progress-panel", "notification-card",
    ]
    return sorted(items, key=lambda a: order.index(a.slug))


BOT_PLACEMENT = {"x": 264, "y": 854, "scale": .43}
BOT_POSE = {
    "base": "pointing", "faceState": "determined",
    "leftArm": {"end": [390, 669], "hand": "mitten"},
    "rightArm": {"end": [824, 535], "hand": "point"},
    "headRotation": -4,
}


def mascot_group() -> str:
    body, _ = assemble_pose(
        "pointing", "determined",
        {"l": (390, 669, "mitten"), "r": (824, 535, "point"), "head_tilt": -4},
    )
    return (f'<g id="canonical-motif-bot" data-source="assets/characters/motif-bot/canonical/v1/motif-bot-v1.json" '
            f'transform="translate({BOT_PLACEMENT["x"]} {BOT_PLACEMENT["y"]}) scale({BOT_PLACEMENT["scale"]})">'
            f'{body}</g>')


def write_assets(items: list[Asset]) -> None:
    for a in items:
        a.file.parent.mkdir(parents=True, exist_ok=True)
        a.file.write_text(svg(a.w, a.h, a.body, a.name))
        meta = {
            "id": f"scene-01-{a.slug}", "name": a.name, "category": a.category,
            "subcategory": a.slug, "concepts": list(a.concepts),
            "keywords": [a.slug, "cut-paper", "night-desk"],
            "style": "motif-default-v1", "orientation": "front",
            "dimensions": {"width": a.w, "height": a.h, "unit": "px"},
            "artBox": {"x": 0, "y": 0, "width": a.w, "height": a.h},
            "anchors": {k: {"x": x, "y": y} for k, (x, y) in a.anchors.items()},
            "compatibleCharacters": ["motif-bot"],
            "supportedActions": ["compose", "swap", "animate"],
            "sourceType": "vector",
            "source": {"file": str(a.file.relative_to(ROOT)), "generator": "scripts/build_scene_01.py"},
            "version": 1, "status": "canonical", "preview": "previews/scene-01/contact-sheet.png",
            "license": "project-original",
            "scenePlacement": {"x": a.x, "y": a.y, "layer": a.layer},
        }
        a.file.with_suffix(".json").write_text(json.dumps(meta, indent=2) + "\n")


def scene_markup(items: list[Asset]) -> str:
    output = []
    for a in items:
        if a.slug == "desk":
            output.append(mascot_group())
        output.append(a.placed())
    return "\n".join(output)


def write_scene(items: list[Asset]) -> Path:
    SCENE.mkdir(parents=True, exist_ok=True)
    body = scene_markup(items)
    path = SCENE / "scene-01-night-work.svg"
    path.write_text(svg(W, H, body, "Motif Bot working while you sleep", DEFS + BOT_DEFS))
    layer_order = ["background", "midground", "character", "foreground", "ui"]
    manifest = {
        "id": "scene-01-night-work", "name": "An AI agent works while you sleep",
        "version": 1, "status": "canonical", "benchmark": True, "style": "motif-default-v1",
        "dimensions": {"width": W, "height": H, "unit": "px"},
        "render": str(path.relative_to(ROOT)),
        "generator": "scripts/build_scene_01.py",
        "layerOrder": layer_order,
        "headlineSafeArea": {"x": 90, "y": 55, "width": 900, "height": 185},
        "captionSafeArea": {"x": 100, "y": 1660, "width": 880, "height": 210},
        "character": {
            "source": "assets/characters/motif-bot/canonical/v1/motif-bot-v1.json",
            "geometrySource": "scripts/build_motif_bot.py",
            "placement": BOT_PLACEMENT, "pose": BOT_POSE, "status": "canonical",
        },
        "assets": [
            {"id": f"scene-01-{a.slug}", "source": str(a.file.relative_to(ROOT)),
             "metadata": str(a.file.with_suffix(".json").relative_to(ROOT)),
             "layer": a.layer, "placement": {"x": a.x, "y": a.y},
             "dimensions": {"width": a.w, "height": a.h}}
            for a in items
        ],
        "note": "The composite contains the independent asset markup in layer order. Rebuild from this manifest and the listed SVGs; Motif Bot comes from the locked canonical generator.",
    }
    (SCENE / "scene-01.json").write_text(json.dumps(manifest, indent=2) + "\n")
    # Useful transparent layer exports for editors and animation.
    for layer in layer_order:
        bits = [a.placed() for a in items if a.layer == layer]
        if layer == "character":
            bits = [mascot_group()]
        (SCENE / f"layer-{layer}.svg").write_text(
            svg(W, H, "\n".join(bits), f"Scene 01 {layer} layer", DEFS + BOT_DEFS)
        )
    return path


def raster(source: str | Path, w: int | None = None, h: int | None = None) -> Image.Image:
    data = source.read_text() if isinstance(source, Path) else source
    kwargs = {"output_width": w} if w else {}
    if h:
        kwargs["output_height"] = h
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=data.encode(), **kwargs))).convert("RGBA")


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(
            "/System/Library/Fonts/HelveticaNeue.ttc", size, index=1 if bold else 0
        )
    except OSError:
        return ImageFont.load_default()


def paste_center(canvas: Image.Image, item: Image.Image, box: tuple[int, int, int, int]) -> None:
    x, y, w, h = box
    item.thumbnail((w, h), Image.Resampling.LANCZOS)
    canvas.alpha_composite(item, (x + (w-item.width)//2, y + (h-item.height)//2))


def contact_sheet(items: list[Asset]) -> None:
    cols = 4
    cw, ch = 360, 330
    rows = (len(items)+cols-1)//cols
    out = Image.new("RGBA", (cols*cw, 110+rows*ch), P["paper"])
    d = ImageDraw.Draw(out)
    d.text((34, 25), "SCENE 01 / REUSABLE ASSETS", font=font(34, True), fill=P["ink"])
    d.text((36, 72), "Independent transparent SVGs · approved benchmark scene", font=font(19), fill=P["tealDark"])
    for i, a in enumerate(items):
        x = (i%cols)*cw+18
        y = 110+(i//cols)*ch+12
        d.rounded_rectangle((x,y,x+cw-36,y+ch-24), radius=17, fill="#CBD7D0", outline="#A9B8AE", width=2)
        art = raster(a.file)
        # Respect a tall background by fitting the whole registered asset.
        paste_center(out, art, (x+12,y+12,cw-60,ch-82))
        d.text((x+13,y+ch-62), a.name, font=font(19, True), fill=P["ink"])
        d.text((x+13,y+ch-38), f"{a.category}  ·  {a.slug}.svg", font=font(13), fill=P["tealDark"])
    out.convert("RGB").save(PREVIEWS / "contact-sheet.png")


def exploded_view(items: list[Asset]) -> None:
    # Every component appears on its own tile; columns follow physical depth.
    col_w, row_h = 330, 275
    groups = [
        ("BACKGROUND", ["wall-background", "floor", "night-sky-moon"]),
        ("MIDGROUND", ["window", "late-night-clock", "chair", "desk-lamp", "laptop", "desktop-monitor"]),
        ("CHARACTER", ["canonical-motif-bot"]),
        ("FOREGROUND", ["desk", "document", "keyboard", "mouse", "coffee-mug", "small-plant"]),
        ("UI", ["task-progress-panel", "notification-card"]),
    ]
    height = 230 + max(len(slugs) for _, slugs in groups)*row_h
    out = Image.new("RGBA", (5*col_w, height), P["paper"])
    d = ImageDraw.Draw(out)
    d.text((40, 25), "SCENE 01 / EXPLODED ASSET VIEW", font=font(36, True), fill=P["ink"])
    d.text((42, 74), "One stage, independent pieces. Left to right follows compositing depth.", font=font(20), fill=P["tealDark"])
    lookup = {a.slug: a for a in items}
    for ci, (heading, slugs) in enumerate(groups):
        x = ci*col_w+20
        d.rounded_rectangle((x,130,x+col_w-40,height-35), radius=16, fill="#D6DED5", outline="#B2BFB6", width=2)
        d.text((x+16,151), heading, font=font(20, True), fill=P["ink"])
        for ri, slug in enumerate(slugs):
            y = 198+ri*row_h
            d.rounded_rectangle((x+12,y,x+col_w-52,y+row_h-20), radius=12, fill="#EEF0E6")
            if slug == "canonical-motif-bot":
                bot, _ = assemble_pose("pointing", "determined",
                                       {"l": (390,669,"mitten"), "r": (824,535,"point"), "head_tilt": -4})
                art = raster(svg(1024,1024,bot,"Canonical Motif Bot",DEFS+BOT_DEFS))
                name, sub = "Motif Bot v1 (locked)", "canonical character / placed pose"
            else:
                a = lookup[slug]
                art = raster(a.file)
                name, sub = a.name, a.slug
            paste_center(out, art, (x+25,y+8,col_w-104,row_h-75))
            d.text((x+28,y+row_h-58), name, font=font(17, True), fill=P["ink"])
            d.text((x+28,y+row_h-34), sub, font=font(14), fill=P["tealDark"])
    out.convert("RGB").save(PREVIEWS / "exploded-view.png")


def layer_diagram(items: list[Asset]) -> None:
    groups = [
        ("01", "BACKGROUND", "wall, floor, night sky + moon", P["plum"]),
        ("02", "MIDGROUND", "window, chair, clock, lamp, laptop, monitor", P["night2"]),
        ("03", "CHARACTER", "locked Motif Bot v1; pointing at active work", P["tealDark"]),
        ("04", "FOREGROUND", "desk, document, keyboard, mouse, mug, plant", P["woodEdge"]),
        ("05", "UI", "task progress panel + completed task card", P["ink"]),
    ]
    out = Image.new("RGB", (1320, 920), P["paper"])
    d = ImageDraw.Draw(out)
    d.text((52,40),"SCENE 01 / LAYER STACK",font=font(38,True),fill=P["ink"])
    d.text((55,97),"Back-to-front compositing order is listed in scene-01.json.",font=font(22),fill=P["tealDark"])
    for i,(num,name,desc,color) in enumerate(groups):
        x=80+i*35
        y=176+i*132
        d.rounded_rectangle((x,y,x+1070,y+108),radius=20,fill=color)
        d.text((x+25,y+19),num,font=font(39,True),fill=P["paper"])
        d.text((x+110,y+18),name,font=font(26,True),fill=P["paper"])
        d.text((x+110,y+59),desc,font=font(19),fill=P["paper"])
        if i<4:
            d.line((x+1050,y+109,x+1075,y+125),fill=P["tealDark"],width=4)
    d.text((55,875),"Headline and caption safe areas remain empty in the scene render.",font=font(19),fill=P["ink"])
    out.save(PREVIEWS / "layer-diagram.png")


def mobile_preview(scene: Image.Image) -> None:
    out = Image.new("RGB", (1080, 790), "#E8E8DF")
    d = ImageDraw.Draw(out)
    d.text((42,35),"MOBILE READABILITY / 360 × 640",font=font(30,True),fill=P["ink"])
    small = scene.resize((360,640),Image.Resampling.LANCZOS).convert("RGB")
    out.paste(small,(54,113))
    # Match actual phone width, then provide a modest cropped detail for QA.
    crop = small.crop((60,240,335,490)).resize((550,500),Image.Resampling.NEAREST)
    out.paste(crop,(465,153))
    d.text((469,116),"Central action enlarged for inspection",font=font(20),fill=P["tealDark"])
    d.text((466,682),"Full scene at native mobile size",font=font(20),fill=P["ink"])
    out.save(PREVIEWS / "mobile-preview.png")


def before_after(scene: Image.Image) -> None:
    baseline = PREVIEWS / "scene-before.png"
    if not baseline.is_file():
        raise FileNotFoundError(
            "The pre-refinement scene snapshot is required for the before/after view"
        )
    original = Image.open(baseline).convert("RGB")
    out = Image.new("RGB", (1500, 1450), P["paper"])
    d = ImageDraw.Draw(out)
    d.text((48, 30), "SCENE 01 / ART DIRECTION REFINEMENT", font=font(36, True), fill=P["ink"])
    d.text((52, 88), "Same modular scene and locked mascot; source assets refined.", font=font(21), fill=P["tealDark"])
    for x, label, im in ((52, "BEFORE", original), (770, "AFTER", scene.convert("RGB"))):
        d.text((x, 135), label, font=font(25, True), fill=P["ink"])
        reduced = im.resize((675, 1200), Image.Resampling.LANCZOS)
        out.paste(reduced, (x, 176))
        d.rectangle((x-1, 175, x+676, 1377), outline=P["edge"], width=2)
    d.text((53, 1400), "Paper edges + material depth  /  stamped task ticket  /  workstation raised 64 px",
           font=font(19), fill=P["tealDark"])
    out.save(PREVIEWS / "before-after.png")


def main() -> None:
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    items = all_assets()
    write_assets(items)
    scene_file = write_scene(items)
    rendered = raster(scene_file)
    rendered.convert("RGB").save(PREVIEWS / "scene-full.png")
    contact_sheet(items)
    exploded_view(items)
    layer_diagram(items)
    mobile_preview(rendered)
    before_after(rendered)
    print(f"Built {len(items)} independent SVG scene assets and 6 preview sheets")
    print(scene_file)


if __name__ == "__main__":
    main()
