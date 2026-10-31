"""Motif Atelier orchestrator.

    intake -> concepts -> direction -> proof -> source -> audio -> rough -> review -> delivery

Each stage records the hashes of what it consumed. `resume` recomputes them,
so a changed upstream file re-runs only what depends on it, cached voice takes
and renders are reused by content key, and a review answers only the exact
request it was made for. Authoring stages stop at AWAITING_AUTHORING with a
handoff file (or run a bounded Codex worker when asked); review stages stop at
AWAITING_REVIEW unless the Codex backend is available. Failed gates stop the
run: nothing reaches REVIEW_REQUIRED past a FAIL, a NOT_ASSESSED, a missing
asset or stale evidence. Only `approve` (a person) sets HUMAN_APPROVED.
"""
import os
import shutil
import subprocess
import time
from pathlib import Path

from . import contracts, playback, review, sound
from .project import ROOT, Project, now, read, sha, sha_value, write

STAGES = ('intake', 'concepts', 'direction', 'proof', 'source', 'audio', 'rough', 'review', 'delivery')
RENDER_FILES = ('playback.py', 'runtime/atelier.js', 'runtime/player.html')   # what can change pixels or the encode
CORE = ('brief_sha256', 'concepts_sha256', 'direction_sha256', 'source_tree_sha256', 'audio_master_sha256', 'render_fingerprint_sha256')
EQUIVALENCE = {'mean': 6.0, 'max': 96}      # delivery (downscaled) vs reviewed preview thumbnails: same picture, different raster size
AUTHORED = {'concepts': 'concepts.json', 'direction': 'direction.json', 'proof': 'source/', 'source': 'source/'}
HANDOFF = {
    'concepts': ('Explore', 'Write concepts.json (atelier/contracts/concepts.schema.json): {n} substantially different premises, each with opening image, '
                 'audience question or emotion, central action, complication and payoff; score clarity, visual potential, originality, appeal and '
                 'feasibility 1-5 as hypotheses (not view predictions); choose one and state the rationale. Do not pick only what existing rigs can draw. '
                 'Classify the film factual, fictional or mixed.'),
    'direction': ('Direct', 'Write direction.json (atelier/contracts/direction.schema.json). Ending and opening promise first; then a shot plan describing '
                  'what the viewer actually sees change; a style sheet (characters, palette, materials, key poses, framing, typography, sound intent); the '
                  'continuity carrier; the hardest shot and its fallback. Factual or mixed: a claim ledger with primary sources and excerpts, each claim '
                  'marked observation, inference, exaggeration or invention. Declare NOT_APPLICABLE dimensions only where the intent establishes it.'),
    'proof': ('Prove the hardest shot', 'Write source/film.json (atelier/contracts/film.schema.json), source/<entry>.js registering with Atelier.register, '
              'and source/asset-ledger.json. The proof range must cover the hardest shot with representative artwork and real motion: it is rendered at '
              '360x640 and inspected before the rest of the film is built.'),
    'source': ('Produce', 'Complete the film in source/: every shot in the direction, the sound plan (narration lines placed on frames or moments, '
               'sound cues on the same moment table as the picture, optional note score), and a ledger entry for every file. '
               'Run `python scripts/motif_atelier.py ledger --project <project>` after editing files to refresh hashes.'),
}


class Blocked(Exception):
    pass


def engine_sha():
    base = Path(__file__).resolve().parent
    return sha_value({f: sha(base / f) for f in RENDER_FILES})


def core(binding):
    """The parts of a request binding that define the film itself (not file paths or container bytes)."""
    return {k: binding[k] for k in CORE if k in binding}


def brief_from_idea(idea, slug, classification='unspecified', audience=None, effect=None, duration=None, style=None):
    brief = {'mode': 'atelier', 'slug': slug, 'idea': idea, 'classification': classification, 'explore': True,
             'audience': audience or 'people scrolling short vertical video on a phone'}
    if effect:brief['intended_effect'] = effect
    if duration:brief['duration_s'] = duration
    if style:brief['style'] = style
    return brief


def start(brief, **options):
    if brief.get('mode') != 'atelier':
        raise ValueError('not an Atelier brief: Atelier needs "mode": "atelier". Classic briefs run through scripts/motif_reel.py; '
                         'a Classic job is never converted to Atelier automatically.')
    errors = contracts.brief(brief)
    if errors:raise ValueError('; '.join(errors))
    project = Project(brief['slug']).create(brief)
    project.set_stage('intake', 'DONE', {'brief.json': project.file_sha('brief.json')})
    return advance(project, **options)


class Run:
    def __init__(self, project, worker='handoff', reviewer='auto', python=None, workers=3):
        self.p = project;self.worker = worker;self.reviewer = reviewer;self.python = python;self.workers = workers

    # helpers -------------------------------------------------------------
    def brief(self):return read(self.p.dir / 'brief.json')
    def concepts(self):return read(self.p.dir / 'concepts.json')
    def direction(self):return read(self.p.dir / 'direction.json')
    def film(self):return read(self.p.source / 'film.json')

    def inputs(self, *rels):
        return {rel: self.p.file_sha(rel) for rel in rels}

    def done(self, stage, inputs, **data):
        old = self.p.stage(stage)
        if old.get('status') != 'DONE' or old.get('inputs') != inputs or any(old.get(k) != v for k, v in data.items()):
            self.p.set_stage(stage, 'DONE', inputs, **data)
        return True

    def author(self, stage, errors):
        """Write the handoff; run the bounded Codex worker if requested. Returns False (stopped)."""
        title, task = HANDOFF[stage]
        text = '\n'.join([f'# Atelier authoring task: {title} ({self.p.slug})', '',
                          'Follow atelier/AGENTS.md (the Atelier creative contract). Work only inside this project folder:', f'`{self.p.dir}`', '',
                          task.format(n=self.p.state['budgets']['concepts']), '',
                          *(['## Errors from the last check', *[f'- {e}' for e in errors], ''] if errors else []),
                          f'When done: `python scripts/motif_atelier.py resume --project {self.p.dir}`', ''])
        path = self.p.dir / f'handoff/{stage}.md';path.parent.mkdir(exist_ok=True);path.write_text(text)
        if self.worker == 'codex' and not getattr(self, '_worked', {}).get(stage):
            self._worked = {**getattr(self, '_worked', {}), stage: True}
            if codex_author(self.p, stage, text):return None   # caller re-checks once
        self.p.set_stage(stage, 'AWAITING_AUTHORING', errors=errors[:30], agent_assisted=True, worker=self.worker)
        self.p.set_status(f'AWAITING_AUTHORING:{stage}', f'complete {path.relative_to(self.p.dir)} then resume')
        return False

    def approach(self):return self.direction()['approach_id']

    def failed_rounds(self, approach):
        return len({f['source_sha256'] for f in self.p.state['failures'].get(approach, [])})

    def exhausted(self, approach):
        return self.failed_rounds(approach) > self.p.state['budgets']['creative_repairs_per_approach']

    def fail(self, approach, role, digest, issues):
        rounds = self.p.state['failures'].setdefault(approach, [])
        if not any(f['request_sha256'] == digest for f in rounds):
            rounds.append({'role': role, 'request_sha256': digest, 'source_sha256': self.p.source_sha(), 'at': now(), 'issues': issues[:20]})
            self.p.event('creative-failure', approach=approach, role=role, round=self.failed_rounds(approach))
        budget = self.p.state['budgets']['creative_repairs_per_approach'];used = self.failed_rounds(approach) - 1
        if self.exhausted(approach):
            self.p.set_status('BLOCKED:REPAIR_BUDGET_EXHAUSTED', f'approach {approach} failed {used + 1} times ({budget} repairs allowed): '
                              'record a concept change (new direction approach_id + `concept-change`) or an unresolved blocker (`blocker`)')
        else:
            self.p.set_status(f'BLOCKED:{role.upper()}_FAILED', f'repair attempt {used + 1} of {budget} for approach {approach}: fix what reviews/{role}.json lists, '
                              'then resume (the old review is archived as stale); or change the concept')
        return False

    def spend(self, minutes_needed=0):
        used = sum(r.get('seconds', 0) for r in self.p.state['renders']) / 60
        if used + minutes_needed > self.p.state['budgets']['render_minutes']:
            self.p.set_status('BLOCKED:RENDER_BUDGET', f'{used:.1f} of {self.p.state["budgets"]["render_minutes"]} render minutes used; raise resources.render_minutes in the brief deliberately')
            raise Blocked()

    def render(self, kind, out, size, frames=None, timing=None, stills=()):
        self.spend()
        film = self.film()
        try:
            rec = playback.render(self.p.source, film, timing or {'lines': {}}, out, size, frames, self.workers, stills=stills)
        except playback.RenderError as e:
            self.p.state['technical_retries'].append({'at': now(), 'kind': kind, 'error': str(e)[:600]});self.p.save()
            self.p.set_status('BLOCKED:RENDER_ERROR', f'{kind} render failed (technical, not a creative repair): {str(e)[:300]}')
            raise Blocked()
        stills = rec.pop('stills')
        self.p.state['renders'].append({'at': now(), 'kind': kind, **{k: rec[k] for k in ('frames', 'size', 'seconds', 'workers')}, 'file': str(Path(rec['file']).relative_to(self.p.root))})
        self.p.save()
        return rec, stills

    def settle(self, role):
        """Before a request is replaced, judge any response bound to it, so a failure is counted even if the request then changes."""
        path = self.p.dir / f'reviews/{role}-request.json';got = review.response(self.p, role)
        if not path.is_file() or not got or got.get('request_sha256') != sha(path):return
        status, issues, _ = contracts.review(got, read(path), sha(path))
        self.p.state.setdefault('settled', {})[role] = {'request_sha256': sha(path), 'core': core(read(path)['binding']), 'status': status}
        self.p.save()
        approach = read(path).get('approach_id') or self.p.stage('direction').get('approach_id') or self.approach()   # the approach the request was made under
        if status == 'FAIL' and not any(f['request_sha256'] == sha(path) for v in self.p.state['failures'].values() for f in v):
            rounds = self.p.state['failures'].setdefault(approach, [])
            if True:
                rounds.append({'role': role, 'request_sha256': sha(path), 'source_sha256': read(path)['binding']['source_tree_sha256'], 'at': now(), 'issues': issues[:20]})
                self.p.event('creative-failure', approach=approach, role=role, round=self.failed_rounds(approach), settled='before the request changed')
                self.p.save()

    def gate(self, role, value, digest):
        """None: awaiting review. True: PASS. False: blocked."""
        got = review.response(self.p, role);bound = digest
        settled = self.p.state.get('settled', {}).get(role, {})
        if got and got.get('request_sha256') != digest and settled.get('request_sha256') == got.get('request_sha256') and settled.get('core') == core(value['binding']):
            bound = got['request_sha256']          # same brief, direction, source, audio and decoded picture: the verdict still applies
            self.p.event('review-carried', role=role, from_request=bound, to_request=digest, reason='identical film; only paths or container bytes changed')
        elif got and got.get('request_sha256') != digest:review.archive(self.p, role, 'stale: the request changed');got = None
        if got is None:
            if self.reviewer == 'codex' or (self.reviewer == 'auto' and review.codex_available()):
                try:got = review.codex_review(self.p, role, value, digest, self.p.runs / 'review-calls')
                except Exception as e:
                    self.p.state['technical_retries'].append({'at': now(), 'kind': f'{role}-review', 'error': str(e)[:600]});self.p.save()
                    return None
            else:return None
        status, issues, deferred = contracts.review(got, value, bound)
        self.p.state.setdefault('reviews', {})[role] = {'status': status, 'request_sha256': digest, 'response_request_sha256': bound, 'reviewer': got.get('reviewer'),
                                                        'issues': issues[:20], 'deferred': deferred, 'at': now()}
        self.p.save()
        if status == 'PASS':return True
        if status in ('INVALID', 'STALE'):
            self.p.set_status('BLOCKED:REVIEW_INVALID', f'reviews/{role}.json is not a valid response to the current request: {"; ".join(issues)[:300]}')
            return False
        return self.fail(self.approach(), role, digest, issues)

    # stages ----------------------------------------------------------------
    def step_intake(self):
        errors = contracts.brief(self.brief())
        if errors:self.p.set_status('BLOCKED:BRIEF', '; '.join(errors));return False
        return self.done('intake', self.inputs('brief.json'))

    def step_concepts(self):
        if not (self.p.dir / 'concepts.json').is_file():return self.author('concepts', [])
        errors = contracts.concepts(self.concepts(), self.brief(), self.p.state['budgets'])
        if errors:return self.author('concepts', errors)
        return self.done('concepts', self.inputs('brief.json', 'concepts.json'), chosen=self.concepts()['chosen'], agent_assisted=True)

    def step_direction(self):
        if not (self.p.dir / 'direction.json').is_file():return self.author('direction', [])
        d = self.direction();errors = contracts.direction(d, self.concepts()['classification'])
        approaches = self.p.state.setdefault('approaches', {})
        if not errors and approaches and d['approach_id'] not in approaches:
            change = [c for c in self.p.state['concept_changes'] if c['to'] == d['approach_id']]
            if not change:errors.append(f'approach_id changed to {d["approach_id"]} without a recorded concept change: run `concept-change --to {d["approach_id"]} --reason ...`')
            elif any(d['logline'] == a['logline'] and d['hardest_shot']['why'] == a['hardest_shot'] for a in approaches.values()):
                errors.append('the new approach repeats a previous logline and hardest shot: a renamed approach is not a concept change')
        if errors:return self.author('direction', errors)
        approaches.setdefault(d['approach_id'], {'logline': d['logline'], 'hardest_shot': d['hardest_shot']['why'], 'at': now()});self.p.save()
        return self.done('direction', self.inputs('concepts.json', 'direction.json'), approach_id=d['approach_id'], agent_assisted=True)

    def source_errors(self, complete):
        errors = contracts.source_files(self.p.source)
        if not (self.p.source / 'film.json').is_file():return errors + ['source: film.json missing']
        if not (self.p.source / 'asset-ledger.json').is_file():errors.append('source: asset-ledger.json missing')
        else:errors += contracts.ledger(read(self.p.source / 'asset-ledger.json'), self.p.source_tree())
        return errors + contracts.film(self.film(), self.direction(), self.brief(), self.p.source, complete)

    def step_proof(self):
        approach = self.approach();old = self.p.stage('proof')
        if old.get('status') == 'DONE' and old.get('approach_id') == approach:return True
        if self.exhausted(approach):return self.fail(approach, 'proof', 'exhausted', [])
        errors = self.source_errors(complete=False)
        if errors:return self.author('proof', errors)
        film = self.film();p = film['proof'];key = sha_value([self.p.source_sha(), engine_sha(), 'proof'])[:12]
        out = self.p.runs / f'proof/{key}';video = out / 'proof.mp4'
        if not video.is_file():self.render('proof', video, playback.PREVIEW, (p['start'], p['end']))
        entries, finger = self.cached_evidence(out, video, film, 'proof', (p['start'], p['end']))
        binding = {'brief_sha256': self.p.file_sha('brief.json'), 'direction_sha256': self.p.file_sha('direction.json'),
                   'source_tree_sha256': self.p.source_sha(), 'render_sha256': sha(video), 'render_fingerprint_sha256': sha_value(finger)}
        self.settle('proof')
        value, digest = review.request(self.p, 'proof', binding, entries, film, {'proof_video': str(video.relative_to(self.p.root)), 'proof_frames': [p['start'], p['end']]})
        result = self.gate('proof', value, digest)
        if result is None:
            self.p.set_status('AWAITING_REVIEW:proof', 'watch the proof at phone size and write reviews/proof.json (builder inspection is allowed here, and recorded as such), then resume')
            return False
        if not result:return False
        return self.done('proof', {'direction.json': self.p.file_sha('direction.json')}, approach_id=approach, request_sha256=digest,
                         reviewer=review.response(self.p, 'proof')['reviewer'])

    def step_source(self):
        errors = self.source_errors(complete=True)
        if errors:return self.author('source', errors)
        return self.done('source', {'source': self.p.source_sha(), 'direction.json': self.p.file_sha('direction.json')}, agent_assisted=True)

    def audio_key(self, film):
        files = [self.p.source / c['file'] for c in film['sound']['sfx'] if c.get('file')]
        return sha_value([film['sound'], film['frames'], film['fps'], film['moments'], sha(Path(sound.__file__)), [sha(f) for f in files]])[:12]

    def step_audio(self):
        film = self.film();key = self.audio_key(film);out = self.p.runs / f'audio/{key}'
        if not (out / 'audio.json').is_file():
            timing, errors, takes = sound.plan(film, self.p.runs / 'cache', self.python)
            if errors:return self.author('source', [f'audio: {e}' for e in errors])
            files, cues = sound.stems(film, timing, takes, self.p.source, out, seed=int(self.p.state['project_id'][:6], 16))
            sound.master(out / 'premix.wav', out / 'master.wav')
            if timing['lines']:sound.captions(timing, out / 'captions.vtt')
            write(out / 'timing.json', timing)
            write(out / 'audio.json', {'key': key, 'takes': takes, 'cues': cues, 'stems': {k: str(Path(v).relative_to(self.p.root)) for k, v in files.items()},
                                       'master_sha256': sha(out / 'master.wav'), 'target': sound.TARGET, 'captions': (out / 'captions.vtt').is_file(),
                                       'method': timing['method'], 'listening': 'NOT_ASSESSED: measurements are not listening approval'})
        record = read(out / 'audio.json')
        return self.done('audio', {'sound': sha_value(film['sound']), 'key': key}, key=key, master_sha256=record['master_sha256'],
                         takes_reused=sum(t['reused_from_cache'] for t in record['takes']), takes=len(record['takes']))

    def audio_dir(self):return self.p.runs / f'audio/{self.p.stage("audio")["key"]}'

    def cached_evidence(self, out, video, film, role, frames=None):
        rec = out / f'evidence-{role}.json'
        if rec.is_file() and read(rec).get('video_sha256') == sha(video):
            value = read(rec);return value['entries'], value['fingerprint']
        entries, finger = review.evidence(self.p, video, film, role, out / f'evidence-{role}', frames)
        write(rec, {'video_sha256': sha(video), 'entries': entries, 'fingerprint': finger})
        return entries, finger

    def step_rough(self):
        if self.exhausted(self.approach()) and any(self.p.state.get('reviews', {}).get(r, {}).get('status') != 'PASS' for r in self.roles()):
            return self.fail(self.approach(), 'review', 'exhausted', [])
        film = self.film();audio = self.audio_dir();key = sha_value([self.p.source_sha(), self.p.stage('audio')['key'], engine_sha()])[:12]
        out = self.p.runs / f'rough/{key}';preview = out / 'preview.mp4'
        if not preview.is_file():
            self.render('rough', out / 'picture.mp4', playback.PREVIEW, timing=read(audio / 'timing.json'))
            playback.mux(out / 'picture.mp4', audio / 'master.wav', preview, audio / 'captions.vtt' if (audio / 'captions.vtt').is_file() else None, duration=film['frames'] / film['fps'])
            (out / 'picture.mp4').unlink()
        info = playback.probe(preview)
        if info['video']['frames'] != film['frames']:
            self.p.set_status('BLOCKED:RENDER_ERROR', f'rough has {info["video"]["frames"]} frames, film declares {film["frames"]}');return False
        self.cached_evidence(out, preview, film, 'review')
        return self.done('rough', {'source': self.p.source_sha(), 'audio': self.p.stage('audio')['key']}, key=key, preview=str(preview.relative_to(self.p.root)),
                         preview_sha256=sha(preview))

    def roles(self):
        return ['story', 'visual'] + (['factual'] if self.concepts()['classification'] in ('factual', 'mixed') else [])

    def step_review(self):
        film = self.film();rough = self.p.stage('rough');out = self.p.runs / f'rough/{rough["key"]}';preview = self.p.root / rough['preview']
        entries, finger = self.cached_evidence(out, preview, film, 'review');audio = read(self.audio_dir() / 'audio.json')
        binding = {'brief_sha256': self.p.file_sha('brief.json'), 'concepts_sha256': self.p.file_sha('concepts.json'), 'direction_sha256': self.p.file_sha('direction.json'),
                   'source_tree_sha256': self.p.source_sha(), 'audio_master_sha256': audio['master_sha256'], 'render_sha256': sha(preview),
                   'render_fingerprint_sha256': sha_value(finger)}
        measured = sound.loudness(preview)
        narration = [{'id': k, **v} for k, v in read(self.audio_dir() / 'timing.json')['lines'].items()]
        extra = {'audio': {'measured_on_preview': measured, 'cues': audio['cues'], 'note': 'measurements only; no reviewer has listened'}, 'narration': narration}
        for role in self.roles():self.settle(role)
        requests = {role: review.request(self.p, role, binding, entries, film, extra) for role in self.roles()}
        results = {role: self.gate(role, *requests[role]) for role in self.roles()}
        if any(r is False for r in results.values()):return False
        waiting = [role for role, r in results.items() if r is None]
        if waiting:
            self.p.set_status('AWAITING_REVIEW:' + ','.join(waiting), 'independent reviewers write ' + ', '.join(f'reviews/{r}.json' for r in waiting) +
                              ' from the matching -request.md, then resume; the builder may not write these')
            return False
        return self.done('review', {role: requests[role][1] for role in self.roles()}, reviewers={r: self.p.state['reviews'][r]['reviewer'] for r in self.roles()})

    def step_delivery(self):
        film = self.film();audio_dir = self.audio_dir();audio = read(audio_dir / 'audio.json');rough = self.p.stage('rough')
        key = sha_value([self.p.stage('review')['inputs'], rough['key']])[:12];out = self.p.runs / f'delivery/{key}'
        final = out / f'{self.p.slug}-delivery-1080x1920.mp4';phone = out / f'{self.p.slug}-preview-360x640.mp4';record_path = out / 'delivery.json'
        if not record_path.is_file():
            done = [r for r in self.p.state['renders'] if r['kind'] == 'delivery']
            if len(done) >= self.p.state['budgets']['delivery_renders']:
                self.p.set_status('BLOCKED:DELIVERY_BUDGET', f'{len(done)} delivery renders used of {self.p.state["budgets"]["delivery_renders"]}');return False
            sample = sorted(int(n) for n in read(self.p.runs / f'rough/{rough["key"]}/evidence-review.json')['fingerprint'])
            checks_at = sample[::max(1, len(sample) // 3)][:3]
            rec, stills = self.render('delivery', out / 'picture.mp4', playback.DELIVERY, timing=read(audio_dir / 'timing.json'), stills=checks_at)
            captions = audio_dir / 'captions.vtt' if audio['captions'] else None
            playback.mux(out / 'picture.mp4', audio_dir / 'master.wav', final, captions, duration=film['frames'] / film['fps'])
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(final), '-map', '0', '-vf', 'scale=360:640:flags=area', '-c:v', 'libx264', '-crf', '23', '-preset', 'medium',
                            '-c:a', 'copy', '-c:s', 'copy', '-movflags', '+faststart', str(phone)], check=True)
            (out / 'picture.mp4').unlink()
            checks = technical(self, film, final, phone, audio, stills, sample)
            write(record_path, {'status': 'PASS' if all(c['status'] in ('PASS', 'NOT_APPLICABLE') for c in checks.values()) else 'FAIL', 'checks': checks,
                                'delivery': str(final.relative_to(self.p.root)), 'delivery_sha256': sha(final), 'preview': str(phone.relative_to(self.p.root)),
                                'preview_sha256': sha(phone), 'render_seconds': rec['seconds'], 'target': sound.TARGET, 'at': now()})
        record = read(record_path)
        if not final.is_file() or sha(final) != record['delivery_sha256']:
            self.p.set_status('BLOCKED:DELIVERY_CHANGED', 'the delivery file differs from its technical record; delete the delivery folder and resume');return False
        if record['status'] != 'PASS':
            bad = {k: v for k, v in record['checks'].items() if v['status'] not in ('PASS', 'NOT_APPLICABLE')}
            self.p.set_status('BLOCKED:TECHNICAL', 'technical checks failed: ' + '; '.join(f'{k}: {v["observed"]}' for k, v in bad.items())[:500]);return False
        metadata(self, film, record)
        return self.done('delivery', {'review': self.p.stage('review')['inputs'], 'rough': rough['key']}, key=key, delivery=record['delivery'],
                         delivery_sha256=record['delivery_sha256'], preview=record['preview'])


def technical(run, film, final, phone, audio, stills, sample):
    """Measured delivery checks; each is PASS, FAIL or NOT_APPLICABLE with a stated reason."""
    fps = film['fps'];frames = film['frames'];duration = frames / fps;checks = {}
    def check(name, ok, observed, expected, na=None):
        checks[name] = {'status': 'NOT_APPLICABLE' if na else 'PASS' if ok else 'FAIL', 'observed': observed, 'expected': expected, **({'reason': na} if na else {})}
    for name, path, size in (('delivery', final, playback.DELIVERY), ('preview', phone, playback.PREVIEW)):
        info = playback.probe(path);v, a = info['video'], info['audio']
        check(f'{name}-format', v and v['codec'] == 'h264' and v['pix_fmt'] == 'yuv420p' and (v['width'], v['height']) == size and abs(v['fps'] - fps) < .01,
              v and f'{v["codec"]} {v["pix_fmt"]} {v["width"]}x{v["height"]} @{v["fps"]:.3f}', f'h264 yuv420p {size[0]}x{size[1]} @{fps}')
        check(f'{name}-frames', v and v['frames'] == frames, v and v['frames'], frames)
        check(f'{name}-audio-stream', a and a['codec'] == 'aac' and a['sample_rate'] == 48000 and a['channels'] == 2, a and f'{a["codec"]} {a["sample_rate"]} Hz {a["channels"]} ch', 'aac 48000 Hz 2 ch')
        check(f'{name}-av-duration', a and abs(a['duration'] - v['duration']) <= 1.5 / fps and abs(v['duration'] - duration) <= 1 / fps,
              a and f'video {v["duration"]:.3f}s audio {a["duration"]:.3f}s', f'{duration:.3f}s within one frame')
        if audio['captions']:check(f'{name}-captions', info['subtitles'] == ['mov_text'], info['subtitles'], ['mov_text'])
        else:check(f'{name}-captions', True, [], [], na='no narration or dialogue: nothing to caption')
    level = sound.loudness(final);t = sound.TARGET
    check('loudness', abs(level['integrated_lufs'] - t['integrated_lufs']) <= t['tolerance_lu'], level['integrated_lufs'], f'{t["integrated_lufs"]} +/- {t["tolerance_lu"]} LUFS')
    check('true-peak', level['true_peak_dbtp'] <= t['true_peak_dbtp'], level['true_peak_dbtp'], f'<= {t["true_peak_dbtp"]} dBTP')
    clipped = sound.clipped_samples(final);check('clipping', clipped == 0, clipped, 0)
    sfx = run.p.root / audio['stems']['sfx']
    offset = sound.av_offset_ms(sfx, final) if audio['cues'] else None
    if offset is None:check('av-sync', True, None, None, na='no sound-design cues to align')
    else:check('av-sync', abs(offset) <= 1000 / fps, f'{offset} ms (cues placed on the moment table the picture uses)', f'within {1000 / fps:.0f} ms')
    rough = read(run.p.runs / f'rough/{run.p.stage("rough")["key"]}/evidence-review.json')['fingerprint']
    mine = playback.fingerprint(final, sample);dist = [playback.thumb_distance(rough[str(n)], mine[str(n)]) for n in sample]
    worst = {'mean': max(d['mean'] for d in dist), 'max': max(d['max'] for d in dist)}
    check('reviewed-picture', worst['mean'] <= EQUIVALENCE['mean'] and worst['max'] <= EQUIVALENCE['max'], worst, f'thumbnail distance to the reviewed preview <= {EQUIVALENCE}')
    repeat = determinism(run, film, sorted(stills, reverse=True))
    same = [repeat[n] == stills[n] for n in stills]
    check('deterministic-seek', all(same), f'{sum(same)}/{len(same)} frames byte-identical when re-rendered in reverse order in a fresh browser', 'all identical')
    ledger = read(run.p.source / 'asset-ledger.json')
    check('rights-ledger', not contracts.ledger(ledger, run.p.source_tree()), f'{len(ledger["assets"])} source files recorded; voice: approved Kokoro takes; sfx/music: seeded code',
          'every file recorded with origin and rights (human rights confirmation still required)')
    check('network', True, 'all non-local requests aborted; none attempted', 'none')
    return checks


def determinism(run, film, frames):
    """Re-render chosen frames in a fresh browser, in reverse order, and return their PNG bytes."""
    keep = {}
    server = playback.Server(run.p.source, read(run.audio_dir() / 'timing.json'));errors, blocked = [], []
    try:playback._worker(server.base, playback.DELIVERY, frames, None, film['fps'], 18, set(frames), blocked, errors, keep)
    finally:server.close()
    if errors or blocked:raise playback.RenderError('; '.join(errors + blocked))
    return keep


def metadata(run, film, record):
    concepts = run.concepts();chosen = next(p for p in concepts['premises'] if p['id'] == concepts['chosen']);d = run.direction()
    write(run.p.dir / 'production-metadata.json', {'project': run.p.slug, 'project_id': run.p.state['project_id'], 'mode': 'motif-atelier',
          'concept': {'id': chosen['id'], 'title': chosen['title']}, 'hook': chosen['opening_image'], 'style': d['style_sheet']['look'],
          'classification': concepts['classification'], 'duration_s': round(film['frames'] / film['fps'], 3), 'approach': d['approach_id'],
          'revision': {'source_tree_sha256': run.p.source_sha(), 'ledger_versions': sum(a['version'] for a in read(run.p.source / 'asset-ledger.json')['assets'])},
          'delivery_sha256': record['delivery_sha256'], 'published': False})


def codex_author(project, stage, text, timeout=1800):
    """Bounded coding-agent worker: Codex in workspace-write mode inside the project folder, minimal environment."""
    try:
        from motif_direct import resolve_codex_cli
        cli = resolve_codex_cli()['cli_path']
    except Exception as e:
        project.event('worker-unavailable', stage=stage, worker='codex', reason=str(e)[:200]);return False
    env = {k: os.environ[k] for k in ('PATH', 'HOME', 'CODEX_HOME', 'LANG') if k in os.environ}
    args = [cli, 'exec', '--ephemeral', '--skip-git-repo-check', '--sandbox', 'workspace-write', '--cd', str(project.dir), '-c', 'approval_policy="never"', '-']
    started = time.time()
    try:result = subprocess.run(args, input=text, text=True, capture_output=True, timeout=timeout, env=env, cwd=project.dir)
    except subprocess.TimeoutExpired:
        project.event('worker-timeout', stage=stage, worker='codex', seconds=timeout);return False
    log = project.runs / f'authoring/{stage}-{int(started)}.json'
    write(log, {'argv': args, 'exit_code': result.returncode, 'seconds': round(time.time() - started, 1), 'stdout_tail': result.stdout[-4000:], 'stderr_tail': result.stderr[-2000:]})
    project.event('worker-run', stage=stage, worker='codex', exit_code=result.returncode, log=str(log.relative_to(project.root)))
    return result.returncode == 0


def advance(project, **options):
    run = Run(project, **options)
    if (project.dir / 'direction.json').is_file() and (project.dir / 'concepts.json').is_file():
        for role in ['proof'] + run.roles():run.settle(role)     # count failed reviews before anything upstream can change
    for stage in STAGES:
        step = getattr(run, f'step_{stage}')
        try:
            result = step()
            if result is None:result = step()   # a worker just authored: check once more
        except Blocked:
            return halted(project, stage)
        if not result:return halted(project, stage)
    decision = project.state.get('human_decision')
    if decision and decision.get('delivery_sha256') == project.stage('delivery')['delivery_sha256']:
        project.set_status(decision['status'], decision.get('note', ''))
    else:
        if decision:project.event('human-decision-invalidated', reason='delivery changed after the decision');project.state['human_decision'] = None
        project.set_status('REVIEW_REQUIRED', 'a person watches the delivery on a phone with sound, confirms rights and facts, then runs `approve`')
    return project


def halted(project, stage):
    """A stage could not complete: it and everything after it are no longer current."""
    stages = project.state['stages'];reason = project.state['status'].split(':')[0]
    if stages.get(stage, {}).get('status') == 'DONE':stages[stage]['status'] = reason
    for later in STAGES[STAGES.index(stage) + 1:]:
        if stages.get(later, {}).get('status') == 'DONE':stages[later]['status'] = 'SUPERSEDED'
    if project.state.get('human_decision') and stages.get('delivery', {}).get('status') != 'DONE':
        project.event('human-decision-invalidated', decision=project.state['human_decision'], reason='the delivery it named is no longer current')
        project.state['human_decision'] = None
    project.save()
    return project


def approve(project, by, decision, note):
    """The only path to HUMAN_APPROVED: a named person's explicit decision on the current delivery."""
    if project.state.get('status') not in ('REVIEW_REQUIRED', 'HUMAN_APPROVED', 'HUMAN_REJECTED'):
        raise ValueError(f'nothing to decide: project status is {project.state.get("status")}')
    delivery = project.stage('delivery')
    if sha(project.root / delivery['delivery']) != delivery['delivery_sha256']:raise ValueError('delivery file changed since its checks; resume first')
    status = {'approved': 'HUMAN_APPROVED', 'rejected': 'HUMAN_REJECTED'}[decision]
    project.state['human_decision'] = {'status': status, 'by': by, 'note': note, 'at': now(), 'delivery_sha256': delivery['delivery_sha256']}
    project.set_status(status, note)
    return project


def concept_change(project, to, reason):
    if len(reason.strip()) < 20:raise ValueError('a concept change needs a substantive reason')
    project.state['concept_changes'].append({'to': to, 'reason': reason, 'at': now(),
                                             'from': project.stage('direction').get('approach_id'), 'failed_rounds': project.state['failures'].get(project.stage('direction').get('approach_id'), [])[-1:]})
    project.event('concept-change', to=to);return project


def blocker(project, note):
    project.state['blocker'] = {'note': note, 'at': now()}
    project.set_status('BLOCKED:UNRESOLVED', note);return project


def refresh_ledger(project, add=None):
    """Update hashes of recorded source files (bumping their version); list unrecorded files.

    add: {origin, author, rights, use} records every unrecorded file with those explicit values.
    """
    path = project.source / 'asset-ledger.json';ledger = read(path) if path.is_file() else {'assets': []};tree = project.source_tree();changed, missing = [], []
    for entry in ledger['assets']:
        digest = tree.get(entry['path'])
        if digest and digest != entry['sha256']:entry['sha256'] = digest;entry['version'] += 1;changed.append(entry['path'])
    recorded = {a['path'] for a in ledger['assets']}
    missing = [rel for rel in tree if rel not in recorded and rel != 'asset-ledger.json']
    if add:
        kinds = {'.js': 'source', '.json': 'data', '.svg': 'art', '.png': 'art', '.webp': 'art', '.jpg': 'art', '.wav': 'audio', '.woff2': 'font', '.ttf': 'font', '.otf': 'font', '.txt': 'license', '.md': 'data'}
        for rel in missing:ledger['assets'].append({'path': rel, 'kind': kinds.get(Path(rel).suffix, 'data'), 'version': 1, 'sha256': tree[rel], **add})
        missing = []
    write(path, ledger);project.event('ledger-refresh', changed=changed, unrecorded=missing)
    return {'changed': changed, 'unrecorded': missing}


def diagnostic(project, frames=None, size='preview', workers=3, stills=None):
    """Render the current source regardless of gates. DIAGNOSTIC_ONLY: never a delivery, never reviewed."""
    film = read(project.source / 'film.json');stamp = now().replace(':', '').replace('-', '')[:15]
    out = project.runs / f'diagnostic/{stamp}-DIAGNOSTIC_ONLY.mp4'
    timing = {'lines': {}}
    audio_key = project.stage('audio').get('key')
    if audio_key and (project.runs / f'audio/{audio_key}/timing.json').is_file():timing = read(project.runs / f'audio/{audio_key}/timing.json')
    if stills:
        folder = project.runs / f'diagnostic/{stamp}-stills-DIAGNOSTIC_ONLY';folder.mkdir(parents=True, exist_ok=True)
        server = playback.Server(project.source, timing);errors, blocked, keep = [], [], {}
        try:playback._worker(server.base, playback.PREVIEW if size == 'preview' else playback.DELIVERY, sorted(stills), None, film['fps'], 18, set(stills), blocked, errors, keep)
        finally:server.close()
        if errors or blocked:raise playback.RenderError('; '.join(errors + blocked))
        for n, png in keep.items():(folder / f'f{n:05d}.png').write_bytes(png)
        return folder
    rec = playback.render(project.source, film, timing, out, playback.PREVIEW if size == 'preview' else playback.DELIVERY, frames, workers)
    rec.pop('stills')
    write(out.with_suffix('.json'), {'status': 'DIAGNOSTIC_ONLY', 'source_tree_sha256': project.source_sha(), **rec,
                                     'note': 'diagnostic render: not reviewed, not a delivery, never counted toward REVIEW_REQUIRED'})
    project.state['renders'].append({'at': now(), 'kind': 'diagnostic', **{k: rec[k] for k in ('frames', 'size', 'seconds', 'workers')}, 'file': str(out.relative_to(project.root))})
    project.event('diagnostic-render', file=str(out.relative_to(project.root)))
    return out


def status(project):
    """Summary with freshness: stages whose recorded inputs no longer match are reported STALE."""
    run = Run(project);s = project.state;stale = []
    checks = {'intake': lambda: run.inputs('brief.json'), 'concepts': lambda: run.inputs('brief.json', 'concepts.json'),
              'direction': lambda: run.inputs('concepts.json', 'direction.json'),
              'source': lambda: {'source': project.source_sha(), 'direction.json': project.file_sha('direction.json')}}
    for name, fn in checks.items():
        st = project.stage(name)
        try:
            if st.get('status') == 'DONE' and st.get('inputs') != fn():stale.append(name)
        except Exception:stale.append(name)
    if project.stage('rough').get('status') == 'DONE' and project.stage('rough')['inputs'].get('source') != project.source_sha():stale.append('rough')
    deliv = project.stage('delivery')
    local = bool(deliv.get('delivery')) and (project.root / deliv['delivery']).is_file()
    used = sum(r.get('seconds', 0) for r in s['renders']) / 60
    return {'project': project.slug, 'project_id': s['project_id'], 'mode': s['mode'], 'status': s['status'], 'next_step': s.get('next_step', ''),
            'stages': {k: project.stage(k).get('status', 'PENDING') for k in STAGES}, 'stale': stale,
            'reviews': {k: {'status': v['status'], 'reviewer': (v.get('reviewer') or {}).get('id')} for k, v in s.get('reviews', {}).items()},
            'failures': {k: len({f['source_sha256'] for f in v}) for k, v in s['failures'].items()},
            'budgets': s['budgets'], 'render_minutes_used': round(used, 2), 'renders': len(s['renders']), 'technical_retries': len(s['technical_retries']),
            'delivery': deliv.get('delivery'), 'delivery_present_locally': local, 'human_decision': s.get('human_decision'),
            'folders': {'project': str(project.dir), 'runs': str(project.runs)}}
