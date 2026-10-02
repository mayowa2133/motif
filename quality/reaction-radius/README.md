# Selected reaction primitive

`scripts/motif_reaction.py` extracts v6's decaying local response into bounded seconds-based channels. Explicit origin/target, radius ≤2000 authoring units, relevance 0–1, duration ≤1.2 s, delay ≤0.3 s, translation ≤30 units and rotation ≤12 degrees. Continuous taper reaches zero at the end. No randomness, element discovery or whole-frame shake.

`compose(main, local)` retains the main transform. `grip(prop_transform, anchor, puppet_transform)` resolves inverse endpoints after both composed transforms. Static SVG bindings wrap selected groups outside the main action; attached targets require an anchor-aware hook. The high-energy paper hook computes selected prop responses before their hand endpoints, then solves hands through the final squash/rotation matrix. Unknown targets stop rather than silently vanish. Tests derive contacts from actual canonical hand transforms, not a declared zero-error flag.
