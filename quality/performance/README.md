# Named canonical performances

Registry: `registry.json`; executable `scripts/motif_performance.py`.

Thirteen states: talking, listening, focused, anticipating, impact-light, impact-heavy, worried, burdened, surprised, relieved, celebrating, climbing, typing. Channels adjust existing head/face, whole-pose squash, arms, canonical hand states, antennae and feet. No new paths or anatomy. Burden/release/startle/contact concepts come from v6; climbing/typing also reuse canonical poses and hands.

`render(state, seconds, contacts)` is pure and seekable. Contact bindings carry composed prop/puppet matrices and normalized or resolved local anchors. The compiler binds these to existing event/frame machinery. The high-energy paper hook composes posture and selected prop response before solving both hand endpoints. A renderer without the required hook fails explicitly.
