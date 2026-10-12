"""Closed-form springs for things that move inside a scene.

The 2026-10-12 motion study (raycfu's "motion design studio" guide, assessed in the project thread):
eased moves stop dead, so arrivals read floaty; a damped spring arrives fast, overshoots a little and
settles, and a value that gets a new target keeps its velocity instead of restarting. Cards, stacked
windows and the host's entrances use these. The camera does not: it always eases (lesson L027).

spring(t) is in seconds (stiffness k, damping d, mass 1). pop(u) is the same curve over a 0..1
progress, for code that times moves as a share of a shot, and is exactly 1 from u = 1 on.
track(t, keys) stacks one spring per change of target.
"""
import math


def spring(t, k=170.0, d=26.0):
    """Damped spring from 0 to 1 after t seconds."""
    if t <= 0:return 0.0
    w0 = math.sqrt(k);z = d / (2 * w0)
    if z < 1:
        wd = w0 * math.sqrt(1 - z * z)
        return 1 - math.exp(-z * w0 * t) * (math.cos(wd * t) + (z * w0 / wd) * math.sin(wd * t))
    return 1 - math.exp(-w0 * t) * (1 + w0 * t)


def pop(u, zeta=0.5):
    """Spring over a 0..1 progress: overshoots (about 16% at zeta .5, 5% at .7) and is settled by u = 1.
    Lower zeta bounces more; use about .7 on UI and type, .4 to .5 on objects and the host."""
    if u <= 0:return 0.0
    if u >= 1:return 1.0
    w0 = 4.6 / zeta                                   # the envelope falls to 1% by u = 1
    wd = w0 * math.sqrt(1 - zeta * zeta);decay = math.exp(-zeta * w0 * u)
    rest = decay * (math.cos(wd * u) + (zeta * w0 / wd) * math.sin(wd * u))
    return 1 - rest * (1 - u ** 8)                    # fold the last 1% in so u = 1 lands exactly


def track(t, keys, k=170.0, d=26.0):
    """Value at t seconds for keys [(time, value), ...]: one spring per change, stacked, so a value that
    is retargeted mid-move carries its velocity into the next move."""
    v = keys[0][1]
    for i in range(1, len(keys)):
        v += (keys[i][1] - keys[i - 1][1]) * spring(t - keys[i][0], k, d)
    return v
