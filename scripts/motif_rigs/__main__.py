"""python -m motif_rigs docs|proofs OUT|manifest  (run from scripts/)."""
import json
import sys
from pathlib import Path

import motif_rigs
from motif_rigs.base import ROOT
from motif_rigs.palettes import rotation


def docs():
    folder = ROOT / 'docs/rigs';folder.mkdir(parents=True, exist_ok=True)
    for name, rig in motif_rigs.all_rigs().items():
        m = rig.manifest();lines = [f'# Rig: {name}', '', m['description'], '',
                                    '**Origin:** original Motif design, authored SVG in `scripts/motif_rigs/library.py`. Style inputs: `docs/STYLE_BIBLE.md` and `docs/style-reference-analysis.md` only; no reference frame traced or copied.', '',
                                    f'**Tags:** {", ".join(m["tags"])}', '', f'**States:** {" → ".join(m["states"])}', '', '## Actions', '']
        for a, v in m['actions'].items():
            lines.append(f'- `{a}`: {v["from"]} → {v["to"]}, {v["frames"]} frames; contact `{v["contact"]}` closes at frame {v["contact_frame"]} (distance 0, tested).')
        lines += ['', '## Parameters', '', '```json', json.dumps(m['defaults'], indent=2), '```', '',
                  f'**Bot slot:** x {m["bot_slot"]["x"]}, y {m["bot_slot"]["y"]}, scale {m["bot_slot"]["scale"]}: {m["bot_slot"]["role"]}.', '',
                  f'**Palettes:** renders in all {len(m["palettes"])} Motif palettes ({", ".join(m["palettes"])}); films rotate them per scene.', '',
                  '**Status:** draft proof; awaiting Mayowa approval (plan task 2.2).', '']
        (folder / f'{name}.md').write_text('\n'.join(lines))
    print(f'wrote {len(motif_rigs.all_rigs())} rig notes to docs/rigs/')


def proofs(out):
    from motif_frame_snapshot import sheet
    rigs = motif_rigs.all_rigs();rows = []
    for (name, rig), palette in zip(rigs.items(), rotation(len(rigs))):
        for action in rig.actions:
            rec = rig.proof(Path(out) / 'stills', action=action, palette=palette)
            rows.append((f'{name} / {action} / {palette}', [rec['stills'][k] for k in ('before', 'contact', 'after')]))
    for i in range(0, len(rows), 5):sheet(rows[i:i + 5], Path(out) / f'rig-proofs-{i // 5 + 1}.png', width=240)
    print(f'{len(rows)} proofs -> {out}')


if __name__ == '__main__':
    {'docs': lambda: docs(), 'proofs': lambda: proofs(sys.argv[2]),
     'manifest': lambda: print(json.dumps({n: r.manifest() for n, r in motif_rigs.all_rigs().items()}, indent=1))}[sys.argv[1]]()
