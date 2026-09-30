#!/usr/bin/env python3
"""Build the arena and inspection benchmark scenes from reusable SVG pieces."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_motif_bot import DEFS as BOT_DEFS, assemble_pose  # noqa: E402
from build_scene_01 import DEFS, P, card, font, line, paper_path, paste_center, raster, svg, txt  # noqa: E402

W, H = 1080, 1920
P2 = {
    "arenaWall": "#B99476",
    "arenaWallDark": "#947058",
    "arenaFloor": "#6F5263",
    "terracotta": "#BB725C",
    "blue": "#64869A",
    "bronze": "#BC8660",
    "factoryWall": "#6D8890",
    "factoryDark": "#3C5D68",
    "factoryFloor": "#9B7764",
    "bug": "#D87969",
}


@dataclass(frozen=True)
class Piece:
    slug: str
    category: str
    name: str
    w: int
    h: int
    x: int
    y: int
    layer: str
    body: str
    concepts: tuple[str, ...]
    anchors: dict[str, tuple[float, float]] | None = None

    def file(self, scene_id: str) -> Path:
        return ROOT / "assets/scenes" / scene_id / self.category / f"{self.slug}.svg"

    def placed(self, scene_id: str) -> str:
        source = self.file(scene_id)
        body = source.read_text().split("</defs>", 1)[1].rsplit("</svg>", 1)[0].strip()
        rel = source.relative_to(ROOT)
        return (f'<g id="{self.slug}" data-asset="{rel}" '
                f'transform="translate({self.x} {self.y})">{body}</g>')


@dataclass(frozen=True)
class Spec:
    scene_id: str
    title: str
    description: str
    pieces: list[Piece]
    bot_place: tuple[int, int, float]
    bot_base: str
    bot_face: str
    bot_overrides: dict
    bot_before: str
    safe_headline: dict[str, int]
    safe_caption: dict[str, int]


def cut(d: str, fill: str, grain: str = "paperSpeckle") -> str:
    return paper_path(d, fill, grain)


def layer_texture(d: str, grain: str = "paperSpeckle", opacity: float = .68) -> str:
    return f'<path d="{d}" fill="url(#{grain})" opacity="{opacity}"/>'


def dot(x: float, y: float, r: float, fill: str, opacity: float = 1) -> str:
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}" opacity="{opacity}"/>'


def arena_agent(color: str, mark: str) -> str:
    shell = "M30 34 Q73 24 122 32 Q139 36 143 55 L141 143 Q138 158 118 160 Q71 166 27 158 Q13 152 13 137 L14 55 Q16 39 30 34 Z"
    return (
        f'<ellipse cx="78" cy="204" rx="74" ry="14" fill="{P["shadow"]}" opacity=".14"/>'
        f'{cut(shell, color, "sceneGrain")}'
        f'<path d="M40 63 Q74 56 116 63 Q128 66 129 78 L128 124 Q126 137 113 140 Q74 146 40 138 Q29 134 28 120 L28 80 Q28 68 40 63 Z" fill="{P["ink"]}"/>'
        f'{dot(55,99,8,P["mint"])}{dot(101,99,8,P["mint"])}'
        f'{line("M66 121 Q78 128 91 121", P["mint"], 5)}'
        f'<path d="M30 153 L30 185 M124 153 L124 185" stroke="{P["edge"]}" stroke-width="19" stroke-linecap="round"/>'
        f'<ellipse cx="30" cy="188" rx="31" ry="13" fill="{color}"/><ellipse cx="124" cy="188" rx="31" ry="13" fill="{color}"/>'
        f'{txt(71,44,mark,19,P["paper"],700)}'
    )


def scene02_pieces() -> list[Piece]:
    wall_d = "M0 0 H1080 V1491 Q819 1485 543 1493 Q266 1487 0 1491 Z"
    wall = (
        f'<path d="{wall_d}" fill="{P2["arenaWall"]}"/>'
        + layer_texture(wall_d, "woodFiber", .5)
        + f'<path d="M0 0 H1080 V268 Q545 259 0 267 Z" fill="{P2["arenaWallDark"]}" opacity=".13"/>'
        + f'<path d="M0 780 Q510 768 1080 782 V791 Q500 780 0 793 Z" fill="{P["paper"]}" opacity=".13"/>'
    )
    floor_d = "M0 0 Q290 -5 566 2 Q814 -4 1080 1 V530 H0 Z"
    floor = (
        f'<path d="{floor_d}" fill="{P2["arenaFloor"]}"/>'
        + layer_texture(floor_d, "sceneGrain", .85)
        + f'<path d="M0 1 Q541 11 1080 2 V33 Q541 26 0 31 Z" fill="{P["ink"]}" opacity=".25"/>'
        + f'<ellipse cx="533" cy="122" rx="456" ry="77" fill="{P["ink"]}" opacity=".17"/>'
        + line("M0 264 Q538 253 1080 267", P["ink"], 3, .24)
    )
    # Three broad tiers carry crowd texture without competing with the winner.
    crowd = (
        f'<path d="M0 71 Q476 22 980 69 L980 355 Q477 372 0 357 Z" fill="{P2["arenaWallDark"]}"/>'
        + layer_texture("M0 71 Q476 22 980 69 L980 355 Q477 372 0 357 Z", "paperSpeckle", .44)
    )
    for row in range(3):
        y = 113 + row * 85
        crowd += f'<path d="M0 {y+47} Q490 {y+39} 980 {y+46} L980 {y+71} Q490 {y+60} 0 {y+72} Z" fill="{P["edge"]}" opacity=".67"/>'
        for col in range(22):
            x = 30 + col * 43 + (row % 2) * 18
            if x > 963:
                continue
            color = (P["paper"], P["teal"], P2["terracotta"], P2["blue"])[(col*3+row)%4]
            crowd += f'<path d="M{x-12} {y+18} Q{x-11} {y-2} {x} {y-1} Q{x+12} {y} {x+12} {y+18} L{x+15} {y+44} H{x-15} Z" fill="{color}" opacity=".8"/>'
            crowd += dot(x-3,y+16,1.5,P["ink"],.55)+dot(x+4,y+16,1.5,P["ink"],.55)
    arch = (
        f'<path d="M52 67 Q452 -36 851 67 L871 356 L792 358 L786 107 Q453 26 118 107 L110 357 L29 354 Z" fill="{P["shadow"]}" opacity=".19" transform="translate(8 10)"/>'
        f'{cut("M52 67 Q452 -36 851 67 L871 356 L792 358 L786 107 Q453 26 118 107 L110 357 L29 354 Z", P["paper"])}'
        f'<path d="M76 75 Q455 -14 825 77" fill="none" stroke="{P["edge"]}" stroke-width="8" opacity=".74"/>'
        f'<path d="M41 355 Q449 369 859 355 L872 389 Q454 412 28 390 Z" fill="{P2["terracotta"]}"/>'
        f'<path d="M41 355 Q449 369 859 355 L872 389 Q454 412 28 390 Z" fill="url(#paperSpeckle)" opacity=".55"/>'
        f'<path d="M141 72 L161 67 L160 354 L143 353 Z M746 69 L765 73 L761 353 L747 354 Z" fill="{P["edge"]}" opacity=".48"/>'
    )
    stage = (
        f'<ellipse cx="451" cy="271" rx="444" ry="44" fill="{P["shadow"]}" opacity=".18"/>'
        f'{cut("M29 148 Q454 112 873 149 L892 255 Q448 282 9 257 Z", P2["arenaFloor"], "sceneGrain")}'
        f'<path d="M20 209 Q457 237 881 210 L892 255 Q445 281 9 257 Z" fill="{P["ink"]}" opacity=".32"/>'
        f'{line("M40 168 Q453 142 851 168", P["paper"], 6, .44)}'
        f'<path d="M23 257 Q450 283 888 254 L867 286 Q453 302 44 287 Z" fill="{P2["terracotta"]}"/>'
    )
    podium = (
        f'<ellipse cx="356" cy="373" rx="355" ry="37" fill="{P["shadow"]}" opacity=".14"/>'
        f'{cut("M12 200 Q119 187 221 200 L228 355 Q120 365 8 354 Z", P2["blue"], "sceneGrain")}'
        f'{cut("M235 91 Q352 78 475 91 L480 357 Q354 373 231 355 Z", P["tealDark"], "sceneGrain")}'
        f'{cut("M488 238 Q597 225 707 237 L711 354 Q600 365 484 354 Z", P2["terracotta"], "sceneGrain")}'
        f'<path d="M8 202 Q115 184 226 199 L227 232 Q117 222 9 233 Z" fill="{P["paper"]}"/>'
        f'<path d="M231 92 Q354 76 479 91 L480 125 Q355 111 232 127 Z" fill="{P["paper"]}"/>'
        f'<path d="M484 239 Q594 224 710 238 L710 271 Q599 257 485 272 Z" fill="{P["paper"]}"/>'
        f'{txt(97,222,"2",44,P["ink"],700)}{txt(335,116,"1",50,P["ink"],700)}{txt(583,261,"3",44,P["ink"],700)}'
    )
    evaluation = (
        f'{cut("M19 13 Q290 -3 551 14 L554 132 Q291 145 18 133 Z", P["paper"])}'
        f'{txt(177,46,"ANSWER TRIALS",23,P["ink"],700,1)}'
        f'{line("M63 66 H507", P["edge"], 4, .8)}'
        + "".join(
            f'{card(39+i*174,77,132,43,8,(P2["blue"],P["tealDark"],P2["terracotta"])[i])}'
            f'{txt(77+i*174,105,("A","B","C")[i],25,P["paper"],700)}'
            for i in range(3)
        )
        + f'<path d="M106 132 Q178 183 290 201 Q404 178 465 132" fill="none" stroke="{P["edge"]}" stroke-width="8" opacity=".8"/>'
        + f'<path d="M290 203 L279 188 L300 188 Z" fill="{P["tealDark"]}"/>'
    )
    winner = (
        f'<path d="M116 162 L96 227 L64 189 L28 221 L31 150 Z" fill="{P["tealDark"]}" opacity=".9"/>'
        f'<path d="M120 161 L140 227 L172 190 L211 219 L207 149 Z" fill="{P["tealDark"]}" opacity=".9"/>'
        f'{cut("M118 14 Q179 17 220 70 Q242 123 204 164 Q163 205 106 197 Q45 193 19 148 Q-1 96 31 49 Q64 9 118 14 Z", P["paper"])}'
        f'<circle cx="117" cy="105" r="69" fill="{P["tealDark"]}"/>'
        f'{line("M78 103 l28 30 51 -60", P["paper"], 15)}'
        f'{txt(77,184,"BEST",26,P["ink"],700,1)}'
    )
    confetti = ""
    for i,(x,y,c) in enumerate([
        (40,95,P["coral"]),(105,42,P["gold"]),(270,126,P["teal"]),(340,78,P["paper"]),
        (525,59,P["coral"]),(634,120,P["gold"]),(781,36,P["teal"]),(903,98,P["paper"]),
        (114,220,P["paper"]),(835,201,P["coral"])]):
        confetti += f'<path d="M{x} {y} l{12+i%3} {-8+i%4} l{7+i%2} 12 l-13 7 Z" fill="{c}" opacity=".85"/>'
    pieces = [
        Piece("arena-wall","environment","Warm arena backdrop",1080,1495,0,0,"background",wall,("arena","paper")),
        Piece("arena-floor","environment","Plum stage floor",1080,530,0,1430,"background",floor,("floor","arena")),
        Piece("crowd-tiers","environment","Three quiet crowd tiers",980,390,50,472,"background",crowd,("audience","stadium")),
        Piece("arena-arch","environment","Layered arena proscenium",900,410,90,365,"midground",arch,("arch","stage")),
        Piece("evaluation-board","props","Three-answer evaluation board",570,215,280,750,"midground",evaluation,("competition","answers")),
        Piece("arena-stage","furniture","Cut-paper arena stage",900,310,90,1190,"midground",stage,("stage","platform")),
        Piece("agent-token-blue","contestants","Blue agent token",155,210,260,1060,"character",arena_agent(P2["blue"],"A"),("agent","contestant")),
        Piece("agent-token-teal","contestants","Teal winning agent token",155,210,463,955,"character",arena_agent(P["tealDark"],"B"),("agent","winner")),
        Piece("agent-token-coral","contestants","Coral agent token",155,210,705,1100,"character",arena_agent(P2["terracotta"],"C"),("agent","contestant")),
        Piece("podium","furniture","Three-level result podium",720,400,250,1070,"foreground",podium,("podium","winner")),
        Piece("winner-seal","props","Best-answer paper seal",240,240,640,844,"ui",winner,("winner","best-answer")),
        Piece("paper-confetti","fx","Sparse celebration cutouts",950,255,65,925,"ui",confetti,("celebration","paper")),
    ]
    return pieces


def scene03_pieces() -> list[Piece]:
    wall_d = "M0 0 H1080 V1493 Q799 1483 541 1493 Q245 1485 0 1494 Z"
    wall = (
        f'<path d="{wall_d}" fill="{P2["factoryWall"]}"/>'
        + layer_texture(wall_d, "sceneGrain", .79)
        + f'<path d="M0 0 H1080 V259 Q540 250 0 258 Z" fill="{P2["factoryDark"]}" opacity=".18"/>'
        + f'<path d="M75 319 Q509 309 1002 322 L1002 1391 Q519 1400 74 1389 Z" fill="{P["paper"]}" opacity=".035"/>'
        + line("M76 322 Q545 312 1002 323", P["paper"], 3, .15)
    )
    floor_d = "M0 1 Q242 -3 520 2 Q817 -5 1080 1 V520 H0 Z"
    floor = (
        f'<path d="{floor_d}" fill="{P2["factoryFloor"]}"/>'
        + layer_texture(floor_d, "woodFiber", .78)
        + f'<path d="M0 1 Q544 12 1080 1 V28 Q545 23 0 30 Z" fill="{P2["factoryDark"]}" opacity=".42"/>'
        + line("M0 266 Q520 256 1080 266", P["woodEdge"], 3, .24)
        + f'<ellipse cx="541" cy="119" rx="455" ry="63" fill="{P["shadow"]}" opacity=".14"/>'
    )
    pipes = (
        f'<path d="M53 211 L53 66 Q54 39 79 39 H379 Q401 41 401 67 V194 '
        f'M488 210 L488 95 Q490 75 512 75 H800 Q823 75 823 95 V210" '
        f'fill="none" stroke="{P2["factoryDark"]}" stroke-width="31" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<path d="M53 211 L53 66 Q54 39 79 39 H379 Q401 41 401 67 V194 '
        f'M488 210 L488 95 Q490 75 512 75 H800 Q823 75 823 95 V210" '
        f'fill="none" stroke="{P["edge"]}" stroke-width="20" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<path d="M54 211 L54 66 Q54 40 79 40 H378 Q400 41 400 66 V192 '
        f'M488 209 L488 95 Q490 76 513 76 H799 Q822 76 822 95 V209" '
        f'fill="none" stroke="{P["paper"]}" stroke-width="15" stroke-linecap="round" stroke-linejoin="round"/>'
        + "".join(
            f'<rect x="{x}" y="{y}" width="27" height="34" rx="5" fill="{P["tealDark"]}" opacity=".64"/>'
            for x,y in [(39,103),(386,111),(475,135),(808,129)]
        )
    )
    sign = (
        f'{cut("M20 15 Q143 4 265 15 L270 99 Q145 109 15 101 Z", P["paper"])}'
        f'<circle cx="78" cy="57" r="25" fill="none" stroke="{P["tealDark"]}" stroke-width="8"/>'
        f'{line("M96 76 L117 92", P["tealDark"], 9)}'
        f'{txt(129,68,"SCAN",32,P["ink"],700,1)}'
        f'<path d="M39 13 L51 -10 M235 13 L247 -10" stroke="{P["edge"]}" stroke-width="6"/>'
    )
    conveyor = (
        f'<ellipse cx="443" cy="230" rx="439" ry="29" fill="{P["shadow"]}" opacity=".16"/>'
        f'<path d="M21 64 Q449 52 858 66 L879 104 Q451 117 7 104 Z" fill="{P["shadow"]}" opacity=".22" transform="translate(4 5)"/>'
        f'{cut("M21 64 Q449 52 858 66 L879 104 Q451 117 7 104 Z", P["ink"], "sceneGrain")}'
        f'<path d="M7 104 Q447 117 879 104 L868 179 Q445 195 18 180 Z" fill="{P2["factoryDark"]}"/>'
        + layer_texture("M7 104 Q447 117 879 104 L868 179 Q445 195 18 180 Z", "sceneGrain", .6)
        + "".join(f'<circle cx="{x}" cy="144" r="22" fill="{P["edge"]}"/><circle cx="{x}" cy="144" r="11" fill="{P2["factoryWall"]}"/>' for x in range(70,861,79))
        + f'<path d="M96 179 L99 246 L145 246 L158 182 M719 181 L730 247 L777 247 L789 181" fill="{P["woodEdge"]}"/>'
        + f'<path d="M20 71 Q435 60 856 73" fill="none" stroke="{P["paper"]}" stroke-width="5" opacity=".6"/>'
    )
    scanner = (
        f'<path d="M50 106 Q51 23 125 20 L228 20 Q303 22 306 104 L305 460 L245 461 L245 116 '
        f'Q244 80 214 80 L138 80 Q108 81 107 118 L106 460 L45 461 Z" fill="{P["shadow"]}" opacity=".2" transform="translate(8 9)"/>'
        f'{cut("M50 106 Q51 23 125 20 L228 20 Q303 22 306 104 L305 460 L245 461 L245 116 Q244 80 214 80 L138 80 Q108 81 107 118 L106 460 L45 461 Z", P["paper"])}'
        f'<path d="M107 186 Q178 172 245 186 L245 229 Q178 215 107 231 Z" fill="{P["tealDark"]}" opacity=".74"/>'
        f'<path d="M124 20 Q175 13 226 21" fill="none" stroke="{P["edge"]}" stroke-width="7"/>'
        f'<circle cx="177" cy="64" r="25" fill="{P2["factoryDark"]}"/>'
        f'{line("M164 64 l10 10 18 -23", P["mint"], 6)}'
        f'<rect x="52" y="425" width="55" height="43" rx="9" fill="{P2["factoryDark"]}"/>'
        f'<rect x="245" y="425" width="58" height="43" rx="9" fill="{P2["factoryDark"]}"/>'
    )
    scan_beam = (
        f'<path d="M66 14 Q107 5 153 13 L198 300 Q108 319 9 300 Z" fill="{P["mint"]}" opacity=".13"/>'
        f'<path d="M70 16 Q109 11 149 16 L147 304 Q107 310 72 304 Z" fill="{P["paper"]}" opacity=".095"/>'
        f'{line("M33 174 Q110 160 174 176", P["mint"], 6, .56)}'
        f'{line("M48 230 Q109 217 164 229", P["mint"], 4, .35)}'
    )
    code_in = (
        f'{cut("M16 10 Q81 5 148 12 L154 117 Q86 126 10 119 Z", P["paper"])}'
        f'{txt(36,50,"< >",31,P["tealDark"],700)}'
        f'{line("M33 70 H124 M33 85 H103 M33 100 H116", P["edge"], 6, .9)}'
        f'<path d="M122 12 L149 13 L152 38 Z" fill="{P["edge"]}" opacity=".65"/>'
    )
    code_out = (
        f'{cut("M15 10 Q82 5 150 12 L155 119 Q84 125 10 118 Z", P["paper"])}'
        f'{txt(34,48,"< >",30,P["tealDark"],700)}'
        f'{line("M34 67 H96 M34 85 H83", P["edge"], 6, .8)}'
        f'<circle cx="118" cy="87" r="25" fill="{P["tealDark"]}"/>'
        f'{line("M105 86 l9 9 16 -19", P["paper"], 7)}'
    )
    bug = (
        f'<ellipse cx="70" cy="119" rx="62" ry="13" fill="{P["shadow"]}" opacity=".14"/>'
        f'<circle cx="70" cy="65" r="54" fill="{P["paper"]}" opacity=".85"/>'
        f'<circle cx="70" cy="65" r="54" fill="url(#paperSpeckle)" opacity=".6"/>'
        f'<path d="M52 51 Q41 35 45 22 M88 51 Q99 35 95 22 M43 72 L20 62 M44 84 L19 92 M97 71 L120 62 M96 84 L121 93" '
        f'fill="none" stroke="{P2["bug"]}" stroke-width="7" stroke-linecap="round"/>'
        f'<ellipse cx="70" cy="73" rx="27" ry="36" fill="{P2["bug"]}"/>'
        f'<path d="M70 42 V104" stroke="{P["paper"]}" stroke-width="4" opacity=".7"/>'
        f'{dot(60,58,3,P["ink"])}{dot(81,58,3,P["ink"])}'
    )
    grabber = (
        f'<path d="M47 0 V119 Q46 133 60 141 L74 150" fill="none" stroke="{P["edge"]}" stroke-width="18" stroke-linecap="round"/>'
        f'<path d="M47 0 V119 Q46 133 60 141 L74 150" fill="none" stroke="{P["paper"]}" stroke-width="14" stroke-linecap="round"/>'
        f'<path d="M72 146 Q93 139 95 159 L89 178 M72 146 Q51 137 45 157 L52 179" '
        f'fill="none" stroke="{P["tealDark"]}" stroke-width="13" stroke-linecap="round"/>'
        f'<circle cx="47" cy="116" r="13" fill="{P["tealDark"]}"/>'
    )
    reject = (
        f'<ellipse cx="118" cy="157" rx="113" ry="19" fill="{P["shadow"]}" opacity=".16"/>'
        f'{cut("M18 35 Q114 25 216 35 L199 145 Q117 157 34 145 Z", P2["factoryDark"], "sceneGrain")}'
        f'<path d="M7 32 Q112 16 227 30 L224 48 Q116 58 10 49 Z" fill="{P["edge"]}"/>'
        f'<circle cx="117" cy="96" r="29" fill="{P2["bug"]}"/>'
        f'{line("M103 84 l28 26 M132 84 l-28 27", P["paper"], 7)}'
    )
    pass_stamp = (
        f'{cut("M13 16 Q104 5 198 14 L207 107 Q105 117 10 106 Z", P["paper"])}'
        f'<circle cx="53" cy="60" r="25" fill="{P["tealDark"]}"/>'
        f'{line("M40 59 l11 11 17 -23", P["paper"], 7)}'
        f'{txt(87,72,"PASS",34,P["tealDark"],700,1)}'
        f'<path d="M42 9 L78 6 L80 20 L43 23 Z" fill="{P["edge"]}" opacity=".75"/>'
    )
    gauge = (
        f'{cut("M75 5 Q126 4 145 51 Q161 98 125 129 Q87 158 45 134 Q6 113 5 71 Q4 26 43 10 Q59 4 75 5 Z", P["paper"])}'
        f'<path d="M31 102 Q12 72 34 42 M34 42 Q74 0 116 41 M116 41 Q139 71 119 103" fill="none" stroke="{P["edge"]}" stroke-width="8"/>'
        f'<path d="M32 103 Q72 132 119 103" fill="none" stroke="{P["tealDark"]}" stroke-width="9"/>'
        f'{line("M74 75 L109 57", P["ink"], 7)}'
        f'{dot(74,75,6,P["tealDark"])}'
    )
    return [
        Piece("factory-wall","environment","Slate paper factory wall",1080,1495,0,0,"background",wall,("factory","paper")),
        Piece("factory-floor","environment","Warm inspection floor",1080,520,0,1430,"background",floor,("factory","floor")),
        Piece("wall-pipes","environment","Shallow paper conduit set",900,255,92,415,"midground",pipes,("factory","pipes")),
        Piece("scan-sign","props","Hanging inspection sign",280,115,400,344,"midground",sign,("inspection","sign")),
        Piece("quality-gauge","props","Quality dial",155,160,835,562,"midground",gauge,("quality","gauge")),
        Piece("scanner-frame","machine","Cut-paper scanning gate",350,475,378,785,"midground",scanner,("scanner","machine")),
        Piece("scan-beam","machine","Soft inspection beam",210,320,448,896,"midground",scan_beam,("scan","light")),
        Piece("conveyor-belt","machine","Paper conveyor belt",890,250,95,1185,"foreground",conveyor,("conveyor","process")),
        Piece("incoming-code-sheet","workflow","Incoming code ticket",165,130,300,1118,"foreground",code_in,("code","input")),
        Piece("clean-code-sheet","workflow","Checked code ticket",165,130,785,1115,"foreground",code_out,("code","pass")),
        Piece("reject-bin","machine","Defect reject bin",235,175,703,1363,"foreground",reject,("reject","defect")),
        Piece("caught-bug","workflow","Caught paper bug",140,132,495,947,"character",bug,("bug","defect")),
        Piece("paper-grabber","machine","Scanner bug grabber",130,185,520,802,"character",grabber,("grabber","inspection")),
        Piece("pass-stamp","workflow","Passed inspection card",215,120,728,836,"ui",pass_stamp,("pass","check")),
    ]


def spec_for_id(scene_id: str) -> Spec:
    safe_headline = {"x": 90, "y": 48, "width": 900, "height": 192}
    safe_caption = {"x": 100, "y": 1640, "width": 880, "height": 215}
    if scene_id == "scene-02":
        return Spec(
            scene_id, "Multiple agents compete and the strongest answer wins",
            "Competition arena: three answer agents, a selection board, podium and winner seal.",
            scene02_pieces(),
            (15, 1080, .31), "presenting", "proud",
            {"l": (225, 510, "open"), "r": (795, 508, "open"), "head_tilt": -4},
            "agent-token-blue", safe_headline, safe_caption,
        )
    if scene_id == "scene-03":
        return Spec(
            scene_id, "The system scans your code and catches bugs",
            "Inspection factory: code enters a scanner, a bug is caught, and checked code exits.",
            scene03_pieces(),
            (0, 1100, .35), "pointing", "determined",
            {"l": (278, 670, "mitten"), "r": (825, 523, "point"), "head_tilt": -3},
            "caught-bug", safe_headline, safe_caption,
        )
    raise ValueError(scene_id)


def dirs(scene_id: str) -> tuple[Path, Path, Path]:
    return (ROOT / "assets/scenes" / scene_id,
            ROOT / "scenes" / scene_id,
            ROOT / "previews" / scene_id)


def bot_group(spec: Spec) -> str:
    body, _ = assemble_pose(spec.bot_base, spec.bot_face, spec.bot_overrides)
    x, y, scale = spec.bot_place
    return (
        '<g id="canonical-motif-bot" '
        'data-source="assets/characters/motif-bot/canonical/v1/motif-bot-v1.json" '
        f'transform="translate({x} {y}) scale({scale})">{body}</g>'
    )


def write_assets(spec: Spec) -> None:
    for p in spec.pieces:
        path = p.file(spec.scene_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(svg(p.w, p.h, p.body, p.name))
        metadata = {
            "id": f"{spec.scene_id}-{p.slug}", "name": p.name,
            "category": p.category, "subcategory": p.slug,
            "concepts": list(p.concepts),
            "keywords": [p.slug, "paper-cutout", spec.scene_id],
            "style": "motif-default-v1", "orientation": "front",
            "dimensions": {"width": p.w, "height": p.h, "unit": "px"},
            "artBox": {"x": 0, "y": 0, "width": p.w, "height": p.h},
            "anchors": {key: {"x": xy[0], "y": xy[1]} for key,xy in (p.anchors or {}).items()},
            "compatibleCharacters": ["motif-bot"],
            "supportedActions": ["compose", "swap", "animate"],
            "sourceType": "vector",
            "source": {"file": str(path.relative_to(ROOT)), "generator": "scripts/build_benchmark_scenes.py"},
            "version": 1, "status": "canonical", "benchmark": True,
            "preview": f"previews/{spec.scene_id}/contact-sheet.png",
            "license": "project-original",
            "scenePlacement": {"x": p.x, "y": p.y, "layer": p.layer},
        }
        path.with_suffix(".json").write_text(json.dumps(metadata, indent=2) + "\n")


def layer_order(spec: Spec) -> list[str]:
    if spec.scene_id == "scene-02":
        return ["background","midground","character","foreground","ui"]
    return ["background","midground","foreground","character","ui"]


def write_scene(spec: Spec) -> Path:
    _, out, _ = dirs(spec.scene_id)
    out.mkdir(parents=True, exist_ok=True)
    body = []
    for p in spec.pieces:
        if p.slug == spec.bot_before:
            body.append(bot_group(spec))
        body.append(p.placed(spec.scene_id))
    scene_path = out / f"{spec.scene_id}.svg"
    scene_path.write_text(svg(W,H,"\n".join(body),spec.title,DEFS+BOT_DEFS))
    manifest = {
        "id": spec.scene_id, "name": spec.title, "description": spec.description,
        "version": 1, "status": "canonical", "benchmark": True, "style": "motif-default-v1",
        "dimensions": {"width": W, "height": H, "unit": "px"},
        "render": str(scene_path.relative_to(ROOT)),
        "generator": "scripts/build_benchmark_scenes.py",
        "layerOrder": layer_order(spec),
        "headlineSafeArea": spec.safe_headline,
        "captionSafeArea": spec.safe_caption,
        "character": {
            "source": "assets/characters/motif-bot/canonical/v1/motif-bot-v1.json",
            "geometrySource": "scripts/build_motif_bot.py",
            "status": "canonical",
            "placement": {"x":spec.bot_place[0],"y":spec.bot_place[1],"scale":spec.bot_place[2]},
            "pose": {"base":spec.bot_base,"faceState":spec.bot_face,"overrides":spec.bot_overrides},
            "insertBefore": spec.bot_before,
        },
        "assets": [
            {"id": f"{spec.scene_id}-{p.slug}",
             "source": str(p.file(spec.scene_id).relative_to(ROOT)),
             "metadata": str(p.file(spec.scene_id).with_suffix(".json").relative_to(ROOT)),
             "layer": p.layer, "placement": {"x":p.x,"y":p.y},
             "dimensions": {"width":p.w,"height":p.h}}
            for p in spec.pieces
        ],
        "note": "The composite is reconstructed in list order from independently exported SVGs and the locked Motif Bot puppet.",
    }
    (out / f"{spec.scene_id}.json").write_text(json.dumps(manifest,indent=2)+"\n")
    for layer in layer_order(spec):
        parts=[p.placed(spec.scene_id) for p in spec.pieces if p.layer==layer]
        if layer=="character":
            parts.insert(0,bot_group(spec))
        (out/f"layer-{layer}.svg").write_text(
            svg(W,H,"\n".join(parts),f"{spec.scene_id} {layer} layer",DEFS+BOT_DEFS)
        )
    return scene_path


def preview_contact(spec: Spec) -> None:
    _, _, outdir = dirs(spec.scene_id)
    cols, cw, ch = 4, 360, 330
    rows=(len(spec.pieces)+cols-1)//cols
    out=Image.new("RGBA",(cols*cw,110+rows*ch),P["paper"])
    d=ImageDraw.Draw(out)
    d.text((34,25),f"{spec.scene_id.upper()} / REUSABLE ASSETS",font=font(34,True),fill=P["ink"])
    d.text((36,72),f"{len(spec.pieces)} separate transparent SVGs · approved benchmark",font=font(19),fill=P["tealDark"])
    for i,p in enumerate(spec.pieces):
        x=(i%cols)*cw+18; y=110+(i//cols)*ch+12
        d.rounded_rectangle((x,y,x+cw-36,y+ch-24),radius=17,fill="#CBD7D0",outline="#A9B8AE",width=2)
        art=raster(p.file(spec.scene_id))
        paste_center(out,art,(x+12,y+12,cw-60,ch-82))
        d.text((x+13,y+ch-62),p.name,font=font(18,True),fill=P["ink"])
        d.text((x+13,y+ch-38),f"{p.category} · {p.slug}.svg",font=font(13),fill=P["tealDark"])
    out.convert("RGB").save(outdir/"contact-sheet.png")


def preview_exploded(spec: Spec) -> None:
    _, _, outdir = dirs(spec.scene_id)
    layers=layer_order(spec)
    col_w,row_h=330,275
    groups=[(layer.upper(),[p for p in spec.pieces if p.layer==layer]) for layer in layers]
    height=225+max(len(g)+ (1 if name=="CHARACTER" else 0) for name,g in groups)*row_h
    out=Image.new("RGBA",(len(groups)*col_w,height),P["paper"])
    d=ImageDraw.Draw(out)
    d.text((40,25),f"{spec.scene_id.upper()} / EXPLODED VIEW",font=font(36,True),fill=P["ink"])
    d.text((42,75),"Independent pieces grouped by compositing layer.",font=font(20),fill=P["tealDark"])
    for ci,(heading,group) in enumerate(groups):
        x=ci*col_w+20
        d.rounded_rectangle((x,130,x+col_w-40,height-35),radius=16,fill="#D6DED5",outline="#B2BFB6",width=2)
        d.text((x+16,151),heading,font=font(20,True),fill=P["ink"])
        entries=[("Motif Bot v1 (locked)",None)] + [(p.name,p) for p in group] if heading=="CHARACTER" else [(p.name,p) for p in group]
        for ri,(name,p) in enumerate(entries):
            y=198+ri*row_h
            d.rounded_rectangle((x+12,y,x+col_w-52,y+row_h-20),radius=12,fill="#EEF0E6")
            if p is None:
                bot,_=assemble_pose(spec.bot_base,spec.bot_face,spec.bot_overrides)
                art=raster(svg(1024,1024,bot,"Motif Bot v1",DEFS+BOT_DEFS))
                sub="canonical character"
            else:
                art=raster(p.file(spec.scene_id)); sub=p.slug
            paste_center(out,art,(x+25,y+8,col_w-104,row_h-75))
            d.text((x+28,y+row_h-58),name,font=font(16,True),fill=P["ink"])
            d.text((x+28,y+row_h-34),sub,font=font(14),fill=P["tealDark"])
    out.convert("RGB").save(outdir/"exploded-view.png")


def preview_layers(spec: Spec) -> None:
    _, _, outdir=dirs(spec.scene_id)
    layers=layer_order(spec)
    colors=[P["plum"],P["night2"],P["tealDark"],P["woodEdge"],P["ink"]]
    out=Image.new("RGB",(1320,920),P["paper"]); d=ImageDraw.Draw(out)
    d.text((52,40),f"{spec.scene_id.upper()} / LAYER STACK",font=font(38,True),fill=P["ink"])
    d.text((55,97),"Back-to-front order. Source paths and placements live in the scene manifest.",font=font(21),fill=P["tealDark"])
    for i,layer in enumerate(layers):
        x=80+i*35;y=176+i*132
        names=[p.slug for p in spec.pieces if p.layer==layer]
        if layer=="character": names.insert(0,"canonical Motif Bot")
        summary=", ".join(names)
        if len(summary)>81: summary=summary[:78]+"..."
        d.rounded_rectangle((x,y,x+1070,y+108),radius=20,fill=colors[i])
        d.text((x+25,y+19),f"{i+1:02}",font=font(39,True),fill=P["paper"])
        d.text((x+110,y+18),layer.upper(),font=font(26,True),fill=P["paper"])
        d.text((x+110,y+59),summary,font=font(16),fill=P["paper"])
    d.text((55,875),"Headline and caption safe areas are empty in the scene render.",font=font(19),fill=P["ink"])
    out.save(outdir/"layer-diagram.png")


def preview_mobile(spec: Spec, scene: Image.Image) -> None:
    _, _, outdir=dirs(spec.scene_id)
    out=Image.new("RGB",(1080,790),"#E8E8DF");d=ImageDraw.Draw(out)
    d.text((42,35),"MOBILE READABILITY / 360 × 640",font=font(30,True),fill=P["ink"])
    small=scene.resize((360,640),Image.Resampling.LANCZOS).convert("RGB")
    out.paste(small,(54,113))
    crop=small.crop((45,225,345,505)).resize((540,504),Image.Resampling.NEAREST)
    out.paste(crop,(465,153))
    d.text((469,116),"Central story enlarged for inspection",font=font(20),fill=P["tealDark"])
    d.text((466,682),"Full scene at native mobile size",font=font(20),fill=P["ink"])
    out.save(outdir/"mobile-preview.png")


def build(spec: Spec) -> None:
    _, _, previews=dirs(spec.scene_id)
    previews.mkdir(parents=True,exist_ok=True)
    write_assets(spec)
    scene_path=write_scene(spec)
    rendered=raster(scene_path)
    rendered.convert("RGB").save(previews/"scene-full.png")
    preview_contact(spec)
    preview_exploded(spec)
    preview_layers(spec)
    preview_mobile(spec,rendered)
    print(f"{spec.scene_id}: {len(spec.pieces)} independent SVGs, scene and four review previews")


def benchmark_triptych() -> None:
    scenes=[
        ("01 / NIGHT DESK",ROOT/"previews/scene-01/scene-full.png"),
        ("02 / ARENA",ROOT/"previews/scene-02/scene-full.png"),
        ("03 / INSPECTION",ROOT/"previews/scene-03/scene-full.png"),
    ]
    out=Image.new("RGB",(1240,810),P["paper"])
    d=ImageDraw.Draw(out)
    d.text((38,25),"MOTIF / THREE BENCHMARK WORLDS",font=font(34,True),fill=P["ink"])
    d.text((40,70),"Same locked mascot, matte paper grammar and modular asset contract.",font=font(20),fill=P["tealDark"])
    for i,(label,path) in enumerate(scenes):
        x=40+i*400
        d.text((x,113),label,font=font(19,True),fill=P["ink"])
        image=Image.open(path).convert("RGB").resize((360,640),Image.Resampling.LANCZOS)
        out.paste(image,(x,150))
        d.rectangle((x-1,149,x+361,791),outline=P["edge"],width=2)
    out.save(ROOT/"previews/benchmark-triptych.png")


def main() -> None:
    for scene_id in ("scene-02","scene-03"):
        build(spec_for_id(scene_id))
    benchmark_triptych()


if __name__=="__main__":
    main()
