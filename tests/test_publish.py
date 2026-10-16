import io
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

import motif_publish as mp  # noqa: E402

BRIEF = {'slug': 'demo', 'title': 'Demo reel', 'hook': {'alternates': ['You forget 90% of what you read.'], 'selected': 0},
         'cta': {'keyword': 'BRAIN', 'narration': 'Comment BRAIN for the setup.'}}
CHANNELS = [{'id': 'ig1', 'name': 'motif.ig', 'service': 'instagram', 'displayName': 'Motif', 'isDisconnected': False, 'isLocked': False},
            {'id': 'yt1', 'name': 'Motif', 'service': 'youtube', 'displayName': 'Motif', 'isDisconnected': False, 'isLocked': False}]


class FakeNet:
    """Stands in for urllib: answers Buffer GraphQL and Cloudinary uploads, records every call."""

    def __init__(self):
        self.calls = []

    def __call__(self, req, timeout=None):
        url = req.full_url
        if 'cloudinary' in url:
            self.calls.append(('upload', url))
            return io.BytesIO(json.dumps({'secure_url': 'https://res.cloudinary.com/x/video/upload/motif/demo.mp4'}).encode())
        body = json.loads(req.data)
        assert req.headers['Authorization'] == 'Bearer KEY'
        q = body['query']
        if 'organizations' in q:data = {'account': {'organizations': [{'id': 'org1', 'name': 'Mine'}]}}
        elif 'channels(' in q:data = {'channels': CHANNELS}
        else:
            inp = body['variables']['input']
            self.calls.append(('post', inp))
            data = {'createPost': {'__typename': 'PostActionSuccess', 'post': {'id': 'p-' + inp['channelId'], 'status': 'draft' if inp.get('saveToDraft') else 'scheduled', 'dueAt': None}}}
        return io.BytesIO(json.dumps({'data': data}).encode())

    def posts(self):
        return [c[1] for c in self.calls if c[0] == 'post']


@pytest.fixture
def run(tmp_path):
    brief = tmp_path / 'demo.json';brief.write_text(json.dumps(BRIEF))
    project = tmp_path / 'RUNS/demo';project.mkdir(parents=True)
    record = {'brief': str(brief), 'stages': [{'stage': 'gate', 'status': 'PASS'}, {'stage': 'review', 'status': 'REVIEW_REQUIRED'}]}
    (project / 'reel-record.json').write_text(json.dumps(record))
    finished = tmp_path / 'RUNS/demo-finished';(finished / 'renders').mkdir(parents=True)
    (finished / 'renders/review.mp4').write_bytes(b'fake mp4')
    (finished / 'reel-record.json').write_text(json.dumps(record))
    return project


CFG = {'api_key': 'KEY', 'channels': ['ig1', 'yt1'], 'cloudinary': {'cloud_name': 'x', 'api_key': 'k', 'api_secret': 's'}}


def test_unapproved_reel_is_never_sent(run):
    net = FakeNet()
    with pytest.raises(mp.PublishError, match='no recorded approval'):
        mp.publish(run, config=CFG, opener=net)
    assert net.calls == []


def test_changed_render_needs_new_approval(run):
    mp.approve(run, 'Mayowa')
    (run.parent / 'demo-finished/renders/review.mp4').write_bytes(b'different render')
    with pytest.raises(mp.PublishError, match='changed since Mayowa approved'):
        mp.publish(run, config=CFG, opener=FakeNet())


def test_failed_gate_cannot_be_approved(run):
    rec = json.loads((run / 'reel-record.json').read_text());rec['stages'][0]['status'] = 'FAIL'
    (run / 'reel-record.json').write_text(json.dumps(rec))
    with pytest.raises(mp.PublishError, match='gate did not pass'):
        mp.approve(run, 'Mayowa')


def test_approval_is_written_to_both_records(run):
    a = mp.approve(run.parent / 'demo-finished', 'Mayowa', 'good on phone')
    for p in (run / 'reel-record.json', run.parent / 'demo-finished/reel-record.json'):
        rec = json.loads(p.read_text())
        assert rec['approval']['sha256'] == a['sha256'] and rec['stages'][-1]['status'] == 'APPROVED'


def test_queue_post_per_network_metadata(run):
    mp.approve(run, 'Mayowa');net = FakeNet()
    entry = mp.publish(run, config=CFG, opener=net)
    ig, yt = net.posts()
    assert ig['mode'] == 'addToQueue' and ig['schedulingType'] == 'automatic' and 'saveToDraft' not in ig
    assert ig['metadata'] == {'instagram': {'type': 'reel', 'shouldShareToFeed': True}}
    assert yt['metadata']['youtube']['title'] == 'Demo reel' and yt['metadata']['youtube']['categoryId']
    assert ig['assets'][0]['video']['url'].startswith('https://res.cloudinary.com/')
    assert ig['text'] == 'You forget 90% of what you read.\n\nComment BRAIN for the setup.'
    assert [p['post_id'] for p in entry['posts']] == ['p-ig1', 'p-yt1']
    rec = json.loads((run / 'reel-record.json').read_text())
    assert rec['stages'][-1] == {'stage': 'publish', 'status': 'SCHEDULED', 'posts': 2}


def test_second_publish_is_refused_unless_again(run):
    mp.approve(run, 'Mayowa')
    mp.publish(run, config=CFG, opener=FakeNet())
    with pytest.raises(mp.PublishError, match='already sent'):
        mp.publish(run, config=CFG, opener=FakeNet())
    assert len(mp.publish(run, config=CFG, opener=FakeNet(), again=True)['posts']) == 2


def test_drafts_and_dry_run_do_not_block_a_real_post(run):
    mp.approve(run, 'Mayowa');net = FakeNet()
    out = mp.publish(run, config=CFG, opener=net, dry_run=True)
    assert out['dry_run'] and not net.posts() and not [c for c in net.calls if c[0] == 'upload']
    mp.publish(run, config=CFG, opener=net, draft=True)
    assert all(p['saveToDraft'] for p in net.posts())
    mp.publish(run, config=CFG, opener=FakeNet())


def test_brief_post_block_and_scheduled_time(run, tmp_path):
    brief = dict(BRIEF, post={'caption': 'Own words.', 'title': 'Short title', 'hashtags': ['ai', '#obsidian']})
    (tmp_path / 'demo.json').write_text(json.dumps(brief))
    mp.approve(run, 'Mayowa');net = FakeNet()
    mp.publish(run, config=CFG, opener=net, mode='at', due_at='2026-10-20T17:00:00-04:00', video_url='https://cdn.example/demo.mp4')
    ig, yt = net.posts()
    assert ig['text'] == 'Own words.\n\n#ai #obsidian' and yt['metadata']['youtube']['title'] == 'Short title'
    assert ig['mode'] == 'customScheduled' and ig['dueAt'] == '2026-10-20T17:00:00-04:00'
    assert not [c for c in net.calls if c[0] == 'upload']


def test_unknown_channel_is_refused_before_upload(run):
    mp.approve(run, 'Mayowa');net = FakeNet()
    with pytest.raises(mp.PublishError, match='not channels'):
        mp.publish(run, config=dict(CFG, channels=['nope']), opener=net)
    assert not [c for c in net.calls if c[0] == 'upload']


def test_config_from_env(monkeypatch, tmp_path):
    monkeypatch.setenv('BUFFER_API_KEY', 'K');monkeypatch.setenv('MOTIF_BUFFER_CHANNELS', 'a, b')
    monkeypatch.setenv('CLOUDINARY_URL', 'cloudinary://123:s%40cret@mycloud')
    cfg = mp.load_config(tmp_path / 'missing.json')
    assert cfg == {'api_key': 'K', 'channels': ['a', 'b'], 'cloudinary': {'cloud_name': 'mycloud', 'api_key': '123', 'api_secret': 's@cret'}}


def test_cloudinary_signature():
    net = FakeNet();seen = {}

    def opener(req, timeout=None):
        seen['body'] = req.data
        return net(req, timeout)
    path = Path(__file__)
    url = mp.upload_cloudinary({'cloud_name': 'x', 'api_key': 'k', 'api_secret': 's'}, path, 'motif/demo', opener)
    assert url.startswith('https://') and b'name="signature"' in seen['body'] and b'name="public_id"\r\n\r\nmotif/demo' in seen['body']
