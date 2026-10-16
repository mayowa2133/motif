"""Approve a finished reel and send it to Buffer, so posting is not manual.

    python scripts/motif_publish.py channels                       # list Buffer channel ids
    python scripts/motif_publish.py approve RUNS/<slug> --by Mayowa  # record the human approval
    python scripts/motif_publish.py publish RUNS/<slug> --dry-run    # show what would be sent
    python scripts/motif_publish.py publish RUNS/<slug>              # Buffer's queue (default)
    python scripts/motif_publish.py publish RUNS/<slug> --draft      # Buffer drafts, nothing goes out

Only a reel a human approved is sent, and only the exact file they approved
(its sha256 is stored with the approval). Buffer fetches video from a public
https URL, so the render is first uploaded to Cloudinary (or pass --video-url
for a file hosted elsewhere). Setup and credentials: docs/PUBLISHING.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

BUFFER_API = 'https://api.buffer.com'
CLOUDINARY_MAX = 100 * 1024 * 1024  # single-request video upload limit on Cloudinary's free plan
CONFIG_PATH = Path(os.environ.get('MOTIF_PUBLISH_CONFIG', Path.home() / '.config/motif/publish.json'))
MODES = {'queue': 'addToQueue', 'next': 'shareNext', 'now': 'shareNow', 'at': 'customScheduled'}
YOUTUBE_EDUCATION = '27'


class PublishError(RuntimeError):
    pass


# ---------- config ----------

def load_config(path=None):
    """Env vars win over the config file; neither is ever in the repo."""
    path = Path(path) if path else CONFIG_PATH
    cfg = json.loads(path.read_text()) if path.is_file() else {}
    env = os.environ
    if env.get('BUFFER_API_KEY'):cfg['api_key'] = env['BUFFER_API_KEY']
    if env.get('MOTIF_BUFFER_CHANNELS'):cfg['channels'] = [c.strip() for c in env['MOTIF_BUFFER_CHANNELS'].split(',') if c.strip()]
    if env.get('CLOUDINARY_URL'):cfg['cloudinary'] = parse_cloudinary_url(env['CLOUDINARY_URL'])
    return cfg


def parse_cloudinary_url(url):
    """cloudinary://<api_key>:<api_secret>@<cloud_name>, as Cloudinary's dashboard prints it."""
    u = urllib.parse.urlparse(url)
    if u.scheme != 'cloudinary' or not (u.username and u.password and u.hostname):
        raise PublishError('CLOUDINARY_URL must look like cloudinary://<api_key>:<api_secret>@<cloud_name>')
    return {'cloud_name': u.hostname, 'api_key': urllib.parse.unquote(u.username), 'api_secret': urllib.parse.unquote(u.password)}


# ---------- run folder ----------

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):h.update(block)
    return h.hexdigest()


def locate(run):
    """(project dir, render path, record paths) for RUNS/<slug> or RUNS/<slug>-finished."""
    run = Path(run)
    project = run.with_name(run.name[:-len('-finished')]) if run.name.endswith('-finished') else run
    finished = project.with_name(project.name + '-finished')
    render = next((p for p in (finished / 'renders/review.mp4', project / 'renders/review.mp4') if p.is_file()), None)
    if not (project / 'reel-record.json').is_file():raise PublishError(f'no reel-record.json in {project}')
    if render is None:raise PublishError(f'no render in {project}: run motif_reel.py run with --render first')
    records = [p for p in (project / 'reel-record.json', finished / 'reel-record.json') if p.is_file()]
    return project, render, records


def read_record(project):
    return json.loads((project / 'reel-record.json').read_text())


def write_record(record, paths):
    for p in paths:p.write_text(json.dumps(record, indent=2) + '\n')


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


# ---------- approval ----------

def approve(run, by, note=''):
    """Record that a human watched this render and approved it for posting."""
    if not by.strip():raise PublishError('--by names the person who approved the reel')
    project, render, records = locate(run)
    record = read_record(project)
    gate = [s for s in record.get('stages', []) if s.get('stage') == 'gate']
    if not gate or gate[-1].get('status') != 'PASS':raise PublishError('the quality gate did not pass on this run; nothing to approve')
    record['approval'] = {'by': by.strip(), 'at': now(), 'file': str(render), 'sha256': sha256(render), 'note': note}
    record['stages'].append({'stage': 'review', 'status': 'APPROVED', 'by': by.strip(), 'sha256': record['approval']['sha256']})
    write_record(record, records)
    return record['approval']


def approved_render(project, render):
    record = read_record(project)
    a = record.get('approval')
    if not a:raise PublishError('this reel has no recorded approval: watch it, then run `motif_publish.py approve RUN --by <name>`')
    if sha256(render) != a['sha256']:raise PublishError(f'{render} changed since {a["by"]} approved it; approve the new render first')
    return record


# ---------- post content ----------

def brief_of(record, project):
    path = Path(record.get('brief', ''))
    for p in (path, project / 'brief.json'):
        if p.is_file():return json.loads(p.read_text())
    raise PublishError(f'cannot find the brief {path}')


def hook_line(brief):
    hook = brief.get('hook', {})
    lines = hook.get('alternates') or [hook.get('narration', '')]
    return lines[min(hook.get('selected', 0), len(lines) - 1)].strip()


def post_text(brief):
    """Caption and YouTube title: the brief's own `post` block, else hook + CTA."""
    post = brief.get('post', {})
    caption = post.get('caption') or '\n\n'.join(t for t in (hook_line(brief), brief.get('cta', {}).get('narration', '').strip()) if t)
    tags = ' '.join('#' + t.lstrip('#') for t in post.get('hashtags', []))
    if tags:caption = f'{caption}\n\n{tags}'
    title = (post.get('title') or brief.get('title') or brief['slug'])[:100]
    return caption, title


def post_input(channel, video_url, caption, title, mode, due_at=None, draft=False, thumbnail_ms=1000):
    """CreatePostInput for one channel; per-network metadata from Buffer's schema."""
    service = channel['service']
    inp = {'channelId': channel['id'], 'text': caption, 'schedulingType': 'automatic', 'mode': MODES[mode],
           'assets': [{'video': {'url': video_url, 'metadata': {'thumbnailOffset': thumbnail_ms}}}]}
    if mode == 'at':inp['dueAt'] = due_at
    if draft:inp['saveToDraft'] = True
    meta = {'instagram': {'type': 'reel', 'shouldShareToFeed': True},
            'youtube': {'title': title, 'categoryId': YOUTUBE_EDUCATION, 'privacy': 'public', 'madeForKids': False},
            'facebook': {'type': 'reel'}}.get(service)
    if meta:inp['metadata'] = {service: meta}
    return inp


# ---------- Buffer ----------

def graphql(api_key, query, variables=None, opener=urllib.request.urlopen):
    req = urllib.request.Request(BUFFER_API, data=json.dumps({'query': query, 'variables': variables or {}}).encode(),
                                 headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json', 'User-Agent': 'motif-publish'})
    try:
        with opener(req, timeout=60) as r:body = json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise PublishError(f'Buffer API HTTP {e.code}: {e.read()[:300].decode(errors="replace")}') from None
    if body.get('errors'):raise PublishError('Buffer API: ' + '; '.join(e.get('message', str(e)) for e in body['errors']))
    return body['data']


CHANNELS_QUERY = '''query Channels($org: OrganizationId!) {
  channels(input: {organizationId: $org}) { id name service displayName isDisconnected isLocked }
}'''
ORGS_QUERY = 'query { account { organizations { id name } } }'
CREATE_POST = '''mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    __typename
    ... on PostActionSuccess { post { id status dueAt } }
    ... on MutationError { message }
  }
}'''


def list_channels(api_key, opener=urllib.request.urlopen):
    out = []
    for org in graphql(api_key, ORGS_QUERY, opener=opener)['account']['organizations']:
        for c in graphql(api_key, CHANNELS_QUERY, {'org': org['id']}, opener=opener)['channels']:
            out.append({**c, 'organization': org['name']})
    return out


def create_post(api_key, inp, opener=urllib.request.urlopen):
    res = graphql(api_key, CREATE_POST, {'input': inp}, opener=opener)['createPost']
    if res.get('__typename') != 'PostActionSuccess':raise PublishError(f'Buffer refused the post for {inp["channelId"]}: {res.get("message", res)}')
    return res['post']


# ---------- hosting ----------

def multipart(fields, file_field, path):
    boundary = uuid.uuid4().hex
    head = b''.join(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode() for k, v in fields.items())
    head += f'--{boundary}\r\nContent-Disposition: form-data; name="{file_field}"; filename="{Path(path).name}"\r\nContent-Type: video/mp4\r\n\r\n'.encode()
    return head + Path(path).read_bytes() + f'\r\n--{boundary}--\r\n'.encode(), f'multipart/form-data; boundary={boundary}'


def upload_cloudinary(cfg, render, public_id, opener=urllib.request.urlopen):
    """Signed upload; returns the public https delivery URL Buffer fetches at post time."""
    if Path(render).stat().st_size > CLOUDINARY_MAX:raise PublishError(f'{render} is over 100 MB; host it yourself and pass --video-url')
    params = {'overwrite': 'false', 'public_id': public_id, 'timestamp': str(int(time.time()))}
    to_sign = '&'.join(f'{k}={params[k]}' for k in sorted(params)) + cfg['api_secret']
    fields = {**params, 'api_key': cfg['api_key'], 'signature': hashlib.sha1(to_sign.encode()).hexdigest()}
    body, ctype = multipart(fields, 'file', render)
    req = urllib.request.Request(f'https://api.cloudinary.com/v1_1/{cfg["cloud_name"]}/video/upload', data=body, headers={'Content-Type': ctype})
    try:
        with opener(req, timeout=600) as r:res = json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise PublishError(f'Cloudinary HTTP {e.code}: {e.read()[:300].decode(errors="replace")}') from None
    if not str(res.get('secure_url', '')).startswith('https://'):raise PublishError(f'Cloudinary returned no https URL: {res}')
    return res['secure_url']


# ---------- publish ----------

def publish(run, *, mode='queue', due_at=None, draft=False, dry_run=False, again=False, video_url=None,
            channels=None, config=None, opener=urllib.request.urlopen):
    """Send an approved reel to every configured Buffer channel; returns the publish entry."""
    if mode == 'at' and not due_at:raise PublishError('--at needs an ISO 8601 time with an offset, e.g. 2026-10-20T17:00:00-04:00')
    project, render, records = locate(run)
    record = approved_render(project, render)
    cfg = config if config is not None else load_config()
    wanted = channels or cfg.get('channels') or []
    if not wanted:raise PublishError('no Buffer channels: set MOTIF_BUFFER_CHANNELS or "channels" in the config (ids from `motif_publish.py channels`)')
    done = {p['channel'] for e in record.get('publish', []) if not e.get('draft') and not e.get('dry_run') for p in e['posts']}
    repeat = sorted(set(wanted) & done)
    if repeat and not again:raise PublishError(f'already sent to {", ".join(repeat)}; pass --again to post it twice')
    brief = brief_of(record, project)
    caption, title = post_text(brief)
    if not cfg.get('api_key'):raise PublishError('no Buffer API key: set BUFFER_API_KEY or "api_key" in the config')
    by_id = {c['id']: c for c in list_channels(cfg['api_key'], opener)}  # read-only, safe in a dry run
    missing = [c for c in wanted if c not in by_id]
    if missing:raise PublishError(f'not channels on this Buffer account: {", ".join(missing)}')
    off = [c for c in wanted if by_id[c].get('isDisconnected') or by_id[c].get('isLocked')]
    if off:raise PublishError(f'reconnect these channels in Buffer first: {", ".join(by_id[c]["name"] for c in off)}')
    if dry_run:
        url = video_url or f'https://res.cloudinary.com/<cloud>/video/upload/motif/{brief["slug"]}.mp4'
        return {'dry_run': True, 'inputs': [post_input(by_id[c], url, caption, title, mode, due_at, draft) for c in wanted]}
    if not video_url:
        if not cfg.get('cloudinary'):raise PublishError('no video host: set CLOUDINARY_URL, or pass --video-url with a public https link to the mp4')
        video_url = upload_cloudinary(cfg['cloudinary'], render, f'motif/{brief["slug"]}-{record["approval"]["sha256"][:12]}', opener)
    entry = {'at': now(), 'mode': mode, 'draft': draft, 'video_url': video_url, 'sha256': record['approval']['sha256'], 'posts': []}
    try:
        for c in wanted:
            post = create_post(cfg['api_key'], post_input(by_id[c], video_url, caption, title, mode, due_at, draft), opener)
            entry['posts'].append({'channel': c, 'service': by_id[c]['service'], 'name': by_id[c]['name'], 'post_id': post['id'], 'status': post.get('status'), 'due_at': post.get('dueAt')})
    finally:
        if entry['posts']:
            record.setdefault('publish', []).append(entry)
            record['stages'].append({'stage': 'publish', 'status': 'DRAFTED' if draft else 'SCHEDULED', 'posts': len(entry['posts'])})
            write_record(record, records)
    return entry


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0]);sub = p.add_subparsers(dest='cmd', required=True)
    sub.add_parser('channels', help='list the Buffer channels this API key can post to')
    a = sub.add_parser('approve', help='record that a human watched the render and approved it');a.add_argument('run', type=Path)
    a.add_argument('--by', required=True);a.add_argument('--note', default='')
    pb = sub.add_parser('publish', help='send an approved reel to Buffer');pb.add_argument('run', type=Path)
    when = pb.add_mutually_exclusive_group()
    when.add_argument('--draft', action='store_true', help='save as Buffer drafts; nothing is published')
    when.add_argument('--next', action='store_true', help='put it at the front of the queue')
    when.add_argument('--at', metavar='ISO_TIME', help='publish at this time, e.g. 2026-10-20T17:00:00-04:00')
    when.add_argument('--now', action='store_true', help='publish immediately')
    pb.add_argument('--channel', action='append', help='Buffer channel id (repeatable); default from config')
    pb.add_argument('--video-url', help='public https URL of this exact render, instead of uploading to Cloudinary')
    pb.add_argument('--dry-run', action='store_true', help='check the key and channels, print the Buffer inputs; uploads and posts nothing')
    pb.add_argument('--again', action='store_true', help='post to a channel this reel was already sent to')
    a = p.parse_args(argv)
    try:
        if a.cmd == 'channels':
            cfg = load_config()
            if not cfg.get('api_key'):raise PublishError('no Buffer API key: set BUFFER_API_KEY (docs/PUBLISHING.md)')
            out = list_channels(cfg['api_key'])
        elif a.cmd == 'approve':
            out = approve(a.run, a.by, a.note)
        else:
            mode = 'now' if a.now else 'next' if a.next else 'at' if a.at else 'queue'
            out = publish(a.run, mode=mode, due_at=a.at, draft=a.draft, dry_run=a.dry_run, again=a.again, video_url=a.video_url, channels=a.channel)
    except PublishError as e:
        raise SystemExit(f'motif_publish: {e}')
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
