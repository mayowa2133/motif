# Rig: certificate

One certificate card that keeps its identity: the site's domain, its issuer, a padlock seal and a big days-left counter. Expire mode ticks the days down while the paper ages; renew mode stamps the same card, it turns fresh and the counter rolls back up. Expiry, lifetimes, automatic renewal, HTTPS, licences.

**Origin:** original Motif design, authored SVG in `scripts/motif_rigs/library5.py`. Style inputs: `docs/STYLE_BIBLE.md` and `docs/style-reference-analysis.md` only; no reference frame traced or copied.

**Tags:** certificate, expire, expires, lasts, days, renew, renews, automatic, https, ssl, tls, licence, license, deadline

**States:** idle → done

## Actions

- `run`: idle → done, 66 frames; contact `cert-contact` closes at frame 46 (distance 0, tested).

## Parameters

```json
{
  "mode": "expire",
  "domain": "yoursite.com",
  "issuer": "Let's Encrypt",
  "days_from": 90,
  "days_to": 3,
  "stamp": "RENEWED"
}
```

**Bot slot:** x 300, y 0, scale 0.24: watches the days run down, then cheers as the stamp renews the same card.

**Palettes:** renders in all 19 Motif palettes (berry, candy, citrus, cobalt, forest, lagoon, lilac, meadow, mint-coral, neon-ember, neon-teal, neon-violet, peach, plum-night, poppy, royal, sky, sunflower, sunrise); films rotate them per scene.

**Status:** draft proof; awaiting Mayowa approval (plan task 2.2).
