"""Motif Atelier: an explicitly selected original-animation mode, separate from Motif Classic.

    python scripts/motif_atelier.py run --idea "A silent comedy about ..." --slug runaway-shadow
    python scripts/motif_atelier.py run --brief atelier/examples/science-short.json
    python scripts/motif_atelier.py resume --project atelier/runs/runaway-shadow
    python scripts/motif_atelier.py status --project atelier/runs/runaway-shadow

Classic (`motif_reel.py` and the rest of scripts/) is untouched by this mode;
see atelier/README.md for the stages and atelier/AGENTS.md for the creative
contract. Exit codes: 0 REVIEW_REQUIRED or a human decision, 3 waiting for an
author or reviewer, 2 blocked by a gate or budget, 1 error.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from atelier.engine import studio  # noqa: E402
from atelier.engine.project import Project, read  # noqa: E402


def code(status):
    if status.startswith(('REVIEW_REQUIRED', 'HUMAN_')):return 0
    if status.startswith('AWAITING'):return 3
    return 2


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0]);sub = p.add_subparsers(dest='cmd', required=True)
    def opts(s):
        s.add_argument('--worker', choices=['handoff', 'codex'], default='handoff', help='who authors: write a handoff file, or run a bounded Codex worker')
        s.add_argument('--reviewer', choices=['auto', 'codex', 'handoff'], default='auto', help='auto: Codex when installed and signed in, else handoff')
        s.add_argument('--tts-python', type=Path, help='Python with kokoro-onnx for the approved voices (default .venv/bin/python)')
        s.add_argument('--workers', type=int, default=3, help='parallel render workers (seekable segments)')
    r = sub.add_parser('run', help='start a project from a plain-language idea or an Atelier brief');opts(r)
    src = r.add_mutually_exclusive_group(required=True);src.add_argument('--idea');src.add_argument('--brief', type=Path)
    r.add_argument('--slug');r.add_argument('--classification', choices=['factual', 'fictional', 'mixed', 'unspecified'], default='unspecified')
    r.add_argument('--audience');r.add_argument('--effect');r.add_argument('--duration', type=float);r.add_argument('--style')
    for name, help_ in (('resume', 'continue from the saved state'), ('status', 'stages, freshness, budgets, next step')):
        s = sub.add_parser(name, help=help_);s.add_argument('--project', type=Path, required=True)
        if name == 'resume':opts(s)
    d = sub.add_parser('render', help='DIAGNOSTIC_ONLY render of the current source, regardless of gates');d.add_argument('--project', type=Path, required=True)
    d.add_argument('--range', help='a:b frame range');d.add_argument('--size', choices=['preview', 'delivery'], default='preview');d.add_argument('--workers', type=int, default=3)
    d.add_argument('--stills', help='comma-separated frames to save as PNG instead of a video')
    lg = sub.add_parser('ledger', help='refresh source hashes in asset-ledger.json (bumps versions)');lg.add_argument('--project', type=Path, required=True)
    lg.add_argument('--add-unrecorded', action='store_true', help='record every unrecorded file with the explicit --origin/--author/--rights/--use')
    for k in ('origin', 'author', 'rights', 'use'):lg.add_argument(f'--{k}')
    cc = sub.add_parser('concept-change', help='record a new creative approach after failed repairs');cc.add_argument('--project', type=Path, required=True)
    cc.add_argument('--to', required=True);cc.add_argument('--reason', required=True)
    bl = sub.add_parser('blocker', help='record an unresolved blocker and stop');bl.add_argument('--project', type=Path, required=True);bl.add_argument('--note', required=True)
    ap = sub.add_parser('approve', help='a person records their decision on the current delivery');ap.add_argument('--project', type=Path, required=True)
    ap.add_argument('--by', required=True);ap.add_argument('--decision', choices=['approved', 'rejected'], required=True);ap.add_argument('--note', default='')
    a = p.parse_args(argv)
    if a.cmd == 'run':
        if a.idea:
            if not a.slug:p.error('--idea needs --slug')
            brief = studio.brief_from_idea(a.idea, a.slug, a.classification, a.audience, a.effect, a.duration, a.style)
        else:brief = read(a.brief)
        project = studio.start(brief, worker=a.worker, reviewer=a.reviewer, python=a.tts_python, workers=a.workers)
    else:
        project = Project.locate(a.project)
        if a.cmd == 'resume':studio.advance(project, worker=a.worker, reviewer=a.reviewer, python=a.tts_python, workers=a.workers)
        elif a.cmd == 'render':
            frames = tuple(int(x) for x in a.range.split(':')) if a.range else None
            stills = [int(x) for x in a.stills.split(',')] if a.stills else None
            print(json.dumps({'diagnostic': str(studio.diagnostic(project, frames, a.size, a.workers, stills)), 'status': 'DIAGNOSTIC_ONLY'}, indent=2));return 0
        elif a.cmd == 'ledger':
            add = None
            if a.add_unrecorded:
                add = {k: getattr(a, k) for k in ('origin', 'author', 'rights', 'use')}
                if not all(add.values()):p.error('--add-unrecorded needs --origin, --author, --rights and --use')
            print(json.dumps(studio.refresh_ledger(project, add), indent=2));return 0
        elif a.cmd == 'concept-change':studio.concept_change(project, a.to, a.reason)
        elif a.cmd == 'blocker':studio.blocker(project, a.note)
        elif a.cmd == 'approve':studio.approve(project, a.by, a.decision, a.note)
    summary = studio.status(project);print(json.dumps(summary, indent=2))
    return code(summary['status'])


if __name__ == '__main__':
    raise SystemExit(main())
