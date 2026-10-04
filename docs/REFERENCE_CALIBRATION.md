# Reference Calibration v1

External creative references calibrate ambition and filmmaking grammar. Internal Motif gold calibrates brand execution. Exact scripts and independently verified source packets supply meaning and facts. External footage is never artwork, factual evidence, a template, internal gold, a rendered dependency or shipped with a film.

## Persistent private corpus

Default: `~/.local/share/motif/reference-corpus/private-seven-v1/manifest.json`. Use `MOTIF_REFERENCE_CORPUS` to select a corpus registered at another absolute path. Paths in this v1 manifest are absolute; relocation requires re-registration. Originals are copied intact and SHA verified; later runs use the preserved copies, not Downloads or attachment paths. Git excludes the corpus and per-production external evidence. Do not publish either.

One-time ingestion:

```sh
python3 scripts/motif_reference_ingest.py --sources /absolute/first.mp4 /absolute/second.mp4 /absolute/third.mp4 /absolute/fourth.mp4 /absolute/fifth.mp4 /absolute/sixth.mp4 /absolute/seventh.mp4
python3 scripts/motif_reference.py verify
```

The ingester preserves all seven before live visual indexing. Separate data-only index calls inspect ordered overview frames and measured cut candidates. A visual setup can persist through a punch-in and reset when its semantic rule changes. Boundaries/action centers are reviewed proposals with confidence, not transcript-aligned ground truth. Each setup stores position/duration, semantic center, relationship verbs, hero/environment/choreography, character role, headline/caption behavior, hierarchy, physical interaction, transition, irregularity and material observations. Audio is explicitly uninspected.

Each setup has begin/middle/payoff frames, ordered samples every seven source frames (~0.233 seconds at 30fps), and thirteen consecutive frames around its proposed action center. Labels preserve source indices/timestamps. Native extracted frames remain in the private cache. These are actual decoded images; inspecting strips does not establish playback or listening. Dense centers may need refinement when a retrieved strip misses its intended event.

## Ordinary production path

The shared live planner entry point automatically requires Reference Calibration for new quality plans with an intake brief, including message, supplied-script and news producers. Existing saved productions are not implicitly replanned or migrated. No corpus/calibration fallback exists.

1. A live semantic query derives relationship verbs from exact script/message, not topic nouns.
2. Retrieval covers 3–5 relevant setups with source diversity, plus up to two broader style examples.
3. Selected actual frames and 2–4 internal gold examples enter a separate live Reference Director call.
4. The Director returns a script-specific brief: rhythm, density/scale, interaction, performance, physical interfaces, motion hierarchy, set specificity, irregularity, effects, typography, transitions, original opportunities and antipatterns.
5. Planner receives brief, selected visual evidence, grammar, quality contracts and internal gold. It owns novel chapters/setups/worlds/heroes/actions/tokens/framing.
6. Independent structure critique adds `REFERENCE_STRUCTURE_GAP` and `REFERENCE_SCENE_IMITATION`; either failure requires replan.
7. Every setup gets a representative caption-free concept preview. Independent concept review blocks weak art direction before choreography.
8. Existing direction review follows concept PASS.
9. A real 3–5-second opening proof, with both caption modes and native ordered/dense evidence, gets independent internal review before full implementation.
10. Existing rough renderer and story critic remain; visual critic adds six comparative diagnoses mapped to existing gates. Final human viewing/listening remains required.

The news planning command returns at the concept stage for reference-conditioned runs. An authored adapter supplies the concept previews and choreography; this change does not pretend novel data automatically creates new artwork. Concept/opening commands are executable gates, and ordinary rough rendering rejects missing/stale records:

```sh
python3 scripts/motif_reference.py concept --project /absolute/production --evidence /absolute/concept-evidence.json
python3 scripts/motif_reference.py opening --project /absolute/production --evidence /absolute/opening-evidence.json
```

Evidence manifests bind plan, setup coverage, image hashes and (opening) actual video/source hashes. Director/critic records bind live invocations, prompts, schemas, selected frames, corpus manifest and policy hashes. Changed script, sources, evidence or calibration requires fresh review. A synthetic PASS file cannot replace a live invocation. Keep the frozen failed Dots rough and accepted gold untouched.

## Review rules

| Diagnosis | Existing blocking gate |
| --- | --- |
| REFERENCE_ENERGY_GAP | energy |
| REFERENCE_STAGE_RICHNESS_GAP | art |
| REFERENCE_ACTING_GAP | character-performance |
| REFERENCE_COMPOSITION_GAP | composition |
| REFERENCE_INTERACTION_GAP | physicality |
| REFERENCE_TACTILITY_GAP | art |

Every code is assessed for every shot; FAIL must also fail its owned global/shot gate and include a correction. Unassessed evidence blocks. Absent Bot permits acting NOT_APPLICABLE only. Deliberate dramatic minimalism can pass. No pixel similarity, scene-length quotas, object/particle quotas, mandatory Bot position or identical composition. Borrow relationship, timing, staging and material principles; never deliberately copy hero + environment + choreography together.

Run `python3 -m unittest discover -s tests -q` for integrity regressions and `python3 scripts/motif_reference_validate.py --project /absolute/calibrated-production` for live A–G semantic fixtures. Fixture results are separate from actual painted-film approval. The Dots rerun stops at the new moving rough and reports; it does not finish audio/art or publish.
