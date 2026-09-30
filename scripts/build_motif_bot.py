#!/usr/bin/env python3
"""Build the Motif Bot A cutout puppet and review sheets from editable SVG shapes.

No model or external asset is needed after the approved concept. All generated
SVGs share the same coordinate system, palette, anchors, and ten puppet controls.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/characters/motif-bot/canonical/v1"
PROOFS = ROOT / "previews/motif-bot-a-v1/proofs"
W = H = 1024

C = {
    "paper": "#F4EBD8", "edge": "#DCCDB3", "ink": "#202C32",
    "teal": "#56BFB1", "teal_dark": "#318E85", "mint": "#A6E5D6",
    "coral": "#DF806B", "shadow": "#43534D",
}

DEFS = f'''<defs>
<pattern id="grain" width="31" height="29" patternUnits="userSpaceOnUse">
  <circle cx="4" cy="6" r="1.2" fill="#806F5D" opacity=".16"/>
  <circle cx="23" cy="12" r=".85" fill="#806F5D" opacity=".13"/>
  <circle cx="12" cy="24" r=".7" fill="#806F5D" opacity=".12"/>
  <path d="M18 3 l2 .7 M5 20 l2 -.4" stroke="#806F5D" stroke-width=".8" opacity=".12"/>
  <circle cx="28" cy="27" r="1.5" fill="#FFFFFF" opacity=".16"/>
</pattern>
<pattern id="darkGrain" width="29" height="31" patternUnits="userSpaceOnUse">
  <circle cx="7" cy="9" r=".9" fill="#F4EBD8" opacity=".09"/>
  <circle cx="20" cy="23" r=".7" fill="#F4EBD8" opacity=".08"/>
</pattern>
</defs>'''


def wrap(content: str, title: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}" role="img" aria-label="{title}">\n'
            f'<title>{title}</title>\n{DEFS}\n{content}\n</svg>\n')


def paper_path(d: str, color: str = "paper", edge: bool = True) -> str:
    under = (f'<path d="{d}" transform="translate(7 9)" fill="{C["shadow"]}" opacity=".10"/>'
             f'<path d="{d}" transform="translate(3 5)" fill="{C["edge"]}" opacity=".53"/>') if edge else ""
    return (under + f'<path d="{d}" fill="{C[color]}"/>'
            f'<path d="{d}" fill="url(#grain)" opacity=".78"/>'
            f'<path d="{d}" fill="none" stroke="{C["edge"]}" stroke-width="2" opacity=".35"/>')


HEAD_D = "M328 206 Q360 171 500 166 Q657 160 703 197 Q739 224 746 282 L743 423 Q736 481 687 491 Q515 509 348 484 Q287 472 278 419 L278 288 Q281 234 328 206 Z"
FACE_D = "M353 242 Q502 212 662 241 Q709 251 714 289 L711 407 Q705 450 664 461 Q509 479 361 455 Q316 447 309 405 L309 294 Q314 258 353 242 Z"
TORSO_D = "M435 511 Q503 498 585 513 Q613 518 628 563 L659 719 Q661 746 631 755 Q511 790 388 756 Q358 746 365 713 L394 565 Q403 522 435 511 Z"
CHEST_D = "M433 596 Q512 578 591 597 Q608 605 608 626 L606 704 Q605 721 585 726 Q508 741 435 723 Q418 719 417 698 L417 627 Q418 604 433 596 Z"


def antennae() -> str:
    return '<g id="antennae" data-part="antennae">' + (
        f'<path d="M415 208 Q391 164 366 127" fill="none" stroke="{C["edge"]}" stroke-width="19" stroke-linecap="round"/>'
        f'<path d="M610 206 Q629 160 658 128" fill="none" stroke="{C["edge"]}" stroke-width="19" stroke-linecap="round"/>'
        f'<path d="M365 132 Q311 99 306 44 Q358 42 389 79 Q399 108 365 132 Z" fill="{C["teal"]}"/>'
        f'<path d="M658 131 Q712 104 717 54 Q663 48 635 88 Q625 112 658 131 Z" fill="{C["teal_dark"]}"/>'
        '<path d="M365 132 Q311 99 306 44 Q358 42 389 79 Q399 108 365 132 Z" fill="url(#grain)"/>'
        '<path d="M658 131 Q712 104 717 54 Q663 48 635 88 Q625 112 658 131 Z" fill="url(#grain)"/>'
    ) + '</g>'


def head_shell() -> str:
    side = (f'<ellipse cx="267" cy="344" rx="36" ry="66" fill="{C["edge"]}"/>'
            f'<ellipse cx="267" cy="338" rx="30" ry="60" fill="{C["paper"]}"/>'
            f'<ellipse cx="267" cy="338" rx="19" ry="46" fill="{C["teal_dark"]}"/>'
            f'<ellipse cx="758" cy="344" rx="36" ry="66" fill="{C["edge"]}"/>'
            f'<ellipse cx="758" cy="338" rx="30" ry="60" fill="{C["paper"]}"/>'
            f'<ellipse cx="758" cy="338" rx="19" ry="46" fill="{C["teal_dark"]}"/>')
    return f'<g id="headShell" data-part="headShell">{side}{paper_path(HEAD_D)}</g>'


def face_panel() -> str:
    return (f'<g id="facePanel" data-part="facePanel">'
            f'<path d="{FACE_D}" transform="translate(2 4)" fill="#172127" opacity=".48"/>'
            f'<path d="{FACE_D}" fill="{C["ink"]}"/>'
            f'<path d="{FACE_D}" fill="url(#darkGrain)"/></g>')


def face_state(name: str) -> str:
    # Eyes and mouth are editable paths in one replaceable visual state.
    arc_l = 'M385 345 Q419 294 454 345'
    arc_r = 'M566 345 Q601 294 636 345'
    smile = 'M472 393 Q512 424 552 393'
    eye = f'stroke="{C["mint"]}" stroke-width="19" fill="none" stroke-linecap="round"'
    mouth = f'stroke="{C["mint"]}" stroke-width="13" fill="none" stroke-linecap="round"'
    cheeks = ''
    if name in {'happy', 'excited', 'proud'}:
        cheeks = f'<ellipse cx="358" cy="387" rx="15" ry="10" fill="{C["coral"]}"/><ellipse cx="666" cy="387" rx="15" ry="10" fill="{C["coral"]}"/>'
    if name == 'neutral':
        eyes = f'<ellipse cx="419" cy="338" rx="12" ry="22" fill="{C["mint"]}"/><ellipse cx="601" cy="338" rx="12" ry="22" fill="{C["mint"]}"/>'
        lips = f'<path d="{smile}" {mouth}/>'
    elif name in {'happy', 'proud'}:
        eyes = f'<path d="{arc_l}" {eye}/><path d="{arc_r}" {eye}/>'
        lips = f'<path d="M466 386 Q512 435 558 386" {mouth}/>'
    elif name == 'excited':
        eyes = f'<path d="{arc_l}" {eye}/><path d="{arc_r}" {eye}/>'
        lips = f'<path d="M477 381 Q512 446 548 381 Z" fill="{C["mint"]}"/>'
    elif name in {'surprised', 'shocked'}:
        rad = 18 if name == 'surprised' else 24
        eyes = f'<ellipse cx="419" cy="335" rx="{rad}" ry="{rad+7}" fill="{C["mint"]}"/><ellipse cx="601" cy="335" rx="{rad}" ry="{rad+7}" fill="{C["mint"]}"/>'
        lips = f'<ellipse cx="512" cy="400" rx="{20 if name == "surprised" else 28}" ry="{26 if name == "surprised" else 33}" fill="{C["mint"]}"/>'
    elif name == 'confused':
        eyes = f'<path d="M389 324 Q421 299 452 334" {eye}/><path d="M570 335 Q605 298 635 324" {eye}/>'
        lips = f'<path d="M478 406 Q505 390 531 409 L550 403" {mouth}/>'
    elif name == 'thinking':
        eyes = f'<ellipse cx="430" cy="334" rx="11" ry="19" fill="{C["mint"]}"/><ellipse cx="612" cy="334" rx="11" ry="19" fill="{C["mint"]}"/>'
        lips = f'<path d="M490 406 Q521 396 546 403" {mouth}/>'
    elif name == 'worried':
        eyes = f'<path d="M388 330 Q418 351 451 330" {eye}/><path d="M572 330 Q602 351 635 330" {eye}/>'
        lips = f'<path d="M474 418 Q512 380 550 418" {mouth}/>'
    elif name == 'determined':
        eyes = f'<path d="M388 317 L451 344" {eye}/><path d="M572 344 L635 317" {eye}/>'
        lips = f'<path d="M480 401 L544 401" {mouth}/>'
    elif name == 'annoyed':
        eyes = f'<path d="M390 337 L451 337" {eye}/><path d="M573 337 L634 337" {eye}/>'
        lips = f'<path d="M480 410 Q511 397 545 408" {mouth}/>'
    elif name == 'sleepy':
        eyes = f'<path d="M388 342 Q419 355 451 342" {eye}/><path d="M573 342 Q603 355 635 342" {eye}/>'
        lips = f'<path d="M490 402 Q512 415 536 402" {mouth}/>'
    else:
        raise ValueError(name)
    return f'<g id="faceState" data-part="faceState" data-state="{name}">{cheeks}{eyes}{lips}</g>'


def torso() -> str:
    return (f'<g id="body" data-part="body">{paper_path(TORSO_D)}'
            f'<path d="{CHEST_D}" fill="{C["teal_dark"]}"/>'
            f'<path d="{CHEST_D}" fill="url(#grain)" opacity=".45"/>'
            f'<path d="M482 627 L448 660 L483 693 M542 627 L576 660 L541 693" '
            f'fill="none" stroke="{C["paper"]}" stroke-width="21" stroke-linejoin="round" stroke-linecap="round"/>'
            '</g>')


HAND_D = {
    'mitten': 'M-26 -13 Q-25 -31 -9 -31 Q1 -31 6 -20 Q16 -29 27 -19 Q34 -12 29 1 Q39 8 31 21 Q20 35 0 33 Q-30 33 -32 10 Q-34 -3 -26 -13 Z',
    'open': 'M-30 14 Q-39 4 -32 -7 Q-26 -14 -18 -10 L-22 -36 Q-23 -47 -12 -49 Q-3 -50 0 -39 L4 -49 Q9 -59 19 -54 Q25 -49 20 -37 L29 -43 Q39 -48 44 -39 Q49 -30 38 -20 L28 -8 Q40 2 31 19 Q18 38 -5 35 Q-22 33 -30 14 Z',
    'point': 'M-27 -5 Q-28 -19 -13 -24 L7 -27 L33 -59 Q42 -68 50 -61 Q58 -55 51 -45 L32 -16 Q40 -8 37 7 Q34 31 9 34 Q-28 36 -32 13 Z',
    'grip': 'M-28 -24 Q-5 -39 20 -25 L33 -15 Q42 -7 31 1 L19 7 Q10 10 6 1 L-2 -2 Q-10 4 -8 14 Q-4 23 7 21 L20 14 Q30 8 36 18 Q40 27 30 34 Q9 47 -15 34 Q-38 22 -37 1 Q-37 -15 -28 -24 Z',
    'fist': 'M-28 -12 Q-22 -32 1 -35 Q24 -35 34 -18 Q43 -3 34 18 Q26 36 1 37 Q-24 36 -35 17 Q-42 1 -28 -12 Z',
}


def hand(kind: str, x: float, y: float, rot: float = 0, side: str = 'right') -> str:
    d = HAND_D[kind]
    mirror = 'scale(-1 1)' if side == 'left' else ''
    return (f'<g id="{side}Hand" data-part="{side}Hand" data-state="{kind}" '
            f'transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) {mirror}">'
            f'<path d="{d}" transform="translate(6 7)" fill="{C["shadow"]}" opacity=".1"/>'
            f'<path d="{d}" transform="translate(3 4)" fill="{C["edge"]}" opacity=".62"/>'
            f'<path d="{d}" fill="{C["teal"]}"/>'
            f'<path d="{d}" fill="url(#grain)" opacity=".5"/></g>')


def arm(side: str, ex: float, ey: float, hand_kind: str, curve: float = 0, hand_rot: float = 0) -> tuple[str, str]:
    sx = 396 if side == 'left' else 628
    sy = 554
    cx = (sx + ex) / 2 + curve
    cy = (sy + ey) / 2 - 12
    d = f'M{sx} {sy} Q{cx:.1f} {cy:.1f} {ex:.1f} {ey:.1f}'
    main = (f'<g id="{side}Arm" data-part="{side}Arm" data-control="{cx:.1f},{cy:.1f}">'
            f'<path d="{d}" transform="translate(4 5)" fill="none" stroke="{C["edge"]}" stroke-width="62" stroke-linecap="round"/>'
            f'<path d="{d}" fill="none" stroke="{C["paper"]}" stroke-width="58" stroke-linecap="round"/>'
            f'<path d="{d}" fill="none" stroke="url(#grain)" stroke-width="58" stroke-linecap="round" opacity=".5"/>'
            f'<circle cx="{sx}" cy="{sy}" r="23" fill="{C["teal_dark"]}"/>'
            '</g>')
    return main, hand(hand_kind, ex, ey, hand_rot, side)


def leg(side: str, fx: float, fy: float, rot: float = 0) -> tuple[str, str]:
    hipx = 440 if side == 'left' else 584
    foot_path = 'M-72 -16 Q-69 -39 -35 -43 L30 -43 Q61 -39 69 -12 L74 21 Q75 39 53 43 L-59 43 Q-78 40 -78 22 Z'
    line = (f'<g id="{side}Leg" data-part="{side}Leg">'
            f'<path d="M{hipx} 740 Q{(hipx+fx)/2:.1f} {(740+fy-36)/2:.1f} {fx:.1f} {fy-35:.1f}" '
            f'fill="none" stroke="{C["paper"]}" stroke-width="48" stroke-linecap="round"/></g>')
    shoe = (f'<g id="{side}Foot" data-part="{side}Foot" transform="translate({fx:.1f} {fy:.1f}) rotate({rot:.1f})">'
            f'<path d="{foot_path}" transform="translate(3 4)" fill="{C["edge"]}"/>'
            f'<path d="{foot_path}" fill="{C["paper"]}"/>'
            f'<path d="M-76 17 Q-5 28 73 16 L74 24 Q72 40 52 43 L-58 43 Q-77 40 -78 22 Z" fill="{C["teal_dark"]}"/>'
            f'<path d="{foot_path}" fill="url(#grain)" opacity=".5"/></g>')
    return line, shoe


POSES = {
    'standing': {'l': (278, 676, 'mitten'), 'r': (746, 676, 'mitten')},
    'sitting': {'l': (286, 652, 'mitten'), 'r': (738, 652, 'mitten'), 'feet': ((397, 805, -12), (627, 805, 12)), 'body_y': 24},
    'walking': {'l': (283, 663, 'mitten'), 'r': (731, 618, 'mitten'), 'feet': ((389, 868, -18), (651, 836, 19))},
    'running': {'l': (318, 478, 'fist'), 'r': (752, 690, 'fist'), 'feet': ((368, 860, -27), (667, 814, 30)), 'tilt': 10},
    'pointing': {'l': (278, 670, 'mitten'), 'r': (793, 515, 'point')},
    'typing': {'l': (451, 647, 'mitten'), 'r': (570, 647, 'mitten'), 'feet': ((427, 867, 0), (597, 867, 0))},
    'holding-object': {'l': (298, 684, 'mitten'), 'r': (755, 581, 'grip')},
    'carrying-object': {'l': (417, 654, 'grip'), 'r': (605, 654, 'grip')},
    'inspecting': {'l': (279, 670, 'mitten'), 'r': (670, 435, 'point'), 'face': 'thinking', 'head_tilt': -8},
    'celebrating': {'l': (282, 431, 'open'), 'r': (745, 432, 'open'), 'face': 'excited'},
    'falling': {'l': (285, 495, 'open'), 'r': (731, 473, 'open'), 'feet': ((384, 846, -25), (653, 850, 28)), 'tilt': -38, 'face': 'shocked'},
    'pushing': {'l': (786, 541, 'fist'), 'r': (786, 610, 'mitten'), 'feet': ((383, 879, -14), (638, 846, 10)), 'tilt': 9, 'face': 'determined'},
    'pulling': {'l': (770, 547, 'grip'), 'r': (765, 619, 'grip'), 'feet': ((385, 862, 12), (644, 869, -12)), 'tilt': -9, 'face': 'determined'},
    'presenting': {'l': (233, 562, 'open'), 'r': (791, 562, 'open'), 'face': 'happy'},
    'thinking': {'l': (284, 685, 'mitten'), 'r': (609, 459, 'fist'), 'face': 'thinking', 'head_tilt': -6},
    'magnifying-glass': {'l': (282, 680, 'mitten'), 'r': (652, 445, 'grip'), 'face': 'thinking'},
}

EXPRESSIONS = [
    'neutral', 'happy', 'excited', 'surprised', 'confused', 'thinking',
    'worried', 'determined', 'annoyed', 'proud', 'sleepy', 'shocked',
]


def assemble_pose(name: str = 'standing', expression: str | None = None,
                  overrides: dict | None = None) -> tuple[str, dict[str, str]]:
    p = dict(POSES[name])
    if overrides:
        p.update(overrides)
    left, right = p['l'], p['r']
    feet = p.get('feet', ((425, 861, 0), (599, 861, 0)))
    larm, lhand = arm('left', *left)
    rarm, rhand = arm('right', *right)
    lleg, lfoot = leg('left', *feet[0])
    rleg, rfoot = leg('right', *feet[1])
    head_tilt = p.get('head_tilt', 0)
    selected_face = face_state(expression or p.get('face', 'neutral'))
    head_group = (f'<g id="head" data-part="head" transform="rotate({head_tilt} 512 350)">'
                  f'{antennae()}{head_shell()}{face_panel()}{selected_face}</g>')
    body = (lleg + rleg + lfoot + rfoot + larm + rarm + torso() + head_group + lhand + rhand)
    if p.get('body_y'):
        body = f'<g transform="translate(0 {p["body_y"]})">{body}</g>'
    if p.get('tilt'):
        body = f'<g transform="rotate({p["tilt"]} 512 620)">{body}</g>'
    pieces = {
        'antennae': antennae(), 'head': head_shell(), 'face-panel': face_panel(),
        'face-state': selected_face,
        'body': torso(), 'left-arm': larm, 'right-arm': rarm,
        'left-hand': lhand, 'right-hand': rhand,
        'left-leg': lleg, 'left-foot': lfoot, 'right-leg': rleg, 'right-foot': rfoot,
    }
    return body, pieces


def alternate_view(view: str) -> str:
    # Separate graphic turnarounds; no 3D projection is used.
    if view.startswith('front-three-quarter'):
        side = -1 if view.endswith('left') else 1
        body, _ = assemble_pose()
        plane = (f'<path d="M694 218 Q751 238 764 295 L762 411 Q756 467 704 483 '
                 f'Q719 374 694 218 Z" fill="{C["edge"]}"/>'
                 f'<path d="M706 237 Q748 258 753 310 L750 405 Q743 450 714 469" '
                 f'fill="none" stroke="{C["paper"]}" stroke-width="14"/>'
                 f'<ellipse cx="756" cy="339" rx="34" ry="65" fill="{C["paper"]}"/>'
                 f'<ellipse cx="758" cy="339" rx="20" ry="48" fill="{C["teal_dark"]}"/>')
        mirror = 'translate(1024 0) scale(-1 1)' if side == 1 else ''
        return (f'<g transform="{mirror}">'
                f'<g transform="translate(-26 0) translate(512 0) scale(.93 1) translate(-512 0)">{body}</g>'
                f'<g id="headSidePlane" data-view-only="true">{plane}</g></g>')
    if view in {'left-side', 'right-side'}:
        flip = 'translate(1024 0) scale(-1 1)' if view == 'right-side' else ''
        return (f'<g transform="{flip}">'
                f'{"".join(leg("left", 488, 862))}'
                f'<g id="body">{paper_path("M452 509 Q516 491 572 515 L606 718 Q600 758 475 759 Q439 746 440 707 Z")}'
                f'<path d="M538 620 L558 657 L538 690" fill="none" stroke="{C["teal_dark"]}" stroke-width="17" stroke-linecap="round"/></g>'
                f'<path d="M468 550 Q404 580 419 694" fill="none" stroke="{C["paper"]}" stroke-width="52" stroke-linecap="round"/>'
                f'{hand("mitten", 419, 694, 0, "left")}'
                f'<g id="head"><g id="antennae"><path d="M520 211 L505 121" stroke="{C["edge"]}" stroke-width="17"/>'
                f'<path d="M505 124 Q451 92 468 50 Q526 69 535 104 Q528 121 505 124 Z" fill="{C["teal"]}"/></g>'
                f'<g id="headShell">{paper_path("M421 201 Q488 166 569 183 Q630 196 649 266 L647 414 Q636 480 563 495 Q463 503 416 456 Q389 427 391 342 L396 279 Q399 229 421 201 Z")}'
                f'<ellipse cx="409" cy="342" rx="32" ry="61" fill="{C["paper"]}"/>'
                f'<ellipse cx="408" cy="340" rx="21" ry="47" fill="{C["teal_dark"]}"/></g>'
                f'<g id="facePanel"><path d="M515 239 Q605 225 625 281 L626 400 Q616 454 516 458 Q487 409 486 344 Q487 277 515 239 Z" fill="{C["ink"]}"/></g>'
                f'<g id="faceState"><ellipse cx="558" cy="337" rx="11" ry="20" fill="{C["mint"]}"/>'
                f'<path d="M540 391 Q562 408 583 391" stroke="{C["mint"]}" stroke-width="11" fill="none" stroke-linecap="round"/></g></g>'
                f'</g>')
    if view == 'back':
        return (f'{"".join(leg("left", 425, 861))}{"".join(leg("right", 599, 861))}'
                f'{arm("left", 278, 676, "mitten")[0]}{arm("right", 746, 676, "mitten")[0]}'
                f'<g id="body">{paper_path(TORSO_D)}'
                f'<rect x="480" y="642" width="64" height="32" rx="8" fill="{C["edge"]}"/>'
                f'<rect x="490" y="651" width="44" height="14" rx="4" fill="{C["teal_dark"]}"/></g>'
                f'{antennae()}<g id="head">{paper_path(HEAD_D)}'
                f'<rect x="469" y="327" width="86" height="64" rx="13" fill="{C["edge"]}"/>'
                f'<rect x="482" y="340" width="60" height="11" rx="3" fill="{C["teal_dark"]}"/>'
                f'<rect x="482" y="365" width="60" height="11" rx="3" fill="{C["teal_dark"]}"/></g>'
                f'{hand("mitten",278,676,0,"left")}{hand("mitten",746,676,0,"right")}')
    raise ValueError(view)


def demo_prop(name: str) -> str:
    """Disposable pose-reading aids, exported separately from the puppet files."""
    ink, teal, paper = C['ink'], C['teal_dark'], C['paper']
    art = {
        'sitting': f'<path d="M345 762 L682 762" stroke="{teal}" stroke-width="18"/><path d="M400 764 L384 882 M625 764 L641 882" stroke="{ink}" stroke-width="13"/>',
        'typing': f'<rect x="392" y="690" width="240" height="50" rx="8" fill="{ink}"/><path d="M412 706 H612 M412 723 H612" stroke="{paper}" stroke-width="6" stroke-dasharray="17 7"/>',
        'holding-object': f'<rect x="755" y="529" width="96" height="90" rx="13" fill="{teal}"/><rect x="773" y="548" width="58" height="45" rx="6" fill="{paper}"/>',
        'carrying-object': f'<rect x="438" y="590" width="148" height="104" rx="9" fill="{C["edge"]}" stroke="{ink}" stroke-width="5"/><path d="M511 591 L511 694" stroke="{ink}" stroke-width="5"/>',
        'inspecting': f'<rect x="705" y="376" width="118" height="133" rx="8" fill="{paper}" stroke="{ink}" stroke-width="5"/><circle cx="764" cy="432" r="22" fill="none" stroke="{teal}" stroke-width="7"/>',
        'pushing': f'<rect x="786" y="521" width="174" height="177" rx="14" fill="{C["edge"]}" stroke="{ink}" stroke-width="5"/>',
        'pulling': f'<path d="M769 579 L865 579" stroke="{ink}" stroke-width="10"/><rect x="865" y="522" width="97" height="145" rx="11" fill="{C["edge"]}" stroke="{ink}" stroke-width="5"/>',
        'magnifying-glass': f'<path d="M651 444 L687 409" stroke="{ink}" stroke-width="16" stroke-linecap="round"/><circle cx="717" cy="379" r="48" fill="{paper}" stroke="{ink}" stroke-width="12"/><circle cx="717" cy="379" r="34" fill="{C["mint"]}" opacity=".35"/>',
    }.get(name, '')
    return f'<g id="demoProp" data-preview-only="true">{art}</g>' if art else ''


def write(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data)


def preset_record(name: str, p: dict) -> dict:
    feet = p.get('feet', ((425, 861, 0), (599, 861, 0)))
    return {
        'id': name,
        'leftArm': {'end': [p['l'][0], p['l'][1]], 'hand': p['l'][2], 'curve': 0},
        'rightArm': {'end': [p['r'][0], p['r'][1]], 'hand': p['r'][2], 'curve': 0},
        'leftFoot': {'position': [feet[0][0], feet[0][1]], 'rotation': feet[0][2]},
        'rightFoot': {'position': [feet[1][0], feet[1][1]], 'rotation': feet[1][2]},
        'headRotation': p.get('head_tilt', 0),
        'bodyRotation': p.get('tilt', 0),
        'bodyOffsetY': p.get('body_y', 0),
        'faceState': p.get('face', 'neutral'),
    }


def main() -> None:
    # Retire only exports generated by the preceding review build. The phase 2
    # concept files and any unrelated project work are untouched.
    for old_dir in ('poses', 'pose-demos', 'expressions'):
        path = OUT / old_dir
        if path.is_dir():
            shutil.rmtree(path)
    for old_file in ('parts/left-leg-foot.svg', 'parts/left-leg-foot.json',
                     'parts/right-leg-foot.svg', 'parts/right-leg-foot.json',
                     'parts/torso.svg', 'parts/torso.json',
                     'hands/wave.svg', 'hands/wave.json'):
        (OUT / old_file).unlink(missing_ok=True)
    body, parts = assemble_pose()
    write(OUT / 'motif-bot-front-neutral-v1.svg', wrap(body, 'Motif Bot A front neutral'))
    for name, markup in parts.items():
        write(OUT / 'parts' / f'{name}.svg', wrap(markup, f'Motif Bot {name} part'))
    for kind in HAND_D:
        write(OUT / 'hands' / f'{kind}.svg', wrap(hand(kind, 512, 512), f'Motif Bot {kind} hand'))
    for name in EXPRESSIONS:
        whole, _ = assemble_pose('standing', name)
        write(PROOFS / 'expressions' / f'{name}.svg', wrap(whole, f'Motif Bot {name} expression proof'))
        write(OUT / 'face-states' / f'{name}.svg', wrap(face_state(name), f'Motif Bot {name} face state'))
    for name in POSES:
        whole, _ = assemble_pose(name)
        write(PROOFS / 'poses' / f'{name}.svg', wrap(whole, f'Motif Bot {name} pose proof'))
        if demo_prop(name):
            write(PROOFS / 'pose-demos' / f'{name}.svg', wrap(whole + demo_prop(name), f'Motif Bot {name} pose demonstration'))
    for name in ['front', 'front-three-quarter-left', 'front-three-quarter-right', 'left-side', 'right-side', 'back']:
        if name == 'front':
            whole = body
        else:
            whole = alternate_view(name)
        write(OUT / 'views' / f'{name}.svg', wrap(whole, f'Motif Bot {name} view'))
    presets = {
        'schemaVersion': 1, 'id': 'motif-bot-a-v1-pose-presets',
        'coordinateSpace': {'width': W, 'height': H, 'unit': 'px'},
        'representation': 'parameters',
        'description': 'Pose recipes for one reusable puppet; proof SVGs are preview artifacts.',
        'presets': {name: preset_record(name, spec) for name, spec in POSES.items()},
    }
    write(OUT / 'pose-presets.json', json.dumps(presets, indent=2) + '\n')
    art_box = {'x': 205, 'y': 44, 'width': 614, 'height': 867}
    anchor_pixels = {
        'neck': (512, 505), 'headAccessory': (512, 190), 'faceAccessory': (512, 347),
        'leftShoulder': (396, 554), 'rightShoulder': (628, 554),
        'leftHand': (278, 676), 'rightHand': (746, 676),
        'torsoAccessory': (512, 660), 'backAccessory': (512, 660),
        'leftHip': (440, 740), 'rightHip': (584, 740),
        'leftFoot': (425, 861), 'rightFoot': (599, 861),
        'groundContact': (512, 906),
    }
    anchors = {key: {'x': round((xy[0]-art_box['x'])/art_box['width'], 5),
                     'y': round((xy[1]-art_box['y'])/art_box['height'], 5)}
               for key, xy in anchor_pixels.items()}
    manifest = {
        'id': 'motif-bot-a-v1', 'name': 'Motif Bot A minimal cutout puppet',
        'category': 'character', 'subcategory': 'mascot',
        'concepts': ['assistant', 'coding', 'friendly', 'paper-cutout'],
        'keywords': ['robot', 'cream', 'teal', 'dark-display', 'antennae', 'code-badge'],
        'style': 'motif-default-v1', 'orientation': 'front',
        'dimensions': {'width': W, 'height': H, 'unit': 'px'},
        'artBox': art_box,
        'anchors': anchors,
        'anchorPixels': {key: {'x': xy[0], 'y': xy[1]} for key, xy in anchor_pixels.items()},
        'visualGroups': ['head', 'body', 'leftArm', 'leftHand', 'rightArm', 'rightHand', 'leftLeg', 'leftFoot', 'rightLeg', 'rightFoot'],
        'headSubcomponents': ['headShell', 'facePanel', 'faceState', 'antennae'],
        'handStates': list(HAND_D), 'faceStates': EXPRESSIONS,
        'views': ['front', 'front-three-quarter-left', 'front-three-quarter-right', 'left-side', 'right-side', 'back'],
        'posePresets': str((OUT / 'pose-presets.json').relative_to(ROOT)),
        'poseRenderMode': 'parameterized', 'poseProofs': str(PROOFS.relative_to(ROOT)),
        'supportedActions': list(POSES), 'compatibleCharacters': ['motif-bot'],
        'sourceType': 'vector',
        'source': {'file': str((OUT / 'motif-bot-front-neutral-v1.svg').relative_to(ROOT)),
                   'generator': 'scripts/build_motif_bot.py',
                   'identityReference': 'user-supplied robot image',
                   'styleReference': 'seven user-supplied videos and selected concept A'},
        'version': 1, 'status': 'canonical', 'riggable': True,
        'license': 'project-original',
    }
    write(OUT / 'motif-bot-v1.json', json.dumps(manifest, indent=2) + '\n')
    # Each exported file is independently discoverable; the manifest above is
    # the authoritative assembled-puppet contract.
    for path in sorted(OUT.rglob('*.svg')):
        rel = path.relative_to(OUT)
        family = rel.parts[0] if len(rel.parts) > 1 else 'master'
        label = path.stem.replace('-', ' ')
        if family == 'views':
            orientation = path.stem
            actions = ['stand']
            preview = 'previews/mascot-turnaround.png'
        elif family == 'face-states':
            orientation = 'front'
            actions = ['express']
            preview = 'previews/mascot-expressions.png'
        else:
            orientation = 'front'
            actions = ['compose']
            preview = 'previews/motif-bot-front-neutral-v1.png'
        if family == 'hands':
            local_anchors = {'grip': {'x': .5, 'y': .5}}
        elif family == 'parts':
            local_names = {
                'head': ['neck', 'headAccessory', 'faceAccessory'],
                'body': ['neck', 'leftShoulder', 'rightShoulder', 'leftHip', 'rightHip'],
                'left-arm': ['leftShoulder', 'leftHand'],
                'right-arm': ['rightShoulder', 'rightHand'],
                'left-leg': ['leftHip', 'leftFoot'],
                'right-leg': ['rightHip', 'rightFoot'],
                'left-foot': ['leftFoot'],
                'right-foot': ['rightFoot'],
                'left-hand': ['leftHand'],
                'right-hand': ['rightHand'],
            }.get(path.stem, [])
            local_anchors = {n: {'x': round(anchor_pixels[n][0]/W, 5), 'y': round(anchor_pixels[n][1]/H, 5)} for n in local_names}
        else:
            local_anchors = {}
        sidecar = {
            'id': 'motif-bot-v1-' + '-'.join(rel.with_suffix('').parts),
            'name': 'Motif Bot ' + label, 'category': 'character',
            'subcategory': family, 'concepts': ['assistant', 'coding', 'paper-cutout'],
            'keywords': ['cream', 'teal', family, path.stem],
            'style': 'motif-default-v1', 'orientation': orientation,
            'dimensions': {'width': W, 'height': H, 'unit': 'px'},
            'artBox': {'x': 0, 'y': 0, 'width': W, 'height': H},
            'anchors': local_anchors, 'compatibleCharacters': ['motif-bot'],
            'supportedActions': actions, 'sourceType': 'vector',
            'source': {'file': str(path.relative_to(ROOT)), 'generator': 'scripts/build_motif_bot.py'},
            'version': 1, 'status': 'canonical',
            'preview': preview, 'previewOnly': False,
            'license': 'project-original',
        }
        write(path.with_suffix('.json'), json.dumps(sidecar, indent=2) + '\n')
    print(f'Wrote mascot SVG package to {OUT}')


if __name__ == '__main__':
    main()
