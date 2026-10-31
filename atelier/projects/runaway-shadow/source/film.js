// Runaway Shadow (Motif Atelier pilot B): one continuous take on a sunset meadow.
// Every cast shadow is a projection of the caster's pose through one light direction,
// drawn into a single flat layer so overlapping shadows merge (that is how the twin
// can melt into the tree's shade). Times below are in seconds.
(function () {
  'use strict';
  const PLUM = '#2B1B33', CREAM = '#FFF1D6', RED = '#E2483A', RED_D = '#B8322A', PINK = '#F59AA0', SHADE = '#2B1B3A';
  const LEG = 34, BH = 224, BW = 192, ARM = 122;
  let grass = [], stars = [], layer = null, lctx = null, A = null;

  // ---------- timing helpers ----------
  function kf(t, keys) {                       // [[time, value, ease?], ...] ease applies to the segment ending at that key
    if (t <= keys[0][0]) return keys[0][1];
    for (let i = 1; i < keys.length; i++) {
      const [t1, v1, e] = keys[i];
      if (t <= t1) {
        const [t0, v0] = keys[i - 1];
        const u = (A.ease[e || 'inOutSine'])((t - t0) / (t1 - t0));
        return v0 + (v1 - v0) * u;
      }
    }
    return keys[keys.length - 1][1];
  }
  const wob = (t, t0, amp, f = 16, d = 6) => (t < t0 ? 0 : amp * Math.exp(-d * (t - t0)) * Math.sin(f * (t - t0)));
  const pulse = (t, a, b) => (t >= a && t < b ? 1 : 0);
  const mix = (c1, c2, u) => {
    const p = (c) => [1, 3, 5].map((i) => parseInt(c.substr(i, 2), 16));
    const a = p(c1), b = p(c2);
    return 'rgb(' + a.map((v, i) => Math.round(v + (b[i] - v) * u)).join(',') + ')';
  };

  // ---------- world light ----------
  const night = (t) => A.ease.inOutSine(A.seg(t, 24.4, 26.2));
  const light = (t) => 1 - night(t);
  const shadowLen = (t) => 1.12 + 0.18 * A.seg(t, 0, 24.4) + 1.1 * A.ease.inQuad(A.seg(t, 24.4, 26.2));
  const lightDir = (t) => { const k = shadowLen(t); return [-0.32 * k, 1.0 * k]; };
  const sunY = (t) => kf(t, [[0, 1040], [24.4, 1065], [26.2, 1250, 'inQuad']]);

  // ---------- Pim choreography ----------
  function walkLegs(t, rate, stride) { const ph = t * rate * Math.PI * 2; return { l: Math.sin(ph) * stride, r: -Math.sin(ph) * stride, bob: -Math.abs(Math.sin(ph)) * 10 }; }

  function pim(t) {
    const P = { x: 700, y: 1232, s: 1, facing: 0, squash: 1, lean: 0, lift: 0, rot: 0, armL: 0.25, armR: 0.25, bendL: 0.3, bendR: 0.3, frontR: false, frontL: false,
      legL: 0, legR: 0, sit: 0, eyeOpen: 1, lookX: 0, lookY: 0, eyeSize: 1, squint: 0, brows: 0, mouth: 'smile', open: 0, hatTilt: 0.35, hatUp: 0, hatOff: 0, dazed: 0, flat: 0 };
    // sunset: walk in, stop, sigh
    if (t < 2.4) { const w = walkLegs(t, 1.15, 0.42); P.x = kf(t, [[0, 990], [2.4, 700, 'outQuad']]); P.legL = w.l; P.legR = w.r; P.lift = -w.bob * 0.6; P.facing = -0.8;
      P.armL = 0.25 + w.r * 0.5; P.armR = 0.25 + w.l * 0.5; P.hatTilt = 0.55 + Math.sin(t * 7.2) * 0.08; }
    else P.facing = kf(t, [[2.4, -0.8], [2.9, 0]]);
    P.squash *= 1 + wob(t, 2.4, 0.06, 18, 7);
    P.squash *= kf(t, [[2.6, 1], [2.95, 1.06], [3.25, 0.98], [3.4, 1]]);
    P.eyeOpen = kf(t, [[2.6, 1], [2.9, 0.45], [3.3, 0.45], [3.45, 1]]);
    P.hatTilt += wob(t, 2.4, 0.25, 12, 5);
    // lag: stretch, double take, suspicious test
    const st = kf(t, [[3.35, 0], [3.6, -0.6, 'outQuad'], [4.0, 1, 'outBack'], [4.6, 1], [4.95, 0, 'inOutQuad']]);
    if (t > 3.3 && t < 5.1) { P.squash *= 1 + 0.15 * Math.max(0, st) - 0.1 * Math.max(0, -st); P.armL = P.armR = 0.25 + 2.3 * Math.max(0, st); P.bendL = P.bendR = 0.3 - 0.25 * Math.max(0, st);
      P.eyeOpen = st > 0.3 ? 0.05 : 1; P.mouth = st > 0.3 ? 'o' : 'smile'; P.open = Math.max(0, st); }
    // glance, look back, snap back (double take)
    P.lookX = kf(t, [[5.1, 0], [5.25, -0.7], [5.45, -0.7], [5.6, 0], [5.75, 0], [5.82, -0.8, 'outQuad'], [7.5, -0.8], [7.8, -0.4]]);
    P.lookY = kf(t, [[5.1, 0], [5.25, 0.8], [5.45, 0.8], [5.6, 0], [5.75, 0], [5.82, 0.9, 'outQuad'], [7.5, 0.9], [7.8, 0.5]]);
    if (t > 5.8) { P.eyeSize = 1 + kf(t, [[5.8, 0], [5.86, 0.45, 'outQuad'], [6.3, 0.1], [6.5, 0]]); P.hatUp = kf(t, [[5.8, 0], [5.86, 1, 'outQuad'], [6.25, 1], [6.6, 0, 'outBack']]);
      P.squash *= 1 + wob(t, 5.8, 0.12, 22, 6); P.mouth = t < 6.4 ? 'o' : 'flat'; P.open = t < 6.4 ? 0.6 : 0;
      P.facing = kf(t, [[5.8, 0], [5.86, -0.55, 'outQuad'], [8.8, -0.55], [9.0, -0.3]]); P.lean += kf(t, [[5.8, 0], [5.86, -0.07, 'outQuad'], [6.4, -0.04]]); }
    if (t > 6.4 && t < 9.0) { P.squint = kf(t, [[6.4, 0], [6.7, 0.65], [8.6, 0.65], [9.0, 0.4]]); P.brows = -kf(t, [[6.4, 0], [6.7, 0.8]]); P.lean = kf(t, [[6.4, 0], [6.9, -0.08]]);
      P.armR = kf(t, [[6.9, 0.25], [7.4, 2.2, 'outQuad'], [7.9, 2.2], [8.05, 0.25, 'inQuad']]); P.bendR = 0.15; }
    // escape: lean in to squint, recoil as the twin stands up
    if (t >= 9.0 && t < 13.2) {
      const lean = kf(t, [[9.0, 0], [9.5, 1, 'outQuad'], [10.15, 1], [10.35, 0, 'outBack']]);
      P.lean = -0.08 - 0.22 * lean; P.squash = 1 - 0.1 * lean + wob(t, 10.35, 0.14, 20, 6); P.lookX = -0.6 - 0.3 * lean; P.lookY = 0.9;
      P.squint = 0.7 * lean; P.brows = -0.8 * lean; P.mouth = 'flat';
      if (t >= 10.3) { P.eyeSize = 1 + kf(t, [[10.3, 0], [10.36, 0.5, 'outQuad'], [11.6, 0.35], [12.2, 0.15]]); P.hatUp = kf(t, [[10.3, 0], [10.36, 1, 'outQuad'], [11.8, 1], [12.3, 0, 'outBack']]);
        P.mouth = 'o'; P.open = kf(t, [[10.3, 0], [10.38, 0.9], [11.6, 0.7]]);
        const shock = kf(t, [[10.3, 0], [10.38, 1, 'outBack'], [11.7, 0.85], [12.2, 0]]), shake = Math.sin(t * 46) * 0.06 * shock;
        P.armL = 0.25 + 2.05 * shock + shake; P.armR = 0.25 + 2.15 * shock - shake; P.bendL = P.bendR = 0.3 + 0.5 * shock; P.lean = P.lean + 0.1 * shock; P.lift = 14 * shock;
        P.lookX = kf(t, [[11.6, -0.6], [12.3, -0.95]]); P.lookY = kf(t, [[11.6, 0.7], [12.3, 0.25]]); }
      if (t >= 12.55) { P.lookY = kf(t, [[12.55, 0.1], [12.7, 1, 'outQuad'], [13.0, 1], [13.12, 0, 'outQuad']]); P.lookX = kf(t, [[12.55, -0.9], [12.7, 0], [13.12, 0]]);
        P.mouth = 'flat'; P.brows = kf(t, [[13.0, 0], [13.12, -0.9]]); P.eyeSize = 1; P.open = 0; P.armL = P.armR = 0.3; P.hatUp = kf(t, [[12.55, 0.4], [12.75, 0, 'outBack']]); }
    }
    // chase: wind-up, a visible run across open grass, cap off as a net, dive, faceplant
    if (t >= 13.2 && t < 17.8) {
      const run = A.seg(t, 13.45, 14.35);
      P.x = kf(t, [[13.45, 700], [14.35, 565, 'inOutQuad']]); P.facing = kf(t, [[13.2, -0.3], [13.35, -0.9]]);
      P.lean = kf(t, [[13.2, -0.05], [13.4, 0.18, 'outQuad'], [13.5, -0.22], [14.3, -0.22], [14.45, 0.05]]); P.brows = -0.9; P.mouth = 'flat'; P.lookX = -0.9; P.lookY = 0.3;
      if (run > 0 && run < 1) { const w = walkLegs(t, 2.6, 0.62); P.legL = w.l; P.legR = w.r; P.lift = -w.bob; P.armL = 1.0 + w.l * 1.1; P.armR = 1.0 + w.r * 1.1; P.hatTilt = 0.9 + Math.sin(t * 16) * 0.12; }
      if (t >= 14.35) {
        const d = A.seg(t, 15.0, 15.6);
        P.hatOff = t >= 14.55 ? 1 : 0; P.armR = kf(t, [[14.35, 0.5], [14.55, 2.7, 'outQuad'], [14.9, 2.2], [15.3, 2.45]]); P.armL = kf(t, [[14.35, 0.5], [14.95, 1.8], [15.3, 2.4]]);
        P.squash = kf(t, [[14.75, 1], [14.95, 0.8, 'outQuad'], [15.02, 1.12]]); P.eyeSize = t < 14.95 ? 1.15 : 1;
        P.x = kf(t, [[15.0, 565], [15.6, 345, 'linear']]); P.y = kf(t, [[15.0, 1232], [15.6, 1462, 'inQuad']]); P.lift = Math.sin(Math.PI * d) * 160; P.back = t > 15.35 ? 1 : 0;
        P.rot = kf(t, [[15.0, 0], [15.6, -1.45, 'inOutQuad']]); P.s = kf(t, [[15.0, 1], [15.6, 1.1]]);
        if (t >= 15.6) { P.rot = -1.5 + wob(t, 15.6, 0.08, 18, 7); P.squash = 1 + wob(t, 15.6, -0.18, 20, 7); P.lift = 0; P.back = 1;
          P.legL = 0.9 + Math.sin(t * 11) * 0.35 * (1 - A.seg(t, 16.6, 17.2)); P.legR = -0.5 - Math.sin(t * 11 + 1) * 0.35 * (1 - A.seg(t, 16.6, 17.2)); P.armL = 2.9; P.armR = 2.85; P.bendL = P.bendR = 0.1; P.mouth = 'flat'; P.brows = 0; }
      }
    }
    // sit up, glare at the giggling eyes, think, get the idea, put the cap back on
    if (t >= 17.8 && t < 20.05) {
      const up = A.ease.outBack(A.seg(t, 17.8, 18.3));
      P.x = 345; P.y = 1462; P.s = 1.1; P.rot = -1.5 * (1 - up); P.sit = up; P.hatOff = 1; P.dazed = t < 18.3 ? 1 : 0; P.back = t < 17.95 ? 1 : 0;
      P.lookX = -0.9; P.lookY = 0.55; P.brows = -0.9; P.mouth = 'flat'; P.armL = 0.6; P.armR = 0.6; P.legL = 1.1; P.legR = 1.0;
      if (t > 18.6) { P.armR = 2.0 + Math.sin(t * 14) * 0.08; P.frontR = true; P.bendR = 1.1; P.lookX = kf(t, [[18.6, -0.9], [18.9, 0.3]]); P.lookY = kf(t, [[18.6, 0.55], [18.9, -0.7]]); P.squint = 0.35; P.brows = -0.2; }
      if (t > 19.4) {                                        // the idea: a glance at the eyes, then mitten up
        const aha = kf(t, [[19.4, 0], [19.5, 1, 'outBack'], [19.8, 1], [19.9, 0]]);
        P.frontR = false; P.armR = 0.6 + 2.3 * aha; P.bendR = 0.1; P.squint = 0; P.eyeSize = 1 + 0.25 * aha; P.brows = 0.9 * aha; P.mouth = 'grin'; P.squash = 1 + 0.08 * aha;
        P.lookX = kf(t, [[19.4, 0.3], [19.5, -0.9], [19.75, -0.9], [19.85, 0]]); P.lookY = kf(t, [[19.4, -0.7], [19.5, 0.5], [19.85, 0]]); P.hatUp = 0.6 * aha;
      }
      if (t > 19.85) { P.armR = kf(t, [[19.85, 1.2], [19.95, 1.8, 'outQuad'], [20.05, 2.6]]); P.sit = kf(t, [[19.85, 1], [20.05, 0.4]]); P.lookX = 0.6; }
    }
    // lure: walk back into the sun, dance, freeze, wind up, stomp, pinned hold, smug
    if (t >= 20.05 && t < 24.4) {
      const back = A.seg(t, 20.05, 20.6);
      P.hatOff = 0; P.sit = kf(t, [[20.05, 0.4], [20.2, 0, 'outQuad']]);
      P.x = kf(t, [[20.05, 345], [20.6, 640, 'inOutQuad']]); P.y = kf(t, [[20.05, 1462], [20.6, 1262, 'inOutQuad']]); P.s = kf(t, [[20.05, 1.1], [20.6, 1.04]]);
      P.brows = 0.6; P.mouth = 'grin'; P.lookX = -0.5; P.lookY = 0.2; P.facing = back > 0 && back < 1 ? 0.8 : 0;
      if (back > 0 && back < 1) { const w = walkLegs(t, 2.2, 0.45); P.legL = w.l; P.legR = w.r; P.lift = -w.bob; P.squash = 1 + Math.sin(t * 25) * 0.03; }
      if (t >= 20.6 && t < 22.6) {
        const beat = (t - 20.6) * 2.2 * Math.PI;                  // the dance sits on the score's beat
        P.lean = Math.sin(beat) * 0.22; P.lift = Math.max(0, Math.sin(beat * 2)) * 26; P.squash = 1 + Math.sin(beat * 2) * 0.06;
        P.armL = 1.6 + Math.sin(beat) * 1.0; P.armR = 1.6 - Math.sin(beat) * 1.0; P.bendL = P.bendR = 0.5; P.legL = Math.sin(beat) * 0.35; P.legR = -Math.sin(beat) * 0.35;
        P.mouth = 'grin'; P.hatTilt = 0.35 - Math.sin(beat) * 0.35;
        const side = pulse(t, 21.5, 21.85) + pulse(t, 22.1, 22.45);           // sneaky side-eye at the creeping shadow
        P.eyeOpen = side ? 1 : 0.5; P.lookX = side ? -0.9 : 0; P.lookY = side ? 0.8 : 0;
      }
      if (t >= 22.6) {                                          // freeze, wind up (8 frames), slam, hold the pin
        P.eyeOpen = 1; P.lookX = -0.6; P.lookY = 0.9; P.brows = -0.8; P.mouth = 'flat';
        P.legL = kf(t, [[22.6, 0], [22.85, -0.7, 'outQuad'], [23.0, 0.1, 'inQuad'], [23.15, 0]]); P.legR = kf(t, [[22.6, 0], [22.85, 0.7, 'outQuad'], [23.0, -0.1, 'inQuad'], [23.15, 0]]); P.lift = kf(t, [[22.6, 0], [22.68, -10], [22.85, 120, 'outQuad'], [23.0, 0, 'inQuad']]);
        P.lean = kf(t, [[22.6, 0], [22.85, 0.16, 'outQuad'], [23.0, -0.1, 'inQuad'], [23.4, -0.04]]);
        P.squash = kf(t, [[22.6, 1], [22.85, 1.1], [23.0, 1]]) * (1 + wob(t, 23.0, -0.25, 24, 7));
        P.armL = kf(t, [[22.6, 0.25], [22.85, 2.2, 'outQuad'], [23.05, 0.7]]); P.armR = kf(t, [[22.6, 0.25], [22.85, 2.0, 'outQuad'], [23.05, 0.6]]);
        P.eyeSize = 1 + kf(t, [[22.95, 0], [23.0, 0.2], [23.4, 0]]);
      }
      if (t >= 23.45) { const dust = Math.sin((t - 23.45) * 26) * pulse(t, 23.45, 23.95);
        P.frontL = P.frontR = true; P.armL = 1.25 + dust * 0.15; P.armR = 1.25 - dust * 0.15; P.bendL = P.bendR = 1.25; P.legL = 0;
        P.eyeOpen = t > 23.95 ? 0.45 : 1; P.mouth = 'grin'; P.brows = 0.3; P.lookX = 0; P.lookY = t > 23.95 ? -0.2 : 0.6; P.lean = kf(t, [[23.95, 0], [24.2, 0.06]]); }
    }
    // nightfall: smug, then worried look-down, then the eyes
    if (t >= 24.4) {
      P.x = 640; P.y = 1262; P.s = 1.04; P.armL = P.armR = 0.3; P.mouth = t < 26.0 ? 'grin' : 'frown'; P.eyeOpen = t < 26.0 ? 0.45 : 1; P.brows = t < 26.0 ? 0.3 : 0.7;
      P.lookX = kf(t, [[26.0, 0], [26.2, -0.2], [26.6, -0.9], [26.9, 0.9], [27.25, 0.9], [27.45, -0.55, 'outQuad']]);
      P.lookY = kf(t, [[26.0, -0.2], [26.2, 1, 'outQuad'], [26.6, 0.3], [27.25, 0.3], [27.45, 0.95, 'outQuad']]);
      P.eyeSize = 1 + kf(t, [[27.3, 0], [27.42, 0.4, 'outQuad'], [29.6, 0.3]]); P.squash = 1 + wob(t, 27.4, -0.08, 30, 5); P.hatUp = kf(t, [[27.35, 0], [27.45, 0.8, 'outQuad']]);
      P.armL = P.armR = kf(t, [[27.35, 0.3], [27.45, 0.9, 'outQuad']]) + Math.sin(t * 40) * 0.05 * (t > 27.45 ? 1 : 0);
    }
    P.hatTilt += wob(t, 5.82, 0.3, 14, 5) + wob(t, 13.4, 0.35, 12, 4) + wob(t, 23.0, 0.35, 14, 5) + wob(t, 27.45, 0.2, 14, 4);
    return P;
  }

  // ---------- the shadow ----------
  // mode: attached (projection of Pim with a lag), free-flat (own anchor, projected), standing twin (u -> 1)
  function shadow(t, P) {
    const lag = t < 3.3 ? kf(t, [[0, 0.3], [2.6, 0.34], [3.3, 0.16]]) : t < 5.85 ? 0.16 : t < 9.6 || t >= 23.0 ? 0.0 : 0.25;   // a beat late from the first steps
    const src = pim(Math.max(0, t - lag));
    const S = { pose: Object.assign({}, src), anchor: [P.x, P.y], u: 0, scale: P.s, eyes: 0, face: 'none', alive: false, attached: true, tongue: 0, k: 0.9 };
    S.pose.x = P.x; S.pose.y = P.y;
    if (t >= 3.3 && t < 5.85) {                               // holds the stretch, adds a flourish, then snaps innocent
      const hold = A.seg(t, 4.6, 5.85);
      if (t >= 4.6) { S.pose.armL = S.pose.armR = 2.55 + Math.sin(hold * Math.PI * 4) * 0.2; S.pose.eyeOpen = 0.05; S.pose.squash = 1.15 + Math.sin(hold * Math.PI * 2) * 0.04; S.pose.lean = Math.sin(hold * Math.PI * 2.5) * 0.28 * (1 - A.seg(t, 5.55, 5.8)); }
    }
    if (t >= 9.6 && t < 23.0) {
      S.attached = false;
      const g = kf(t, [[9.6, 0], [10.1, 1, 'inOutQuad']]);          // slithers away from Pim's feet, then hinges up
      const base = { facing: 0.3, squash: 1, lean: 0, armL: 0.3, armR: 0.3, bendL: 0.3, bendR: 0.3, legL: 0, legR: 0, lift: 0, rot: 0, sit: 0, hatUp: 0, hatOff: 0, eyeSize: 1, brows: 0, squint: 0, frontL: false, frontR: false };
      S.pose = Object.assign({}, P, base); S.anchor = [P.x - 235 * g, P.y + 215 * g - Math.sin(g * Math.PI) * 30];
      S.u = kf(t, [[10.1, 0], [10.55, 1, 'outBack']]); S.scale = 1.0 + 0.1 * S.u;
      S.eyes = kf(t, [[10.58, 0], [10.66, 1, 'outBack']]); S.alive = true; S.face = 'mischief'; S.look = [0.9, -0.3];
      S.tongue = kf(t, [[10.82, 0], [10.92, 1, 'outQuad'], [11.3, 1], [11.4, 0]]);
      S.pose.lean = Math.sin((t - 10.82) * 30) * 0.07 * S.tongue; S.pose.squash = 1 + Math.sin((t - 10.82) * 30) * 0.03 * S.tongue;
      S.pose.armL = 0.3 + 1.9 * S.tongue; S.pose.armR = 0.3 + 1.9 * S.tongue; S.pose.bendL = S.pose.bendR = 1.2 * S.tongue;
      const home = [P.x - 235, P.y + 215], edge = [262, 1340];       // one straight dash, left, to the edge of the tree's shade
      if (t >= 11.45) {
        const k = A.ease.inOutQuad(A.seg(t, 11.6, 12.3));
        S.anchor = [home[0] + (edge[0] - home[0]) * k - 12 * A.seg(t, 11.45, 11.6) * (1 - k), home[1] + (edge[1] - home[1]) * k - Math.sin(Math.PI * k) * 40];
        S.pose.facing = -0.9; S.pose.lean = t < 11.6 ? 0.18 * A.seg(t, 11.45, 11.6) : -0.25 * (1 - A.seg(t, 12.2, 12.35));
        if (t >= 11.6 && t < 12.3) { const w = walkLegs(t, 3.4, 0.75); S.pose.legL = w.l; S.pose.legR = w.r; S.pose.lift = -w.bob * 1.5; S.pose.armL = 1.0 + w.l; S.pose.armR = 1.0 + w.r; S.look = [-0.9, 0]; }
        S.scale = 1.1 - 0.12 * A.seg(t, 11.6, 12.3);
      }
      if (t >= 12.3 && t < 14.15) {                           // taunt at the edge of the shade while Pim comes
        S.pose.facing = 0.5; S.pose.armL = S.pose.armR = 2.65 + Math.sin(t * 18) * 0.15; S.pose.lean = Math.sin(t * 12) * 0.12; S.face = 'grin'; S.look = [0.9, -0.2];
      }
      if (t >= 14.0) {                                          // melt: hinge down flat into the shade, held long enough to read
        const m = A.seg(t, 14.05, 14.55);
        S.u = 1 - A.ease.inQuad(m); S.anchor = [262 - 82 * m, 1340 + 140 * m]; S.pose.armL = S.pose.armR = 2.5; S.eyes = 1 - A.seg(t, 14.4, 14.55); S.face = 'grin';
      }
      if (t >= 14.55) { S.u = 0; S.anchor = [180, 1480]; S.eyes = 0; S.hidden = true; }
      if (t >= 16.6 && t < 20.95) {                             // peek from another patch of shade, giggle, watch the dance
        S.eyes = kf(t, [[16.6, 0], [16.75, 1, 'outBack'], [16.85, 0.1], [16.95, 1]]); S.peek = [40, 1600]; S.k = 1.4;
        S.face = t > 17.15 && t < 18.0 ? 'giggle' : 'mischief'; S.giggle = S.face === 'giggle' ? Math.sin(t * 40) * 7 : 0;
        S.look = t > 20.2 ? [0.9, -0.4] : [0.7, -0.5];
      }
      if (t >= 20.85) {                                         // cannot resist: slides out copying the dance
        S.hidden = false; S.peek = null; const c = A.seg(t, 20.85, 22.5);
        const copy = pim(t - 0.28); S.pose = Object.assign({}, copy);
        if (t > 22.6) S.pose = Object.assign({}, pim(22.6 - 0.28));          // caught mid-move when Pim freezes
        S.anchor = [180 + (P.x - 180) * A.ease.inOutQuad(c), 1480 + (P.y + 2 - 1480) * A.ease.inOutQuad(c)];
        S.u = 0; S.eyes = 1; S.k = 1.15; S.face = t < 22.6 ? 'mischief' : 'busted'; S.look = [0.7, -0.6];
        S.scale = 1.0 + 0.05 * (1 - c);
      }
    }
    if (t >= 23.0 && t < 23.6) {                               // stomp: snaps back into place and stays pinned, busted
      S.eyes = 1 - A.seg(t, 23.4, 23.58); S.face = 'busted'; S.alive = true; S.k = 1.15;
      S.pose.squash = 1 + wob(t, 23.0, 0.3, 26, 8);
    }
    if (t >= 26.9) {                                           // the last word: big eyes by Pim's feet, a long wink
      S.eyes = kf(t, [[27.15, 0], [27.3, 1, 'outBack']]); S.alive = true; S.face = t > 27.8 && t < 29.0 ? 'wink' : 'mischief'; S.look = [0.6, -0.8]; S.peek = [P.x - 75, P.y + 70]; S.k = 1.7;
    }
    return S;
  }

  // ---------- drawing: Pim ----------
  function egg(ctx, cx, cy, w, h) {
    ctx.beginPath();
    ctx.moveTo(cx, cy - h / 2);
    ctx.bezierCurveTo(cx + w * 0.47, cy - h / 2, cx + w / 2, cy + h * 0.02, cx + w / 2, cy + h * 0.12);
    ctx.bezierCurveTo(cx + w / 2, cy + h * 0.4, cx + w * 0.27, cy + h / 2, cx, cy + h / 2);
    ctx.bezierCurveTo(cx - w * 0.27, cy + h / 2, cx - w / 2, cy + h * 0.4, cx - w / 2, cy + h * 0.12);
    ctx.bezierCurveTo(cx - w / 2, cy + h * 0.02, cx - w * 0.47, cy - h / 2, cx, cy - h / 2);
    ctx.closePath();
  }

  function paint(ctx, o, fill, stroke = true) {
    if (o.sil) { ctx.fillStyle = o.sil; ctx.fill(); return; }
    ctx.fillStyle = fill; ctx.fill(); if (stroke) { ctx.strokeStyle = PLUM; ctx.lineWidth = 7; ctx.stroke(); }
  }

  function arm(ctx, P, side, o) {
    const a = side > 0 ? P.armR : P.armL, bend = side > 0 ? P.bendR : P.bendL;
    const sx = side * BW * 0.42, sy = -LEG - BH * 0.5;
    const dx = side * Math.sin(a), dy = Math.cos(a);
    const ex = sx + dx * ARM, ey = sy + dy * ARM;
    const cx = (sx + ex) / 2 - dy * side * 30 * bend, cy = (sy + ey) / 2 + dx * side * 30 * bend;
    ctx.beginPath(); ctx.moveTo(sx, sy); ctx.quadraticCurveTo(cx, cy, ex, ey);
    ctx.lineCap = 'round';
    if (o.sil) { ctx.strokeStyle = o.sil; ctx.lineWidth = 22; ctx.stroke(); }
    else { ctx.strokeStyle = PLUM; ctx.lineWidth = 22; ctx.stroke(); ctx.strokeStyle = CREAM; ctx.lineWidth = 9; ctx.stroke(); }
    ctx.beginPath(); ctx.ellipse(ex, ey, 21, 19, a * side, 0, Math.PI * 2); paint(ctx, o, CREAM);
  }

  function leg(ctx, P, side, o) {
    const ang = side > 0 ? P.legR : P.legL;
    ctx.save(); ctx.translate(side * 42, -LEG - 4); ctx.rotate(ang * (P.sit ? 0.2 : 1) - (P.sit ? side * 0.2 : 0));
    const len = LEG + 6;
    ctx.beginPath(); ctx.roundRect(-13, 0, 26, len, 10); paint(ctx, o, PLUM, false);
    ctx.beginPath(); ctx.ellipse(side * 8 + (P.facing * 10), len, 25, 15, 0, 0, Math.PI * 2); paint(ctx, o, PLUM, false);
    ctx.restore();
  }

  function hat(ctx, P, o) {
    if (P.hatOff) return;
    const top = -LEG - BH + 22;
    const tilt = (1 - P.hatUp) * P.hatTilt * (P.facing < -0.2 ? -1 : 1) * (P.facing === 0 ? 1 : 1);
    const L = 175 + 50 * P.hatUp;
    const tipX = Math.sin(tilt) * L * 0.85 + Math.sin(tilt * 1.6) * 40, tipY = top - Math.cos(tilt) * L;
    ctx.beginPath();
    ctx.moveTo(-74, top + 10);
    ctx.quadraticCurveTo(-60 + tipX * 0.2, top - L * 0.55, tipX, tipY);
    ctx.quadraticCurveTo(64 + tipX * 0.45, top - L * 0.4, 74, top + 10);
    ctx.closePath(); paint(ctx, o, RED);
    ctx.beginPath(); ctx.roundRect(-82, top - 6, 164, 34, 16); paint(ctx, o, RED_D);
    if (!o.sil) { ctx.fillStyle = 'rgba(255,241,214,0.85)'; ctx.fillRect(-70, top + 6, 140, 7); }
    ctx.beginPath(); ctx.arc(tipX, tipY, 26, 0, Math.PI * 2); paint(ctx, o, '#FFFFFF');
  }

  function face(ctx, P) {
    const fx = P.facing * 26, fy = -LEG - BH * 0.6;
    for (const side of [-1, 1]) {
      const ex = fx + side * 38, ey = fy, w = 25 * P.eyeSize, h = 31 * P.eyeSize;
      ctx.save();
      ctx.beginPath(); ctx.ellipse(ex, ey, w, h, 0, 0, Math.PI * 2); ctx.fillStyle = '#FFFFFF'; ctx.fill(); ctx.strokeStyle = PLUM; ctx.lineWidth = 5; ctx.stroke();
      ctx.clip();
      if (P.dazed) { ctx.strokeStyle = PLUM; ctx.lineWidth = 5; ctx.beginPath(); for (let k = 0; k < 18; k++) { const r = k * 1.3, a = k * 0.9 + P._t * 9; ctx.lineTo(ex + Math.cos(a) * r, ey + Math.sin(a) * r); } ctx.stroke(); }
      else { const ps = 12 * (P.eyeSize > 1.2 ? 0.75 : 1); ctx.beginPath(); ctx.arc(ex + P.lookX * 11, ey + P.lookY * 13, ps, 0, Math.PI * 2); ctx.fillStyle = PLUM; ctx.fill();
        ctx.beginPath(); ctx.arc(ex + P.lookX * 11 - 4, ey + P.lookY * 13 - 5, 3.5, 0, Math.PI * 2); ctx.fillStyle = '#FFFFFF'; ctx.fill(); }
      const lid = (1 - P.eyeOpen) * 2 * h, low = P.squint * h * 0.9;
      ctx.fillStyle = CREAM;
      if (lid > 0) ctx.fillRect(ex - w - 4, ey - h - 4, w * 2 + 8, lid + 4);
      if (low > 0) ctx.fillRect(ex - w - 4, ey + h - low, w * 2 + 8, low + 4);
      ctx.restore();
      if (lid > 1) { ctx.beginPath(); ctx.moveTo(ex - w, ey - h + lid); ctx.lineTo(ex + w, ey - h + lid); ctx.strokeStyle = PLUM; ctx.lineWidth = 5; ctx.stroke(); }
      if (low > 1) { ctx.beginPath(); ctx.moveTo(ex - w, ey + h - low); ctx.lineTo(ex + w, ey + h - low); ctx.strokeStyle = PLUM; ctx.lineWidth = 5; ctx.stroke(); }
      if (Math.abs(P.brows) > 0.05) {
        ctx.beginPath(); const by = ey - h - 14 - Math.max(0, P.brows) * 10, tilt = -P.brows * side * 12;
        ctx.moveTo(ex - 20, by - tilt); ctx.lineTo(ex + 20, by + tilt); ctx.strokeStyle = PLUM; ctx.lineWidth = 8; ctx.lineCap = 'round'; ctx.stroke();
      }
    }
    const mx = fx, my = fy + 62;
    ctx.fillStyle = PINK; ctx.globalAlpha = 0.75;
    ctx.beginPath(); ctx.ellipse(mx - 66, my - 18, 17, 11, 0, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.ellipse(mx + 66, my - 18, 17, 11, 0, 0, Math.PI * 2); ctx.fill(); ctx.globalAlpha = 1;
    ctx.strokeStyle = PLUM; ctx.lineWidth = 6; ctx.lineCap = 'round'; ctx.beginPath();
    if (P.mouth === 'smile') { ctx.arc(mx, my - 12, 16, 0.2 * Math.PI, 0.8 * Math.PI); ctx.stroke(); }
    else if (P.mouth === 'grin') { ctx.arc(mx, my - 18, 24, 0.1 * Math.PI, 0.9 * Math.PI); ctx.closePath(); ctx.fillStyle = '#7A2E3A'; ctx.fill(); ctx.stroke(); }
    else if (P.mouth === 'flat') { ctx.moveTo(mx - 14, my); ctx.lineTo(mx + 14, my + 2); ctx.stroke(); }
    else if (P.mouth === 'frown') { ctx.arc(mx, my + 14, 15, 1.2 * Math.PI, 1.8 * Math.PI); ctx.stroke(); }
    else if (P.mouth === 'o') { ctx.ellipse(mx, my, 9 + 7 * P.open, 8 + 16 * P.open, 0, 0, Math.PI * 2); ctx.fillStyle = '#7A2E3A'; ctx.fill(); ctx.stroke(); }
  }

  // Pim in local space: origin between the feet, up is -y.
  function body(ctx, P, o) {
    const back = (side) => !(side > 0 ? P.frontR : P.frontL);
    for (const side of [-1, 1]) if (back(side)) arm(ctx, P, side, o);
    leg(ctx, P, -1, o); leg(ctx, P, 1, o);
    egg(ctx, 0, -LEG - BH / 2, BW, BH); paint(ctx, o, CREAM);
    if (!o.sil) { ctx.save(); egg(ctx, 0, -LEG - BH / 2, BW, BH); ctx.clip(); ctx.fillStyle = 'rgba(226,72,58,0.10)'; ctx.fillRect(-BW, -LEG - BH * 0.3, BW * 2, BH); ctx.restore(); }
    if (o.face && !P.back) face(ctx, P);
    if (o.face && P.back && !o.sil) { ctx.strokeStyle = 'rgba(43,27,51,0.35)'; ctx.lineWidth = 5; ctx.beginPath(); ctx.moveTo(0, -LEG - BH * 0.9); ctx.quadraticCurveTo(14, -LEG - BH * 0.5, 0, -LEG - BH * 0.12); ctx.stroke(); }
    hat(ctx, P, o);
    for (const side of [-1, 1]) if (!back(side)) arm(ctx, P, side, o);
  }

  function poseTransform(ctx, P) {             // squash about the feet, lean about the feet, dive rotation about the body centre
    ctx.translate(0, -P.lift);
    ctx.rotate(P.lean);
    if (P.rot) { ctx.translate(0, -LEG - BH / 2); ctx.rotate(P.rot); ctx.translate(0, LEG + BH / 2); }
    if (P.sit) ctx.translate(0, P.sit * 26);
    ctx.scale(P.s / Math.sqrt(P.squash), P.s * P.squash);
  }

  function handPos(P, side) {                  // the mitten in world space, through the same transform chain as poseTransform
    const a = side > 0 ? P.armR : P.armL;
    let x = side * BW * 0.42 + side * Math.sin(a) * ARM, y = -LEG - BH * 0.5 + Math.cos(a) * ARM;
    x *= P.s / Math.sqrt(P.squash); y *= P.s * P.squash; y += P.sit * 26;
    if (P.rot) { y += LEG + BH / 2; const c = Math.cos(P.rot), s = Math.sin(P.rot); [x, y] = [x * c - y * s, x * s + y * c]; y -= LEG + BH / 2; }
    const c = Math.cos(P.lean), sn = Math.sin(P.lean); [x, y] = [x * c - y * sn, x * sn + y * c];
    return [P.x + x, P.y + y - P.lift];
  }

  function drawPim(ctx, P, t) {
    P._t = t;
    ctx.save(); ctx.translate(P.x, P.y); poseTransform(ctx, P); body(ctx, P, { face: true }); ctx.restore();
  }

  // ---------- environment ----------
  function sky(ctx, t, W, H) {
    const n = night(t);
    const g = ctx.createLinearGradient(0, 0, 0, 1150);
    g.addColorStop(0, mix('#3B2A5C', '#0B0F2A', n)); g.addColorStop(0.42, mix('#B9507A', '#18204A', n));
    g.addColorStop(0.75, mix('#F08A5D', '#232A57', n)); g.addColorStop(1, mix('#FFC36B', '#2E2F5C', n));
    ctx.fillStyle = g; ctx.fillRect(-500, -400, W + 1000, 1600);
    for (const s of stars) { ctx.globalAlpha = n * s.a * (0.7 + 0.3 * Math.sin(t * 3 + s.p)); ctx.fillStyle = '#FFF6E0'; ctx.fillRect(s.x, s.y, s.r, s.r); }
    ctx.globalAlpha = 1;
    const sy = sunY(t);
    const glow = ctx.createRadialGradient(470, sy, 40, 470, sy, 420);
    glow.addColorStop(0, `rgba(255,226,154,${0.85 * light(t)})`); glow.addColorStop(1, 'rgba(255,190,110,0)');
    ctx.fillStyle = glow; ctx.fillRect(-200, sy - 440, W + 400, 880);
    ctx.beginPath(); ctx.arc(470, sy, 118, 0, Math.PI * 2); ctx.fillStyle = mix('#FFE7A6', '#FF9A6B', A.seg(t, 23, 26)); ctx.fill();
    ctx.strokeStyle = `rgba(255,236,190,${0.55 * light(t)})`; ctx.lineWidth = 5;
    for (const [y, x0, x1] of [[860, 120, 470], [905, 690, 1010], [960, 40, 300]]) { ctx.beginPath(); ctx.moveTo(x0 + t * 4, y); ctx.lineTo(x1 + t * 4, y); ctx.stroke(); }
  }

  function hills(ctx, t, W) {
    const n = night(t);
    ctx.fillStyle = mix('#8D5C86', '#1E1F44', n); ctx.beginPath(); ctx.moveTo(-500, 1120);
    for (let x = -500; x <= W + 500; x += 40) ctx.lineTo(x, 1085 + Math.sin(x * 0.006) * 28 + Math.sin(x * 0.017) * 9);
    ctx.lineTo(W + 500, 1300); ctx.lineTo(-500, 1300); ctx.closePath(); ctx.fill();
    ctx.fillStyle = mix('#6F7A3C', '#1B2238', n); ctx.beginPath(); ctx.moveTo(-500, 1160);
    for (let x = -500; x <= W + 500; x += 40) ctx.lineTo(x, 1128 + Math.sin(x * 0.004 + 1.3) * 22);
    ctx.lineTo(W + 500, 1300); ctx.lineTo(-500, 1300); ctx.closePath(); ctx.fill();
  }

  function meadow(ctx, t, W, H) {
    const n = night(t);
    const g = ctx.createLinearGradient(0, 1150, 0, H + 600);
    g.addColorStop(0, mix('#D2B75C', '#1E2A3C', n)); g.addColorStop(0.35, mix('#A5B356', '#1A2636', n)); g.addColorStop(1, mix('#5E7F35', '#121C2A', n));
    ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(-500, 1175);
    for (let x = -500; x <= W + 500; x += 40) ctx.lineTo(x, 1160 + Math.sin(x * 0.003 + 0.5) * 14);
    ctx.lineTo(W + 500, H + 800); ctx.lineTo(-500, H + 800); ctx.closePath(); ctx.fill();
    ctx.strokeStyle = mix('#5D7A30', '#0F1824', n); ctx.lineCap = 'round';
    for (const g2 of grass) {
      const sway = Math.sin(t * 1.6 + g2.p) * 3 * g2.s;
      ctx.lineWidth = 4 * g2.s; ctx.beginPath(); ctx.moveTo(g2.x - 8 * g2.s, g2.y); ctx.lineTo(g2.x - 10 * g2.s + sway, g2.y - 18 * g2.s);
      ctx.moveTo(g2.x, g2.y); ctx.lineTo(g2.x + sway, g2.y - 26 * g2.s); ctx.moveTo(g2.x + 8 * g2.s, g2.y); ctx.lineTo(g2.x + 11 * g2.s + sway, g2.y - 16 * g2.s); ctx.stroke();
    }
  }

  const TREE = { x: 215, y: 1192 };
  function treeShape(ctx, o) {                 // local: origin at trunk base, up is -y
    ctx.beginPath(); ctx.moveTo(-26, 0); ctx.lineTo(-18, -300); ctx.lineTo(18, -300); ctx.lineTo(26, 0); ctx.closePath();
    if (o.sil) { ctx.fillStyle = o.sil; ctx.fill(); } else { ctx.fillStyle = '#5A3A3E'; ctx.fill(); ctx.strokeStyle = PLUM; ctx.lineWidth = 7; ctx.stroke(); }
    const blobs = [[0, -420, 150], [-110, -350, 105], [105, -345, 110], [-55, -515, 105], [70, -500, 100]];
    ctx.beginPath(); for (const [x, y, r] of blobs) { ctx.moveTo(x + r, y); ctx.arc(x, y, r, 0, Math.PI * 2); }
    if (o.sil) { ctx.fillStyle = o.sil; ctx.fill(); }
    else { ctx.fillStyle = o.leaf; ctx.strokeStyle = PLUM; ctx.lineWidth = 7; ctx.stroke(); ctx.fill(); }
  }
  function tree(ctx, t) {
    ctx.save(); ctx.translate(TREE.x, TREE.y);
    treeShape(ctx, { leaf: mix('#3E6B3A', '#132033', night(t)) });
    ctx.restore();
  }

  // ---------- shadows ----------
  function project(ctx, ax, ay, dir, u, scale) {  // u=0 flat on the ground along dir, u=1 standing upright
    const c = -dir[0] * (1 - u), d = -dir[1] * (1 - u) + u;
    ctx.transform(scale, 0, c * scale, d * scale, ax, ay);
  }

  function shadows(ctx, t, P, S) {
    const W = ctx.canvas.width, H = ctx.canvas.height;
    if (!layer || layer.width !== W || layer.height !== H) { layer = document.createElement('canvas'); layer.width = W; layer.height = H; lctx = layer.getContext('2d'); }
    lctx.setTransform(1, 0, 0, 1, 0, 0); lctx.clearRect(0, 0, W, H); lctx.setTransform(ctx.getTransform());
    const dir = lightDir(t), sil = { sil: '#000' };
    lctx.save(); project(lctx, TREE.x, TREE.y, dir, 0, 1); treeShape(lctx, sil); lctx.restore();
    const flat = S.attached ? 1 : 1 - S.u;
    if (flat > 0) {
      lctx.save(); project(lctx, S.anchor[0], S.anchor[1], dir, S.attached ? 0 : Math.min(S.u, 0.999), S.scale);
      poseTransform(lctx, Object.assign({}, S.pose, { s: 1 })); lctx.globalAlpha = S.attached ? 1 : flat; body(lctx, S.pose, sil); lctx.restore();
    }
    lctx.setTransform(1, 0, 0, 1, 0, 0); lctx.globalCompositeOperation = 'source-in'; lctx.fillStyle = SHADE; lctx.fillRect(0, 0, W, H); lctx.globalCompositeOperation = 'source-over';
    ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 0.52 * light(t); ctx.drawImage(layer, 0, 0); ctx.restore();
  }

  function twin(ctx, t, S) {                    // the standing dark twin (and the free shadow's eyes)
    const dir = lightDir(t);
    if (!S.attached && S.u > 0.02) {
      ctx.save(); project(ctx, S.anchor[0], S.anchor[1], dir, Math.min(S.u, 1.15), S.scale); poseTransform(ctx, Object.assign({}, S.pose, { s: 1 }));
      ctx.globalAlpha = Math.min(1, S.u * 1.4) * 0.94; body(ctx, S.pose, { sil: '#24152E' }); ctx.globalAlpha = 1;
      if (S.eyes > 0) twinFace(ctx, S, 0, -LEG - BH * 0.6, 1);
      if (S.tongue > 0) { ctx.beginPath(); ctx.ellipse(8, -LEG - BH * 0.6 + 70, 20, 10 + 22 * S.tongue, 0.15, 0, Math.PI); ctx.fillStyle = '#F07A93'; ctx.fill(); }
      ctx.restore();
    }
    let at = null;
    if (S.peek) at = S.peek;
    else if (!S.attached && S.u <= 0.02 && S.eyes > 0) {        // eyes on a flat free shadow: at the projected head, drawn upright
      const hy = -(LEG + BH * 0.6) * S.scale * (S.pose.squash || 1); at = [S.anchor[0] - dir[0] * hy, S.anchor[1] - dir[1] * hy];
    } else if (S.attached && S.eyes > 0) {
      const hy = -(LEG + BH * 0.6) * S.scale; at = [S.anchor[0] - dir[0] * hy, S.anchor[1] - dir[1] * hy];
    }
    if (at && S.eyes > 0) { ctx.save(); ctx.translate(at[0] + (S.giggle || 0), at[1]); twinFace(ctx, S, 0, 0, S.k || 0.9); ctx.restore(); }
  }

  function twinFace(ctx, S, x, y, k) {
    const e = S.eyes, look = S.look || [0.4, 0.2];
    for (const side of [-1, 1]) {
      const ex = x + side * 34 * k, ey = y, w = 21 * k, h = 26 * k * e;
      ctx.save(); ctx.translate(ex, ey);
      if (S.face === 'giggle' || (S.face === 'wink' && side < 0)) {
        ctx.beginPath(); ctx.arc(0, 8 * k, 16 * k, 1.15 * Math.PI, 1.85 * Math.PI); ctx.strokeStyle = '#FFFFFF'; ctx.lineWidth = 7 * k; ctx.lineCap = 'round'; ctx.stroke();
      } else if (S.face === 'busted') {
        ctx.beginPath(); ctx.moveTo(-w, 0); ctx.lineTo(w, 0); ctx.strokeStyle = '#FFFFFF'; ctx.lineWidth = 7 * k; ctx.stroke();
      } else {
        ctx.beginPath(); ctx.ellipse(0, 0, w, Math.max(1, h), side * 0.12, 0, Math.PI * 2); ctx.fillStyle = '#FFFFFF'; ctx.fill();
        if (S.face === 'mischief' || S.face === 'grin') { ctx.fillStyle = '#24152E'; ctx.fillRect(-w - 2, -h - 2, w * 2 + 4, h * 0.55); }
        ctx.beginPath(); ctx.arc(look[0] * 8 * k, look[1] * 8 * k + 3 * k, 7 * k * e, 0, Math.PI * 2); ctx.fillStyle = '#24152E'; ctx.fill();
      }
      ctx.restore();
    }
  }

  function camera(t) {
    const z = kf(t, [[0, 1.0], [3.0, 1.0], [4.4, 1.2], [9.0, 1.2], [10.4, 1.14], [12.0, 1.1], [13.3, 1.0], [14.5, 1.05], [19.9, 1.05], [20.6, 1.0], [22.3, 1.0], [22.8, 1.15], [23.6, 1.18], [24.4, 1.18], [29.6, 1.36]]);
    const fx = kf(t, [[0, 600], [3.0, 600], [4.4, 610], [9.0, 610], [10.4, 560], [12.0, 520], [13.3, 520], [14.5, 300], [19.9, 300], [20.6, 330], [22.3, 360], [22.8, 560], [23.6, 560], [24.4, 580], [29.6, 620]]);
    const fy = kf(t, [[0, 1010], [3.0, 1010], [4.4, 1180], [9.0, 1200], [10.4, 1250], [12.0, 1240], [13.3, 1120], [14.5, 1430], [19.9, 1430], [20.6, 1440], [22.3, 1420], [22.8, 1280], [23.6, 1260], [24.4, 1240], [29.6, 1240]]);
    const jolt = t >= 23.0 && t < 23.1 ? Math.sin((t - 23.0) * 90) * 14 : 0;
    return { z, fx, fy: fy + jolt };
  }

  function dust(ctx, x, y, t, t0, n, rng0, size) {
    if (t < t0 || t > t0 + 0.7) return;
    const u = (t - t0) / 0.7, r = A.rng(rng0);
    for (let i = 0; i < n; i++) {
      const a = Math.PI + r() * Math.PI, sp = (60 + r() * 120) * size;
      ctx.beginPath(); ctx.arc(x + Math.cos(a) * sp * u, y + Math.sin(a) * sp * u * 0.35, Math.max(0, (14 + r() * 12) * size * (1 - u)), 0, Math.PI * 2);
      ctx.fillStyle = `rgba(240,226,190,${0.8 * (1 - u)})`; ctx.fill();
    }
  }

  Atelier.register({
    setup(env) {
      A = env;
      const r = env.rng(7);
      for (let i = 0; i < 190; i++) { const y = 1190 + Math.pow(r(), 0.8) * 1000; grass.push({ x: -400 + r() * 1700, y, s: 0.5 + (y - 1190) / 700, p: r() * 6 }); }
      grass.sort((a, b) => a.y - b.y);
      for (let i = 0; i < 70; i++) stars.push({ x: r() * 1300 - 100, y: r() * 900, r: 2 + r() * 3, a: 0.4 + r() * 0.6, p: r() * 6 });
    },
    render(ctx, env) {
      const t = env.t, W = env.W, H = env.H;
      const cam = camera(t);
      ctx.translate(W / 2, H / 2); ctx.scale(cam.z, cam.z); ctx.translate(-cam.fx, -cam.fy);
      sky(ctx, t, W, H); hills(ctx, t, W); meadow(ctx, t, W, H);
      const P = pim(t), S = shadow(t, P);
      tree(ctx, t);
      shadows(ctx, t, P, S);
      dust(ctx, 230, 1470, t, 15.6, 9, 11, 1.3); dust(ctx, P.x - 30, P.y + 6, t, 23.0, 12, 12, 1.7); dust(ctx, 700, 1236, t, 2.4, 4, 13, 1);
      if (t >= 23.0 && t < 23.2) { const u = (t - 23.0) / 0.2; ctx.save(); ctx.strokeStyle = `rgba(255,246,220,${1 - u})`; ctx.lineWidth = 9; ctx.lineCap = 'round';
        for (let i = 0; i < 7; i++) { const a = Math.PI + 0.2 + i * 0.46, r0 = 70 + 40 * u, r1 = 110 + 90 * u; ctx.beginPath(); ctx.moveTo(P.x - 20 + Math.cos(a) * r0, P.y + Math.sin(a) * r0 * 0.5); ctx.lineTo(P.x - 20 + Math.cos(a) * r1, P.y + Math.sin(a) * r1 * 0.5); ctx.stroke(); } ctx.restore(); }
      if (t >= 14.5 && t < 15.15) { const u = (t - 14.5) / 0.65; ctx.beginPath(); ctx.ellipse(180, 1480, 40 + 140 * u, 14 + 46 * u, 0, 0, Math.PI * 2); ctx.strokeStyle = `rgba(36,21,46,${0.6 * (1 - u)})`; ctx.lineWidth = 8; ctx.stroke(); }
      const twinInFront = !S.attached && S.u > 0.02 && S.anchor[1] > P.y;
      if (!twinInFront) twin(ctx, t, S);
      if (t >= 14.55 && t < 20.05) {                     // the cap as a net: in hand, lands net-down on the shade (empty), tossed back on
        let hx, hy, rot;
        if (t < 15.6) { [hx, hy] = handPos(P, 1); rot = P.armR - Math.PI + P.rot + P.lean; }
        else if (t < 19.85) { const bo = A.ease.outQuad(A.seg(t, 15.6, 16.1)); hx = 230 + 270 * bo; hy = 1480 + 22 * bo - Math.sin(Math.PI * bo) * 120; rot = Math.PI + 2.4 * bo + Math.max(0, wob(t, 16.1, 0.2, 18, 8)); }
        else { const u = A.ease.inOutQuad(A.seg(t, 19.85, 20.05)); hx = 500 + (P.x - 500) * u; hy = 1502 + (P.y - LEG - BH - 20 - 1502) * u - Math.sin(Math.PI * u) * 170; rot = Math.PI + 2.4 + (6.28 - Math.PI - 2.4) * u; }
        ctx.save(); ctx.translate(hx, hy); ctx.rotate(rot);
        ctx.beginPath(); ctx.moveTo(-60, 0); ctx.quadraticCurveTo(-40, -110, 40, -150); ctx.quadraticCurveTo(50, -60, 60, 0); ctx.closePath(); ctx.fillStyle = RED; ctx.fill(); ctx.strokeStyle = PLUM; ctx.lineWidth = 7; ctx.stroke();
        ctx.beginPath(); ctx.roundRect(-68, -8, 136, 26, 12); ctx.fillStyle = RED_D; ctx.fill(); ctx.stroke();
        ctx.beginPath(); ctx.arc(40, -150, 22, 0, Math.PI * 2); ctx.fillStyle = '#FFF'; ctx.fill(); ctx.stroke(); ctx.restore();
      }
      drawPim(ctx, P, t);
      if (twinInFront) twin(ctx, t, S);
      const n = night(t);
      if (n > 0) {                                        // night: everything darkens; eyes still catch the last light
        ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = `rgba(8,10,34,${0.62 * n})`; ctx.fillRect(0, 0, ctx.canvas.width, ctx.canvas.height); ctx.restore();
        if (t > 26.0) { ctx.save(); ctx.translate(P.x, P.y); poseTransform(ctx, P); ctx.globalAlpha = A.seg(t, 26.0, 26.5); face(ctx, Object.assign({}, P, { _t: t })); ctx.restore(); }
        if (S.eyes > 0) twin(ctx, t, S);
      }
    },
  });
})();
