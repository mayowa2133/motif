# Rig: receipt-stack

Receipts drop onto a growing pile with a running count. Bills, subscriptions, hidden costs.

**Origin:** original Motif design, authored SVG in `scripts/motif_rigs/library.py`. Style inputs: `docs/STYLE_BIBLE.md` and `docs/style-reference-analysis.md` only; no reference frame traced or copied.

**Tags:** cost, bills, subscription, expense, invoice, pile

**States:** few → pile

## Actions

- `pile`: few → pile, 54 frames; contact `top-slip` closes at frame 42 (distance 0, tested).

## Parameters

```json
{
  "from": 2,
  "to": 14,
  "amount": "$20",
  "label": "BILLS"
}
```

**Bot slot:** x 250, y 0, scale 0.24: buried or reading the top slip.

**Palettes:** renders in all 19 Motif palettes (berry, candy, citrus, cobalt, forest, lagoon, lilac, meadow, mint-coral, neon-ember, neon-teal, neon-violet, peach, plum-night, poppy, royal, sky, sunflower, sunrise); films rotate them per scene.

**Status:** draft proof; awaiting Mayowa approval (plan task 2.2).
