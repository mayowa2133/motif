# Asset lifecycle

Implementation: `scripts/motif_asset_quality.py`; exposed through `motif_quality.py asset-transition`.

GENERATED may enter REVIEW without promotion. CANONICAL requires current asset SHA, id, scope, materials, actual SVG layer IDs, normalized anchors, supported interactions, provenance and license. Raster metadata names intentional solid or transparent background. Check alpha pixels/background quality in the review, not merely the existence of an alpha channel.

The external review names the matching asset hash, reviewer/date, explicit human approval, and separate PASS results for silhouette, mobile, material, layers, anchors, geometry, interaction, alpha, provenance and licensing. A stale or missing check fails. These are reviewed evidence, not automated claims about visual appeal or legal clearance. No automatic canonicalization.

```sh
python3 scripts/motif_quality.py asset-transition --asset /absolute/prop.svg \
  --metadata /absolute/generated.json --state REVIEW --output /absolute/review.json
python3 scripts/motif_quality.py asset-transition --asset /absolute/prop.svg \
  --metadata /absolute/review.json --review /absolute/human-asset-review.json \
  --state CANONICAL --output /absolute/canonical.json
```

Use `scope: scene-specific` for a one-off. Explicitly nominate `candidate-reusable` before requesting promotion. An executable performance state is a shared capability; it does not approve new mascot geometry or new artwork.
