"""Metaphor fit: pick the machine by what the claim means, not by what is free.

The 2026-10-09 review of the PR #14 benchmarks found the biggest gap to the
reference reels was meaning: an overflowing bus under "INSIDE EVERY PHONE", a
thermometer under "ASK PYTHON ITSELF". The labels carried the explanation and
the machine was decoration. A reference reel's prop *is* the claim (109 riders
on a 96-seat bus is the memory overflow), so it reads with the sound off.

Every claim beat therefore names one relation, the shape of what it says:

  over-capacity    more than fits (demand > limit)
  pile-up          something accumulates over time (backlog, bills, volunteers' edits)
  cost-crush       a cost or barrier is squeezed to nothing
  race             one option is faster or ahead of others
  trade-off        two things weighed against each other
  big-number       a count grows large (users, stars, databases)
  level            a measured quantity rises to a mark (heat, hype, rating, limit)
  approve          something is allowed, certified, permitted, or refused
  transform        inputs go in, one result comes out (a pipeline, one app, one file)
  spread           one action sets off many (adoption, chain reaction, renewals)
  attract          many things are drawn to one (apps building on a platform)
  launch           a new version or feature goes live
  unlock           a lock comes off: free, open, access, turning a restriction off
  grow             something small is nurtured into something big (community)
  connect          a gap is bridged between two parties
  everywhere       the same thing is inside many devices or places

Each rig declares the relations it can show (RIG_RELATIONS). The planner may
only place a rig whose relations include the beat's; a mismatch is a plan
error, not a warning. sound_off() then checks each claim beat the way a
viewer with the sound off would: the machine shows the right relation, its
labels carry the beat's own nouns (not library defaults), and the product's
mark is somewhere in the frame.
"""
import re

RELATIONS = ('over-capacity', 'pile-up', 'cost-crush', 'race', 'trade-off', 'big-number', 'level', 'approve',
             'transform', 'spread', 'attract', 'launch', 'unlock', 'grow', 'connect', 'everywhere')

RIG_RELATIONS = {
    'overflow-vehicle': ('over-capacity',),
    'plate-stack': ('pile-up',),
    'receipt-stack': ('pile-up', 'cost-crush'),
    'hydraulic-press': ('cost-crush',),
    'race-track': ('race',),
    'balance-scale': ('trade-off',),
    'stacked-meter': ('big-number',),
    'thermometer': ('level',),
    'stamp-gate': ('approve',),
    'conveyor': ('transform',),
    'domino-run': ('spread',),
    'magnet-pull': ('attract',),
    'launch-pad': ('launch',),
    'lock-and-key': ('unlock',),
    'sprout-grow': ('grow',),
    'bridge-span': ('connect',),
    'device-wall': ('everywhere',),
}

# Words that suggest a relation when a brief does not name one. Deliberately
# conservative: an unclassified beat must declare its relation.
CUES = {
    'over-capacity': ('more than', 'too many', 'overflow', 'over capacity', 'not enough room', 'exceeds'),
    'pile-up': ('piles', 'pile', 'backlog', 'adds up', 'street by street', 'one by one'),
    'cost-crush': ('costs nothing', 'cost zero', 'cost nothing', 'used to cost', 'no fee', 'for free', '$0'),
    'race': ('faster', 'slower than', 'beats', 'ahead of', 'outruns'),
    'trade-off': ('the catch', 'but it', 'trade-off', 'tradeoff', 'versus', 'slower'),
    'big-number': ('million', 'billion', 'trillion', 'thousand', 'over a', 'more than'),
    'level': ('lasts', 'days', 'expires', 'limit', 'percent', 'temperature', 'rating'),
    'approve': ('allowed', 'permission', 'credit', 'certified', 'approve', 'license', 'checkbox'),
    'transform': ('one app', 'one file', 'all in one', 'turns into', 'into one'),
    'spread': ('renews', 'automatically', 'chain', 'spreads', 'everyone'),
    'attract': ('build on it', 'so many apps', 'flock', 'draws'),
    'launch': ('since', 'new build', 'released', 'launched', 'ships'),
    'unlock': ('turned off', 'unlock', 'open source', 'free and open', 'forever'),
    'grow': ('volunteers', 'community', 'donations', 'grows', 'growing'),
    'connect': ('share it back', 'connect', 'bridge', 'together'),
    'everywhere': ('every phone', 'every iphone', 'every android', 'every browser', 'inside every', 'on every', 'everywhere'),
}

GENERIC = {'ITEM', 'ITEMS', 'LABEL', 'THING', 'STUFF', 'DATA', 'APP', 'APPS', 'YOU', 'IT', 'DONE', 'MAX', 'NEW'}
STOP = {'the', 'a', 'an', 'and', 'or', 'of', 'to', 'in', 'on', 'for', 'it', 'is', 'its', 'you', 'your', 'with', 'that', 'this', 'just', 'now', 'can', 'so', 'by', 'are', 'be', 'at', 'as', 'from', 'all', 'even', 'every', 'any', 'one', 'not'}


def classify(text):
    """Best relation for a sentence, or None when no cue matches."""
    low = ' ' + re.sub(r'\s+', ' ', text.lower()) + ' ';best = None
    for relation in RELATIONS:
        hits = sum(1 for cue in CUES[relation] if cue in low)
        if hits and (best is None or hits > best[0]):best = (hits, relation)
    return best[1] if best else None


def relation_of(beat, fact=None):
    """Declared relation, else the classifier over narration + claim."""
    declared = beat.get('relation') or (beat.get('visual') or {}).get('relation')
    if declared:return declared
    return classify(beat.get('narration', '') + ' ' + ((fact or {}).get('claim') or ''))


def rigs_for(relation):
    return [name for name, rels in RIG_RELATIONS.items() if relation in rels]


def fits(rig, relation):
    return relation in RIG_RELATIONS.get(rig, ())


def _stem(w):
    """Crude stem so STREETS matches street and CREDITED matches credit."""
    w = w.removesuffix("'s")
    for end, new in (('ies', 'y'), ('ed', ''), ('s', '')):
        if w.endswith(end) and len(w) - len(end) >= 3:return w[:-len(end)] + new
    return w


def _words(text):
    return {_stem(w) for w in re.findall(r"[a-z0-9']+", str(text).lower()) if w not in STOP and len(w) > 1}


def rig_text(params):
    """Every string a rig will print, from its params."""
    out = []
    for v in (params or {}).values():
        if isinstance(v, str):out.append(v)
        elif isinstance(v, list):out += [x for x in v if isinstance(x, str)]
    return out


def sound_off(plan, brief=None):
    """Per claim beat: does the frame say the claim without the narration?

    Checks (all must hold):
      relation   the beat declares (or the classifier finds) a relation, and its rig shows it
      specific   at least one rig label shares a word with the beat's narration or fact,
                 and no rig label is a placeholder word the claim never uses
      subject    the product mark is in the beat (brand on the plan) when the brief names one
    Returns {'status', 'beats': [...], 'failures': [...]}."""
    facts = {f['id']: f for f in (brief or {}).get('facts', [])};briefs = {b['id']: b for b in (brief or {}).get('beats', [])}
    rows, failures = [], []
    for beat in plan['beats']:
        if beat.get('kind') != 'claim':continue
        shot = beat['shots'][0];rig = (shot.get('rig') or {}).get('id');params = (shot.get('rig') or {}).get('params', {})
        relation = beat.get('relation') or relation_of(briefs.get(beat['id'], beat), facts.get(beat.get('fact')))
        text = beat['narration'] + ' ' + (facts.get(beat.get('fact'), {}).get('claim') or '') + ' ' + (facts.get(beat.get('fact'), {}).get('value') or '')
        labels = rig_text(params);shared = sorted(set().union(*[_words(l) for l in labels]) & _words(text)) if labels else []
        # A stock word is only a placeholder when the claim itself never says it.
        placeholder = [l for l in labels if l.strip().upper() in GENERIC and not _words(l) & _words(text)]
        row = {'beat': beat['id'], 'rig': rig, 'relation': relation, 'relation_ok': bool(relation and rig and fits(rig, relation)),
               'labels': labels, 'shared_words': shared, 'placeholder_labels': placeholder,
               'subject': bool(plan.get('brand')) or not (brief or {}).get('brand')}
        row['specific'] = bool(shared) and not placeholder
        if not relation:failures.append(f'{beat["id"]}: no relation declared and none recognised; add "relation" to the beat ({", ".join(RELATIONS)})')
        elif not row['relation_ok']:failures.append(f'{beat["id"]}: {rig} shows {RIG_RELATIONS.get(rig, ("nothing known",))}, but the claim is {relation}; use one of {rigs_for(relation)}')
        if not row['specific']:failures.append(f'{beat["id"]}: rig labels {labels} do not name anything from the claim' + (f' (placeholders {placeholder})' if placeholder else ''))
        if not row['subject']:failures.append(f'{beat["id"]}: the brief names a product but the plan carries no brand mark')
        rows.append(row)
    return {'status': 'FAIL' if failures else 'PASS', 'beats': rows, 'failures': failures}
