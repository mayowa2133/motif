# Asset provenance

Every picture, font or sound a Motif render can contain is registered in [`assets/PROVENANCE.json`](../assets/PROVENANCE.json) with its hash, origin, generator and approval. The technical gate (`motif_quality.py technical`) measures the `provenance` check itself: any file under a project's `assets/` that is unregistered, registered as `reference-derived`, or rejected fails it, whatever a supplied report says.

```sh
python scripts/motif_provenance.py check <project>          # export check
python scripts/motif_provenance.py register <file> --id ... --origin ... --generator ...
python scripts/motif_provenance.py bootstrap                # rebuild from evidence in the repo
python scripts/motif_materials.py --check                   # textures reproduce from their seeds
python scripts/motif_materials.py --swatches out.png        # review sheet
```

Origins: `procedural-seeded`, `motif-image-gen` (prompt recorded), `motif-authored-svg`, `motif-tts`, `motif-derived` (re-encode of another entry, `derived_from` required), `licensed` (licence recorded), `reference-derived` (always fails). Images also match by decoded pixels, so a lossless re-encode of a registered texture is recognised, and derivation chains are walked so a re-encode cannot hide a reference origin. Reference study media under `references/reconstruction/study/` are registered as `reference-derived` so a copy anywhere fails by hash.

Per-film generated outputs such as narration takes are declared by glob in the project's `asset-provenance.json` (`motif-tts` or `procedural-seeded` only, generator required).

## Materials

`scripts/motif_materials.py` holds two seeded sets of 2048 px RGBA overlays (tone in RGB, strength in alpha):

- `legacy-v0`: paper, card, wood, wall. The generator first written in `reference-reconstruction-01-finishing/materials.py`; ported verbatim and proven to reproduce the committed pixels. Shared code installs `wall.png` from here instead of copying it out of a reference study folder. This stays the default.
- `motif-v1`: matte paper, felt, card, kraft, wood, dark card. Built on a torus (spectral noise, wrap-around fibres) so tiles have no seam; tests check seam and repeat scores. Awaiting approval; a brief opts in with `"material_set": "motif-v1"`.
