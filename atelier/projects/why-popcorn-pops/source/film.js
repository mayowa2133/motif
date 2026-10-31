// Why Popcorn Pops (Motif Atelier pilot A): a risograph science short.
// Three inks (blue line, fluorescent pink, yellow) multiply on paper; blue linework
// prints slightly off register; halftone dots shade. The two kernels are the story:
// sealed (left) and cracked (right). Times are seconds on the film's clock.
(function () {
  'use strict';
  const PAPER = '#ECE3D1', BLUE = '#1F4FA8', PINK = '#FF4F9A', YEL = '#FFC93C', ORANGE = '#FF7A2F', STARCH = '#FFF6E4';
  const MIS = [4, 3];
  let A = null, pats = {}, grain = null, heap = [], drops = [], flakeLobes = [], bowlKernels = [];
  const K1 = { x: 450, y: 1258 }, K2 = { x: 770, y: 1258 }, KH = 300, KW = 236, PAN_Y = 1262;
  const BURST = 21.0;

  // ---------- helpers ----------
  function kf(t, keys) {
    if (t <= keys[0][0]) return keys[0][1];
    for (let i = 1; i < keys.length; i++) {
      const [t1, v1, e] = keys[i];
      if (t <= t1) { const [t0, v0] = keys[i - 1]; return v0 + (v1 - v0) * A.ease[e || 'inOutSine']((t - t0) / (t1 - t0)); }
    }
    return keys[keys.length - 1][1];
  }
  const seg = (t, a, b) => A.seg(t, a, b);
  function ink(ctx, path, fill, line = BLUE, width = 6) {          // fill on paper, then the blue plate off register
    ctx.save(); ctx.globalCompositeOperation = 'multiply';
    if (fill) { path(); ctx.fillStyle = fill; ctx.fill(); }
    if (line) { ctx.translate(MIS[0], MIS[1]); path(); ctx.strokeStyle = line; ctx.lineWidth = width; ctx.lineJoin = 'round'; ctx.lineCap = 'round'; ctx.stroke(); }
    ctx.restore();
  }
  function dots(ctx, path, which, alpha = 1) {
    ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.globalAlpha = alpha; path(); ctx.fillStyle = pats[which]; ctx.fill(); ctx.restore();
  }
  function label(ctx, text, x, y, size, color = BLUE, align = 'left') {
    ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.font = `900 ${size}px Inter`; ctx.textAlign = align; ctx.textBaseline = 'middle';
    ctx.fillStyle = color; ctx.fillText(text, x, y); ctx.restore();
  }

  // ---------- kernel ----------
  function kernelPath(ctx, w = KW, h = KH) {
    ctx.beginPath(); ctx.moveTo(0, 0);
    ctx.bezierCurveTo(w * 0.42, -h * 0.08, w * 0.62, -h * 0.62, w * 0.36, -h * 0.9);
    ctx.bezierCurveTo(w * 0.2, -h * 1.04, -w * 0.2, -h * 1.04, -w * 0.36, -h * 0.9);
    ctx.bezierCurveTo(-w * 0.62, -h * 0.62, -w * 0.42, -h * 0.08, 0, 0); ctx.closePath();
  }
  function crackPath(ctx) {                         // on the inner (left) shoulder of the cracked kernel
    ctx.beginPath(); ctx.moveTo(-KW * 0.3, -KH * 0.8); ctx.lineTo(-KW * 0.22, -KH * 0.72); ctx.lineTo(-KW * 0.3, -KH * 0.66); ctx.lineTo(-KW * 0.21, -KH * 0.57);
  }
  // state of each kernel at time t
  function kstate(t, which) {
    const sealed = which === 1;
    const heat = seg(t, 9.6, 12.0);
    const p = sealed ? 0.25 * A.ease.outQuad(seg(t, 10.6, 13.0)) + 0.75 * seg(t, 11.0, BURST) : kf(t, [[10.6, 0], [13.6, 0.45], [15.6, 0.45], [17.4, 0, 'outQuad']]);
    return { sealed, cut: A.ease.inOutCubic(seg(t, 5.0, 6.4)), heat, p, brown: sealed ? 0 : seg(t, 15.5, 18.5), leaking: !sealed && t > 14.9 && t < 17.8,
      crackSeen: !sealed ? seg(t, 14.75, 15.1) : 0 };
  }

  function drawKernel(ctx, t, K, s, tt) {        // tt: time used for bubbles (lets the replay re-run them)
    const { x, y } = K;
    ctx.save(); ctx.translate(x, y);
    const tremble = s.sealed ? Math.sin(tt * 61) * 0.04 * s.p * s.p : 0;
    ctx.rotate((s.sealed ? -0.06 : 0.07) + tremble);
    ctx.scale(1 + 0.13 * s.p, 1 + 0.08 * s.p);
    // hull exterior: golden, shiny
    ink(ctx, () => kernelPath(ctx), s.brown ? mixc(YEL, '#D9922E', s.brown) : YEL, BLUE, 7);
    dots(ctx, () => { kernelPath(ctx); }, 'orange', 0.35 + 0.25 * s.brown);
    ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.fillStyle = 'rgba(255,255,255,0.75)';
    ctx.beginPath(); ctx.ellipse(-KW * 0.18, -KH * 0.72, 18, 42, -0.4, 0, Math.PI * 2); ctx.fill(); ctx.restore();
    if (s.cut > 0) {                          // cutaway: the front of the hull wipes away to show the inside
      ctx.save(); kernelPath(ctx); ctx.clip();
      ctx.beginPath(); ctx.rect(-KW, -KH * 1.1, KW * 2, KH * 1.2 * s.cut); ctx.clip();
      ctx.save(); ctx.scale(0.86, 0.9); ctx.translate(0, -KH * 0.03);
      ink(ctx, () => kernelPath(ctx), s.brown ? mixc(STARCH, '#F2C98F', s.brown) : STARCH, null);
      dots(ctx, () => kernelPath(ctx), 'yellow', 0.55);
      ctx.beginPath(); ctx.ellipse(0, -KH * 0.12, KW * 0.14, KH * 0.13, 0, 0, Math.PI * 2); ctx.fillStyle = PINK; ctx.globalCompositeOperation = 'multiply'; ctx.globalAlpha = 0.75; ctx.fill();
      ctx.restore();
      if (s.p > 0) dots(ctx, () => { ctx.save(); ctx.scale(0.86, 0.9); kernelPath(ctx); ctx.restore(); }, 'pink', 0.7 * s.p);
      bubbles(ctx, tt, s);
      ctx.restore();
      ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.translate(MIS[0], MIS[1]); ctx.beginPath(); ctx.moveTo(-KW * 0.6, -KH * 1.1 + KH * 1.2 * s.cut); ctx.lineTo(KW * 0.6, -KH * 1.1 + KH * 1.2 * s.cut);
      ctx.restore();
      ink(ctx, () => kernelPath(ctx), null, BLUE, 7);
    }
    if (!s.sealed && s.crackSeen > 0) {
      ctx.save(); ctx.globalCompositeOperation = 'multiply'; crackPath(ctx); ctx.strokeStyle = BLUE; ctx.lineWidth = 5 + 3 * s.crackSeen; ctx.lineJoin = 'miter'; ctx.stroke(); ctx.restore();
    }
    ctx.restore();
  }

  function bubbles(ctx, tt, s) {                 // water drops boil into steam that merges into one white mass
    const steam = [];
    for (const d of drops) {
      const b = A.ease.outQuad(seg(tt, 9.7 + d.delay, 10.9 + d.delay));
      let x = d.x * KW, y = d.y * KH;
      if (s.sealed) {
        const crowd = s.p;
        x += Math.sin(tt * (5 + d.w) + d.ph) * 6 * b + (0 - x) * 0.2 * crowd; y += Math.cos(tt * (4 + d.w) + d.ph) * 6 * b - 12 * crowd;
        if (b <= 0.02) { drop(ctx, x, y); continue; }
        steam.push([x, y, 12 + 14 * b + 34 * crowd]);
        if (crowd > 0.35) steam.push([x + 24 * Math.cos(d.ph), y + 20 * Math.sin(d.ph), 10 + 30 * crowd]);
      } else {
        const out = seg(tt, 14.9 + d.delay * 0.8, 16.4 + d.delay * 0.8);
        if (out >= 1) continue;
        const cx = -KW * 0.27, cy = -KH * 0.7;
        x += (cx - x) * A.ease.inQuad(out) + Math.sin(tt * (5 + d.w) + d.ph) * 5 * b; y += (cy - y) * A.ease.inQuad(out);
        if (b <= 0.02) { drop(ctx, x, y); continue; }
        steam.push([x, y, (12 + 14 * b + 16 * s.p) * (1 - 0.7 * out)]);
      }
    }
    if (!steam.length) return;
    ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.translate(MIS[0], MIS[1]); ctx.beginPath();
    for (const [x, y, r] of steam) { ctx.moveTo(x + r + 4, y); ctx.arc(x, y, r + 4, 0, Math.PI * 2); }
    ctx.fillStyle = BLUE; ctx.fill(); ctx.restore();
    ctx.beginPath(); for (const [x, y, r] of steam) { ctx.moveTo(x + r, y); ctx.arc(x, y, r, 0, Math.PI * 2); }
    ctx.fillStyle = '#FFFFFF'; ctx.fill();
    ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.strokeStyle = 'rgba(31,79,168,0.35)'; ctx.lineWidth = 3;
    for (const [x, y, r] of steam) { ctx.beginPath(); ctx.arc(x - r * 0.2, y - r * 0.2, r * 0.55, 3.6, 4.6); ctx.stroke(); }
    ctx.restore();
  }
  function circle(ctx, x, y, r, fill, line) {
    ink(ctx, () => { ctx.beginPath(); ctx.arc(x, y, Math.max(0.5, r), 0, Math.PI * 2); }, fill, line ? BLUE : null, 3);
  }
  function drop(ctx, x, y) {                        // a water drop: blue ink with a paper highlight
    const dp = () => { ctx.beginPath(); ctx.moveTo(x, y - 30); ctx.quadraticCurveTo(x + 22, y - 2, x, y + 15); ctx.quadraticCurveTo(x - 22, y - 2, x, y - 30); };
    dp(); ctx.fillStyle = '#3F8BF0'; ctx.fill(); ink(ctx, dp, null, BLUE, 3);
    ctx.save(); ctx.fillStyle = 'rgba(255,255,255,0.9)'; ctx.beginPath(); ctx.arc(x - 5, y - 4, 5, 0, Math.PI * 2); ctx.fill(); ctx.restore();
  }
  function mixc(c1, c2, u) {
    const p = (c) => [1, 3, 5].map((i) => parseInt(c.substr(i, 2), 16)), a = p(c1), b = p(c2);
    return 'rgb(' + a.map((v, i) => Math.round(v + (b[i] - v) * u)).join(',') + ')';
  }

  // ---------- steam outside the cracked kernel ----------
  function plume(ctx, t) {
    if (t < 14.9 || t > 18.6) return;
    const r = A.rng(31), fade = 1 - seg(t, 17.6, 18.6);
    for (let i = 0; i < 26; i++) {
      const born = 14.9 + r() * 2.7, age = t - born; if (age < 0 || age > 1.6) continue;
      const u = age / 1.6, sx = K2.x - KW * 0.3, sy = K2.y - KH * 0.72;
      const x = sx - 30 * u + Math.sin(u * 5 + i) * 30 * u - 40 * u * u, y = sy - 330 * u;
      ctx.save(); ctx.globalAlpha = Math.min(1, 1.5 * (1 - u)) * fade;
      const pf = () => { ctx.beginPath(); ctx.arc(x, y, 18 + 46 * u, 0, Math.PI * 2); }; pf(); ctx.fillStyle = '#FFFFFF'; ctx.fill(); ink(ctx, pf, null, BLUE, 5); ctx.restore();
    }
  }

  // ---------- popcorn flake (foam lobes) ----------
  function halves(ctx, open, front) {               // the hero kernel's hull splits in two and folds back about its tip
    if ((open < 0.5) !== front) return;
    for (const side of [-1, 1]) {
      const path = () => { ctx.beginPath(); ctx.moveTo(0, 135); ctx.bezierCurveTo(side * KW * 0.42, 135 - KH * 0.08, side * KW * 0.62, 135 - KH * 0.62, side * KW * 0.36, 135 - KH * 0.9);
        ctx.bezierCurveTo(side * KW * 0.2, 135 - KH * 1.04, side * 6, 135 - KH * 1.0, side * 6, 135 - KH * 0.97); ctx.lineTo(side * 4, 120); ctx.closePath(); };
      const bulge = 1 - A.ease.outQuad(Math.min(1, open * 2));
      ctx.save(); ctx.translate(0, 135); ctx.rotate(side * 0.95 * A.ease.outCubic(open) - 0.06 * bulge); const k = 1 - 0.35 * open; ctx.scale(k * (1 + 0.13 * bulge), k * (1 + 0.08 * bulge)); ctx.translate(0, -135);
      ink(ctx, path, YEL, BLUE, 7); dots(ctx, path, 'orange', 0.4);
      ctx.save(); path(); ctx.clip(); ctx.translate(0, 135); ctx.scale(0.86, 0.9); ctx.translate(0, -KH * 0.03);   // the cut face: trapped steam and the germ
      kernelPath(ctx); ctx.fillStyle = '#FFFFFF'; ctx.fill();
      ctx.beginPath(); ctx.ellipse(0, -KH * 0.12, KW * 0.14, KH * 0.13, 0, 0, Math.PI * 2); ctx.fillStyle = PINK; ctx.globalCompositeOperation = 'multiply'; ctx.globalAlpha = 0.75; ctx.fill(); ctx.restore();
      ink(ctx, path, null, BLUE, 7); ctx.restore();
    }
  }
  function flake(ctx, lobes, bloom, scale = 1, hullOpen = 1, seed = 0, leg = 0, hero = false) {
    ctx.save(); ctx.scale(scale, scale);
    const live = lobes.map((l) => { const g = l.core ? 0.95 + 0.2 * A.ease.outBack(seg(bloom, 0, 0.4)) : A.ease.outBack(seg(bloom, l.delay, l.delay + 0.45)); return { x: Math.cos(l.a) * l.d * g, y: Math.sin(l.a) * l.d * g, r: l.r * g }; }).filter((l) => l.r > 0.5);
    if (leg > 0) live.push({ x: -10, y: 70 + 55 * leg, r: 42 * leg, leg: true });
    if (hero) halves(ctx, hullOpen, false);
    else if (hullOpen > 0) for (const side of [-1, 1]) {   // small hull petals left at the base
      ctx.save(); ctx.rotate(side * (0.3 + 1.6 * hullOpen)); ink(ctx, () => { ctx.beginPath(); ctx.moveTo(0, 30); ctx.quadraticCurveTo(side * 85, -10, side * 60, -110); ctx.quadraticCurveTo(side * 20, -60, 0, 30); }, YEL, BLUE, 6);
      dots(ctx, () => { ctx.beginPath(); ctx.moveTo(0, 30); ctx.quadraticCurveTo(side * 85, -10, side * 60, -110); ctx.quadraticCurveTo(side * 20, -60, 0, 30); }, 'orange', 0.5); ctx.restore();
    }
    ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.translate(MIS[0], MIS[1]);
    for (const l of live) { ctx.beginPath(); ctx.arc(l.x, l.y, l.r + 4, 0, Math.PI * 2); ctx.fillStyle = BLUE; ctx.fill(); }
    ctx.restore();
    ctx.beginPath(); for (const l of live) { ctx.moveTo(l.x + l.r, l.y); ctx.arc(l.x, l.y, l.r, 0, Math.PI * 2); }
    ctx.fillStyle = '#FFFFFF'; ctx.fill();
    ctx.save(); ctx.beginPath(); for (const l of live) { ctx.moveTo(l.x + l.r, l.y); ctx.arc(l.x, l.y, l.r, 0, Math.PI * 2); } ctx.clip();
    for (const l of live) { ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.globalAlpha = 0.38; ctx.beginPath(); ctx.arc(l.x + l.r * 0.5, l.y + l.r * 0.5, l.r * 0.55, 0, Math.PI * 2); ctx.fillStyle = pats.yellow; ctx.fill(); ctx.restore(); }
    ctx.restore();
    if (hero) halves(ctx, hullOpen, true);
    ctx.restore();
    return live;
  }
  function makeLobes(r, n, size) {
    const out = [];
    for (let i = 0; i < n; i++) { const a = -Math.PI / 2 + (r() - 0.5) * Math.PI * 1.25; out.push({ a, d: (40 + r() * 105) * size, r: (24 + r() * 50) * size, delay: (i / n) * 0.55 * (0.6 + 0.4 * r()) }); }
    out.push({ a: 0, d: -10 * size, r: 100 * size, delay: 0, core: true });
    return out;
  }

  // ---------- scenes ----------
  function paper(ctx, W, H) { ctx.fillStyle = PAPER; ctx.fillRect(-400, -1200, W + 800, H + 2600); }

  function bowl(ctx, t, extraFlake, falling) {
    const cx = 540, rim = 880, bottom = 1720, w = 470;
    // back wall interior tint
    ink(ctx, () => { ctx.beginPath(); ctx.moveTo(cx - w, rim); ctx.bezierCurveTo(cx - w, bottom + 60, cx + w, bottom + 60, cx + w, rim); ctx.closePath(); }, '#FFE3EE', null);
    for (const k of bowlKernels) { if (k.extra && !falling.landed) continue; drawSmallKernel(ctx, k.x, k.y, k.rot, k.brown, k.crack, k.s); }
    const ring = seg(t, 2.3, 3.3);                     // the question points at the two kernels
    if (t < 3.56 && ring > 0) for (const k of bowlKernels.slice(0, 2)) { ctx.save(); ctx.globalAlpha = Math.sin(Math.PI * ring); ink(ctx, () => { ctx.beginPath(); ctx.arc(k.x, k.y, 60 + 20 * ring, 0, Math.PI * 2); }, null, BLUE, 7); ctx.restore(); }
    for (const f of heap) { ctx.save(); ctx.translate(f.x, f.y); ctx.rotate(f.rot); flake(ctx, f.lobes, 1, f.s, 0.25, 0); ctx.restore(); }
    if (extraFlake) { ctx.save(); ctx.translate(extraFlake.x, extraFlake.y); ctx.rotate(extraFlake.rot); flake(ctx, flakeLobes, 1, 0.62, 1, 0, 0, true); ctx.restore(); }
    if (falling.on) drawSmallKernel(ctx, falling.x, falling.y, falling.rot, 1, true, 0.4);
    // bowl wall in cross-section (front cut), pink with halftone
    const wall = () => { ctx.beginPath(); ctx.moveTo(cx - w - 40, rim); ctx.bezierCurveTo(cx - w - 40, bottom + 110, cx + w + 40, bottom + 110, cx + w + 40, rim);
      ctx.lineTo(cx + w, rim); ctx.bezierCurveTo(cx + w, bottom + 60, cx - w, bottom + 60, cx - w, rim); ctx.closePath(); };
    ink(ctx, wall, PINK, BLUE, 6); dots(ctx, wall, 'blue', 0.35);
    ink(ctx, () => { ctx.beginPath(); ctx.ellipse(cx, rim, w + 20, 26, 0, 0, Math.PI * 2); }, null, BLUE, 6);
  }
  function drawSmallKernel(ctx, x, y, rot, brown, crack, k = 0.34) {        // centred on (x, y)
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(k, k); ctx.translate(0, KH * 0.5);
    ink(ctx, () => kernelPath(ctx), brown ? mixc(YEL, '#C9852A', brown) : YEL, BLUE, 16); dots(ctx, () => kernelPath(ctx), 'orange', 0.5);
    if (crack) { ctx.save(); ctx.globalCompositeOperation = 'multiply'; crackPath(ctx); ctx.strokeStyle = BLUE; ctx.lineWidth = 24; ctx.stroke(); ctx.restore(); }
    ctx.restore();
  }

  function stove(ctx, t) {
    const on = seg(t, 9.25, 9.6);
    // flames
    if (on > 0) {
      for (let i = 0; i < 8; i++) {
        const fx = 290 + i * 88, fl = Math.sin(t * 11 + i * 1.7) * 0.18 + Math.sin(t * 17 + i) * 0.1, h = (130 + 40 * Math.sin(i * 2.3)) * on * (1 + fl);
        const path = () => { ctx.beginPath(); ctx.moveTo(fx - 40, 1470); ctx.quadraticCurveTo(fx - 50, 1470 - h * 0.5, fx + 8 * fl * 10, 1470 - h); ctx.quadraticCurveTo(fx + 50, 1470 - h * 0.5, fx + 40, 1470); ctx.closePath(); };
        ink(ctx, path, i % 2 ? ORANGE : PINK, null); dots(ctx, path, 'yellow', 0.6);
      }
    }
    ink(ctx, () => { ctx.beginPath(); ctx.roundRect(230, 1470, 740, 40, 12); }, '#C9D3E6', BLUE, 6);
    // pan in cross-section with a handle running off frame
    const pan = () => { ctx.beginPath(); ctx.moveTo(180, PAN_Y - 70); ctx.lineTo(220, PAN_Y + 22); ctx.lineTo(980, PAN_Y + 22); ctx.lineTo(1020, PAN_Y - 70); ctx.lineTo(1002, PAN_Y - 70); ctx.lineTo(966, PAN_Y + 4); ctx.lineTo(234, PAN_Y + 4); ctx.lineTo(198, PAN_Y - 70); ctx.closePath(); };
    ink(ctx, pan, '#3B5FB0', BLUE, 6); dots(ctx, pan, 'blue', 0.5);
    ink(ctx, () => { ctx.beginPath(); ctx.roundRect(1010, PAN_Y - 92, 400, 30, 12); }, '#3B5FB0', BLUE, 6);
    if (on > 0) for (let i = 0; i < 4; i++) {          // heat shimmer
      const sx = 260 + i * 220, ph = t * 3 + i;
      ctx.save(); ctx.globalAlpha = 0.5 * on; ink(ctx, () => { ctx.beginPath(); ctx.moveTo(sx, PAN_Y - 90); for (let k = 1; k <= 8; k++) ctx.lineTo(sx + Math.sin(ph + k) * 10, PAN_Y - 90 - k * 22); }, null, PINK, 4); ctx.restore();
    }
  }

  function gauge(ctx, t, T) {                    // a print-style thermometer fixed to the top of the frame
    const on = seg(t, 3.7, 4.1) * (1 - seg(t, 29.7, 29.9)); if (on <= 0) return;
    const x0 = 150, x1 = 930, y = 300, frac = (T - 20) / 180;
    ctx.save(); ctx.globalAlpha = on;
    ink(ctx, () => { ctx.beginPath(); ctx.roundRect(x0, y - 26, x1 - x0 + 30, 52, 26); }, '#FFFFFF', BLUE, 7);
    ink(ctx, () => { ctx.beginPath(); ctx.roundRect(x0 + 8, y - 13, (x1 - x0) * frac + 12, 26, 13); }, PINK, null);
    ink(ctx, () => { ctx.beginPath(); ctx.arc(x0 - 6, y, 46, 0, Math.PI * 2); }, PINK, BLUE, 7);
    const x180 = x0 + 8 + (x1 - x0), x100 = x0 + 8 + (x1 - x0) * 80 / 180;
    ink(ctx, () => { ctx.beginPath(); ctx.moveTo(x100, y - 40); ctx.lineTo(x100, y - 26); ctx.moveTo(x180, y - 40); ctx.lineTo(x180, y - 26); }, null, BLUE, 6);
    const hit = seg(t, 19.0, 19.3), pulse = 1 + 0.3 * Math.exp(-6 * Math.max(0, t - 19.2)) * (t > 19.2 ? 1 : 0);
    if (hit > 0) { ctx.save(); ctx.globalAlpha = on * hit; label(ctx, '180 °C', x180, y - 92, 64 * pulse, PINK, 'right'); ctx.restore(); }
    if (t >= 26.95 && t < 30.0) { const r = seg(t, 27.0, 27.2) * (1 - seg(t, 29.7, 30.0)); ctx.save(); ctx.globalAlpha = r; label(ctx, 'REPLAY', 540, 430, 64, BLUE, 'center'); ctx.restore(); }
    ctx.restore();
  }
  const temp = (t) => kf(t, [[9.3, 22], [10.6, 100, 'inOutQuad'], [14.5, 150], [19.2, 180, 'inOutQuad']]);

  // the sealed kernel's burst; tau is time on the burst clock (the replay re-runs it)
  function burstPose(tau) {
    const b = seg(tau, BURST, 23.2), leg = kf(tau, [[23.5, 0], [24.3, 1, 'outQuad'], [24.42, 1], [24.62, 0, 'inQuad']]);
    const rise = A.ease.outCubic(seg(tau, 24.45, 26.4)), drop = A.ease.inQuad(seg(tau, 26.4, 27.0));
    const hull = A.ease.outQuad(seg(tau, BURST, BURST + 0.9));
    const y = K1.y - 135 - 28 * hull - 560 * rise - 120 * leg * (tau < 24.45 ? 1 : 0) + 420 * drop;
    return { bloom: b, leg, x: K1.x + 60 * rise + 140 * drop, y, rot: -0.06 + 1.3 * rise + 0.8 * drop, scale: 1.0 + 0.25 * b, hull };
  }

  function camera(t) {
    const keys = (v) => kf(t, v);
    const z = keys([[0, 1.1], [3.0, 1.6], [3.55, 2.4, 'inQuad'], [3.56, 1.25], [4.8, 1.25], [5.6, 1.5], [8.8, 1.5], [9.4, 1.35], [14.4, 1.35], [15.2, 1.5], [17.9, 1.5], [18.6, 1.42], [24.2, 1.42], [26.4, 1.1],
      [26.95, 1.1], [27.4, 1.5], [29.6, 1.5], [30.0, 1.0], [30.6, 1.0], [32.6, 1.7]]);
    const fx = keys([[0, 540], [3.0, 540], [3.56, 610], [14.4, 610], [15.2, 670], [17.9, 670], [18.6, 585], [24.2, 585], [26.4, 560], [26.95, 560], [27.4, 595], [29.6, 595], [30.0, 540], [30.6, 540], [32.6, 560]]);
    const fy = keys([[0, 1150], [3.0, 1440], [3.56, 1460], [3.57, 1060], [4.8, 1060], [5.6, 1080], [8.8, 1080], [9.4, 1060], [24.2, 1060], [26.4, 860],
      [26.95, 900], [27.4, 1070], [29.6, 1070], [30.0, 900], [30.6, 900], [32.6, 1420]]);
    return { z, fx, fy };
  }

  Atelier.register({
    setup(env) {
      A = env;
      const mk = (color, step, r) => { const c = document.createElement('canvas'); c.width = c.height = step; const g = c.getContext('2d'); g.fillStyle = color; g.beginPath(); g.arc(step / 2, step / 2, r, 0, Math.PI * 2); g.fill(); return c; };
      const tmp = document.createElement('canvas').getContext('2d');
      pats.yellow = tmp.createPattern(mk('#F0B428', 16, 4.2), 'repeat'); pats.orange = tmp.createPattern(mk('#FF7A2F', 14, 3.4), 'repeat');
      pats.blue = tmp.createPattern(mk('#1F4FA8', 14, 3.0), 'repeat'); pats.pink = tmp.createPattern(mk('#FF4F9A', 14, 3.4), 'repeat');
      const g = document.createElement('canvas'); g.width = g.height = 256; const gc = g.getContext('2d'), img = gc.createImageData(256, 256), r = env.rng(5);
      for (let i = 0; i < img.data.length; i += 4) { const v = 200 + r() * 55; img.data[i] = v; img.data[i + 1] = v * 0.98; img.data[i + 2] = v * 0.94; img.data[i + 3] = 255; }
      gc.putImageData(img, 0, 0); grain = tmp.createPattern(g, 'repeat');
      const rd = env.rng(11);
      for (let i = 0; i < 6; i++) drops.push({ x: (i % 2 ? 0.16 : -0.16) + (rd() - 0.5) * 0.12, y: -0.3 - (Math.floor(i / 2) * 0.2) - rd() * 0.06, delay: rd() * 0.9, w: rd() * 3, ph: rd() * 6 });
      flakeLobes = makeLobes(env.rng(21), 17, 1.0);
      const rh = env.rng(41);
      for (let i = 0; i < 46; i++) {
        const row = rh(), y = 740 + row * 680, half = 440 * Math.sqrt(Math.max(0.02, 1 - Math.pow((y - 860) / 640, 2)));
        heap.push({ x: 540 + (rh() - 0.5) * 2 * half * 0.92, y, rot: rh() * 6.28, s: 0.34 + rh() * 0.1, lobes: makeLobes(rh, 8, 1.0) });
      }
      heap.sort((a, b) => a.y - b.y);
      bowlKernels = [{ x: 430, y: 1488, rot: 1.4, brown: 0.3, s: 0.34 }, { x: 690, y: 1484, rot: -1.7, brown: 0.2, s: 0.34 }, { x: 562, y: 1470, rot: 0.3, brown: 1, crack: true, extra: true, s: 0.4 }];
    },
    render(ctx, env) {
      const t = env.t, W = env.W, H = env.H, cam = camera(t);
      ctx.save();
      ctx.translate(W / 2, H / 2); ctx.scale(cam.z, cam.z); ctx.translate(-cam.fx, -cam.fy);
      paper(ctx, W, H);
      if (t < 3.56 || t >= 30.0) {
        // the bowl: opening question and the answer
        let extra = null, falling = { on: false, landed: false };
        if (t >= 30.0) {
          const land = seg(t, 30.1, 30.7);
          extra = { x: 560, y: 560 + 230 * A.ease.inQuad(land) - Math.sin(Math.PI * seg(t, 30.7, 30.95)) * 30, rot: 2 * land };
          const f = seg(t, 31.0, 32.2);
          if (t >= 31.0) { falling.on = f < 1; falling.landed = f >= 1; falling.x = 562 + Math.sin(f * 9) * 40 * (1 - f); falling.y = 700 + (1470 - 700) * A.ease.inQuad(f); falling.rot = 0.3 + 6.28 * (1 - f); }
        }
        bowl(ctx, t, extra, falling);
      } else {
        stove(ctx, t);
        const T = temp(t);
        // cracked kernel (right), with its steam plume
        const s2 = kstate(t, 2);
        drawKernel(ctx, t, K2, s2, t);
        plume(ctx, t);
        // sealed kernel (left): before the burst it is a kernel; after, a flake (the replay re-runs the burst clock)
        let tau = t;
        if (t >= 26.95 && t < 30.0) tau = t < 27.5 ? kf(t, [[26.95, 26.9], [27.5, 20.85, 'inOutQuad']]) : kf(t, [[27.5, 20.85], [28.3, 20.995, 'linear'], [29.0, 21.075, 'linear'], [29.7, 21.45, 'linear']]);
        if (tau < BURST) drawKernel(ctx, t, K1, kstate(tau, 1), tau);
        else {
          const bp = burstPose(tau);
          ctx.save(); ctx.translate(bp.x, bp.y); ctx.rotate(bp.rot); flake(ctx, flakeLobes, bp.bloom * 1.3, bp.scale, bp.hull, 0, 0, true); ctx.restore();
          if (bp.leg > 0) {                                   // the starch leg: a solid lobe from the flake down to the pan, pushing it up, then kicking
            const top = bp.y + 40, foot = PAN_Y - 2, w = 96 + 30 * (1 - bp.leg);
            const strut = () => { ctx.beginPath(); ctx.moveTo(bp.x - 10 - w * 0.35, top); ctx.quadraticCurveTo(bp.x - 10 - w * 0.55, (top + foot) / 2, bp.x - 10 - w * 0.6, foot); ctx.lineTo(bp.x - 10 + w * 0.6, foot); ctx.quadraticCurveTo(bp.x - 10 + w * 0.55, (top + foot) / 2, bp.x - 10 + w * 0.35, top); ctx.closePath(); };
            ctx.save(); ctx.globalAlpha = Math.sqrt(bp.leg);
            strut(); ctx.fillStyle = '#FFFFFF'; ctx.fill(); ink(ctx, strut, null, BLUE, 8); dots(ctx, strut, 'yellow', 0.45);   // opaque: white under multiply would paint nothing
            ctx.restore();
            ink(ctx, () => { ctx.beginPath(); ctx.ellipse(bp.x - 10, PAN_Y + 2, 70 + 40 * bp.leg, 12 + 6 * bp.leg, 0, 0, Math.PI * 2); }, null, PINK, 8);
          }
          const jet = seg(tau, 21.02, 21.4);                 // steam jet from the opening, and the pop's sound rings after it
          if (jet > 0 && jet < 1) for (let i = 0; i < 9; i++) {
            const u = Math.min(1, jet * 1.4 - i * 0.05); if (u <= 0) continue;
            const a = -Math.PI / 2 + (i - 4) * 0.22;
            ctx.save(); ctx.globalAlpha = 1 - jet; ink(ctx, () => { ctx.beginPath(); ctx.arc(bp.x + Math.cos(a) * 240 * u, bp.y - 80 + Math.sin(a) * 240 * u, 20 + 30 * u, 0, Math.PI * 2); }, '#FFFFFF', BLUE, 4); ctx.restore();
          }
          const ring = seg(tau, 21.08, 21.45);
          if (ring > 0 && ring < 1) for (let k = 0; k < 3; k++) {
            const u = ring - k * 0.15; if (u <= 0) continue;
            ctx.save(); ctx.globalAlpha = 1 - u; ink(ctx, () => { ctx.beginPath(); ctx.arc(bp.x, bp.y - 100, 120 + 420 * u, -Math.PI * 0.95, -Math.PI * 0.05); }, null, PINK, 14 - 8 * u); ctx.restore();
          }
        }
        if (t > 6.2 && t < 9.0) {                              // the only label on the inside: the water
          const on = seg(t, 6.3, 6.7) * (1 - seg(t, 8.6, 9.0));
          ctx.save(); ctx.globalAlpha = on;
          ink(ctx, () => { ctx.beginPath(); ctx.moveTo(K1.x + 10, K1.y - 190); ctx.lineTo(610, K1.y - 400); ctx.lineTo(K2.x - 10, K2.y - 190); }, null, BLUE, 6);
          label(ctx, 'WATER', 610, K1.y - 500, 70, BLUE, 'center'); label(ctx, '14%', 610, K1.y - 432, 70, PINK, 'center'); ctx.restore();
        }
      }
      ctx.restore();
      if (t >= 3.56 && t < 30.0) gauge(ctx, t, temp(t));
      // print texture over everything, fixed to the page
      ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.globalAlpha = 0.22; ctx.fillStyle = grain; ctx.fillRect(0, 0, W, H); ctx.restore();
      // wipe into the pan at 3.56s: a pink ink block
      const wipe = seg(t, 3.3, 3.8);
      if (wipe > 0 && wipe < 1) { ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = PINK; const y = H * (A.ease.inOutCubic(wipe) * 2 - 1); ctx.fillRect(0, y, W, H); ctx.restore(); }
      const wipe2 = seg(t, 29.75, 30.25);
      if (wipe2 > 0 && wipe2 < 1) { ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = YEL; const y = -H + H * 2 * A.ease.inOutCubic(wipe2); ctx.fillRect(0, y, W, H); ctx.restore(); }
    },
  });
})();
