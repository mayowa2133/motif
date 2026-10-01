"""Typed focus registry and geometry-derived, bounded SVG camera transforms.

Coordinates are authored scene geometry, not model coordinates. Asset envelopes
come from the stored SVG viewBoxes; critical bounds include visible identity,
diagnostic marks and contact/swept motion. The compiler uses these same placements.
"""
import re
from pathlib import Path
from motif_workshop import WORKSHOP_BOUNDS

ROOT = Path(__file__).resolve().parents[1]
SAFE = (90, 260, 900, 1290)  # headline ends at 197; caption starts at 1660
SHEET_PLACEMENTS = {
    'arena-pair': {'A': ('pair-A', 110, 570, .48), 'B': ('pair-B', 605, 570, .48)},
    'arena-a': {'A': ('close-A', 160, 390, 1)},
    'arena-b': {'B': ('close-B', 160, 390, 1)},
    'arena-review': {'A': ('review-A', 160, 600, .40), 'B': ('review-B', 510, 600, .40)},
}
CALENDAR_PLACEMENTS = {
    'calendar.board': ('calendar-board', 120, 315, 1, 'calendar-board'),
    'calendar.proposal': ('proposed', 590, 975, .85, 'proposal'),
    'calendar.booking': ('committed', 590, 975, .85, 'appointment'),
    'calendar.decision': ('decision', 613, 1238, 1, 'decision-tab'),
}
FOCUS_SHOTS = {
    **{k: {'workshop-wide'} for k in WORKSHOP_BOUNDS},
    **{k: {'calendar-wide', 'calendar-detail'} for k in CALENDAR_PLACEMENTS},
    'arena.answers': {'arena-pair'},
    'answer-A.sheet': {'arena-pair', 'arena-a', 'arena-review'},
    'answer-B.sheet': {'arena-pair', 'arena-b', 'arena-review'},
    'answer-A.connection': {'arena-a'},
    'answer-B.connection': {'arena-b'},
    'arena.handoff': {'arena-review'},
}


def union(*boxes):
    x = min(b[0] for b in boxes); y = min(b[1] for b in boxes)
    return (x, y, max(b[0]+b[2] for b in boxes)-x, max(b[1]+b[3] for b in boxes)-y)


def placed(box, x, y, scale):
    return (x+box[0]*scale, y+box[1]*scale, box[2]*scale, box[3]*scale)


def asset_box(asset, assets):
    svg = (ROOT/assets[asset]).read_text()
    values = re.search(r'viewBox="([^"]+)"', svg)
    if not values: raise ValueError('missing geometry for '+asset)
    box = tuple(map(float, values[1].split()))
    if len(box) != 4 or min(box[2:]) <= 0: raise ValueError('invalid geometry for '+asset)
    return box


def focus_bounds(target, shot, assets):
    if target not in FOCUS_SHOTS or shot not in FOCUS_SHOTS[target]:
        raise ValueError('unsupported focus/shot binding: '+target+' / '+shot)
    if target in WORKSHOP_BOUNDS: return WORKSHOP_BOUNDS[target]
    if target.startswith('calendar.'):
        _, x, y, s, asset = CALENDAR_PLACEMENTS[target]
        box = placed(asset_box(asset, assets), x, y, s)
        critical = box
        if target == 'calendar.proposal':
            critical = union(box, placed(asset_box(asset, assets), x, y-110, s))
        elif target == 'calendar.decision':
            # Contact and resulting proposal removal remain visible. The entry
            # hand is intentionally allowed to travel in from outside the crop.
            critical = union(box, (690, 1160, 320, 265), (590, 975, 331.5, 149.6))
        return box, critical
    placements = SHEET_PLACEMENTS[shot]
    sheets = [placed(asset_box('answer-sheet', assets), x, y, s) for _, x, y, s in placements.values()]
    if target == 'arena.answers': return union(*sheets), union(*sheets)
    if target == 'arena.handoff':
        # Include both sheets at source and destination, rotation margin, and
        # the receiving hand throughout its authored final shift.
        destinations = [placed((-55,-55,870,960), x+dx*s, y+225*s, s)
                        for (_,x,y,s),dx in zip(placements.values(),(370,80))]
        box = union(*sheets, *destinations, (653,850,315,207))
        return box, box
    candidate = target.split('.')[0][-1]
    _, x, y, s = placements[candidate]
    if target.endswith('.sheet'):
        box = placed(asset_box('answer-sheet', assets), x, y, s)
        return box, box
    # Actual connection ends, route, gap, cross/check and candidate letter.
    # Entire paper sheet is not the diagnostic target.
    box = placed((105, 490, 550, 124), x, y, s)
    critical = union(box, placed((80, 25, 125, 115), x, y, s),
                     placed((95, 460, 580, 175), x, y, s))
    return box, critical


def project_box(box, transform):
    return placed(box, transform['x'], transform['y'], transform['scale'])


def contains(outer, inner, tolerance=.05):
    return (inner[0] >= outer[0]-tolerance and inner[1] >= outer[1]-tolerance
            and inner[0]+inner[2] <= outer[0]+outer[2]+tolerance
            and inner[1]+inner[3] <= outer[1]+outer[3]+tolerance)


def camera_for(beat, assets, selected=None):
    target, shot, framing = beat['focus_target'], beat['shot'], beat['framing']
    box, critical = focus_bounds(target, shot, assets)
    if selected:
        if selected not in SHEET_PLACEMENTS.get(shot, {}):
            raise ValueError('selected indicator hidden by shot')
        _,x,y,s = SHEET_PLACEMENTS[shot][selected]
        seal = placed((55, 650, 650, 145), x, y, s)
        critical = union(critical, seal)
    if framing not in ('establish','subject','detail'): raise ValueError('unsupported framing')
    sx, sy, sw, sh = SAFE
    if framing == 'establish':
        box = (40, 640, 970, 900) if target.startswith('workshop.') else (0, 240, 1080, 1350)
        scale = min(sw/box[2], sh/box[3])
    else:
        padding = 1.08 if target=='workshop.jobs' and framing=='subject' else 1.48 if framing == 'subject' else 1.10
        scale = min(sw/(box[2]*padding), sh/(box[3]*padding), 3.0)
    # Geometry fit also constrains the action/identity envelope. This safety
    # clamp can limit zoom; it never silently discards required visual evidence.
    scale = min(scale, sw/(critical[2]+36), sh/(critical[3]+36))
    x = sx+sw/2-(box[0]+box[2]/2)*scale
    anchor = .60 if target.endswith('.connection') else .5
    y = sy+sh*anchor-(box[1]+box[3]/2)*scale
    x = max(sx-critical[0]*scale, min(x, sx+sw-(critical[0]+critical[2])*scale))
    y = max(sy-critical[1]*scale, min(y, sy+sh-(critical[1]+critical[3])*scale))
    transform = {'x':round(x,4), 'y':round(y,4), 'scale':round(scale,6)}
    if not contains(SAFE, project_box(critical, transform)):
        raise ValueError('critical focus bounds exceed safe area')
    if selected and 76*SHEET_PLACEMENTS[shot][selected][3]*scale < 34:
        raise ValueError('selected indicator is too small for mobile; focus the selected sheet')
    return {'focus_target':target, 'framing':framing, 'shot':shot,
            'target_bounds':box, 'critical_bounds':critical, 'safe_area':SAFE,
            'camera':transform, 'projected_target_bounds':project_box(box,transform),
            'projected_critical_bounds':project_box(critical,transform),
            'selected_candidate':selected}
