# Creative benchmark — The Little Book Workshop

**Status: completed workshop prototype approved and frozen on 2026-09-30.** One film about dividing a project into independent jobs, working on them together, then returning one assembled result.

## Approved version

[Accepted staging film](../videos/productions/little-book-workshop-staging/renders/final.mp4): **17.8 seconds, 1080 × 1920, 30 fps, 534 frames**. SHA-256: `836db38ea0dcfbddfd5fb76b5489ff9f32de4def6bdcd6b3b14bb392c504b09d`. Freeze this version; no further refinement is requested. Preserve `little-book-workshop`, `little-book-workshop-refined`, and `little-book-workshop-final` as earlier iterations.

Staging examples retained in the [existing planner](../planning/PLANNER.md):

- [Opening loose materials](../videos/productions/little-book-workshop-staging/review/project-dividing.png) make the before/after distinct while preserving the finished book's identifying shapes and colors.
- [Vertical parallel work](../videos/productions/little-book-workshop-staging/review/parallel-work.png) keeps simultaneous jobs readable in a full 360 × 640 frame. Two stations above and one below is an example, not a required layout.
- [Assembly](../videos/productions/little-book-workshop-staging/review/parts-assembling.png) gives the book and material contact priority; complete outer figures need not fit when they are no longer the subject.
- [Delivery](../videos/productions/little-book-workshop-staging/review/book-received.png) prioritizes the book and distinct receiving hands.

**Non-blocking limitation:** around **13.3–13.7 seconds**, the delivery framing moves up and then settles down before the receiving hands arrive. Record this for future transition polish: use a clean cut or one purposeful move. Do not reopen this film.

The user reviewed full phone-sized frames and independently confirmed unchanged encoded and decoded soundtrack hashes, approximately **−16.17 LUFS / −1.52 dBTP**. This approval covers the completed prototype; it does not establish subjective voice/SFX balance, the original references' entertainment level, or autonomous staging for arbitrary subjects. The accepted staging was agent-assisted, with no new live plan or narration. Individual prop metadata remains `review`; prototype acceptance does not promote the full library.

## Previous delivery (preserved)

- [Final film](../videos/productions/little-book-workshop-final/renders/final.mp4): **17.8 seconds, 1080 × 1920, 30 fps, 534 frames**.
- [Mobile export](../videos/productions/little-book-workshop-final/renders/mobile.mp4): 360 × 640.
- [Sampled picture frames](../validation/creative-benchmark/final-contact.jpg).
- [Asset contact sheet](../assets/scenes/book-workshop/contact-sheet.jpg).
- [Final storyboard](../videos/productions/little-book-workshop-final/STORYBOARD.md).

The folio opens and distributes its cover, pages and binding. Three participating Bots fold, press and unroll them in one sustained view. The three operations overlap from **5.545–6.735 seconds** (1.19 seconds). Those same SVG pieces join into the book, then move with the carrier Bot into separate receiving hands. The Bot releases before the hands withdraw. The final hold is about 0.8 seconds. Color, shape, contact and movement carry the main story; captions are secondary. There are no verdict headlines or celebration bounces.

## Reuse and additions

Reused: locked canonical Bot geometry and hand shapes; Scene 01 desk; Scene 03 wall and floor materials/support shadow; existing paper grain, palette and shadows; unchanged Motif event engine/primitives; GSAP runtime; local font; Kokoro **af_nova at .85**; three existing restrained interaction sounds. The floor material extends into a continuous plane so camera movement cannot detach the furniture from its ground.

Only five new SVG props were introduced, each with metadata and a PNG preview in [book-workshop](../assets/scenes/book-workshop/):

| Asset | Reusable behavior |
|---|---|
| Project folio kit | Separate cover/pages/binding; fold; recombine; deliver the same pieces |
| Hinged crease jig | Feed, hinge, crease, release |
| Tabletop page press | Press, align, release |
| Assembly cradle | Receive, join, release |
| Receiving hands | Receive, hold, withdraw |

Four bounded actions extend the existing compiler: `workshop.dispatch`, `workshop.work_parallel`, `workshop.assemble`, `workshop.deliver`. Typed workshop focus targets protect participants and source/destination contact. State validation rejects assembly before the jobs are worked and delivery before assembly. No replacement engine or speculative prop library was built.

## What the model did; what the agent built

The [recorded live concept](../validation/creative-benchmark/preproduction/creative-concept.json) chose the book metaphor before the new kit existed. Live Codex calls requested `gpt-5.6-sol`; the CLI does not expose a separately resolved model ID. Two live production plans supplied narration, actions, speech cues, focus and framing. The second received concrete feedback from inspection of the preserved first render. Each passed without an internal bounded replan.

**The agent authored the SVG geometry and finite choreography.** Frame inspection led to layer, grounding and grip repairs. The final export is explicitly an **agent-assisted recompile of the second accepted live plan and unchanged measured narration**, not a new autonomous model-generated film. [Picture repair record](../videos/productions/little-book-workshop-final/picture-repair.json), [final run record](../videos/productions/little-book-workshop-final/run-record.json). Both earlier rendered iterations remain intact.

## Previous delivery verification and limits

For the previous delivery, all **18 tests passed**. HyperFrames 0.8.98 reported no lint/runtime errors and all five text contrast checks passed. One layout warning concerned the crease leaf rotating about its intentional hinge rather than its center. Sampled mobile-size decoded frames were inspected; human approval was pending at that stage. Subjective listening was not assessed.

The encoded final mix measures **−16.17 LUFS / −1.52 dBTP**. Audio finishing preserves the encoded picture stream and duration. [Measurements](../videos/productions/little-book-workshop-final/verification.json). **658 preserved files remain unchanged**, including the canonical Bot, accepted assets, earlier productions and legacy producer. [Preservation check](../validation/creative-benchmark/preservation-check.json).

The materials and shallow paper layers remain coherent with Motif's established world. This tests a physical collaboration story beyond calendar/arena verdicts; it does not establish arbitrary scene generation, dependency scheduling or measured speedup. Three equal-looking jobs are an illustrative simplification. New assets remain `review`. The subsequent staging version is approved above. No commit or push was made in this closeout. Work stops here.
