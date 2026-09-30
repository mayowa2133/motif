#!/usr/bin/env python3
"""Compose one Motif Bot SVG with pose, face and simple arm/hand overrides.

Example:
  python3 scripts/compose_motif_bot.py --pose pointing --expression happy \
    --right-hand grip --right-end 800,520 --output /tmp/motif-custom.svg
"""

from __future__ import annotations

import argparse
from pathlib import Path

from build_motif_bot import EXPRESSIONS, HAND_D, POSES, assemble_pose, wrap


def point(value: str) -> tuple[float, float]:
    try:
        x, y = (float(v) for v in value.split(',', 1))
    except (ValueError, TypeError) as exc:
        raise argparse.ArgumentTypeError('Expected X,Y coordinates in the 1024 master canvas') from exc
    if not (0 <= x <= 1024 and 0 <= y <= 1024):
        raise argparse.ArgumentTypeError('Coordinates must be within 0..1024')
    return x, y


def foot(value: str) -> tuple[float, float, float]:
    try:
        x, y, angle = (float(v) for v in value.split(',', 2))
    except (ValueError, TypeError) as exc:
        raise argparse.ArgumentTypeError('Expected X,Y,ANGLE') from exc
    if not (0 <= x <= 1024 and 0 <= y <= 1024 and -180 <= angle <= 180):
        raise argparse.ArgumentTypeError('Foot values are outside the master canvas or rotation range')
    return x, y, angle


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pose', choices=POSES, default='standing')
    parser.add_argument('--expression', choices=EXPRESSIONS)
    parser.add_argument('--left-hand', choices=HAND_D)
    parser.add_argument('--right-hand', choices=HAND_D)
    parser.add_argument('--left-end', type=point, metavar='X,Y')
    parser.add_argument('--right-end', type=point, metavar='X,Y')
    parser.add_argument('--left-foot', type=foot, metavar='X,Y,ANGLE')
    parser.add_argument('--right-foot', type=foot, metavar='X,Y,ANGLE')
    parser.add_argument('--head-rotation', type=float)
    parser.add_argument('--body-rotation', type=float)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    base = POSES[args.pose]
    overrides = {}
    for side in ('left', 'right'):
        existing = base['l' if side == 'left' else 'r']
        endpoint = getattr(args, f'{side}_end')
        hand = getattr(args, f'{side}_hand')
        if endpoint or hand:
            overrides['l' if side == 'left' else 'r'] = (
                endpoint[0] if endpoint else existing[0],
                endpoint[1] if endpoint else existing[1],
                hand or existing[2],
            )
    if args.left_foot or args.right_foot:
        current = base.get('feet', ((425, 861, 0), (599, 861, 0)))
        overrides['feet'] = (args.left_foot or current[0], args.right_foot or current[1])
    if args.head_rotation is not None:
        overrides['head_tilt'] = args.head_rotation
    if args.body_rotation is not None:
        overrides['tilt'] = args.body_rotation
    body, _ = assemble_pose(args.pose, args.expression, overrides)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(wrap(body, f'Motif Bot custom {args.pose} pose'))
    print(args.output)


if __name__ == '__main__':
    main()
