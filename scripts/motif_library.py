"""Motif's original library catalogue: what a planner may pick from.

Kinds: rig (motif_rigs), room (motif_sets.ROOMS), prop (motif_props),
costume (motif_bot_kit), insert (motif_inserts). Every entry carries tags for
retrieval and a review status from assets/library/approvals.json:

  DRAFT      authored, awaiting Mayowa (usable only with allow_draft)
  CANONICAL  approved; the planner's default pool
  REJECTED   never offered

Retrieval scores entries by tag overlap with the beat text, so a planner
prompt (or the deterministic planner) only sees entries that exist.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPROVALS = ROOT / 'assets/library/approvals.json'
STATUSES = ('DRAFT', 'CANONICAL', 'REJECTED')
INSERTS = {
    'counter': ('number', 'count', 'money', 'price', 'users', 'stars', 'growth', 'total'),
    'star_badge': ('rating', 'stars', 'reviews', 'quality', 'github'),
    'price_tag': ('price', 'cost', 'free', 'cheap', 'subscription', 'pricing', 'discount'),
    'gauge': ('speed', 'level', 'pressure', 'risk', 'hype', 'performance'),
    'progress_bar': ('progress', 'percent', 'loading', 'done', 'share', 'complete'),
    'comment_end_card': ('cta', 'comment', 'link', 'follow'),
}
STOP = {'the', 'a', 'an', 'and', 'or', 'of', 'to', 'in', 'on', 'for', 'it', 'is', 'its', 'it\'s', 'you', 'your', 'with', 'that', 'this', 'just', 'now', 'can'}


def words(text):
    out = set()
    for w in re.findall(r"[a-z0-9$%']+", text.lower()):
        if w in STOP:continue
        out.add(w)
        if w.endswith('s') and len(w) > 3:out.add(w[:-1])
    return out


def approvals():
    return json.loads(APPROVALS.read_text()) if APPROVALS.exists() else {'entries': {}}


def catalog(allow_draft=False):
    from motif_bot_kit import COSTUMES
    from motif_props import PROPS
    from motif_rigs import all_rigs
    from motif_sets import ROOMS
    status = approvals()['entries']
    entries = []
    for name, rig in sorted(all_rigs().items()):
        entries.append({'kind': 'rig', 'id': name, 'tags': list(rig.tags), 'description': rig.description, 'params': rig.defaults, 'actions': list(rig.actions)})
    for name, room in sorted(ROOMS.items()):
        tags = sorted({t for p in room['dressing'] for t in PROPS[p].tags} | {name})
        entries.append({'kind': 'room', 'id': name, 'tags': tags, 'costumes': list(room['costumes'])})
    for name, prop in sorted(PROPS.items()):entries.append({'kind': 'prop', 'id': name, 'tags': list(prop.tags), 'mount': prop.mount})
    for name in sorted(COSTUMES):
        if name != 'none':entries.append({'kind': 'costume', 'id': name, 'tags': [name]})
    for name, tags in INSERTS.items():entries.append({'kind': 'insert', 'id': name, 'tags': list(tags)})
    for e in entries:
        e['status'] = status.get(f'{e["kind"]}/{e["id"]}', 'DRAFT')
        if e['status'] not in STATUSES:raise ValueError(f'{e["kind"]}/{e["id"]}: bad status {e["status"]}')
    allowed = ('CANONICAL', 'DRAFT') if allow_draft else ('CANONICAL',)
    return [e for e in entries if e['status'] in allowed]


def ids(cat, kind):
    return {e['id'] for e in cat if e['kind'] == kind}


def retrieve(cat, text, kind, limit=5, exclude=()):
    """Entries of one kind ranked by tag overlap with the text (ties by id)."""
    want = words(text);scored = []
    for e in cat:
        if e['kind'] != kind or e['id'] in exclude:continue
        tags = set(t for tag in e['tags'] for t in words(tag.replace('-', ' '))) | words(e['id'].replace('-', ' '))
        scored.append((len(want & tags), e['id'], e))
    scored.sort(key=lambda s: (-s[0], s[1]))
    return [e for score, _, e in scored[:limit]]


def set_status(kind, id_, status, note=''):
    if status not in STATUSES:raise ValueError(status)
    data = approvals();data['entries'][f'{kind}/{id_}'] = status
    if note:data.setdefault('notes', {})[f'{kind}/{id_}'] = note
    APPROVALS.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')
