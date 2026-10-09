"""Asset-origin registry and export check.

Every reusable picture, font or sound a render can contain is recorded in
assets/PROVENANCE.json with its hash, its origin and how it was made. The
export check walks a project's assets/ folder and fails on any file whose hash
is unknown, whose registered origin is `reference-derived`, or whose approval
was rejected.

Origins
    procedural-seeded   deterministic code with a seed and no image/audio input
    motif-image-gen     Motif's own image-generation call; the prompt is recorded
    motif-authored-svg  vector art authored in Motif code or by hand
    motif-tts           narration synthesised for a Motif script
    motif-derived       lossless re-encode or crop of another registered asset
    licensed            third-party file under a recorded licence
    reference-derived   anything traced, sampled or extracted from reference media

Per-film generated outputs (narration takes, per-film SFX) are not reusable,
so a project may declare them with glob rules in asset-provenance.json; rules
may only use the per-film origins below and must name their generator.
"""
import argparse
import fnmatch
import hashlib
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'assets/PROVENANCE.json'
ORIGINS = ('procedural-seeded', 'motif-image-gen', 'motif-authored-svg', 'motif-tts', 'motif-derived', 'licensed', 'reference-derived')
RULE_ORIGINS = ('motif-tts', 'procedural-seeded')
APPROVALS = ('APPROVED', 'LEGACY_ACCEPTED', 'PENDING', 'REJECTED')
MEDIA = {'.png', '.webp', '.jpg', '.jpeg', '.gif', '.svg', '.woff', '.woff2', '.ttf', '.otf', '.wav', '.mp3', '.m4a', '.aac', '.flac', '.ogg'}
IMAGES = {'.png', '.webp', '.jpg', '.jpeg', '.gif'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pixel_sha(path):
    from motif_materials import pixel_sha as pixels
    from PIL import Image
    with Image.open(path) as image:return pixels(image)


def load(path=REGISTRY):
    data = json.loads(Path(path).read_text()) if Path(path).exists() else {'version': 1, 'assets': []}
    validate(data);return data


def validate(data):
    if data.get('version') != 1:raise ValueError('provenance registry version 1 required')
    seen = set()
    for entry in data['assets']:
        for key in ('id', 'sha256', 'origin', 'generator', 'approval'):
            if not entry.get(key):raise ValueError(f'provenance entry {entry.get("id")} missing {key}')
        if entry['id'] in seen:raise ValueError('duplicate provenance id ' + entry['id'])
        seen.add(entry['id'])
        if entry['origin'] not in ORIGINS:raise ValueError(f'{entry["id"]}: unknown origin {entry["origin"]}')
        if entry['approval'].get('status') not in APPROVALS:raise ValueError(f'{entry["id"]}: unknown approval status')
        if entry['origin'] == 'motif-derived' and not entry.get('derived_from'):raise ValueError(f'{entry["id"]}: derived asset must name derived_from')
        if entry['origin'] == 'licensed' and not entry.get('license'):raise ValueError(f'{entry["id"]}: licensed asset must record its licence')
        if entry['origin'] == 'motif-image-gen' and not entry.get('prompt'):raise ValueError(f'{entry["id"]}: image-gen asset must record its prompt')
    ids = {e['id'] for e in data['assets']}
    for entry in data['assets']:
        if entry.get('derived_from') and entry['derived_from'] not in ids:raise ValueError(f'{entry["id"]}: derived_from {entry["derived_from"]} not registered')
    return data


def index(data):
    by_sha, by_pixels = {}, {}
    for entry in data['assets']:
        by_sha.setdefault(entry['sha256'], entry)
        if entry.get('pixel_sha256'):by_pixels.setdefault(entry['pixel_sha256'], entry)
    return by_sha, by_pixels


def inventory(project):
    """Media files a render of this project can contain."""
    folder = Path(project) / 'assets'
    if not folder.is_dir():return []
    return sorted(p for p in folder.rglob('*') if p.is_file() and p.suffix.lower() in MEDIA)


def project_rules(project, extra=None):
    path = Path(project) / 'asset-provenance.json'
    rules = list(extra or []) + (json.loads(path.read_text()).get('rules', []) if path.exists() else [])
    for rule in rules:
        if rule.get('origin') not in RULE_ORIGINS:raise ValueError(f'project rule {rule.get("glob")}: per-film rules may only declare {RULE_ORIGINS}')
        if not rule.get('glob') or not rule.get('generator'):raise ValueError('project rule needs glob and generator')
    return rules


def lineage(entry, data):
    """Walk derived_from to the root so a re-encode cannot launder a reference asset."""
    ids = {e['id']: e for e in data['assets']};chain = [entry]
    while chain[-1].get('derived_from'):
        chain.append(ids[chain[-1]['derived_from']])
        if len(chain) > 20:raise ValueError('provenance derivation loop at ' + entry['id'])
    return chain


def check(project, registry=None, rules=None):
    """Export check. Returns a record; `status` is PASS or FAIL."""
    project = Path(project);data = registry if registry is not None else load()
    validate(data);by_sha, by_pixels = index(data);rules = project_rules(project, rules)
    files, unknown, rejected, reference = [], [], [], []
    for path in inventory(project):
        rel = path.relative_to(project).as_posix();digest = sha(path)
        entry = by_sha.get(digest)
        if entry is None and path.suffix.lower() in IMAGES:
            try:entry = by_pixels.get(pixel_sha(path))
            except OSError:entry = None
        if entry is not None:
            chain = lineage(entry, data)
            files.append({'path': rel, 'id': entry['id'], 'origin': chain[-1]['origin']})
            if any(e['origin'] == 'reference-derived' for e in chain):reference.append(rel)
            if any(e['approval']['status'] == 'REJECTED' for e in chain):rejected.append(rel)
            continue
        rule = next((r for r in rules if fnmatch.fnmatch(rel, r['glob'])), None)
        if rule:files.append({'path': rel, 'rule': rule['glob'], 'origin': rule['origin']});continue
        unknown.append(rel)
    status = 'FAIL' if unknown or reference or rejected else 'PASS'
    return {'status': status, 'checked': len(files) + len(unknown), 'unknown': unknown, 'reference_derived': reference, 'rejected': rejected, 'files': files}


def entry_for(path, id_, origin, generator, approval, **extra):
    path = Path(path)
    value = {'id': id_, 'sha256': sha(path), 'origin': origin, 'generator': generator, 'approval': approval}
    if path.suffix.lower() in IMAGES:value['pixel_sha256'] = pixel_sha(path)
    try:value['path'] = path.resolve().relative_to(ROOT).as_posix()
    except ValueError:pass
    value.update({k: v for k, v in extra.items() if v is not None})
    return value


def add(data, entry):
    """Insert or replace by id; identical hashes under a new id are refused."""
    for i, existing in enumerate(data['assets']):
        if existing['id'] == entry['id']:data['assets'][i] = entry;return entry
        if existing['sha256'] == entry['sha256']:return existing
    data['assets'].append(entry);return entry


# Registry seeding from evidence already in the repository ---------------------

LEGACY = {'status': 'LEGACY_ACCEPTED', 'by': 'Mayowa', 'date': '2026-10-02', 'note': 'Shipped in VoiceStudio v6, accepted as the gold visual-craft benchmark.'}
PENDING = {'status': 'PENDING', 'by': None, 'date': None, 'note': 'Awaiting Mayowa review.'}
V6 = ROOT / 'videos/productions/voicestudio-craft-v6'


def bootstrap():
    data = {'version': 1, 'assets': []}
    manifest = json.loads((ROOT / 'assets/materials/materials-manifest.json').read_text())
    for set_name, records in manifest.items():
        for name, record in records.items():
            add(data, entry_for(ROOT / record['path'], f'material/{set_name}/{name}', 'procedural-seeded',
                                f'python scripts/motif_materials.py --set {set_name}', LEGACY if set_name == 'legacy-v0' else PENDING,
                                note='Port of reference-reconstruction-01-finishing/materials.py: seeded noise, no image inputs; pixels reproduced by --check.' if set_name == 'legacy-v0' else None))
    add(data, entry_for(V6 / 'assets/materials/world-paper.webp', 'material/legacy-v0/wall@webp', 'motif-derived',
                        'scripts/motif_ui_production.py: lossless WebP of wall.png', LEGACY, derived_from='material/legacy-v0/wall'))
    for folder in ('art-v3', 'art-v4'):
        source = V6 / 'assets' / folder / 'provenance.json'
        if not source.exists():source = ROOT / 'videos/productions/voicestudio-hero-art-v4/assets' / folder / 'provenance.json'
        record = json.loads(source.read_text())
        for item in record['assets']:
            png = V6 / 'assets' / folder / (item['id'] + '.png')
            if not png.exists():continue
            master = add(data, entry_for(png, f'art/{folder}/{item["id"]}', 'motif-image-gen', item.get('method', record.get('method', 'image_gen')), LEGACY,
                                         prompt=item['prompt'], evidence=source.relative_to(ROOT).as_posix(), edit_of=record.get('source_style_reference')))
            webp = png.with_suffix('.webp')
            if webp.exists():add(data, entry_for(webp, master['id'] + '@webp', 'motif-derived', 'cwebp lossless derivative', LEGACY, derived_from=master['id']))
    sfx = json.loads((V6 / 'sfx-source-manifest.json').read_text())
    for item in sfx['assets']:
        add(data, entry_for(V6 / item['file'], 'sfx/v6/' + item['id'], 'procedural-seeded', f'{item["source"]}; seed {item["seed"]}', LEGACY,
                            evidence=(V6 / 'sfx-source-manifest.json').relative_to(ROOT).as_posix()))
    for font, licence in (('Inter-700', 'OFL-inter.txt'), ('Inter-900', 'OFL-inter.txt'), ('EBGaramond-700', 'OFL-eb-garamond.txt')):
        add(data, entry_for(V6 / 'assets/fonts' / (font + '.woff2'), 'font/' + font, 'licensed', 'distributed font binary', LEGACY,
                            license='SIL Open Font License 1.1', evidence=(V6 / 'assets/fonts' / licence).relative_to(ROOT).as_posix()))
    for path in sorted((ROOT / 'assets/characters/motif-bot/canonical').rglob('*')):
        if path.is_file() and path.suffix.lower() in MEDIA:
            add(data, entry_for(path, 'bot/' + path.relative_to(ROOT / 'assets/characters/motif-bot/canonical').with_suffix('').as_posix(), 'motif-authored-svg',
                                'python scripts/build_motif_bot.py', {**LEGACY, 'note': 'Canonical Motif Bot v1 (Direction A).'}))
    scenes = ROOT / 'assets/scenes'
    for path in sorted(scenes.rglob('*.svg')):
        master = add(data, entry_for(path, 'scene/' + path.relative_to(scenes).with_suffix('').as_posix(), 'motif-authored-svg',
                                     'authored scene SVG; see sibling metadata json', LEGACY))
        preview = path.with_suffix('.png')
        if preview.exists():add(data, entry_for(preview, master['id'] + '@png', 'motif-derived', 'raster preview of the SVG master', LEGACY, derived_from=master['id']))
    # Deny-list: reference study media. Registered so a copy anywhere fails the check by hash.
    study = ROOT / 'references/reconstruction/study'
    for path in sorted(study.rglob('*')):
        if path.is_file() and path.suffix.lower() in MEDIA:
            add(data, entry_for(path, 'reference/' + path.relative_to(study).as_posix(), 'reference-derived', 'reference study capture',
                                {'status': 'REJECTED', 'by': 'policy', 'date': '2026-10-09', 'note': 'Reference media are never render inputs.'}))
    return validate(data)


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = p.add_subparsers(dest='action', required=True)
    c = sub.add_parser('check', help='export check for one project');c.add_argument('project', type=Path);c.add_argument('--rules', type=Path, help='extra per-film rules JSON (for frozen projects that cannot be edited)')
    sub.add_parser('bootstrap', help='rebuild the registry from evidence already in the repository')
    r = sub.add_parser('register', help='register one file');r.add_argument('file', type=Path);r.add_argument('--id', required=True);r.add_argument('--origin', choices=ORIGINS, required=True)
    r.add_argument('--generator', required=True);r.add_argument('--prompt');r.add_argument('--license');r.add_argument('--derived-from')
    a = p.parse_args()
    if a.action == 'check':
        rules = json.loads(a.rules.read_text())['rules'] if a.rules else None
        result = check(a.project, rules=rules);print(json.dumps({k: v for k, v in result.items() if k != 'files'}, indent=2));raise SystemExit(0 if result['status'] == 'PASS' else 1)
    if a.action == 'bootstrap':
        data = bootstrap()
    else:
        data = load();add(data, entry_for(a.file, a.id, a.origin, a.generator, PENDING, prompt=a.prompt, license=a.license, derived_from=a.derived_from));validate(data)
    REGISTRY.write_text(json.dumps(data, indent=1) + '\n');print(f'{len(data["assets"])} registered assets -> {REGISTRY.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
