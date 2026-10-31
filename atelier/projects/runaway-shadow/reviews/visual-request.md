# Visual review request: runaway-shadow

You are an independent reviewer for a short vertical film made in Motif Atelier. You did not make it. Judge only the rendered evidence listed here against the stated intent: do not read the project source, builder notes or earlier reviews. Be specific and critical; a polite PASS on weak work defeats the purpose. For every dimension give PASS, FAIL or NOT_ASSESSED with a one-sentence note citing times or frames. Use NOT_ASSESSED whenever the evidence cannot establish the dimension (for example motion smoothness between sampled frames, or how the mix sounds). NOT_APPLICABLE is allowed only for the dimensions listed under not_applicable, with that reason. List every problem that should block release as a critical issue with the smallest fix. Disclose your sampling limits. Do not reward effort, technique or a description of intentions; reward what a first-time phone viewer would see.

Write your response as JSON to `/home/user/motif/atelier/projects/runaway-shadow/reviews/visual.json`, valid against `/home/user/motif/atelier/contracts/review.schema.json`, with
`"request_sha256": "66b59d642014948389ab8ccac6e4172f904f8b980655f6aebced08a394b1f87c"` and `"role": "visual"`. Set `reviewer` honestly (kind, id, independence, playback: "ordered-frames").

## Intent
```json
{
 "idea": "A silent comedy about a character trying to catch its runaway shadow",
 "audience": "people scrolling short vertical video on a phone",
 "classification": "fictional",
 "intended_effect": "laughter at a clever, character-driven payoff",
 "premise": {
  "title": "The Copycat",
  "opening_image": "A small round creature in a long red stocking cap walks onto a meadow at sunset; its long shadow walks with it across the grass toward us.",
  "audience_hook": "Why is the shadow a beat late, and what will it do next?",
  "central_action": "The shadow peels itself off the ground, stands up as a dark twin with white eyes, blows a raspberry and runs off; the creature chases it into the long shadow of a tree, where it hides.",
  "complication": "Chasing fails: the shadow can melt into any darker shadow, and the creature's hat-net dive ends face-first in the grass while two white eyes giggle from the tree's shade.",
  "payoff": "The creature stops chasing and starts a goofy dance; the shadow cannot resist copying, slides out of hiding mid-dance, and the creature stomps on its feet to pin it back in place. Then the sun sets, every shadow vanishes, and two white eyes wink up from the dark."
 },
 "logline": "A small creature's shadow runs off at sunset; force cannot catch it, so the creature dances until the copycat shadow cannot resist copying its way back.",
 "opening_promise": "Pim walks onto a sunset meadow and stops to enjoy the view; its long shadow copies every move, one beat late.",
 "ending": "The sun sets, the meadow goes dark and the shadow vanishes with the light; Pim looks down, worried, and two white eyes open on the dark grass beside its feet and wink.",
 "style": "Flat bold cartoon: solid shapes, 7-unit dark plum outlines, no gradients on characters, a backlit sunset sky graded from violet to gold.",
 "audio_intent": {
  "narration": "none",
  "voice": null,
  "music": "original note-list score (pizzicato, marimba, celesta) synthesised in code",
  "sfx": "seeded procedural sound design placed on the picture's moment table"
 },
 "shot_plan": [
  {
   "id": "sunset",
   "purpose": "establish Pim, the meadow and a shadow that copies",
   "sees": "Pim walks in and stops to sigh at the sunset; the long shadow on the grass walks and sighs with it",
   "frames": [
    0,
    96
   ]
  },
  {
   "id": "lag",
   "purpose": "reveal the shadow has a mind of its own",
   "sees": "Pim stretches; the shadow holds the stretch after Pim stops, adds an extra flourish, then snaps innocent when Pim double-takes",
   "frames": [
    96,
    270
   ]
  },
  {
   "id": "escape",
   "purpose": "the shadow breaks free",
   "sees": "Pim leans in to squint; the shadow slides away from Pim's feet, hinges up into a dark twin with white eyes, blows a raspberry and sprints off, leaving Pim with no shadow at all",
   "frames": [
    270,
    396
   ]
  },
  {
   "id": "chase",
   "purpose": "force fails",
   "sees": "Pim chases; the twin dives flat into the tree's long shade and disappears; Pim's hat-net dive lands face-first and two white eyes giggle from the shade",
   "frames": [
    396,
    534
   ]
  },
  {
   "id": "lure",
   "purpose": "wit wins",
   "sees": "Pim gets an idea and dances in the sunlight; the shadow cannot resist copying, slides out of the shade copying the dance and creeps to Pim's feet; Pim stomps on its feet and it snaps back attached",
   "frames": [
    534,
    732
   ]
  },
  {
   "id": "nightfall",
   "purpose": "button: the shadow gets the last word",
   "sees": "the sun sinks, the light and every shadow fade, Pim looks down worried, and two white eyes open in the dark grass by its feet and wink",
   "frames": [
    732,
    888
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
- `/home/user/motif/atelier/runs/runaway-shadow/rough/8118c6a03c78/evidence-review/ordered-frames.png`: ordered frames every 15 frames (0.50s), in playback order, labelled time / frame / shot
- `/home/user/motif/atelier/runs/runaway-shadow/rough/8118c6a03c78/evidence-review/strip-double_take.png`: dense strip around moment "double_take" (frame 174, 5.80s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/runaway-shadow/rough/8118c6a03c78/evidence-review/strip-detach.png`: dense strip around moment "detach" (frame 288, 9.60s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/runaway-shadow/rough/8118c6a03c78/evidence-review/strip-stand_up.png`: dense strip around moment "stand_up" (frame 302, 10.07s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/runaway-shadow/rough/8118c6a03c78/evidence-review/strip-raspberry.png`: dense strip around moment "raspberry" (frame 325, 10.83s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/runaway-shadow/rough/8118c6a03c78/evidence-review/strip-run_off.png`: dense strip around moment "run_off" (frame 348, 11.60s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/runaway-shadow/rough/8118c6a03c78/evidence-review/strip-melt.png`: dense strip around moment "melt" (frame 422, 14.07s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/runaway-shadow/rough/8118c6a03c78/evidence-review/strip-faceplant.png`: dense strip around moment "faceplant" (frame 468, 15.60s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/runaway-shadow/rough/8118c6a03c78/evidence-review/strip-peek.png`: dense strip around moment "peek" (frame 498, 16.60s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/runaway-shadow/rough/8118c6a03c78/evidence-review/strip-idea.png`: dense strip around moment "idea" (frame 584, 19.47s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/runaway-shadow/rough/8118c6a03c78/evidence-review/strip-creep.png`: dense strip around moment "creep" (frame 626, 20.87s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/runaway-shadow/rough/8118c6a03c78/evidence-review/strip-stomp.png`: dense strip around moment "stomp" (frame 690, 23.00s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/runaway-shadow/rough/8118c6a03c78/evidence-review/strip-wink.png`: dense strip around moment "wink" (frame 835, 27.83s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/runaway-shadow/rough/8118c6a03c78/evidence-review/phone-f00048.png`: full preview frame at phone size 360x640, shot sunset midpoint (1.60s)
- `/home/user/motif/atelier/runs/runaway-shadow/rough/8118c6a03c78/evidence-review/phone-f00183.png`: full preview frame at phone size 360x640, shot lag midpoint (6.10s)
- `/home/user/motif/atelier/runs/runaway-shadow/rough/8118c6a03c78/evidence-review/phone-f00333.png`: full preview frame at phone size 360x640, shot escape midpoint (11.10s)
- `/home/user/motif/atelier/runs/runaway-shadow/rough/8118c6a03c78/evidence-review/phone-f00465.png`: full preview frame at phone size 360x640, shot chase midpoint (15.50s)
- `/home/user/motif/atelier/runs/runaway-shadow/rough/8118c6a03c78/evidence-review/phone-f00633.png`: full preview frame at phone size 360x640, shot lure midpoint (21.10s)
- `/home/user/motif/atelier/runs/runaway-shadow/rough/8118c6a03c78/evidence-review/phone-f00810.png`: full preview frame at phone size 360x640, shot nightfall midpoint (27.00s)

## Audio
```json
{
 "measured_on_preview": {
  "integrated_lufs": -14.16,
  "true_peak_dbtp": -1.87,
  "lra_lu": 7.0
 },
 "cues": [
  {
   "at": 13,
   "frame": 13,
   "time": 0.4333,
   "sound": "step"
  },
  {
   "at": 26,
   "frame": 26,
   "time": 0.8667,
   "sound": "step"
  },
  {
   "at": 39,
   "frame": 39,
   "time": 1.3,
   "sound": "step"
  },
  {
   "at": 52,
   "frame": 52,
   "time": 1.7333,
   "sound": "step"
  },
  {
   "at": 65,
   "frame": 65,
   "time": 2.1667,
   "sound": "step"
  },
  {
   "at": "sigh",
   "frame": 84,
   "time": 2.8,
   "sound": "whoosh"
  },
  {
   "at": "stretch_peak",
   "frame": 106,
   "time": 3.5333,
   "sound": "stretch"
  },
  {
   "at": "shadow_extra",
   "frame": 150,
   "time": 5.0,
   "sound": "stretch"
  },
  {
   "at": "double_take",
   "frame": 174,
   "time": 5.8,
   "sound": "boing"
  },
  {
   "at": "snap_innocent",
   "frame": 176,
   "time": 5.8667,
   "sound": "tick"
  },
  {
   "at": "arm_test",
   "frame": 213,
   "time": 7.1,
   "sound": "blip"
  },
  {
   "at": "arm_drop",
   "frame": 240,
   "time": 8.0,
   "sound": "tick"
  },
  {
   "at": "detach",
   "frame": 288,
   "time": 9.6,
   "sound": "zip"
  },
  {
   "at": "stand_up",
   "frame": 302,
   "time": 10.0667,
   "sound": "stretch"
  },
  {
   "at": "pim_recoil",
   "frame": 310,
   "time": 10.3333,
   "sound": "squeak"
  },
  {
   "at": "eyes_pop",
   "frame": 317,
   "time": 10.5667,
   "sound": "blip"
  },
  {
   "at": "raspberry",
   "frame": 325,
   "time": 10.8333,
   "sound": "raspberry"
  },
  {
   "at": "run_off",
   "frame": 348,
   "time": 11.6,
   "sound": "zip"
  },
  {
   "at": "chase_start",
   "frame": 404,
   "time": 13.4667,
   "sound": "whoosh"
  },
  {
   "at": 439,
   "frame": 439,
   "time": 14.6333,
   "sound": "step"
  },
  {
   "at": "melt",
   "frame": 422,
   "time": 14.0667,
   "sound": "whoosh"
  },
  {
   "at": "melt",
   "frame": 432,
   "time": 14.4,
   "sound": "blip"
  },
  {
   "at": "hat_dive",
   "frame": 450,
   "time": 15.0,
   "sound": "whoosh"
  },
  {
   "at": "faceplant",
   "frame": 468,
   "time": 15.6,
   "sound": "thud"
  },
  {
   "at": "peek",
   "frame": 498,
   "time": 16.6,
   "sound": "blip"
  },
  {
   "at": "peek",
   "frame": 506,
   "time": 16.8667,
   "sound": "blip"
  },
  {
   "at": "idea",
   "frame": 584,
   "time": 19.4667,
   "sound": "chime"
  },
  {
   "at": "creep",
   "frame": 626,
   "time": 20.8667,
   "sound": "hiss"
  },
  {
   "at": "side_eye",
   "frame": 645,
   "time": 21.5,
   "sound": "tick"
  },
  {
   "at": 668,
   "frame": 668,
   "time": 22.2667,
   "sound": "tick"
  },
  {
   "at": "freeze",
   "frame": 678,
   "time": 22.6,
   "sound": "tick"
  },
  {
   "at": "stomp",
   "frame": 690,
   "time": 23.0,
   "sound": "thud"
  },
  {
   "at": "stomp",
   "frame": 692,
   "time": 23.0667,
   "sound": "pop"
  },
  {
   "at": "sunset",
   "frame": 732,
   "time": 24.4,
   "sound": "chime"
  },
  {
   "at": "look_down",
   "frame": 786,
   "time": 26.2,
   "sound": "squeak"
  },
  {
   "at": "eyes_open",
   "frame": 816,
   "time": 27.2,
   "sound": "blip"
  },
  {
   "at": "jolt",
   "frame": 823,
   "time": 27.4333,
   "sound": "squeak"
  },
  {
   "at": "wink",
   "frame": 835,
   "time": 27.8333,
   "sound": "tick"
  },
  {
   "at": "hat_back",
   "frame": 597,
   "time": 19.9,
   "sound": "pop"
  },
  {
   "at": 349,
   "frame": 349,
   "time": 11.6333,
   "sound": "tick"
  },
  {
   "at": 354,
   "frame": 354,
   "time": 11.8,
   "sound": "tick"
  },
  {
   "at": 359,
   "frame": 359,
   "time": 11.9667,
   "sound": "tick"
  },
  {
   "at": 364,
   "frame": 364,
   "time": 12.1333,
   "sound": "tick"
  },
  {
   "at": 405,
   "frame": 405,
   "time": 13.5,
   "sound": "step"
  },
  {
   "at": 411,
   "frame": 411,
   "time": 13.7,
   "sound": "step"
  },
  {
   "at": 416,
   "frame": 416,
   "time": 13.8667,
   "sound": "step"
  },
  {
   "at": 422,
   "frame": 422,
   "time": 14.0667,
   "sound": "step"
  },
  {
   "at": 428,
   "frame": 428,
   "time": 14.2667,
   "sound": "step"
  },
  {
   "at": 436,
   "frame": 436,
   "time": 14.5333,
   "sound": "whoosh"
  },
  {
   "at": 514,
   "frame": 514,
   "time": 17.1333,
   "sound": "blip"
  },
  {
   "at": 518,
   "frame": 518,
   "time": 17.2667,
   "sound": "blip"
  },
  {
   "at": 521,
   "frame": 521,
   "time": 17.3667,
   "sound": "blip"
  },
  {
   "at": 524,
   "frame": 524,
   "time": 17.4667,
   "sound": "blip"
  },
  {
   "at": 528,
   "frame": 528,
   "time": 17.6,
   "sound": "blip"
  },
  {
   "at": 531,
   "frame": 531,
   "time": 17.7,
   "sound": "blip"
  },
  {
   "at": 603,
   "frame": 603,
   "time": 20.1,
   "sound": "step"
  },
  {
   "at": 609,
   "frame": 609,
   "time": 20.3,
   "sound": "step"
  },
  {
   "at": 615,
   "frame": 615,
   "time": 20.5,
   "sound": "step"
  },
  {
   "at": 705,
   "frame": 705,
   "time": 23.5,
   "sound": "tick"
  },
  {
   "at": 709,
   "frame": 709,
   "time": 23.6333,
   "sound": "tick"
  },
  {
   "at": 713,
   "frame": 713,
   "time": 23.7667,
   "sound": "tick"
  },
  {
   "at": 679,
   "frame": 679,
   "time": 22.6333,
   "sound": "squeak"
  },
  {
   "at": "wink_open",
   "frame": 870,
   "time": 29.0,
   "sound": "blip"
  }
 ],
 "note": "measurements only; no reviewer has listened"
}
```

## Narration
```json
[]
```

Limits: Ordered decoded frames and dense strips only; no moving playback and no listening. Motion between samples and the sound of the mix cannot be judged from this evidence.
