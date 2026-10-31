# Story review request: the-keeper

You are an independent reviewer for a short vertical film made in Motif Atelier. You did not make it. Judge only the rendered evidence listed here against the stated intent: do not read the project source, builder notes or earlier reviews. Be specific and critical; a polite PASS on weak work defeats the purpose. For every dimension give PASS, FAIL or NOT_ASSESSED with a one-sentence note citing times or frames. Use NOT_ASSESSED whenever the evidence cannot establish the dimension (for example motion smoothness between sampled frames, or how the mix sounds). NOT_APPLICABLE is allowed only for the dimensions listed under not_applicable, with that reason. List every problem that should block release as a critical issue with the smallest fix. Disclose your sampling limits. Do not reward effort, technique or a description of intentions; reward what a first-time phone viewer would see.

Write your response as JSON to `/home/user/motif/atelier/projects/the-keeper/reviews/story.json`, valid against `/home/user/motif/atelier/contracts/review.schema.json`, with
`"request_sha256": "9b0d3b689e45c6d68b82561303332241d1810bc140a77789ce0c95354a34a7be"` and `"role": "story"`. Set `reviewer` honestly (kind, id, independence, playback: "ordered-frames").

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
    1014
   ]
  }
 ]
}
```

## Dimensions (all mandatory)
- `opening_promise`: the opening establishes a promise, situation or feeling worth watching
- `progression`: each part develops or complicates it; nothing is a list item
- `payoff`: the ending delivers an intentional result that answers the opening
- `cause_before_effect`: important causes are shown before their consequences
- `clarity_normal_speed`: a first-time viewer follows it at normal speed
- `picture_sound_link`: narration/dialogue and picture tell one story (N/A only for a declared silent film)

## Evidence (open every image)
- `/home/user/motif/atelier/runs/the-keeper/rough/01d02c8be734/evidence-review/ordered-frames.png`: ordered frames every 15 frames (0.50s), in playback order, labelled time / frame / shot
- `/home/user/motif/atelier/runs/the-keeper/rough/01d02c8be734/evidence-review/strip-glint.png`: dense strip around moment "glint" (frame 264, 8.80s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/the-keeper/rough/01d02c8be734/evidence-review/strip-found.png`: dense strip around moment "found" (frame 318, 10.60s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/the-keeper/rough/01d02c8be734/evidence-review/strip-cup_drop.png`: dense strip around moment "cup_drop" (frame 372, 12.40s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/the-keeper/rough/01d02c8be734/evidence-review/strip-lightning.png`: dense strip around moment "lightning" (frame 396, 13.20s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/the-keeper/rough/01d02c8be734/evidence-review/strip-shutter.png`: dense strip around moment "shutter" (frame 450, 15.00s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/the-keeper/rough/01d02c8be734/evidence-review/strip-open.png`: dense strip around moment "open" (frame 510, 17.00s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/the-keeper/rough/01d02c8be734/evidence-review/strip-surface.png`: dense strip around moment "surface" (frame 579, 19.30s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/the-keeper/rough/01d02c8be734/evidence-review/strip-cry.png`: dense strip around moment "cry" (frame 621, 20.70s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/the-keeper/rough/01d02c8be734/evidence-review/strip-soften.png`: dense strip around moment "soften" (frame 660, 22.00s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/the-keeper/rough/01d02c8be734/evidence-review/strip-tail.png`: dense strip around moment "tail" (frame 771, 25.70s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/the-keeper/rough/01d02c8be734/evidence-review/strip-calf_go.png`: dense strip around moment "calf_go" (frame 798, 26.60s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/the-keeper/rough/01d02c8be734/evidence-review/strip-spouts.png`: dense strip around moment "spouts" (frame 930, 31.00s): every 2nd frame from -8 to +8
- `/home/user/motif/atelier/runs/the-keeper/rough/01d02c8be734/evidence-review/phone-f00114.png`: full preview frame at phone size 360x640, shot routine midpoint (3.80s)
- `/home/user/motif/atelier/runs/the-keeper/rough/01d02c8be734/evidence-review/phone-f00327.png`: full preview frame at phone size 360x640, shot sighting midpoint (10.90s)
- `/home/user/motif/atelier/runs/the-keeper/rough/01d02c8be734/evidence-review/phone-f00498.png`: full preview frame at phone size 360x640, shot choice midpoint (16.60s)
- `/home/user/motif/atelier/runs/the-keeper/rough/01d02c8be734/evidence-review/phone-f00649.png`: full preview frame at phone size 360x640, shot reveal midpoint (21.63s)
- `/home/user/motif/atelier/runs/the-keeper/rough/01d02c8be734/evidence-review/phone-f00799.png`: full preview frame at phone size 360x640, shot home midpoint (26.63s)
- `/home/user/motif/atelier/runs/the-keeper/rough/01d02c8be734/evidence-review/phone-f00942.png`: full preview frame at phone size 360x640, shot dawn midpoint (31.40s)

## Audio
```json
{
 "measured_on_preview": {
  "integrated_lufs": -14.31,
  "true_peak_dbtp": -1.86,
  "lra_lu": 10.0
 },
 "cues": [
  {
   "at": 0,
   "frame": 0,
   "time": 0.0,
   "sound": "rain"
  },
  {
   "at": 12,
   "frame": 12,
   "time": 0.4,
   "sound": "wave"
  },
  {
   "at": 114,
   "frame": 114,
   "time": 3.8,
   "sound": "wave"
  },
  {
   "at": 216,
   "frame": 216,
   "time": 7.2,
   "sound": "wave"
  },
  {
   "at": 318,
   "frame": 318,
   "time": 10.6,
   "sound": "wave"
  },
  {
   "at": 420,
   "frame": 420,
   "time": 14.0,
   "sound": "wave"
  },
  {
   "at": 522,
   "frame": 522,
   "time": 17.4,
   "sound": "wave"
  },
  {
   "at": 624,
   "frame": 624,
   "time": 20.8,
   "sound": "wave"
  },
  {
   "at": 726,
   "frame": 726,
   "time": 24.2,
   "sound": "wave"
  },
  {
   "at": 828,
   "frame": 828,
   "time": 27.6,
   "sound": "wave"
  },
  {
   "at": "flash1",
   "frame": 54,
   "time": 1.8,
   "sound": "thunder"
  },
  {
   "at": 96,
   "frame": 96,
   "time": 3.2,
   "sound": "creak"
  },
  {
   "at": 118,
   "frame": 118,
   "time": 3.9333,
   "sound": "creak"
  },
  {
   "at": 141,
   "frame": 141,
   "time": 4.7,
   "sound": "creak"
  },
  {
   "at": "glint",
   "frame": 264,
   "time": 8.8,
   "sound": "chime"
  },
  {
   "at": "glint",
   "frame": 268,
   "time": 8.9333,
   "sound": "rumble"
  },
  {
   "at": "stop_lamp",
   "frame": 273,
   "time": 9.1,
   "sound": "creak"
  },
  {
   "at": "beat1",
   "frame": 327,
   "time": 10.9,
   "sound": "thud"
  },
  {
   "at": "beat2",
   "frame": 345,
   "time": 11.5,
   "sound": "thud"
  },
  {
   "at": "beat3",
   "frame": 362,
   "time": 12.0667,
   "sound": "thud"
  },
  {
   "at": "cup_land",
   "frame": 379,
   "time": 12.6333,
   "sound": "chime"
  },
  {
   "at": "cup_land",
   "frame": 379,
   "time": 12.6333,
   "sound": "tick"
  },
  {
   "at": "lightning",
   "frame": 396,
   "time": 13.2,
   "sound": "thunder"
  },
  {
   "at": "shutter",
   "frame": 450,
   "time": 15.0,
   "sound": "creak"
  },
  {
   "at": "moan",
   "frame": 468,
   "time": 15.6,
   "sound": "whale"
  },
  {
   "at": "open",
   "frame": 510,
   "time": 17.0,
   "sound": "whoosh"
  },
  {
   "at": "open",
   "frame": 510,
   "time": 17.0,
   "sound": "chime"
  },
  {
   "at": "surface",
   "frame": 579,
   "time": 19.3,
   "sound": "wave"
  },
  {
   "at": "spout",
   "frame": 612,
   "time": 20.4,
   "sound": "hiss"
  },
  {
   "at": "cry",
   "frame": 621,
   "time": 20.7,
   "sound": "whale"
  },
  {
   "at": "swing_out",
   "frame": 735,
   "time": 24.5,
   "sound": "swish"
  },
  {
   "at": "answer",
   "frame": 786,
   "time": 26.2,
   "sound": "whale"
  },
  {
   "at": "calf_spout",
   "frame": 828,
   "time": 27.6,
   "sound": "hiss"
  },
  {
   "at": "tail_down",
   "frame": 849,
   "time": 28.3,
   "sound": "wave"
  },
  {
   "at": "lamp_off",
   "frame": 946,
   "time": 31.5333,
   "sound": "tick"
  },
  {
   "at": 948,
   "frame": 948,
   "time": 31.6,
   "sound": "squeak"
  },
  {
   "at": 959,
   "frame": 959,
   "time": 31.9667,
   "sound": "squeak"
  }
 ],
 "note": "measurements only; no reviewer has listened"
}
```

## Narration
```json
[
 {
  "id": "ritual",
  "start": 1.0,
  "end": 3.2372,
  "text": "Every night, Ada kept the light turning."
 },
 {
  "id": "empty",
  "start": 4.9,
  "end": 7.0369,
  "text": "And every night, the sea stayed empty."
 },
 {
  "id": "tonight",
  "start": 8.1,
  "end": 9.2442,
  "text": "Until tonight."
 },
 {
  "id": "monster",
  "start": 21.0,
  "end": 22.386,
  "text": "It wasn't a monster."
 },
 {
  "id": "lost",
  "start": 22.7,
  "end": 23.6896,
  "text": "It was lost."
 },
 {
  "id": "light",
  "start": 24.2,
  "end": 26.2317,
  "text": "So Ada did what the light was for."
 },
 {
  "id": "never",
  "start": 30.5,
  "end": 32.3426,
  "text": "The sea had never been empty."
 }
]
```

Limits: Ordered decoded frames and dense strips only; no moving playback and no listening. Motion between samples and the sound of the mix cannot be judged from this evidence.
