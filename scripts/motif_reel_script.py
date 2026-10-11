"""Reel script step: the 20 to 32 s paper-reel format (and a 30 to 62 s long format).

  hook      one line (3 alternates; Mayowa picks, the brief records the pick)
  beats     4 to 6 claim beats, each citing one fact from the fact packet
  cta       "comment KEYWORD"

validate() rejects a beat without a cited fact, a fact without a source URL,
and a runtime over 32 s (or under 20 s) at the measured speaking rate.
"""
import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / 'schemas/reel-brief.schema.json').read_text())
# Measured 2026-10-09: Kokoro af_nova via hyperframes tts. Speed .85 gave 2.68
# words/s; the reel pace (speed 1.2, motif_reel.SPEED) gives about 3.7 words/s.
WORDS_PER_SECOND = 3.7
GAP = .12                       # pause between clause takes
RUNTIME = (20.0, 32.0)
# The long format (adaptations, how-tos) keeps the same grammar over more beats.
FORMATS = {'short': {'runtime': RUNTIME, 'beats': (4, 6)}, 'long': {'runtime': (30.0, 62.0), 'beats': (4, 10)}}


def limits(brief):
    return FORMATS[brief.get('format', 'short')]


def count(text):
    return len(re.findall(r"[\w$%'.,-]+", text))


def hooks(brief):
    """Three alternate hook lines built from the fact packet (deterministic)."""
    facts = {f['id']: f for f in brief['facts']};first = facts[brief['beats'][0]['fact']]
    value = first.get('value') or ''
    lead = first['claim'].rstrip('.')
    out = [f'{value}. {lead}.' if value and value.lower() not in lead.lower() else f'{lead}.',
           f'Nobody is talking about this: {lead[0].lower() + lead[1:]}.',
           f'Here is why {brief["topic"]} just changed.']
    seen = [];[seen.append(h) for h in out if h not in seen]
    return seen


def hook_line(brief):
    h = brief.get('hook') or {};alternates = h.get('alternates') or hooks(brief)
    return alternates[h.get('selected') or 0], alternates


def lines(brief):
    """Narration lines in order: hook, beats, CTA."""
    hook, _ = hook_line(brief)
    return [('hook', hook)] + [(b['id'], b['narration']) for b in brief['beats']] + [('cta', brief['cta']['narration'])]


def estimate(brief):
    parts = lines(brief)
    return sum(count(t) for _, t in parts) / WORDS_PER_SECOND + GAP * (len(parts) - 1) + .7


def validate(brief, measured=None):
    errors = [f'{"/".join(map(str, e.path))}: {e.message}' for e in Draft202012Validator(SCHEMA).iter_errors(brief)]
    if errors:return errors
    facts = {f['id']: f for f in brief['facts']}
    for b in brief['beats']:
        if b['fact'] not in facts:errors.append(f'{b["id"]}: cites unknown fact {b["fact"]}')
    if len({b['id'] for b in brief['beats']}) != len(brief['beats']):errors.append('duplicate beat ids')
    if errors:return errors
    if brief['cta']['keyword'].lower() not in brief['cta']['narration'].lower():errors.append('cta narration must say the keyword')
    lim = limits(brief);lo, hi = lim['beats']
    if not lo <= len(brief['beats']) <= hi:errors.append(f'{len(brief["beats"])} beats outside {lo}-{hi} for the {brief.get("format", "short")} format')
    runtime = measured if measured is not None else estimate(brief);rt = lim['runtime']
    if not rt[0] <= runtime <= rt[1]:errors.append(f'runtime {runtime:.1f} s outside {rt[0]:.0f}-{rt[1]:.0f} s at {WORDS_PER_SECOND:.2f} words/s')
    return errors


def script_record(brief):
    hook, alternates = hook_line(brief)
    return {'hook': hook, 'hook_alternates': alternates, 'hook_selected_by': 'brief' if (brief.get('hook') or {}).get('selected') is not None else 'default (first alternate; awaiting Mayowa)',
            'lines': [{'id': i, 'text': t} for i, t in lines(brief)], 'estimated_runtime': round(estimate(brief), 2), 'words_per_second': round(WORDS_PER_SECOND, 3)}
