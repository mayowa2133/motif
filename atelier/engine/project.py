"""Atelier project identity, constrained paths, hashing and the state manifest.

A project is two folders that share one slug under the Atelier home
(`atelier/`, or MOTIF_ATELIER_HOME for tests):

    projects/<slug>/   authored and committed: brief, concepts, direction,
                       source/, reviews/, atelier-project.json
    runs/<slug>/       generated and ignored by Git: voice takes, mixes,
                       renders, review frames, diagnostics

The manifest's history is append-only. Identity (slug + project_id) is fixed at
intake; a renamed or copied folder is refused rather than silently reset.
"""
import hashlib
import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODE = 'motif-atelier'
SCHEMA = 'motif-atelier-project/1'
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*')
MANIFEST = 'atelier-project.json'


def home():
    return Path(os.environ.get('MOTIF_ATELIER_HOME', ROOT / 'atelier')).resolve()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sha_value(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path);path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.tmp');tmp.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n');tmp.replace(path)


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def inside(base, rel):
    """Resolve a project-relative path; no absolute paths, '..', or symlinks."""
    rel = Path(rel)
    if not rel.parts or rel.is_absolute() or '..' in rel.parts:raise ValueError(f'path must be project-relative: {rel}')
    base = Path(base).resolve();target = base / rel
    for part in [target, *target.parents]:
        if part == base:break
        if part.is_symlink():raise ValueError(f'symlinks are not allowed in Atelier projects: {rel}')
    if not target.resolve().is_relative_to(base):raise ValueError(f'path escapes the project: {rel}')
    return target


def tree(folder, skip=()):
    """{relative path: sha256} for every file; symlinks fail."""
    folder = Path(folder);out = {}
    if not folder.is_dir():return out
    for path in sorted(folder.rglob('*')):
        if path.is_symlink():raise ValueError(f'symlinks are not allowed in Atelier projects: {path}')
        rel = path.relative_to(folder).as_posix()
        if path.is_file() and rel not in skip and not rel.endswith('.tmp'):out[rel] = sha(path)
    return out


class Project:
    def __init__(self, slug, root=None):
        if not isinstance(slug, str) or not SLUG.fullmatch(slug):raise ValueError(f'invalid slug: {slug!r}')
        self.slug = slug;self.root = Path(root).resolve() if root else home()
        self.dir = self.root / 'projects' / slug;self.runs = self.root / 'runs' / slug

    @classmethod
    def locate(cls, path):
        """Accept atelier/projects/<slug> or atelier/runs/<slug>, only under the Atelier home."""
        path = Path(path).resolve();base = home()
        if path.parent.name not in ('projects', 'runs') or path.parent.parent != base:
            raise ValueError(f'{path} is not an Atelier project folder under {base}/projects or {base}/runs')
        project = cls(path.name, base)
        if not (project.dir / MANIFEST).is_file():raise FileNotFoundError(f'no Atelier project manifest for {path.name}')
        project.load();return project

    # files ---------------------------------------------------------------
    def path(self, rel):return inside(self.dir, rel)
    def run_path(self, rel):return inside(self.runs, rel)
    @property
    def source(self):return self.dir / 'source'
    def source_tree(self):return tree(self.source)
    def source_sha(self):return sha_value(self.source_tree())
    def file_sha(self, rel):
        path = self.path(rel);return sha(path) if path.is_file() else None

    # manifest ------------------------------------------------------------
    def create(self, brief):
        if self.dir.exists():raise FileExistsError(f'{self.dir} exists; resume it or choose a fresh slug')
        self.dir.mkdir(parents=True);self.runs.mkdir(parents=True, exist_ok=True)
        write(self.dir / 'brief.json', brief)
        self.state = {'schema': SCHEMA, 'mode': MODE, 'slug': self.slug, 'project_id': uuid.uuid4().hex, 'created': now(),
                      'budgets': brief_budgets(brief), 'stages': {}, 'failures': {}, 'concept_changes': [],
                      'technical_retries': [], 'renders': [], 'reviewer_calls': 0, 'human_decision': None,
                      'status': 'NEW', 'history': []}
        self.event('intake', brief_sha256=sha(self.dir / 'brief.json'));return self

    def load(self):
        self.state = read(self.dir / MANIFEST)
        if self.state.get('schema') != SCHEMA or self.state.get('mode') != MODE:raise ValueError('not a Motif Atelier project manifest')
        if self.state.get('slug') != self.slug:
            raise ValueError(f'project identity mismatch: manifest slug {self.state.get("slug")!r} in folder {self.slug!r}; folders are not renamed, start a new project instead')
        return self

    def save(self):write(self.dir / MANIFEST, self.state)

    def event(self, kind, **data):
        self.state['history'].append({'at': now(), 'event': kind, **data});self.save()

    def stage(self, name):return self.state['stages'].get(name, {})

    def set_stage(self, name, status, inputs=None, **data):
        self.state['stages'][name] = {'status': status, 'inputs': inputs or {}, 'at': now(), **data}
        self.event('stage', stage=name, status=status, **{k: v for k, v in data.items() if k in ('agent_assisted', 'worker', 'reason', 'errors')})

    def set_status(self, status, next_step=''):
        if status != self.state.get('status') or next_step != self.state.get('next_step'):
            self.state['status'] = status;self.state['next_step'] = next_step;self.event('status', status=status, next_step=next_step)


def brief_budgets(brief):
    r = brief.get('resources', {})
    return {'concepts': r.get('concepts', 3), 'creative_repairs_per_approach': r.get('creative_repairs_per_approach', 2),
            'delivery_renders': r.get('delivery_renders', 3), 'render_minutes': r.get('render_minutes', 60)}
