/* Motif Atelier playback runtime: the only contract between a film and the renderer.
 *
 * A film registers itself with Atelier.register({setup?, render}). The renderer
 * loads player.html, waits for window.__atelierReady, then calls Atelier.seek(n)
 * for each frame in any order and captures the canvas. render(ctx, env) must
 * draw frame env.frame from scratch: no state carried between calls, no clocks,
 * no unseeded randomness. Math.random, Date.now and performance.now are
 * disabled so a film that depends on them fails loudly instead of drifting.
 */
(function () {
  'use strict';
  const films = [];
  const fail = (name) => () => { throw new Error(name + ' is disabled in Atelier films: use env.rng(seed) and env.t'); };
  Math.random = fail('Math.random');
  Date.now = fail('Date.now');
  performance.now = fail('performance.now');

  function rng(seed) {                       // mulberry32: small, seedable, stable across engines
    let a = (seed >>> 0) || 1;
    return function () {
      a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const lerp = (a, b, t) => a + (b - a) * t;
  const seg = (t, a, b) => clamp((t - a) / (b - a));   // progress of t through [a, b]
  const ease = {
    linear: (t) => t,
    inQuad: (t) => t * t, outQuad: (t) => 1 - (1 - t) * (1 - t),
    inOutQuad: (t) => (t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2),
    inCubic: (t) => t * t * t, outCubic: (t) => 1 - Math.pow(1 - t, 3),
    inOutCubic: (t) => (t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
    inOutSine: (t) => -(Math.cos(Math.PI * t) - 1) / 2,
    outBack: (t, s = 1.70158) => 1 + (s + 1) * Math.pow(t - 1, 3) + s * Math.pow(t - 1, 2),
    inBack: (t, s = 1.70158) => (s + 1) * t * t * t - s * t * t,
    outElastic: (t) => (t === 0 || t === 1 ? t : Math.pow(2, -10 * t) * Math.sin((t * 10 - .75) * (2 * Math.PI) / 3) + 1),
  };

  const state = { film: null, manifest: null, timing: null, ctx: null, scale: 1, images: {} };

  function env(frame) {
    const m = state.manifest;
    return {
      frame, fps: m.fps, t: frame / m.fps, frames: m.frames, W: m.design[0], H: m.design[1],
      moments: m.moments || {}, timing: state.timing, images: state.images, manifest: m,
      rng, clamp, lerp, seg, ease,
      at: (name) => { const v = (m.moments || {})[name]; if (v === undefined) throw new Error('unknown moment ' + name); return v / m.fps; },
    };
  }

  async function boot() {
    try {
      const q = new URLSearchParams(location.search);
      const w = +q.get('w'), h = +q.get('h');
      state.manifest = await (await fetch('/film.json')).json();
      state.timing = await (await fetch('/__atelier/timing.json')).json();
      const canvas = document.getElementById('film');
      canvas.width = w; canvas.height = h;
      state.ctx = canvas.getContext('2d', { alpha: false });
      state.scale = w / state.manifest.design[0];
      for (const font of state.manifest.fonts || []) {
        const face = new FontFace(font.family, 'url(/' + font.path + ')', { weight: String(font.weight || 400) });
        document.fonts.add(await face.load());
      }
      for (const [name, path] of Object.entries(state.manifest.images || {})) {
        const img = new Image(); img.src = '/' + path; await img.decode(); state.images[name] = img;
      }
      await new Promise((resolve, reject) => {
        const s = document.createElement('script');
        s.src = '/' + state.manifest.entry; s.onload = resolve; s.onerror = () => reject(new Error('film entry failed to load'));
        document.head.appendChild(s);
      });
      if (films.length !== 1) throw new Error('a film must register exactly once, got ' + films.length);
      state.film = films[0];
      if (state.film.setup) await state.film.setup(env(0));
      window.__atelierReady = true;
    } catch (e) {
      window.__atelierError = String(e && e.stack || e);
    }
  }

  function seek(n) {
    if (!Number.isInteger(n) || n < 0 || n >= state.manifest.frames) throw new Error('frame out of range: ' + n);
    const ctx = state.ctx;
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over'; ctx.filter = 'none';
    ctx.fillStyle = '#000'; ctx.fillRect(0, 0, ctx.canvas.width, ctx.canvas.height);
    ctx.setTransform(state.scale, 0, 0, state.scale, 0, 0);
    // A film that leaves save/restore unbalanced would leak transforms into the rest of its own frame; fail it loudly.
    const save = ctx.save, restore = ctx.restore;let depth = 0;
    ctx.save = function () { depth++; return save.call(ctx); };
    ctx.restore = function () { if (--depth < 0) throw new Error('frame ' + n + ': restore() without a matching save()'); return restore.call(ctx); };
    save.call(ctx);                     // every frame starts from the same context state, whatever the last frame set
    try { state.film.render(ctx, env(n)); } finally { ctx.save = save; ctx.restore = restore; restore.call(ctx); }
    if (depth !== 0) throw new Error('frame ' + n + ': ' + depth + ' save() without restore()');
    return true;
  }

  window.Atelier = { register: (film) => films.push(film), boot, seek, rng, clamp, lerp, seg, ease };
})();
