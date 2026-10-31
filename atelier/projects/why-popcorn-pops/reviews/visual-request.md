# Visual review request: why-popcorn-pops

You are an independent reviewer for a short vertical film made in Motif Atelier. You did not make it. Judge only the rendered evidence listed here against the stated intent: do not read the project source, builder notes or earlier reviews. Be specific and critical; a polite PASS on weak work defeats the purpose. For every dimension give PASS, FAIL or NOT_ASSESSED with a one-sentence note citing times or frames. Use NOT_ASSESSED whenever the evidence cannot establish the dimension (for example motion smoothness between sampled frames, or how the mix sounds). NOT_APPLICABLE is allowed only for the dimensions listed under not_applicable, with that reason. List every problem that should block release as a critical issue with the smallest fix. Disclose your sampling limits. Do not reward effort, technique or a description of intentions; reward what a first-time phone viewer would see.

Write your response as JSON to `/home/user/motif/atelier/projects/why-popcorn-pops/reviews/visual.json`, valid against `/home/user/motif/atelier/contracts/review.schema.json`, with
`"request_sha256": "ba3c0214849ceeb6d1ee105de2ef191c86be1fe83ee4213573634a160a053fb0"` and `"role": "visual"`. Set `reviewer` honestly (kind, id, independence, playback: "ordered-frames").

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
 ]
}
```

## Dimensions (all mandatory)
- `focal_hierarchy`: the thing that matters now commands attention
- `identity_continuity`: characters and objects keep identity, scale and materials
- `composition`: staging and framing are intentional for a vertical phone
- `readable_action`: meaningful actions are legible; contacts, grips, landings and releases hold up
- `motion_performance`: timing, anticipation, reactions and stillness serve the story, not busyness
- `style_coherence`: one deliberate visual language throughout
- `phone_readability`: essential meaning survives at phone size
- `technical_defects`: no glitches, popping, tearing, unintended clipping or broken frames

## Evidence (open every image)
- `/home/user/motif/atelier/runs/why-popcorn-pops/rough/5f7080a26f0e/evidence-review/ordered-frames.png`: ordered frames every 15 frames (0.50s), in playback order, labelled time / frame / shot
- `/home/user/motif/atelier/runs/why-popcorn-pops/rough/5f7080a26f0e/evidence-review/strip-cutaway.png`: dense strip around moment "cutaway" (frame 150, 5.00s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/why-popcorn-pops/rough/5f7080a26f0e/evidence-review/strip-boil.png`: dense strip around moment "boil" (frame 297, 9.90s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/why-popcorn-pops/rough/5f7080a26f0e/evidence-review/strip-pressure.png`: dense strip around moment "pressure" (frame 360, 12.00s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/why-popcorn-pops/rough/5f7080a26f0e/evidence-review/strip-leak.png`: dense strip around moment "leak" (frame 448, 14.93s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/why-popcorn-pops/rough/5f7080a26f0e/evidence-review/strip-burst.png`: dense strip around moment "burst" (frame 630, 21.00s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/why-popcorn-pops/rough/5f7080a26f0e/evidence-review/strip-foam.png`: dense strip around moment "foam" (frame 642, 21.40s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/why-popcorn-pops/rough/5f7080a26f0e/evidence-review/strip-leg.png`: dense strip around moment "leg" (frame 729, 24.30s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/why-popcorn-pops/rough/5f7080a26f0e/evidence-review/strip-jump.png`: dense strip around moment "jump" (frame 735, 24.50s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/why-popcorn-pops/rough/5f7080a26f0e/evidence-review/strip-replay_split.png`: dense strip around moment "replay_split" (frame 850, 28.33s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/why-popcorn-pops/rough/5f7080a26f0e/evidence-review/strip-replay_pop.png`: dense strip around moment "replay_pop" (frame 872, 29.07s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/why-popcorn-pops/rough/5f7080a26f0e/evidence-review/strip-kernel_lands.png`: dense strip around moment "kernel_lands" (frame 966, 32.20s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/why-popcorn-pops/rough/5f7080a26f0e/evidence-review/phone-f00053.png`: full preview frame at phone size 360x640, shot bowl midpoint (1.77s)
- `/home/user/motif/atelier/runs/why-popcorn-pops/rough/5f7080a26f0e/evidence-review/phone-f00191.png`: full preview frame at phone size 360x640, shot inside midpoint (6.37s)
- `/home/user/motif/atelier/runs/why-popcorn-pops/rough/5f7080a26f0e/evidence-review/phone-f00355.png`: full preview frame at phone size 360x640, shot steam midpoint (11.83s)
- `/home/user/motif/atelier/runs/why-popcorn-pops/rough/5f7080a26f0e/evidence-review/phone-f00490.png`: full preview frame at phone size 360x640, shot leak midpoint (16.33s)
- `/home/user/motif/atelier/runs/why-popcorn-pops/rough/5f7080a26f0e/evidence-review/phone-f00673.png`: full preview frame at phone size 360x640, shot burst midpoint (22.43s)
- `/home/user/motif/atelier/runs/why-popcorn-pops/rough/5f7080a26f0e/evidence-review/phone-f00849.png`: full preview frame at phone size 360x640, shot sound midpoint (28.30s)
- `/home/user/motif/atelier/runs/why-popcorn-pops/rough/5f7080a26f0e/evidence-review/phone-f00961.png`: full preview frame at phone size 360x640, shot answer midpoint (32.03s)

## Audio
```json
{
 "measured_on_preview": {
  "integrated_lufs": -14.1,
  "true_peak_dbtp": -1.85,
  "lra_lu": 2.2
 },
 "cues": [
  {
   "at": "wipe",
   "frame": 107,
   "time": 3.5667,
   "sound": "swish"
  },
  {
   "at": "cutaway",
   "frame": 150,
   "time": 5.0,
   "sound": "zip"
  },
  {
   "at": "water_label",
   "frame": 189,
   "time": 6.3,
   "sound": "blip"
  },
  {
   "at": "flame",
   "frame": 279,
   "time": 9.3,
   "sound": "whoosh"
  },
  {
   "at": "flame",
   "frame": 287,
   "time": 9.5667,
   "sound": "rumble"
  },
  {
   "at": "boil",
   "frame": 297,
   "time": 9.9,
   "sound": "sizzle"
  },
  {
   "at": "hundred",
   "frame": 318,
   "time": 10.6,
   "sound": "tick"
  },
  {
   "at": "crack_seen",
   "frame": 444,
   "time": 14.8,
   "sound": "tick"
  },
  {
   "at": "leak",
   "frame": 448,
   "time": 14.9333,
   "sound": "hiss"
  },
  {
   "at": "one_eighty",
   "frame": 576,
   "time": 19.2,
   "sound": "tick"
  },
  {
   "at": "burst",
   "frame": 630,
   "time": 21.0,
   "sound": "crack"
  },
  {
   "at": "burst",
   "frame": 634,
   "time": 21.1333,
   "sound": "pop"
  },
  {
   "at": "foam",
   "frame": 642,
   "time": 21.4,
   "sound": "whoosh"
  },
  {
   "at": "leg",
   "frame": 729,
   "time": 24.3,
   "sound": "thud"
  },
  {
   "at": "jump",
   "frame": 735,
   "time": 24.5,
   "sound": "whoosh"
  },
  {
   "at": "replay",
   "frame": 810,
   "time": 27.0,
   "sound": "swish"
  },
  {
   "at": "replay_pop",
   "frame": 872,
   "time": 29.0667,
   "sound": "pop"
  },
  {
   "at": "to_bowl",
   "frame": 897,
   "time": 29.9,
   "sound": "swish"
  },
  {
   "at": "flake_lands",
   "frame": 921,
   "time": 30.7,
   "sound": "step"
  },
  {
   "at": "kernel_falls",
   "frame": 930,
   "time": 31.0,
   "sound": "whoosh"
  },
  {
   "at": 940,
   "frame": 940,
   "time": 31.3333,
   "sound": "tick"
  },
  {
   "at": 949,
   "frame": 949,
   "time": 31.6333,
   "sound": "tick"
  },
  {
   "at": 957,
   "frame": 957,
   "time": 31.9,
   "sound": "tick"
  },
  {
   "at": "kernel_lands",
   "frame": 966,
   "time": 32.2,
   "sound": "tick"
  }
 ],
 "note": "measurements only; no reviewer has listened"
}
```

## Narration
```json
[
 {
  "id": "q",
  "start": 0.5,
  "end": 3.0336,
  "text": "Why do a few kernels in every bowl never pop?"
 },
 {
  "id": "inside",
  "start": 3.9,
  "end": 8.9467,
  "text": "Inside each one is a little water, about fourteen percent, sealed in a hard, shiny hull."
 },
 {
  "id": "heat",
  "start": 9.4,
  "end": 11.3542,
  "text": "Heat turns some of that water to steam."
 },
 {
  "id": "trapped",
  "start": 11.6,
  "end": 14.4654,
  "text": "In a sealed kernel it's trapped, and the pressure climbs."
 },
 {
  "id": "crack",
  "start": 14.7,
  "end": 17.9184,
  "text": "But a kernel with one tiny crack just leaks its steam away."
 },
 {
  "id": "burst",
  "start": 18.4,
  "end": 20.9808,
  "text": "At about a hundred and eighty degrees, the hull bursts,"
 },
 {
  "id": "foam",
  "start": 21.3,
  "end": 23.1103,
  "text": "and the hot starch puffs into foam."
 },
 {
  "id": "leg",
  "start": 23.5,
  "end": 26.3041,
  "text": "A leg of starch kicks the pan, and the kernel jumps."
 },
 {
  "id": "pop",
  "start": 26.8,
  "end": 29.6403,
  "text": "And the pop? Researchers think it's the steam rushing out."
 },
 {
  "id": "answer",
  "start": 30.2,
  "end": 33.3476,
  "text": "So the kernels at the bottom of the bowl? Their steam got out."
 }
]
```

Limits: Ordered decoded frames and dense strips only; no moving playback and no listening. Motion between samples and the sound of the mix cannot be judged from this evidence.
