"""Motif rig library: reusable, parameterised metaphor props (see base.py)."""
from motif_rigs.base import Rig, Action, place, raster
from motif_rigs.palettes import PALETTES, palette, rotation

_REGISTRY = {}


def register(rig):
    if rig.name in _REGISTRY:raise ValueError('duplicate rig ' + rig.name)
    _REGISTRY[rig.name] = rig;return rig


def get(name):
    _load();return _REGISTRY[name]


def all_rigs():
    _load();return dict(_REGISTRY)


def _load():
    if _REGISTRY:return
    from motif_rigs import library  # noqa: F401  registers the built-in rigs
