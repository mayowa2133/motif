# Proof review request: why-popcorn-pops

You are an independent reviewer for a short vertical film made in Motif Atelier. You did not make it. Judge only the rendered evidence listed here against the stated intent: do not read the project source, builder notes or earlier reviews. Be specific and critical; a polite PASS on weak work defeats the purpose. For every dimension give PASS, FAIL or NOT_ASSESSED with a one-sentence note citing times or frames. Use NOT_ASSESSED whenever the evidence cannot establish the dimension (for example motion smoothness between sampled frames, or how the mix sounds). NOT_APPLICABLE is allowed only for the dimensions listed under not_applicable, with that reason. List every problem that should block release as a critical issue with the smallest fix. Disclose your sampling limits. Do not reward effort, technique or a description of intentions; reward what a first-time phone viewer would see.

Write your response as JSON to `/home/user/motif/atelier/projects/why-popcorn-pops/reviews/proof.json`, valid against `/home/user/motif/atelier/contracts/review.schema.json`, with
`"request_sha256": "a336956d36374c371767cab253986262b7379160f6e577365da82b73dd38927a"` and `"role": "proof"`. Set `reviewer` honestly (kind, id, independence, playback: "ordered-frames").

## Intent
```json
{
 "idea": "Explain why popcorn pops, and why a few kernels in every bowl never do, through the kernels themselves changing on screen rather than a labelled machine.",
 "audience": "curious adults and teens scrolling short vertical video",
 "classification": "factual",
 "intended_effect": "a satisfying 'oh, that's why' about the unpopped kernels at the bottom of the bowl, plus one surprising fact about the pop sound",
 "premise": {
  "title": "Two Kernels, One Crack",
  "opening_image": "The bottom of a bowl of popcorn seen in cross-section: under the fluffy heap, two hard kernels that never popped.",
  "audience_hook": "Why do a few kernels in every bowl never pop?",
  "central_action": "Two identical-looking kernels heat side by side in a pan, cut open like a diagram: water inside both turns to steam, one hull holds it until it bursts into foam and jumps, the other has a hairline crack and hisses its steam away.",
  "complication": "The kernels look the same from outside; the difference is a crack too small to notice until the steam finds it.",
  "payoff": "The flake lands in the bowl and the leaky kernel ends up at the bottom, answering the opening question; a replay of the burst shows the pop is the steam rushing out."
 },
 "logline": "Two kernels heat in one pan; the sealed one bursts into a flake and jumps, the one with a hairline crack leaks its steam and ends up at the bottom of the bowl.",
 "opening_promise": "A cross-section of a popcorn bowl reveals two hard kernels at the bottom, with the question of why they never popped.",
 "ending": "The flake drops into the bowl, the camera sinks to the bottom, and the dry cracked kernel lies there among the unpopped: their steam got out.",
 "style": "Risograph science zine: off-white paper, overprinted flat inks (blue linework, fluorescent pink, yellow) with 3-unit misregistration, halftone dot shading, paper grain; cutaway diagrams instead of characters.",
 "audio_intent": {
  "narration": "voice-over",
  "voice": "af_heart",
  "music": "original note-list score synthesised in code",
  "sfx": "seeded procedural sound design on the moment table"
 },
 "shot_plan": [
  {
   "id": "bowl",
   "purpose": "the question",
   "sees": "a cross-section bowl of popcorn; the camera sinks to two hard kernels at the bottom",
   "frames": [
    0,
    107
   ]
  },
  {
   "id": "inside",
   "purpose": "what a kernel holds",
   "sees": "two kernels in a cold pan open like a diagram: soft starch, blue water drops, a hard shiny hull that glints",
   "frames": [
    107,
    276
   ]
  },
  {
   "id": "steam",
   "purpose": "demonstrate pressure",
   "sees": "the flame lights, the thermometer passes 100 \u00b0C, water drops boil into bubbles; in the sealed kernel bubbles crowd and the hull bulges and trembles",
   "frames": [
    276,
    435
   ]
  },
  {
   "id": "leak",
   "purpose": "complicate: the crack",
   "sees": "the camera finds a hairline crack in the right kernel; steam hisses out of it in a plume, its bubbles drain away and its hull relaxes and browns",
   "frames": [
    435,
    546
   ]
  },
  {
   "id": "burst",
   "purpose": "reveal the pop",
   "sees": "the thermometer reaches 180 \u00b0C; the sealed hull splits, petals of hull fold back and white starch foam blooms out in slow motion; a leg of starch presses the pan and the kernel jumps",
   "frames": [
    546,
    801
   ]
  },
  {
   "id": "sound",
   "purpose": "the surprising fact",
   "sees": "a replay of the burst: the hull cracks silently, then the steam jet bursts out and sound rings spread from the jet",
   "frames": [
    801,
    897
   ]
  },
  {
   "id": "answer",
   "purpose": "resolve the question",
   "sees": "the flake drops into the bowl and the camera sinks to the bottom where the dry cracked kernel lies",
   "frames": [
    897,
    1026
   ]
  }
 ],
 "hardest_shot": {
  "shot": "burst",
  "why": "The burst must look like real popcorn forming (hull splitting, foam lobes blooming into a recognisable flake) and the leg-kick jump must read as a physical push on the pan; a generic white blob or a cut would lose the payoff.",
  "fallback": "Stage the burst as a cut from a straining kernel to a fully formed flake mid-air with a sound accent, and drop the leg line."
 }
}
```

## Dimensions (all mandatory)
- `action_reads`: the hardest action reads at phone size: cause, contact and result are visible
- `performance`: poses, timing and reactions sell the action (not a slide across a still)
- `feasible_look`: the representative artwork holds up at 360x640

## Evidence (open every image)
- `/home/user/motif/atelier/runs/why-popcorn-pops/proof/59c229c2f5db/evidence-proof/ordered-frames.png`: ordered frames every 2 frames (0.07s), in playback order, labelled time / frame / shot
- `/home/user/motif/atelier/runs/why-popcorn-pops/proof/59c229c2f5db/evidence-proof/strip-burst.png`: dense strip around moment "burst" (frame 630, 21.00s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/why-popcorn-pops/proof/59c229c2f5db/evidence-proof/strip-foam.png`: dense strip around moment "foam" (frame 642, 21.40s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/why-popcorn-pops/proof/59c229c2f5db/evidence-proof/strip-leg.png`: dense strip around moment "leg" (frame 729, 24.30s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/why-popcorn-pops/proof/59c229c2f5db/evidence-proof/strip-jump.png`: dense strip around moment "jump" (frame 735, 24.50s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/why-popcorn-pops/proof/59c229c2f5db/evidence-proof/phone-f00673.png`: full preview frame at phone size 360x640, shot burst midpoint (22.43s)

Limits: Ordered decoded frames and dense strips only; no moving playback and no listening. Motion between samples and the sound of the mix cannot be judged from this evidence.
