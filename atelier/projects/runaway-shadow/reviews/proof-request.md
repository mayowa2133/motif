# Proof review request: runaway-shadow

You are an independent reviewer for a short vertical film made in Motif Atelier. You did not make it. Judge only the rendered evidence listed here against the stated intent: do not read the project source, builder notes or earlier reviews. Be specific and critical; a polite PASS on weak work defeats the purpose. For every dimension give PASS, FAIL or NOT_ASSESSED with a one-sentence note citing times or frames. Use NOT_ASSESSED whenever the evidence cannot establish the dimension (for example motion smoothness between sampled frames, or how the mix sounds). NOT_APPLICABLE is allowed only for the dimensions listed under not_applicable, with that reason. List every problem that should block release as a critical issue with the smallest fix. Disclose your sampling limits. Do not reward effort, technique or a description of intentions; reward what a first-time phone viewer would see.

Write your response as JSON to `/home/user/motif/atelier/projects/runaway-shadow/reviews/proof.json`, valid against `/home/user/motif/atelier/contracts/review.schema.json`, with
`"request_sha256": "d7fff4961b8ff8806e985948aad3dfc5c3f40fab3e03116555089dafb1247cc0"` and `"role": "proof"`. Set `reviewer` honestly (kind, id, independence, playback: "ordered-frames").

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
 "logline": "A small creature's shadow runs off at sunset; three stomps can't pin it down, so the creature dances until the copycat shadow copies its way under its feet for the fourth.",
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
   "purpose": "force fails, and plants the stomp",
   "sees": "the twin drops flat on the grass; Pim stomps at it three times and it slides away each time, the third time into the tree's long shade where it vanishes; two white eyes giggle from the shade while Pim hops on a sore foot",
   "frames": [
    396,
    534
   ]
  },
  {
   "id": "lure",
   "purpose": "wit wins",
   "sees": "Pim gets an idea and dances in the sunlight; the shadow cannot resist copying, slides out of the shade copying the dance and creeps under Pim's feet; the fourth stomp lands and it snaps back attached",
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
 ],
 "hardest_shot": {
  "shot": "escape",
  "why": "The shadow must read as Pim's own projection, then visibly detach, hinge up into a standing twin and run, while Pim's feet are left without a shadow; if the detach or the stand-up reads as a sticker swap the premise fails.",
  "fallback": "Stage the escape as the flat shadow sliding away along the grass without standing up, and keep the dark twin for the chase only."
 }
}
```

## Dimensions (all mandatory)
- `action_reads`: the hardest action reads at phone size: cause, contact and result are visible
- `performance`: poses, timing and reactions sell the action (not a slide across a still)
- `feasible_look`: the representative artwork holds up at 360x640

## Evidence (open every image)
- `/home/user/motif/atelier/runs/runaway-shadow/proof/cdeae8e22838/evidence-proof/ordered-frames.png`: ordered frames every 2 frames (0.07s), in playback order, labelled time / frame / shot
- `/home/user/motif/atelier/runs/runaway-shadow/proof/cdeae8e22838/evidence-proof/strip-detach.png`: dense strip around moment "detach" (frame 288, 9.60s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/runaway-shadow/proof/cdeae8e22838/evidence-proof/strip-stand_up.png`: dense strip around moment "stand_up" (frame 302, 10.07s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/runaway-shadow/proof/cdeae8e22838/evidence-proof/strip-raspberry.png`: dense strip around moment "raspberry" (frame 325, 10.83s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/runaway-shadow/proof/cdeae8e22838/evidence-proof/strip-run_off.png`: dense strip around moment "run_off" (frame 348, 11.60s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/runaway-shadow/proof/cdeae8e22838/evidence-proof/phone-f00333.png`: full preview frame at phone size 360x640, shot escape midpoint (11.10s)

Limits: Ordered decoded frames and dense strips only; no moving playback and no listening. Motion between samples and the sound of the mix cannot be judged from this evidence.
