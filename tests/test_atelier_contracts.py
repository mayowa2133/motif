"""Motif Atelier contracts, gates, paths and Classic separation (no rendering).

Reviews written here are TEST STUBS, labelled as such: they exercise the gate
logic and are not reviews of any film.
"""
import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT));sys.path.insert(0, str(ROOT / 'scripts'))

from atelier.engine import contracts, studio  # noqa: E402
from atelier.engine.project import Project, inside, tree  # noqa: E402

FIXTURE = ROOT / 'tests/fixtures/atelier-smoke'


def stub_review(request, digest, role, status='PASS', kind='model', playback='ordered-frames', dims=None):
    """A TEST STUB response: no one reviewed anything."""
    dims = dims or {d: {'status': 'NOT_APPLICABLE' if d in request['not_applicable'] else status, 'note': 'test stub'} for d in contracts.ROLES[role]['dims']}
    value = {'request_sha256': digest, 'role': role, 'dimensions': dims, 'critical_issues': [], 'sampling_limits': 'test stub: nothing inspected',
             'summary': 'test stub response used to exercise the gate',
             'reviewer': {'kind': kind, 'id': 'TEST STUB', 'independence': 'builder-self-inspection' if kind == 'builder' else 'separate-context-same-family', 'playback': playback}}
    if role == 'proof':value['verdict'] = 'PROCEED'
    return value


class Home(unittest.TestCase):
    """Each test gets its own Atelier home; nothing touches atelier/projects."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory();self.home = Path(self.tmp.name)
        self.old = os.environ.get('MOTIF_ATELIER_HOME');os.environ['MOTIF_ATELIER_HOME'] = str(self.home)

    def tearDown(self):
        if self.old is None:os.environ.pop('MOTIF_ATELIER_HOME', None)
        else:os.environ['MOTIF_ATELIER_HOME'] = self.old
        self.tmp.cleanup()

    def brief(self, **change):
        return {**json.loads((FIXTURE / 'brief.json').read_text()), **change}


class ExplicitSelection(Home):
    def test_classic_brief_is_refused_and_never_converted(self):
        classic = json.loads((ROOT / 'quality/benchmark-briefs/bench-sqlite-everywhere.json').read_text())
        with self.assertRaisesRegex(ValueError, 'not an Atelier brief'):
            studio.start(classic)
        self.assertFalse((self.home / 'projects').exists())

    def test_idea_becomes_a_small_brief_that_waits_for_authoring(self):
        project = studio.start(studio.brief_from_idea('A silent comedy about a character trying to catch its runaway shadow', 'shadow-test'))
        self.assertEqual(project.state['status'], 'AWAITING_AUTHORING:concepts')
        self.assertTrue((project.dir / 'handoff/concepts.md').is_file())
        self.assertEqual(project.state['mode'], 'motif-atelier')
        self.assertTrue(project.runs.is_dir())

    def test_brief_contract_is_small_and_strict(self):
        self.assertTrue(contracts.brief({'mode': 'atelier', 'slug': 'x', 'idea': 'too short'}))
        self.assertTrue(contracts.brief(self.brief(shots=[])))       # detailed shot plans belong downstream
        self.assertEqual(contracts.brief(self.brief()), [])


class AuthoringContracts(Home):
    def test_concepts_need_the_budgeted_number_of_different_premises(self):
        concepts = json.loads((FIXTURE / 'concepts.json').read_text());budgets = {'concepts': 3}
        self.assertEqual(contracts.concepts(concepts, self.brief(), budgets), [])
        two = copy.deepcopy(concepts);two['premises'] = two['premises'][:2]
        self.assertTrue(contracts.concepts(two, self.brief(), budgets))
        dup = copy.deepcopy(concepts);dup['premises'][1] = {**dup['premises'][0], 'id': 'copy', 'title': 'Copy'}
        self.assertTrue(any('near-duplicates' in e for e in contracts.concepts(dup, self.brief(), budgets)))

    def test_factual_direction_needs_sourced_claims(self):
        direction = json.loads((FIXTURE / 'direction.json').read_text())
        errors = contracts.direction(direction, 'factual')
        self.assertTrue(any('claim/source ledger' in e for e in errors))
        direction['claims'] = [{'id': 'c1', 'statement': 'A ball falls at about 9.8 m/s squared near the ground.', 'kind': 'observation'}]
        self.assertTrue(any('source_url' in e for e in contracts.direction(direction, 'factual')))

    def test_not_applicable_must_be_declared_by_intent_not_after_failure(self):
        direction = json.loads((FIXTURE / 'direction.json').read_text())
        direction['applicability']['payoff'] = 'we decided the ending does not matter for this one'
        self.assertTrue(any('cannot be declared' in e for e in contracts.direction(direction, 'fictional')))
        narrated = json.loads((FIXTURE / 'direction.json').read_text());narrated['audio']['narration'] = 'voice-over'
        self.assertTrue(any('picture_sound_link' in e for e in contracts.direction(narrated, 'fictional')))

    def test_film_rejects_missing_assets_and_unknown_moments(self):
        film = json.loads((FIXTURE / 'source/film.json').read_text());direction = json.loads((FIXTURE / 'direction.json').read_text())
        film['images'] = {'hero': 'art/hero.png'}
        self.assertTrue(any('authoring task' in e for e in contracts.film(film, direction, self.brief(), FIXTURE / 'source')))
        film = json.loads((FIXTURE / 'source/film.json').read_text());film['sound']['sfx'][0]['at'] = 'nowhere'
        self.assertTrue(any('unknown moment' in e for e in contracts.film(film, direction, self.brief(), FIXTURE / 'source')))

    def test_ledger_records_every_file_with_matching_hashes(self):
        ledger = json.loads((FIXTURE / 'source/asset-ledger.json').read_text())
        self.assertEqual(contracts.ledger(ledger, tree(FIXTURE / 'source')), [])
        changed = {**tree(FIXTURE / 'source'), 'film.js': '0' * 64, 'extra.svg': '1' * 64}
        errors = contracts.ledger(ledger, changed)
        self.assertTrue(any('changed since it was recorded' in e for e in errors) and any('not recorded' in e for e in errors))


class ReviewGate(unittest.TestCase):
    def setUp(self):
        self.request = {'role': 'story', 'not_applicable': {'picture_sound_link': 'silent by design'}}

    def test_pass_needs_every_dimension(self):
        ok = stub_review(self.request, 'a' * 64, 'story')
        self.assertEqual(contracts.review(ok, self.request, 'a' * 64)[0], 'PASS')
        missing = copy.deepcopy(ok);del missing['dimensions']['payoff']
        self.assertEqual(contracts.review(missing, self.request, 'a' * 64)[0], 'FAIL')

    def test_not_assessed_blocks_except_playback_only_dimensions_without_playback(self):
        value = stub_review(self.request, 'a' * 64, 'story');value['dimensions']['payoff'] = {'status': 'NOT_ASSESSED', 'note': 'not seen'}
        self.assertEqual(contracts.review(value, self.request, 'a' * 64)[0], 'FAIL')
        value = stub_review(self.request, 'a' * 64, 'story');value['dimensions']['clarity_normal_speed'] = {'status': 'NOT_ASSESSED', 'note': 'frames only'}
        status, _, deferred = contracts.review(value, self.request, 'a' * 64)
        self.assertEqual(status, 'PASS');self.assertEqual(deferred[0]['dimension'], 'clarity_normal_speed')   # deferred to human playback, never PASS
        value['reviewer']['playback'] = 'moving'
        self.assertEqual(contracts.review(value, self.request, 'a' * 64)[0], 'FAIL')

    def test_builder_self_description_cannot_pass_story(self):
        value = stub_review(self.request, 'a' * 64, 'story', kind='builder')
        self.assertEqual(contracts.review(value, self.request, 'a' * 64)[0], 'INVALID')

    def test_response_for_another_request_is_stale_and_critical_issues_block(self):
        value = stub_review(self.request, 'a' * 64, 'story')
        self.assertEqual(contracts.review(value, self.request, 'b' * 64)[0], 'STALE')
        value['critical_issues'] = [{'dimension': 'payoff', 'where': '3.0 s', 'problem': 'no ending', 'smallest_fix': 'add one'}]
        self.assertEqual(contracts.review(value, self.request, 'a' * 64)[0], 'FAIL')

    def test_undeclared_not_applicable_blocks(self):
        value = stub_review(self.request, 'a' * 64, 'story');value['dimensions']['payoff'] = {'status': 'NOT_APPLICABLE', 'note': 'not needed'}
        self.assertEqual(contracts.review(value, self.request, 'a' * 64)[0], 'FAIL')


class PathsAndBoundaries(Home):
    def test_inside_rejects_escape_absolute_and_symlinks(self):
        base = self.home / 'p';base.mkdir()
        for bad in ('../x', '/etc/passwd', 'a/../../x'):
            with self.assertRaises(ValueError):inside(base, bad)
        (base / 'link').symlink_to(self.home)
        with self.assertRaises(ValueError):inside(base, 'link/x')
        with self.assertRaises(ValueError):tree(base)

    def test_source_lint_flags_network_clocks_and_randomness(self):
        src = self.home / 'src';src.mkdir()
        (src / 'film.js').write_text('fetch("https://x.example/a"); Math.random(); Date.now(); setTimeout(f, 1);')
        (src / 'tool.py').write_text('print(1)')
        errors = contracts.source_files(src);text = ' '.join(errors)
        for word in ('fetch', 'remote URL', 'Math.random', 'clock', 'timers', 'file type not allowed'):self.assertIn(word, text)

    def test_project_locate_is_confined_to_the_atelier_home(self):
        with self.assertRaises(ValueError):Project.locate(ROOT / 'videos/productions/voicestudio-craft-v6')
        with self.assertRaises(ValueError):Project.locate(self.home / 'elsewhere/thing')
        with self.assertRaises(ValueError):Project('Bad Slug')

    def test_renamed_project_folder_is_refused_not_reset(self):
        project = studio.start(self.brief())
        (self.home / 'projects/smoke-drop').rename(self.home / 'projects/smoke-drop-2')
        with self.assertRaisesRegex(ValueError, 'identity mismatch'):Project.locate(self.home / 'projects/smoke-drop-2')
        self.assertTrue(project.state['project_id'])

    def test_cli_exit_codes(self):
        from motif_atelier import code
        self.assertEqual(code('REVIEW_REQUIRED'), 0);self.assertEqual(code('HUMAN_APPROVED'), 0)
        self.assertEqual(code('AWAITING_REVIEW:story'), 3);self.assertEqual(code('BLOCKED:VISUAL_FAILED'), 2)


class ClassicUntouched(unittest.TestCase):
    def test_classic_cli_and_defaults_are_unchanged(self):
        import motif_reel
        out = subprocess.run([sys.executable, str(ROOT / 'scripts/motif_reel.py'), '--help'], capture_output=True, text=True, cwd=ROOT).stdout
        for cmd in ('run', 'plan', 'check', 'animatic', 'catalog'):self.assertIn(cmd, out)
        self.assertNotIn('atelier', out.lower())
        self.assertEqual(motif_reel.DELIVERY, (1080, 1920));self.assertEqual(motif_reel.VOICES, ('af_heart', 'af_bella', 'bf_emma'))
        import inspect
        self.assertIn("ROOT / 'videos/productions'", inspect.getsource(motif_reel.run))

    def test_classic_catalogue_has_no_atelier_entries(self):
        import motif_reel
        catalog = json.dumps(motif_reel.catalog_for_agents()).lower()
        self.assertNotIn('atelier', catalog)
        for slug in ('runaway-shadow', 'why-popcorn-pops', 'the-keeper', 'pim', 'ada'):
            self.assertNotIn(f'"{slug}"', catalog)

    def test_atelier_assets_are_not_in_the_classic_provenance_registry(self):
        registry = json.loads((ROOT / 'assets/PROVENANCE.json').read_text())
        self.assertFalse([a for a in registry['assets'] if 'atelier' in json.dumps(a).lower()])

    def test_canonical_bot_bytes_match_the_registry(self):
        registry = json.loads((ROOT / 'assets/PROVENANCE.json').read_text())
        canonical = [a for a in registry['assets'] if a.get('path', '').startswith('assets/characters/motif-bot/canonical')]
        self.assertTrue(canonical)
        for entry in canonical:
            path = ROOT / entry['path']
            if path.is_file():self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), entry['sha256'], entry['path'])

    def test_root_instructions_route_atelier_explicitly(self):
        text = (ROOT / 'AGENTS.md').read_text()
        self.assertIn('Motif Classic', text);self.assertIn('Motif Atelier', text);self.assertIn('atelier/AGENTS.md', text)
        nested = (ROOT / 'atelier/AGENTS.md').read_text()
        self.assertIn('root AGENTS.md', nested)        # the nested contract names the rule it narrows instead of pretending it is absent


if __name__ == '__main__':
    unittest.main()
