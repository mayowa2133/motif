// The Keeper (Motif Atelier pilot C): a storm, a lighthouse, a shape in the water.
// Painterly chiaroscuro: the lamp beam is the only strong light (additive), the sea is
// parallax layers, rain and lightning sit in screen space, grain and vignette on top.
(function () {
  'use strict';
  let A = null, rain = [], grain = null, clouds = [], spray = [];
  const LAMP = { x: 800, y: 640 }, HORIZON = 880;
  const NIGHT_SEA = ['#2F6274', '#2A586A', '#244E60', '#1F4556', '#1A3C4C', '#153342'];
  const DAWN_SEA = ['#8FB0C0', '#7BA1B4', '#6893A8', '#56849B', '#47768E', '#3A6880'];
  const LAYERS = [[HORIZON, 4, 0.004, 0.5], [960, 10, 0.006, 0.8], [1080, 18, 0.005, 1.1], [1240, 28, 0.004, 1.4], [1460, 40, 0.0035, 1.8], [1720, 55, 0.003, 2.2]];

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
  const mixc = (c1, c2, u) => { const p = (c) => (c[0] === '#' ? [1, 3, 5].map((i) => parseInt(c.substr(i, 2), 16)) : c.slice(4, -1).split(',').map(Number)), a = p(c1), b = p(c2); return 'rgb(' + a.map((v, i) => Math.round(v + (b[i] - v) * u)).join(',') + ')'; };
  const dawn = (t) => A.ease.inOutSine(seg(t, 29.0, 31.4));
  const storm = (t) => 1 - 0.65 * dawn(t);
  function flash(t) { return Math.max(0.35 * Math.exp(-14 * Math.max(0, t - 1.8)) * (t > 1.8 ? 1 : 0), (t > 13.2 ? 1 : 0) * Math.exp(-7 * (t - 13.2)) * (1 + 0.5 * Math.sin((t - 13.2) * 60))); }

  // ---------- the beam ----------
  function aim(t) {                              // where the beam meets the sea
    const sweep = (tt) => [260 + 430 * Math.sin(tt * 1.1 - 0.25), 1040 + 60 * Math.cos(tt * 1.1 - 0.25)];   // crosses the shape at 8.8 s
    if (t < 9.6) return sweep(t);
    const back = sweep(9.6), shape = shapeAt(t);
    if (t < 10.6) { const u = A.ease.inOutCubic(seg(t, 9.6, 10.6)); return [back[0] + (shape[0] - back[0]) * u, back[1] + (shape[1] - back[1]) * u]; }
    if (t < 24.4) return [shape[0] + 10, shape[1] - 20];
    const calf = shapeAt(24.4), far = [70, 905];
    const u = A.ease.inOutCubic(seg(t, 24.4, 25.6));
    return [calf[0] + (far[0] - calf[0]) * u, calf[1] + (far[1] - calf[1]) * u];
  }
  function intensity(t) {
    return kf(t, [[0, 1], [14.9, 1], [15.6, 0.32, 'outQuad'], [16.6, 0.32], [17.0, 1.35, 'outQuad'], [17.6, 1], [30.6, 1], [31.6, 0]]);
  }
  function beam(ctx, t) {
    const I = intensity(t);
    if (I <= 0.01) return;
    const [tx, ty] = aim(t), dx = tx - LAMP.x, dy = ty - LAMP.y, L = Math.hypot(dx, dy), nx = -dy / L, ny = dx / L, w = 40 + L * 0.2;
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    const g = ctx.createLinearGradient(LAMP.x, LAMP.y, tx, ty);
    g.addColorStop(0, `rgba(255,236,170,${0.55 * I})`); g.addColorStop(0.6, `rgba(255,226,150,${0.22 * I})`); g.addColorStop(1, `rgba(255,220,140,${0.06 * I})`);
    ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(LAMP.x + nx * 10, LAMP.y + ny * 10); ctx.lineTo(tx + nx * w, ty + ny * w); ctx.lineTo(tx - nx * w, ty - ny * w); ctx.lineTo(LAMP.x - nx * 10, LAMP.y - ny * 10); ctx.closePath(); ctx.fill();
    const pool = ctx.createRadialGradient(tx, ty, 10, tx, ty, w * 1.6);
    pool.addColorStop(0, `rgba(255,232,160,${0.35 * I})`); pool.addColorStop(1, 'rgba(255,232,160,0)');
    ctx.fillStyle = pool; ctx.beginPath(); ctx.ellipse(tx, ty, w * 1.6, w * 0.55, 0, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
  }
  function inBeam(t, x, y) {                     // 0..1: how lit a point is by the beam
    const [tx, ty] = aim(t), dx = tx - LAMP.x, dy = ty - LAMP.y, L = Math.hypot(dx, dy);
    const px = x - LAMP.x, py = y - LAMP.y, along = (px * dx + py * dy) / L, across = Math.abs(px * -dy + py * dx) / L;
    if (along < 0) return 0;
    const w = 40 + along * 0.2;
    return Math.max(0, 1 - across / w) * Math.min(1, intensity(t));
  }

  // ---------- sky, sea, rock, lighthouse ----------
  function sky(ctx, t) {
    const d = dawn(t), f = flash(t);
    const g = ctx.createLinearGradient(0, -200, 0, HORIZON + 20);
    g.addColorStop(0, mixc('#0A1D2A', '#E9A98C', d)); g.addColorStop(0.55, mixc('#173847', '#F4BE9C', d)); g.addColorStop(1, mixc('#2C5465', '#FBD9B0', d));
    ctx.fillStyle = g; ctx.fillRect(-600, -400, 2300, HORIZON + 420);
    if (d > 0) { const sun = ctx.createRadialGradient(330, HORIZON, 10, 330, HORIZON, 520); sun.addColorStop(0, `rgba(255,236,200,${0.9 * d})`); sun.addColorStop(1, 'rgba(255,210,170,0)'); ctx.fillStyle = sun; ctx.fillRect(-600, HORIZON - 540, 2300, 560); }
    for (const c of clouds) {
      const x = c.x + t * c.v * 8 - d * c.part * 500;
      const cg = ctx.createRadialGradient(x, c.y, 10, x, c.y, c.r);
      cg.addColorStop(0, `rgba(${mixc('#08151D', '#F6CBB0', d).slice(4, -1)},${0.8 * (1 - 0.7 * d)})`); cg.addColorStop(1, 'rgba(8,21,29,0)');
      ctx.fillStyle = cg; ctx.beginPath(); ctx.ellipse(x, c.y, c.r * 1.6, c.r * 0.6, 0, 0, Math.PI * 2); ctx.fill();
    }
    if (f > 0.02) { ctx.fillStyle = `rgba(200,225,240,${0.5 * f})`; ctx.fillRect(-600, -400, 2300, HORIZON + 420); }
    if (t > 13.2 && t < 13.5) {                  // the bolt
      const r = A.rng(77); ctx.save(); ctx.strokeStyle = `rgba(235,245,255,${1 - seg(t, 13.2, 13.5)})`; ctx.lineWidth = 6; ctx.beginPath();
      let x = 260, y = -200; ctx.moveTo(x, y); while (y < HORIZON - 10) { x += (r() - 0.5) * 120; y += 60 + r() * 50; ctx.lineTo(x, y); } ctx.stroke(); ctx.restore();
    }
  }
  function waveY(i, x, t) {
    const [base, amp, k, sp] = LAYERS[i], a = amp * storm(t);
    return base + a * Math.sin(x * k - t * sp + i * 1.7) + a * 0.45 * Math.sin(x * k * 2.3 + t * sp * 1.3 + i);
  }
  function seaLayer(ctx, t, i) {
    const d = dawn(t), f = flash(t);
    const base = mixc(mixc(NIGHT_SEA[i], DAWN_SEA[i], d), '#9FC4D4', 0.35 * f), deep = mixc(base, '#04121A', 0.55 - 0.3 * d);
    const top = LAYERS[i][0] - LAYERS[i][1], gr = ctx.createLinearGradient(0, top, 0, top + 260 + i * 40);
    gr.addColorStop(0, base); gr.addColorStop(1, deep); ctx.fillStyle = gr;
    ctx.beginPath(); ctx.moveTo(-600, 2400);
    for (let x = -600; x <= 1700; x += 30) ctx.lineTo(x, waveY(i, x, t));
    ctx.lineTo(1700, 2400); ctx.closePath(); ctx.fill();
    if (i >= 1) {                                 // foam on the crests, brighter where the beam touches
      ctx.lineCap = 'round';
      for (let x = -600; x <= 1700; x += 90) {
        const y = waveY(i, x, t), lit = inBeam(t, x, y);
        ctx.strokeStyle = `rgba(${lit > 0.1 ? '255,236,190' : '170,205,215'},${(0.18 + 0.6 * lit) * storm(t)})`; ctx.lineWidth = 2 + i * 1.2;
        ctx.beginPath(); ctx.moveTo(x - 24 - i * 6, waveY(i, x - 24 - i * 6, t) + 2); ctx.quadraticCurveTo(x, y - 4, x + 24 + i * 6, waveY(i, x + 24 + i * 6, t) + 2); ctx.stroke();
      }
    }
  }
  function rock(ctx, t) {
    const d = dawn(t);
    ctx.fillStyle = mixc('#05121A', '#2E3F4A', d);
    ctx.beginPath(); ctx.moveTo(610, 1520); ctx.lineTo(650, 1430); ctx.lineTo(700, 1405); ctx.lineTo(760, 1385); ctx.lineTo(860, 1390); ctx.lineTo(930, 1415); ctx.lineTo(985, 1460); ctx.lineTo(1010, 1530); ctx.closePath(); ctx.fill();
    for (const s of spray) {                      // a wave breaking on the rock every few seconds
      const age = (((t - s.t0) % 3.4) + 3.4) % 3.4; if (age > 1.2) continue;
      const u = age / 1.2;
      ctx.fillStyle = `rgba(200,225,232,${(1 - u) * 0.7 * storm(t)})`;
      ctx.beginPath(); ctx.arc(s.x + s.vx * u * 120, 1420 - Math.sin(Math.PI * u) * s.h, 6 + 10 * u, 0, Math.PI * 2); ctx.fill();
    }
  }
  function lighthouse(ctx, t) {
    const d = dawn(t), lit = Math.min(1, intensity(t));
    const body = mixc('#152B36', '#C9B9AE', d), band = mixc('#3A1E22', '#B04A3E', d);
    ctx.fillStyle = body; ctx.beginPath(); ctx.moveTo(715, 1400); ctx.lineTo(745, 712); ctx.lineTo(855, 712); ctx.lineTo(885, 1400); ctx.closePath(); ctx.fill();
    ctx.save(); ctx.clip(); ctx.fillStyle = band; for (const y of [880, 1080, 1280]) ctx.fillRect(700, y, 200, 70); ctx.restore();
    const rim = ctx.createLinearGradient(745, 0, 855, 0); rim.addColorStop(0, 'rgba(255,230,170,0)'); rim.addColorStop(1, `rgba(255,230,170,${0.15 * lit * (1 - d)})`);
    ctx.fillStyle = rim; ctx.beginPath(); ctx.moveTo(715, 1400); ctx.lineTo(745, 712); ctx.lineTo(855, 712); ctx.lineTo(885, 1400); ctx.closePath(); ctx.fill();
    ctx.fillStyle = mixc('#0B1A22', '#5A4A44', d); ctx.fillRect(782, 1300, 36, 70);                    // door
    ctx.fillStyle = mixc('#0E1E27', '#6E6058', d); ctx.fillRect(705, 700, 190, 14);                     // gallery floor
    ctx.strokeStyle = mixc('#0E1E27', '#6E6058', d); ctx.lineWidth = 4;
    ctx.beginPath(); ctx.moveTo(705, 668); ctx.lineTo(895, 668); for (let x = 710; x <= 890; x += 20) { ctx.moveTo(x, 668); ctx.lineTo(x, 702); } ctx.stroke();
    // lamp room glass, warm when lit
    const glass = ctx.createLinearGradient(0, 572, 0, 700); glass.addColorStop(0, `rgba(255,224,150,${0.2 + 0.25 * lit * (1 - d)})`); glass.addColorStop(1, `rgba(255,200,120,${0.12 + 0.18 * lit * (1 - d)})`);
    ctx.fillStyle = glass; ctx.fillRect(725, 572, 150, 128);
    ctx.strokeStyle = mixc('#0A161D', '#4A3C36', d); ctx.lineWidth = 5; ctx.strokeRect(725, 572, 150, 128); ctx.beginPath(); ctx.moveTo(775, 572); ctx.lineTo(775, 700); ctx.moveTo(825, 572); ctx.lineTo(825, 700); ctx.stroke();
    ctx.fillStyle = mixc('#0A161D', '#4A3C36', d); ctx.beginPath(); ctx.moveTo(712, 574); ctx.quadraticCurveTo(800, 500, 888, 574); ctx.closePath(); ctx.fill(); ctx.beginPath(); ctx.arc(800, 512, 9, 0, Math.PI * 2); ctx.fill();
    // the lamp: lens on a pedestal, shutter lever on the left post
    ctx.fillStyle = mixc('#3A3020', '#7A6A55', d); ctx.fillRect(788, 662, 24, 38);
    ctx.fillStyle = `rgba(255,248,220,${0.35 + 0.65 * lit})`; ctx.beginPath(); ctx.ellipse(LAMP.x, LAMP.y, 26, 24, 0, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = 'rgba(120,100,60,0.6)'; ctx.lineWidth = 2; for (const r of [8, 15, 21]) { ctx.beginPath(); ctx.ellipse(LAMP.x, LAMP.y, r, r * 0.92, 0, 0, Math.PI * 2); ctx.stroke(); }
    const I = intensity(t);
    if (I > 0.01) { ctx.save(); ctx.globalCompositeOperation = 'lighter'; const glow = ctx.createRadialGradient(LAMP.x + 10, LAMP.y, 4, LAMP.x + 10, LAMP.y, 70 * I);
      glow.addColorStop(0, `rgba(255,245,210,${0.85 * Math.min(1, I)})`); glow.addColorStop(1, 'rgba(255,230,160,0)'); ctx.fillStyle = glow; ctx.beginPath(); ctx.arc(LAMP.x + 10, LAMP.y, 70 * I, 0, Math.PI * 2); ctx.fill(); ctx.restore(); }
    const lever = kf(t, [[14.6, 0], [15.6, 1], [16.7, 1], [17.0, 0, 'outBack']]);
    ctx.save(); ctx.translate(742, 650); ctx.rotate(-0.6 + 1.1 * lever); ctx.fillStyle = '#2A2016'; ctx.fillRect(-3, -30, 6, 32); ctx.fillStyle = '#B8342A'; ctx.beginPath(); ctx.arc(0, -30, 7, 0, Math.PI * 2); ctx.fill(); ctx.restore();
  }

  // ---------- Ada ----------
  function ada(t) {
    const P = { x: 765, y: 700, s: 1, armR: 0.3, armL: 0.3, bendR: 0.4, bendL: 0.4, reachR: 0, mouth: 'smile', open: 0, brows: 0, eyes: 1, look: [0.3, 0], cup: 'hand', lean: 0, bob: 0, wave: 0, heart: 0 };
    // routine: crank the lamp (right arm circles), sip (left hand)
    if (t < 7.6) { const c = t * 5.2; P.armR = 1.3 + Math.sin(c) * 0.45; P.bendR = 0.8 + Math.cos(c) * 0.3; P.bob = Math.abs(Math.sin(c)) * 1.5;
      P.armL = kf(t, [[4.6, 0.6], [5.0, 2.3], [5.9, 2.3], [6.3, 0.6]]); P.bendL = kf(t, [[4.6, 0.4], [5.0, 1.6], [5.9, 1.6], [6.3, 0.4]]); P.eyes = t > 5.0 && t < 5.9 ? 0.2 : 1; P.look = [-0.6, 0.3]; }
    // sighting: stops cranking, leans to the glass, swings the lamp back, drops the cup
    if (t >= 7.6 && t < 14.2) {
      P.armR = kf(t, [[8.8, 1.3], [9.1, 0.4], [9.6, 1.6], [10.6, 1.9], [12.2, 1.9]]); P.bendR = 0.5; P.armL = 0.7; P.bendL = 0.8;
      P.look = [-0.9, kf(t, [[8.6, 0.2], [9.0, 0.6], [12.0, 0.9]])]; P.lean = kf(t, [[8.8, 0], [9.2, -0.12], [12.2, -0.15], [12.4, 0.05, 'outBack']]);
      P.mouth = t > 8.85 ? 'o' : 'smile'; P.open = kf(t, [[8.85, 0], [9.0, 0.4], [12.3, 0.4], [12.45, 1, 'outQuad']]); P.brows = kf(t, [[8.85, 0], [9.0, 0.6], [12.35, 1]]);
      P.eyes = 1 + kf(t, [[12.3, 0], [12.4, 0.4, 'outQuad']]); P.cup = t < 12.4 ? 'hand' : 'falling'; P.armL = t > 12.4 ? kf(t, [[12.4, 0.7], [12.5, 1.6]]) : 0.7;
    }
    // choice: reach for the shutter, freeze at the moan, resolve, throw it open, steer down
    if (t >= 14.2 && t < 19.0) {
      P.cup = 'gone'; P.look = [kf(t, [[14.2, -0.9], [14.6, -1], [15.7, -1], [15.9, -0.6]]), kf(t, [[14.2, 0.9], [14.6, 0.1], [15.7, 0.1], [15.9, 0.9]])];
      P.armL = kf(t, [[14.3, 0.4], [14.7, 1.55, 'outQuad'], [16.7, 1.55], [17.0, 1.3]]); P.bendL = 0.1; P.reachR = 0;
      P.mouth = t < 16.2 ? 'wobble' : 'flat'; P.brows = kf(t, [[15.6, 0.9], [15.8, 1.2], [16.2, 1.2], [16.6, -0.9, 'outQuad']]); P.eyes = kf(t, [[15.6, 1.1], [15.8, 1.4], [16.2, 1.2], [16.6, 0.85]]);
      P.lean = kf(t, [[15.6, -0.05], [15.75, 0.08, 'outQuad'], [16.6, 0], [17.0, -0.1]]);
      P.armR = kf(t, [[16.9, 0.4], [17.4, 1.7, 'outQuad'], [19.0, 1.7]]); P.bendR = 0.4;
    }
    // reveal: watches, then softens, hand on heart
    if (t >= 19.0 && t < 24.3) {
      P.cup = 'gone'; P.armR = 1.7; P.armL = kf(t, [[19.0, 1.3], [19.6, 0.6]]); P.look = [-0.9, 0.9]; P.lean = -0.08;
      P.brows = kf(t, [[19.0, -0.9], [19.6, 0.4], [21.8, 0.6], [22.4, 0.9]]); P.eyes = kf(t, [[19.0, 0.9], [19.8, 1.25], [21.9, 1.1], [22.5, 0.35]]);
      P.mouth = t < 21.9 ? 'o' : 'smile'; P.open = 0.3; P.heart = seg(t, 22.0, 22.6); if (P.heart > 0) { P.armL = 0.6 + 0.9 * P.heart; P.bendL = 0.4 + 1.4 * P.heart; }
    }
    // home: steers the beam out to sea, watches the calf go
    if (t >= 24.3 && t < 29.0) {
      P.cup = 'gone'; P.armR = kf(t, [[24.3, 1.7], [25.6, 2.2]]); P.armL = kf(t, [[24.3, 1.5], [24.8, 1.6]]); P.bendL = 0.4; P.look = [kf(t, [[24.3, -0.9], [25.6, -1]]), kf(t, [[24.3, 0.9], [25.6, 0.1]])];
      P.lean = kf(t, [[24.3, -0.08], [25.6, 0.02]]); P.brows = 0.7; P.eyes = kf(t, [[25.6, 0.9], [26.3, 1.3], [27.2, 1.0]]); P.mouth = t > 26.3 ? 'smile' : 'o'; P.open = 0.25;
    }
    // dawn: waves
    if (t >= 29.0) { P.cup = 'gone'; P.wave = seg(t, 30.9, 31.3); P.armR = 0.4 + 2.2 * P.wave + Math.sin(t * 9) * 0.25 * P.wave; P.bendR = 0.3; P.armL = 0.4; P.look = [-1, 0.1]; P.mouth = 'smile'; P.eyes = t > 32.2 ? 0.3 : 1; P.brows = 0.5; }
    return P;
  }
  function drawAda(ctx, P, t) {
    const lit = 0.6 + 0.4 * Math.min(1, intensity(t)), d = dawn(t);
    const coat = mixc('#6E5216', '#E8B23A', Math.max(lit * 0.9, d)), skin = mixc('#7A5C4A', '#F2C9A8', Math.max(lit * 0.9, d)), dark = '#1A1410';
    ctx.save(); ctx.translate(P.x, P.y); ctx.rotate(P.lean); ctx.translate(0, -P.bob); ctx.scale(P.s, P.s);
    const arm = (side, a, bend) => {
      const sx = side * 13, sy = -55, ex = sx + side * Math.sin(a) * 26, ey = sy + Math.cos(a) * 26;
      const cx = (sx + ex) / 2 - Math.cos(a) * side * 8 * bend, cy = (sy + ey) / 2 + Math.sin(a) * 8 * bend;
      ctx.strokeStyle = coat; ctx.lineWidth = 9; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(sx, sy); ctx.quadraticCurveTo(cx, cy, ex, ey); ctx.stroke();
      ctx.fillStyle = skin; ctx.beginPath(); ctx.arc(ex, ey, 4.5, 0, Math.PI * 2); ctx.fill();
      return [ex, ey];
    };
    ctx.fillStyle = dark; ctx.fillRect(-12, -9, 10, 9); ctx.fillRect(2, -9, 10, 9);
    ctx.fillStyle = coat; ctx.beginPath(); ctx.moveTo(-22, -8); ctx.lineTo(-13, -60); ctx.lineTo(13, -60); ctx.lineTo(22, -8); ctx.closePath(); ctx.fill();
    ctx.strokeStyle = 'rgba(60,40,10,0.45)'; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(0, -58); ctx.lineTo(0, -10); ctx.moveTo(-8, -40); ctx.lineTo(-11, -12); ctx.stroke();
    const handR = arm(1, P.armR, P.bendR), handL = arm(-1, P.armL, P.bendL);
    // head
    ctx.fillStyle = '#B9B4AE'; ctx.beginPath(); ctx.arc(-9, -78, 6, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = skin; ctx.beginPath(); ctx.arc(0, -72, 12, 0, Math.PI * 2); ctx.fill();
    const lx = P.look[0] * 2, ly = P.look[1] * 1.6;
    for (const side of [-1, 1]) {
      const gx = side * 5 + lx * 0.6, gy = -73;
      ctx.fillStyle = dark; ctx.beginPath(); ctx.ellipse(gx + lx * 0.5, gy + ly, 1.6, 1.6 * Math.min(1.4, P.eyes), 0, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = '#2A2420'; ctx.lineWidth = 1.2; ctx.beginPath(); ctx.arc(gx, gy, 4.2, 0, Math.PI * 2); ctx.stroke();
      if (inBeam(t, P.x, P.y - 70) > 0.05 || intensity(t) > 1.05) { ctx.fillStyle = 'rgba(255,245,210,0.8)'; ctx.beginPath(); ctx.arc(gx - 1.5, gy - 1.5, 1.2, 0, Math.PI * 2); ctx.fill(); }
      ctx.strokeStyle = '#6E6862'; ctx.lineWidth = 1.6; ctx.beginPath(); const by = gy - 6.5 - Math.max(0, P.brows) * 1.6, tilt = -P.brows * side * 1.4; ctx.moveTo(gx - 3.5, by - tilt); ctx.lineTo(gx + 3.5, by + tilt); ctx.stroke();
      if (P.eyes < 0.5) { ctx.strokeStyle = dark; ctx.lineWidth = 1.2; ctx.beginPath(); ctx.arc(gx, gy + 1, 2.4, 1.1 * Math.PI, 1.9 * Math.PI); ctx.stroke(); }
    }
    ctx.strokeStyle = '#4A2A22'; ctx.lineWidth = 1.4; ctx.beginPath();
    if (P.mouth === 'smile') { ctx.arc(lx * 0.4, -67, 3.2, 0.15 * Math.PI, 0.85 * Math.PI); ctx.stroke(); }
    else if (P.mouth === 'o') { ctx.fillStyle = '#4A2A22'; ctx.ellipse(lx * 0.4, -65.5, 1.6 + P.open, 1.4 + 2.2 * P.open, 0, 0, Math.PI * 2); ctx.fill(); }
    else if (P.mouth === 'wobble') { ctx.moveTo(-3, -65.5); for (let k = 0; k <= 6; k++) ctx.lineTo(-3 + k, -65.5 + Math.sin(k * 2 + t * 30) * 0.8); ctx.stroke(); }
    else { ctx.moveTo(-3, -65.5); ctx.lineTo(3, -65.5); ctx.stroke(); }
    // sou'wester
    ctx.fillStyle = coat; ctx.beginPath(); ctx.ellipse(0, -82, 21, 5, -0.08, 0, Math.PI * 2); ctx.fill(); ctx.beginPath(); ctx.arc(0, -84, 11, Math.PI, 0); ctx.fill();
    // the cup
    if (P.cup === 'hand') { ctx.fillStyle = '#E8E2D6'; ctx.fillRect(handL[0] - 3.5, handL[1] - 6, 7, 7); }
    ctx.restore();
    if (P.cup === 'falling') {                         // cup tumbles to the gallery floor and bounces
      const u = seg(t, 12.4, 12.62), bx = P.x - 16, by = kf(t, [[12.4, P.y - 58], [12.62, P.y - 4, 'inQuad'], [12.72, P.y - 12, 'outQuad'], [12.82, P.y - 4, 'inQuad']]);
      ctx.save(); ctx.translate(bx - 10 * u, by); ctx.rotate(u * 5); ctx.fillStyle = '#E8E2D6'; ctx.fillRect(-3.5, -3.5, 7, 7); ctx.restore();
    }
  }

  // ---------- the shape, the calf, the mother ----------
  function shapeAt(t) {
    return [kf(t, [[8.0, 230], [9.6, 330], [12.0, 470], [13.2, 560], [19.0, 575]]), kf(t, [[8.0, 1000], [9.6, 1120], [12.0, 1260], [13.2, 1350], [19.0, 1370]])];
  }
  function under(ctx, t) {                           // the dark mass under the swell, and the eye that catches the light
    if (t < 8.0 || t > 20.2) return;
    const [x, y] = shapeAt(t), big = kf(t, [[8.0, 0.8], [13.2, 1.25], [19.0, 1.2]]), lit = inBeam(t, x, y - 10), f = flash(t);
    const alpha = Math.min(0.92, 0.12 + 0.85 * lit + 0.7 * f) * (1 - seg(t, 19.4, 20.2));   // only the light shows it
    ctx.save(); ctx.translate(x, y); ctx.scale(big, big);
    const m = ctx.createRadialGradient(0, 0, 20, 0, 0, 260);             // soft-edged and shapeless: something big, not yet a whale
    m.addColorStop(0, `rgba(3,10,16,${alpha})`); m.addColorStop(0.6, `rgba(3,10,16,${alpha * 0.8})`); m.addColorStop(1, 'rgba(3,10,16,0)');
    ctx.fillStyle = m; ctx.beginPath(); ctx.ellipse(40, 0, 300, 80 + 8 * Math.sin(t * 2), 0.03, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
    const glint = Math.max(lit > 0.35 ? lit : 0, f > 0.3 ? f : 0) * (t < 19.2 ? 1 : 0);
    if (glint > 0) {
      const ex = x - 110 * big, ey = y - 14 * big; ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = `rgba(255,250,225,${glint})`;
      ctx.beginPath(); ctx.moveTo(ex - 26, ey); ctx.lineTo(ex, ey - 4); ctx.lineTo(ex + 26, ey); ctx.lineTo(ex, ey + 4); ctx.closePath(); ctx.fill();
      ctx.beginPath(); ctx.moveTo(ex, ey - 18); ctx.lineTo(ex + 3, ey); ctx.lineTo(ex, ey + 18); ctx.lineTo(ex - 3, ey); ctx.closePath(); ctx.fill();
      ctx.beginPath(); ctx.arc(ex, ey, 5, 0, Math.PI * 2); ctx.fill(); ctx.restore();
    }
  }
  function calf(ctx, t) {
    if (t < 19.0 || t > 29.2) return;
    const rise = A.ease.outCubic(seg(t, 19.1, 20.5));
    const go = A.ease.inOutSine(seg(t, 26.6, 29.0)), start = [585, 1372], end = [130, 912];
    const x = start[0] + (end[0] - start[0]) * go, y = start[1] + (end[1] - start[1]) * go + 70 * (1 - rise), s = 1 - 0.85 * go;
    const turn = kf(t, [[25.8, 1], [26.6, -1]]), lit = Math.max(0.25, inBeam(t, x, y - 40)), d = dawn(t);
    const cry = seg(t, 20.6, 20.9) * (1 - seg(t, 21.6, 22.0)), blink = (t > 19.8 && t < 19.95) || (t > 23.2 && t < 23.3);
    ctx.save(); ctx.translate(x, y); ctx.scale(s * turn, s);
    const body = mixc('#2A3E4B', '#5F8297', 0.35 + 0.65 * lit), belly = mixc('#4C6270', '#C6D8E0', 0.35 + 0.65 * lit);
    ctx.rotate(-0.06 - 0.12 * cry + Math.sin(t * 3) * 0.03);
    ctx.fillStyle = body; ctx.beginPath(); ctx.moveTo(-150, 10); ctx.bezierCurveTo(-160, -90, -40, -130, 50, -100); ctx.bezierCurveTo(130, -80, 190, -40, 230, -5); ctx.lineTo(230, 40); ctx.lineTo(-150, 40); ctx.closePath(); ctx.fill();
    ctx.fillStyle = belly; ctx.beginPath(); ctx.moveTo(-150, 10); ctx.bezierCurveTo(-140, -18, -90, -26, -40, -18); ctx.bezierCurveTo(10, -10, 40, 10, 60, 40); ctx.lineTo(-150, 40); ctx.closePath(); ctx.fill();
    const hl = ctx.createLinearGradient(0, -130, 0, -40); hl.addColorStop(0, `rgba(255,226,170,${0.45 * lit})`); hl.addColorStop(1, 'rgba(255,236,190,0)');
    ctx.fillStyle = hl; ctx.beginPath(); ctx.moveTo(-140, -40); ctx.bezierCurveTo(-120, -100, -30, -126, 50, -100); ctx.bezierCurveTo(120, -80, 170, -50, 200, -25); ctx.bezierCurveTo(100, -60, 0, -80, -140, -40); ctx.fill();
    ctx.fillStyle = mixc('#22343F', '#6A8899', lit); ctx.beginPath(); ctx.ellipse(-20, 20, 34, 13, 0.5, 0, Math.PI * 2); ctx.fill();          // fin
    // the eye: big, wet, catches the beam; a tear when it cries
    const ex = -95, ey = -48;
    ctx.fillStyle = '#0B1218'; ctx.beginPath(); ctx.ellipse(ex, ey, 21, blink ? 3 : 21 - 7 * cry, 0, 0, Math.PI * 2); ctx.fill();
    if (!blink) { ctx.fillStyle = `rgba(255,250,230,${0.65 + 0.35 * lit})`; ctx.beginPath(); ctx.arc(ex - 7, ey - 7, 7, 0, Math.PI * 2); ctx.fill(); ctx.beginPath(); ctx.arc(ex + 7, ey + 6, 3, 0, Math.PI * 2); ctx.fill(); }
    ctx.strokeStyle = 'rgba(10,20,26,0.8)'; ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(ex + 2, ey - 8, 20, 1.15 * Math.PI, 1.65 * Math.PI); ctx.stroke();                     // brow ridge
    ctx.beginPath(); ctx.moveTo(-148, -6); ctx.quadraticCurveTo(-120, 4 + 10 * cry, -90, -2); ctx.stroke();                                                                     // mouth
    if (cry > 0 || (t > 21.6 && t < 23.0)) { const tu = seg(t, 20.8, 22.6); ctx.fillStyle = `rgba(210,236,250,${0.95 * (1 - tu)})`; ctx.beginPath(); ctx.ellipse(ex + 6, ey + 28 + 50 * tu, 7, 10, 0, 0, Math.PI * 2); ctx.fill(); }
    ctx.restore();
    // spout
    for (const [t0, k] of [[20.4, 1], [27.6, 0.5]]) {
      const u = seg(t, t0, t0 + 1.0); if (u <= 0 || u >= 1) continue;
      const r = A.rng(Math.round(t0 * 10)), bx = x + (-20) * s * turn, by = y - 120 * s;
      for (let i = 0; i < 18; i++) { const a = -Math.PI / 2 + (r() - 0.5) * 0.9, sp = (90 + r() * 120) * k * s;
        ctx.fillStyle = `rgba(220,236,242,${0.75 * (1 - u)})`; ctx.beginPath(); ctx.arc(bx + Math.cos(a) * sp * u, by + Math.sin(a) * sp * u + 60 * u * u, (4 + r() * 5) * s, 0, Math.PI * 2); ctx.fill(); }
    }
    if (rise > 0 && rise < 1) { ctx.strokeStyle = `rgba(220,236,242,${0.7 * (1 - rise)})`; ctx.lineWidth = 5; ctx.beginPath(); ctx.ellipse(x, start[1] + 20, 120 + 160 * rise, 18 + 20 * rise, 0, 0, Math.PI * 2); ctx.stroke(); }
  }
  function mother(ctx, t) {
    if (t < 25.6) return;
    const up = A.ease.outCubic(seg(t, 25.6, 26.5)) * (1 - A.ease.inCubic(seg(t, 27.9, 28.7))), x = 70, y = 912, lit = Math.min(1, intensity(t)) * (1 - dawn(t));
    if (up > 0.01) {
      ctx.save(); ctx.translate(x, y); ctx.scale(1, up);
      ctx.fillStyle = '#071722'; ctx.beginPath(); ctx.moveTo(-16, 0); ctx.lineTo(-10, -70); ctx.bezierCurveTo(-60, -90, -110, -120, -130, -150); ctx.bezierCurveTo(-80, -140, -30, -125, 0, -100);
      ctx.bezierCurveTo(30, -125, 80, -140, 130, -150); ctx.bezierCurveTo(110, -120, 60, -90, 10, -70); ctx.lineTo(16, 0); ctx.closePath(); ctx.fill();
      ctx.strokeStyle = `rgba(255,232,170,${0.8 * lit})`; ctx.lineWidth = 3; ctx.stroke(); ctx.restore();
    }
    for (const [t0, bx, k] of [[26.8, 70, 1], [31.0, 200, 1], [31.6, 262, 0.55]]) {      // spouts: hers, then both at dawn
      const u = seg(t, t0, t0 + 1.4); if (u <= 0 || u >= 1) continue;
      const r = A.rng(Math.round(t0 * 10));
      for (let i = 0; i < 30; i++) { const a = -Math.PI / 2 + (r() - 0.5) * 0.7, sp = (100 + r() * 150) * k;
        ctx.fillStyle = `rgba(${dawn(t) > 0.5 ? '255,245,235' : '210,228,236'},${0.8 * (1 - u)})`; ctx.beginPath(); ctx.arc(bx + Math.cos(a) * sp * u, 905 + Math.sin(a) * sp * u + 70 * u * u, 4 + r() * 5 * k, 0, Math.PI * 2); ctx.fill(); }
    }
  }

  // ---------- camera ----------
  function camera(t) {                          // close-ups on Ada are hard cuts (one-frame key pairs), pushes elsewhere
    const c = 0.034;
    const z = kf(t, [[0, 1.0], [2.6, 1.0], [3.2, 4.2], [4.6, 4.4], [5.2, 1.15], [7.6, 1.15], [8.4, 1.3], [9.6, 1.3], [11.8, 1.35], [12.0 - c, 1.35], [12.0, 5.0], [13.1 - c, 5.0], [13.1, 1.3], [14.4 - c, 1.3], [14.4, 5.0], [17.1 - c, 5.2],
      [17.1, 1.5], [19.0, 2.1], [21.9 - c, 2.25], [21.9, 5.2], [23.7 - c, 5.2], [23.7, 1.6], [24.3, 1.5], [25.8, 1.0], [29.0, 1.0], [30.6, 1.2], [33.0, 1.3]]);
    const fx = kf(t, [[0, 600], [2.6, 600], [3.2, 772], [4.6, 772], [5.2, 470], [7.6, 470], [8.4, 420], [9.6, 420], [11.8, 560], [12.0 - c, 560], [12.0, 768], [13.1 - c, 768], [13.1, 600], [14.4 - c, 600], [14.4, 765], [17.1 - c, 765],
      [17.1, 640], [19.0, 560], [21.9 - c, 560], [21.9, 768], [23.7 - c, 768], [23.7, 560], [24.3, 560], [25.8, 470], [29.0, 470], [30.6, 450], [33.0, 440]]);
    const fy = kf(t, [[0, 1020], [2.6, 1020], [3.2, 655], [4.6, 655], [5.2, 1060], [7.6, 1060], [8.4, 1130], [9.6, 1130], [11.8, 1230], [12.0 - c, 1230], [12.0, 655], [13.1 - c, 655], [13.1, 1180], [14.4 - c, 1180], [14.4, 655], [17.1 - c, 655],
      [17.1, 1160], [19.0, 1300], [21.9 - c, 1310], [21.9, 655], [23.7 - c, 655], [23.7, 1150], [24.3, 1150], [25.8, 1020], [29.0, 1020], [30.6, 960], [33.0, 940]]);
    return { z, fx, fy };
  }

  Atelier.register({
    setup(env) {
      A = env;
      const r = env.rng(9);
      for (let i = 0; i < 260; i++) rain.push({ x: r() * 1400 - 160, y: r() * 2100, v: 0.8 + r() * 0.6, l: 26 + r() * 30 });
      for (let i = 0; i < 9; i++) clouds.push({ x: r() * 1400 - 200, y: 80 + r() * 600, r: 160 + r() * 200, v: 0.5 + r(), part: r() > 0.5 ? 1 : -1 });
      for (let i = 0; i < 26; i++) spray.push({ t0: (i % 3) * 1.1 + r() * 0.3, x: 650 + r() * 330, vx: (r() - 0.5) * 2, h: 60 + r() * 140 });
      const g = document.createElement('canvas'); g.width = g.height = 256; const gc = g.getContext('2d'), img = gc.createImageData(256, 256);
      for (let i = 0; i < img.data.length; i += 4) { const v = 110 + r() * 145; img.data[i] = img.data[i + 1] = img.data[i + 2] = v; img.data[i + 3] = 255; }
      gc.putImageData(img, 0, 0); grain = gc.createPattern(g, 'repeat');
    },
    render(ctx, env) {
      const t = env.t, W = env.W, H = env.H, cam = camera(t);
      ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(cam.z, cam.z); ctx.translate(-cam.fx, -cam.fy);
      sky(ctx, t);
      seaLayer(ctx, t, 0); mother(ctx, t); seaLayer(ctx, t, 1); seaLayer(ctx, t, 2);
      seaLayer(ctx, t, 3);
      under(ctx, t);                                // seen through the near water
      lighthouse(ctx, t); drawAda(ctx, ada(t), t); rock(ctx, t);
      beam(ctx, t);
      calf(ctx, t);
      seaLayer(ctx, t, 4);
      seaLayer(ctx, t, 5);
      ctx.restore();
      // rain, grain and vignette in screen space
      const ra = (1 - seg(t, 28.6, 29.8)) * 0.4;
      if (ra > 0) { ctx.save(); ctx.strokeStyle = `rgba(190,215,225,${ra})`; ctx.lineWidth = 2; ctx.beginPath();
        for (const d of rain) { const y = ((d.y + t * 1500 * d.v) % 2100) - 100, x = d.x - (y / 1920) * 120; ctx.moveTo(x, y); ctx.lineTo(x - 0.35 * d.l, y + d.l); } ctx.stroke(); ctx.restore(); }
      ctx.save(); ctx.globalCompositeOperation = 'overlay'; ctx.globalAlpha = 0.16; ctx.fillStyle = grain; ctx.fillRect(0, 0, W, H); ctx.restore();
      const v = ctx.createRadialGradient(W / 2, H * 0.48, H * 0.3, W / 2, H * 0.5, H * 0.75);
      v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, `rgba(0,6,10,${0.42 - 0.3 * dawn(t)})`); ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
    },
  });
})();
