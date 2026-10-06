# Local regression checks

Use Python 3.12 and Node.js. On Linux, CairoSVG also needs the system Cairo library. Create a local environment and install the existing test dependencies:

The consolidation was tested with Python 3.12.14 and Node.js 24.19.0. Other runtime versions have not been validated here. Python utility tests also use Node.js to exercise packed frame data with the existing compiler.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r scripts/requirements-tests.txt
.venv/bin/python -m pip check
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests -v
node --test tests/test_frame_sequence.cjs
```

These checks exercise schema, planning, frame geometry, ownership and evidence-gate behavior with saved fixtures and synthetic unit inputs. They do not invoke a live planner, generate narration, render a new film or approve a production. Render and live-critic validation have separate requirements in the production and quality workflow documents.

The optional Pixi ownership regression uses Pixi 8.22.0. Install it in an ignored local tools directory and run:

```sh
npm install --prefix .test-tools --no-package-lock --ignore-scripts pixi.js@8.22.0
NODE_PATH="$PWD/.test-tools/node_modules" node scripts/test_motif_pixi_owner.cjs
```

Frozen evidence records retain the original capture paths and hashes. Tests that inspect a relocated checkout should resolve the recorded relative paths against the local fixture directory. Do not rewrite frozen manifests, regenerate evidence or create compatibility paths to make a test pass. Missing fixture files must still fail.

Keep production experiments separate from reusable changes. Include only original implementation and reusable prose/assets with documented provenance in public contributions. Raw private reference media, proprietary source artwork, source-specific screenshots, credentials and unlicensed fonts are excluded. Candidate creative assets require independent validation before promotion.

The legacy directed producer now copies an installed DejaVu Sans Bold font together with its distribution notice and writes a font provenance record. On systems without the default Debian font and notice paths, set both `MOTIF_FONT_PATH` and `MOTIF_FONT_LICENSE_PATH` to an explicitly cleared font and its redistribution notice. An incomplete or missing override fails. The font substitution is a portability default; typography/style equivalence has not been validated. No font binary is added to the repository.
