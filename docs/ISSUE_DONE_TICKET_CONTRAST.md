# Component issue — DONE ticket contrast

Status: **recorded for a versioned component update; Demo 01 stays frozen**.

The approved `notification-card.svg` uses coral `#DF806B` for the stamped DONE text against cream paper. HyperFrames reports a **2.38:1** contrast ratio at the night and morning appearances, below its 3:1 large-text target. The same SVG component appears twice in Demo 01, producing two warnings.

Proposed small fix for `notification-card` **v1.1**: darken the DONE stamp text and border to at least the tool's suggested `#C5715E`, verify the rendered contrast and visual fit, then make future compositions opt into v1.1. Preserve the canonical v1 SVG and approved Demo 01 export. No broader color or art-direction change is needed.

Source component SHA-256 at issue creation: `3754edc9240e34a8161fb05ecd5b6d8211d924cf10f41e52b629467d836adc3a`.
