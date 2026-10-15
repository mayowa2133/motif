#!/usr/bin/env python3
"""Narration voice: lint a brief's spoken lines for the tells that make a script read as AI.

    python scripts/motif_narration.py BRIEF

Adapted on 2026-10-15 from the "/human" writing skill (millee.md), which is
built on StoryScope (Russell et al., arXiv 2604.03136): over 61,000 human and AI
stories told apart at 93% from structure alone. AI stories state their moral
(77% of AI narrators against 52% of human ones), keep one tidy track and
escalate flatly. The stated moral and the surface tells are measurable, so
they are gated here; specificity is a warning. Subplots and unresolved endings
are fiction advice and do not fit a 30 s explainer, so Motif does not take them.
docs/STORY_PASS.md ("Voice") says how to write lines that pass.
"""
import json
import re
import sys
from pathlib import Path

# A line that tells the viewer what the film meant instead of letting the last change show it.
MORAL = [r"\bthat'?s (why|how|when|the (real|whole|true))\b", r"\bthe (real|true|whole) (point|lesson|secret|power|magic|beauty|trick)\b",
         r"\bat the end of the day\b", r"\bbottom line\b", r"\bin (short|a nutshell|summary)\b", r"\b(the )?takeaway\b",
         r"\b(you|we) (finally )?reali[sz]e\b", r"\bit'?s (that|as) (simple|easy)\b", r"\bsimple as that\b", r"\bchanges everything\b", r"\bwork smarter\b"]
# "It's not X, it's Y": the most common AI sentence shape.
CONTRAST = [r"\b(it|this|that)(?:'s| is) not (?:just )?[^.,;:]{1,40}[,;:] (?:it'?s|but)\b", r"\bisn'?t just\b", r"\bnot just [^.]{1,40}\bbut\b",
            r"\bmore than just\b", r"\bnot because [^.]{1,40}, but\b"]
STOCK = ['delve', 'seamless', 'seamlessly', 'game-changer', 'game changer', 'supercharge', 'revolutionize', 'revolutionise', 'effortless',
         'effortlessly', 'elevate', 'harness', 'leverage', 'robust', 'landscape', 'empower', 'streamline', 'cutting-edge', 'next-level',
         'level up', 'unleash', 'transformative', 'ever-evolving', "in today's", 'deep dive', 'dive in', 'tapestry', 'testament', 'unlock the power',
         'magic', 'magical', 'superpower']
DASH = re.compile(r"[—–]|\s-\s")
FILLER = ['actually', 'basically', 'literally', 'truly', 'incredibly', 'really', 'simply']
NUMBER_WORDS = set('zero one two three four five six seven eight nine ten eleven twelve twenty thirty forty fifty sixty seventy eighty ninety hundred thousand million billion trillion half double twice percent first second third'.split())


def lines(brief):
    """(where, narration) for every spoken line: hook, each beat, CTA."""
    hook = brief.get('hook') or {};alts = hook.get('alternates') or []
    out = [('hook', alts[hook.get('selected') or 0])] if alts else []
    out += [(b['id'], b.get('narration', '')) for b in brief.get('beats', [])]
    return out + [('cta', (brief.get('cta') or {}).get('narration', ''))]


def names(brief):
    """Lower-case names the film is about (title words, brand, carried object, CTA keyword): 'uv' and 'git' count as specific."""
    seen = {w.lower() for w in re.findall(r"[A-Za-z][\w.+-]*", brief.get('title', '')) if len(w) > 1 and w.lower() not in ('the', 'and', 'makes', 'your', 'that', 'with', 'for')}
    for value in [(brief.get('brand') or {}).get('slug'), (brief.get('carry') or {}).get('label'), (brief.get('cta') or {}).get('keyword')]:
        if value:seen |= {w.lower() for w in re.findall(r"[\w.+-]+", value)}
    return seen


def specific(text, known):
    """True when the line carries a number, a name or a command the viewer can hold on to."""
    if re.search(r"\d", text):return True
    for sentence in re.split(r'(?<=[.!?:])\s+', text):
        tokens = re.findall(r"[A-Za-z][\w.'+-]*", sentence)
        if any(t[0].isupper() and t not in ('I', "I'll", "I'm") for t in tokens[1:]):return True
    lowered = re.findall(r"[a-z][\w.'+-]*", text.lower())
    return any(t in NUMBER_WORDS or t in known or re.search(r"[._/]\w", t) for t in lowered)


def lint(brief):
    """{'failures': [...], 'warnings': [...]}, each 'where: detail'."""
    failures, warnings = [], [];known = names(brief)
    for where, text in lines(brief):
        low = text.lower()
        for pattern in MORAL:
            if (m := re.search(pattern, low)):failures.append(f'{where}: states the moral ("{m.group(0)}"); let the last change on screen land it')
        for pattern in CONTRAST:
            if (m := re.search(pattern, low)):failures.append(f'{where}: "not X, it\'s Y" shape ("{m.group(0)}"); say what it is')
        for word in STOCK:
            if re.search(r'\b' + re.escape(word) + r'\b', low):failures.append(f'{where}: stock AI word "{word}"')
        if DASH.search(text):failures.append(f'{where}: dash in narration; use a full stop or a comma')
        for word in FILLER:
            if re.search(r'\b' + word + r'\b', low):warnings.append(f'{where}: filler "{word}"')
        if where not in ('hook', 'cta') and not specific(text, known):warnings.append(f'{where}: no number, name or command in the line')
    return {'status': 'FAIL' if failures else 'PASS', 'failures': failures, 'warnings': warnings}


if __name__ == '__main__':
    report = lint(json.loads(Path(sys.argv[1]).read_text()))
    print(json.dumps(report, indent=2));raise SystemExit(0 if report['status'] == 'PASS' else 1)
