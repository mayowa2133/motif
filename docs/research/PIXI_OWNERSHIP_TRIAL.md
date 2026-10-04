# Scoped Pixi ownership integration trial

Status: optional experimental helper; no default renderer migration or canonical art promotion.

Externally seeking a paused scene can change parent and child transforms before a render. PixiJS8.22.0 `reparentChild` reads cached `worldTransform`; a stale cache can move a transferred object to its previous rendered position. A fresh public `getGlobalTransform()` query for child and destination, then `addChild`/`setFromMatrix`, preserves the authored current world pose. The helper owns no clock and starts no ticker.

The isolated project pins pixi.js8.22.0 locally, with install scripts disabled. Forty transfers across rotated, nonuniformly scaled parent graphs pass with maximum affine component error1.43e-13; the cached-transfer control demonstrably fails.103 existing repository tests pass. Native browser capture confirms9/9 arbitrary reverse seeks produce byte-identical Pixi frames after the fix. A matched SVG baseline is visually comparable;8/9 exact hashes match, with localized image-edge interpolation differences on one sample. Neither result establishes improved creative direction.

Recommendation: retain the small helper for experimental Pixi scenes needing genuine ownership transfers. Keep the existing production renderer; this trial supplies no visible reason to migrate it. Coherent asset improvements are independent of the renderer: both paths used identical authored layers and timing. Costs include an additional project-local dependency, raster texture memory, asset preparation and GPU/readback setup. Human creative review remains required.

Run the isolated no-GPU regression with `node scripts/test_motif_pixi_owner.cjs /absolute/path/to/project/node_modules/pixi.js`. The root project gains no package installation.

Public sources: [official Pixi container skill](https://github.com/pixijs/pixijs-skills/blob/main/skills/pixijs-scene-container/SKILL.md), [Container API](https://pixijs.download/v8.22.0/docs/scene.Container.html), [coherent asset guidance](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/blob/main/skills/disciplines/create-game-assets/SKILL.md). Private reconstruction evidence, source pixels and copied staging stay outside this source change.
