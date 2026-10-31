# Proof review request: the-keeper

You are an independent reviewer for a short vertical film made in Motif Atelier. You did not make it. Judge only the rendered evidence listed here against the stated intent: do not read the project source, builder notes or earlier reviews. Be specific and critical; a polite PASS on weak work defeats the purpose. For every dimension give PASS, FAIL or NOT_ASSESSED with a one-sentence note citing times or frames. Use NOT_ASSESSED whenever the evidence cannot establish the dimension (for example motion smoothness between sampled frames, or how the mix sounds). NOT_APPLICABLE is allowed only for the dimensions listed under not_applicable, with that reason. List every problem that should block release as a critical issue with the smallest fix. Disclose your sampling limits. Do not reward effort, technique or a description of intentions; reward what a first-time phone viewer would see.

Write your response as JSON to `/home/user/motif/atelier/projects/the-keeper/reviews/proof.json`, valid against `/home/user/motif/atelier/contracts/review.schema.json`, with
`"request_sha256": "b4ad10d928bd466943ea89937e46e829b698ce42e54c05457f80feb8b6a69c74"` and `"role": "proof"`. Set `reviewer` honestly (kind, id, independence, playback: "ordered-frames").

## Intent
```json
{
 "idea": "A short fictional suspense story with a genuine reveal: a lighthouse keeper in a storm sees a huge dark shape closing on the rock, and has to choose whether to hide the light",
 "audience": "people scrolling short vertical video on a phone",
 "classification": "fictional",
 "intended_effect": "suspense that turns into tenderness at the reveal",
 "premise": {
  "title": "The Keeper",
  "opening_image": "A lighthouse on a black rock in a storm, its beam sweeping an empty sea; a small keeper in a yellow oilskin turns the lamp by hand.",
  "audience_hook": "What is the huge dark shape the beam just caught under the waves, and will she hide the light?",
  "central_action": "The keeper tracks a giant shape with a glinting eye as it closes on the rock, starts to shutter the lamp to hide, hears it moan, and instead turns the full beam onto it.",
  "complication": "Every clue (the swell, the size of its shadow in the lightning, the moan) says monster, and hiding is the safe choice.",
  "payoff": "A whale calf surfaces in the beam, small and crying; she swings the light out to sea, a vast tail rises where it ends, and the calf swims home. At dawn two spouts rise from a sea that was never empty."
 },
 "logline": "A lighthouse keeper spots a giant shape closing on her rock in a storm, chooses to shine the light instead of hiding it, and finds a lost whale calf she guides home.",
 "opening_promise": "A storm, a lighthouse and a keeper whose nightly routine is turning the light over a sea that is always empty.",
 "ending": "Dawn over a calm sea: the lamp goes dark for the day, Ada waves from the gallery, and two spouts, one big and one small, rise on the horizon. 'The sea had never been empty.'",
 "style": "Painterly chiaroscuro night: deep teal and navy shapes, soft gradients, a warm additive beam as the only strong light, lightning flashes, rain, film grain and vignette; dawn turns the same shapes peach and blue.",
 "audio_intent": {
  "narration": "voice-over",
  "voice": "bf_emma",
  "music": "sparse original pad and celesta notes synthesised in code",
  "sfx": "seeded procedural storm, surf, drone, cup, whale calls"
 },
 "shot_plan": [
  {
   "id": "routine",
   "purpose": "establish the ritual and the empty sea",
   "sees": "the storm and the sweeping beam, Ada cranking the lamp with tea at hand, the beam passing over empty water",
   "frames": [
    0,
    228
   ]
  },
  {
   "id": "sighting",
   "purpose": "the threat appears",
   "sees": "the beam crosses a huge dark mass under the waves and an eye glints; Ada stops the lamp, swings back and finds it closer; she drops her cup; lightning shows its shadow under the swell beside the rock",
   "frames": [
    228,
    426
   ]
  },
  {
   "id": "choice",
   "purpose": "the decision",
   "sees": "Ada reaches for the shutter lever and the light starts to dim; a moan rises from the sea; she stops, sets her jaw, throws the shutter open and steers the full beam down onto the shape",
   "frames": [
    426,
    570
   ]
  },
  {
   "id": "reveal",
   "purpose": "the reveal",
   "sees": "in the beam a small whale calf surfaces, blinks, spouts and cries; Ada's face softens, hand on heart",
   "frames": [
    570,
    729
   ]
  },
  {
   "id": "home",
   "purpose": "use the light",
   "sees": "Ada lays the beam across the sea; far out where it ends a vast tail rises and answers; the calf turns and swims along the beam toward it",
   "frames": [
    729,
    870
   ]
  },
  {
   "id": "dawn",
   "purpose": "release",
   "sees": "rain stops, the sky turns to dawn, the lamp goes dark, two spouts rise on the horizon and Ada waves",
   "frames": [
    870,
    990
   ]
  }
 ],
 "hardest_shot": {
  "shot": "reveal",
  "why": "The surfacing must flip the audience's read in one move: the same shape that read as a giant has to become a small, sympathetic calf with a readable face at phone size, lit only by the beam; if it reads as a generic blob or still looks threatening, the story fails.",
  "fallback": "Reveal the calf in a closer framing with a cut instead of one continuous surfacing, and let its cry carry the change."
 }
}
```

## Dimensions (all mandatory)
- `action_reads`: the hardest action reads at phone size: cause, contact and result are visible
- `performance`: poses, timing and reactions sell the action (not a slide across a still)
- `feasible_look`: the representative artwork holds up at 360x640

## Evidence (open every image)
- `/home/user/motif/atelier/runs/the-keeper/proof/df8c54770acb/evidence-proof/ordered-frames.png`: ordered frames every 2 frames (0.07s), in playback order, labelled time / frame / shot
- `/home/user/motif/atelier/runs/the-keeper/proof/df8c54770acb/evidence-proof/strip-surface.png`: dense strip around moment "surface" (frame 579, 19.30s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/the-keeper/proof/df8c54770acb/evidence-proof/strip-cry.png`: dense strip around moment "cry" (frame 621, 20.70s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/the-keeper/proof/df8c54770acb/evidence-proof/strip-soften.png`: dense strip around moment "soften" (frame 660, 22.00s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/the-keeper/proof/df8c54770acb/evidence-proof/phone-f00564.png`: full preview frame at phone size 360x640, shot choice midpoint (18.80s)
- `/home/user/motif/atelier/runs/the-keeper/proof/df8c54770acb/evidence-proof/phone-f00649.png`: full preview frame at phone size 360x640, shot reveal midpoint (21.63s)

Limits: Ordered decoded frames and dense strips only; no moving playback and no listening. Motion between samples and the sound of the mix cannot be judged from this evidence.
