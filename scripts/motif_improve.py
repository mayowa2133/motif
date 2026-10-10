"""The improvement loop: every reel Motif makes leaves the next one better.

    python scripts/motif_improve.py retro PROJECT [--feedback "what the reviewer said"] [--reviewer NAME]
    python scripts/motif_improve.py lesson --source S --symptom S --rule S [--check ID] [--level gate|warn|brief]
    python scripts/motif_improve.py backlog
    python scripts/motif_improve.py regress [--briefs DIR ...]

retro    after a run: gathers the run's stage results, lesson findings, library
         requests and plan warnings into PROJECT/retro.md and appends one line to
         quality/run-log.jsonl, with any reviewer feedback verbatim
lesson   turns feedback into a ledger lesson (quality/lessons.json); when the rule
         can be measured, add a check to motif_lessons.CHECKS and name it here so
         every later film is held to it
backlog  ranks what the library is missing across all logged runs (machines,
         rooms, inserts, costumes that briefs asked for, and lessons that keep
         warning) into quality/library-backlog.json: the next art to build
regress  re-checks every brief in the repo (script, plan, sound-off and the
         plan-level lessons) so a new rule is proven on old films too

The loop: brief -> run -> retro (+ feedback) -> lesson/check or library work ->
regress -> next brief. See docs/IMPROVEMENT_LOOP.md.
"""
import argparse
import collections
import datetime
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
RUN_LOG = ROOT / 'quality/run-log.jsonl'
BACKLOG = ROOT / 'quality/library-backlog.json'
BRIEF_DIRS = (ROOT / 'quality/benchmark-briefs', ROOT / 'quality/adaptation-briefs')


def _read(p, default=None):
    p = Path(p);return json.loads(p.read_text()) if p.exists() else default


def retro(project, feedback=None, reviewer=None):
    project = Path(project);record = _read(project / 'reel-record.json', {'stages': []})
    brief = _read(project / 'brief.json', {});lessons = _read(project / 'lessons.json')
    if lessons is None:
        from motif_lessons import run
        lessons = run(project)
    requests = _read(project / 'library-requests.json', [])
    stages = {s['stage']: s['status'] for s in record['stages']}
    plan_stage = next((s for s in record['stages'] if s['stage'] == 'plan'), {})
    findings = [{'lesson': r['lesson'], 'status': r['status'], **f} for r in lessons['lessons'] for f in r['findings']]
    render = next((s for s in record['stages'] if s['stage'] == 'render'), {})
    entry = {'date': datetime.date.today().isoformat(), 'slug': brief.get('slug', project.name), 'brief': record.get('brief'),
             'mascot': brief.get('mascot', 'bot'), 'look': plan_stage.get('look'), 'stages': stages, 'findings': findings,
             'library_requests': requests, 'warnings': plan_stage.get('warnings', []), 'render': render.get('file'),
             'feedback': [{'by': reviewer or 'reviewer', 'text': feedback}] if feedback else []}
    RUN_LOG.parent.mkdir(parents=True, exist_ok=True)
    with RUN_LOG.open('a') as f:f.write(json.dumps(entry) + '\n')
    lines = [f'# Retro: {entry["slug"]} ({entry["date"]})', '', '## Stages', '']
    lines += [f'- {k}: {v}' for k, v in stages.items()]
    lines += ['', '## What the lessons caught', '']
    lines += [f'- {x["lesson"]} {x["status"]} at {x["where"]}: {x["detail"]}' for x in findings] or ['- nothing']
    lines += ['', '## Library requests', ''] + ([f'- {r["kind"]} {r["id"]} (needed by {r["needed_by"]})' for r in requests] or ['- none'])
    lines += ['', '## Reviewer feedback', ''] + ([f'- {x["by"]}: {x["text"]}' for x in entry['feedback']] or ['- none yet; add with: motif_improve.py retro PROJECT --feedback "..."'])
    lines += ['', '## Next', '', '- Turn each new symptom into a lesson (motif_improve.py lesson), with a check when it can be measured.',
              '- Build the top items of quality/library-backlog.json (motif_improve.py backlog).', '- Run motif_improve.py regress before the next film.', '']
    (project / 'retro.md').write_text('\n'.join(lines))
    return entry


def add_lesson(source, symptom, rule, check=None, level=None, enforced_by=None):
    from motif_lessons import CHECKS, LEDGER
    if check and check not in CHECKS:raise SystemExit(f'unknown check {check}; add it to motif_lessons.CHECKS first ({sorted(CHECKS)})')
    data = json.loads(LEDGER.read_text());n = max(int(l['id'][1:]) for l in data['lessons']) + 1
    lesson = {'id': f'L{n:03d}', 'date': datetime.date.today().isoformat(), 'source': source, 'symptom': symptom, 'rule': rule}
    if check:lesson['check'] = check
    if enforced_by:lesson['enforced_by'] = enforced_by
    lesson['level'] = level or ('gate' if check else 'brief')
    data['lessons'].append(lesson);LEDGER.write_text(json.dumps(data, indent=2) + '\n')
    return lesson


def backlog():
    runs = [json.loads(l) for l in RUN_LOG.read_text().splitlines() if l.strip()] if RUN_LOG.exists() else []
    wanted = collections.Counter();warns = collections.Counter();examples = {}
    for r in runs:
        for q in r.get('library_requests', []):
            key = f'{q["kind"]}/{q["id"]}';wanted[key] += 1;examples.setdefault(key, f'{r["slug"]}:{q["needed_by"]}')
        for f in r.get('findings', []):warns[f['lesson']] += 1
    from motif_lessons import ledger
    rules = {l['id']: l['rule'] for l in ledger()['lessons']}
    out = {'runs': len(runs), 'missing_library': [{'entry': k, 'requests': v, 'first_seen': examples[k]} for k, v in wanted.most_common()],
           'recurring_findings': [{'lesson': k, 'runs': v, 'rule': rules.get(k)} for k, v in warns.most_common()]}
    BACKLOG.write_text(json.dumps(out, indent=2) + '\n')
    return out


def regress(dirs=BRIEF_DIRS):
    from motif_reel import check_brief
    rows = []
    for d in dirs:
        for path in sorted(Path(d).glob('*.json')):
            report = check_brief(json.loads(path.read_text()), allow_draft=True)
            problems = report.get('script', []) + report.get('plan', []) + report.get('sound_off', []) + report.get('lessons', [])
            rows.append({'brief': str(path.relative_to(ROOT)), 'status': report['status'], 'problems': problems})
    return {'status': 'FAIL' if any(r['status'] != 'PASS' for r in rows) else 'PASS', 'briefs': rows}


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0]);sub = p.add_subparsers(dest='cmd', required=True)
    r = sub.add_parser('retro');r.add_argument('project', type=Path);r.add_argument('--feedback');r.add_argument('--reviewer')
    l = sub.add_parser('lesson');l.add_argument('--source', required=True);l.add_argument('--symptom', required=True);l.add_argument('--rule', required=True)
    l.add_argument('--check');l.add_argument('--level', choices=('gate', 'warn', 'brief'));l.add_argument('--enforced-by')
    sub.add_parser('backlog')
    g = sub.add_parser('regress');g.add_argument('--briefs', type=Path, nargs='*')
    a = p.parse_args()
    if a.cmd == 'retro':out = retro(a.project, a.feedback, a.reviewer)
    elif a.cmd == 'lesson':out = add_lesson(a.source, a.symptom, a.rule, a.check, a.level, a.enforced_by)
    elif a.cmd == 'backlog':out = backlog()
    else:
        out = regress(a.briefs or BRIEF_DIRS);print(json.dumps(out, indent=2));raise SystemExit(0 if out['status'] == 'PASS' else 1)
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
