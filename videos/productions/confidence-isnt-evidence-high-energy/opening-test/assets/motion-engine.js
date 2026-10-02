/* Motif event compiler v0.1. JSON is the executable motion source. */
(function () {
  const primitiveNames = new Set([
    'POP_IN', 'POP_OUT', 'SLIDE', 'DROP', 'STAMP', 'BOUNCE', 'WOBBLE',
    'SHAKE', 'SQUASH', 'STRETCH', 'CAMERA_PUSH', 'CAMERA_PULL'
  ]);
  const allActions = new Set([...primitiveNames, 'SET', 'TWEEN', 'FROM_TO', 'PULSE', 'POSE_SWAP', 'SCENE_CUT', 'CAPTION_REPLACE']);

  function hasTarget(selector) {
    return typeof selector === 'string' && !!document.querySelector(selector);
  }

  function validateEvent(event, index, durationSec) {
    const { time, target, action, params = {} } = event;
    if (!Number.isFinite(time) || time < 0 || time > durationSec) {
      throw new Error(`Event ${index} has invalid time: ${time}`);
    }
    if (!hasTarget(target)) throw new Error(`Event ${index} has missing target: ${target}`);
    if (!allActions.has(action)) throw new Error(`Event ${index} uses unsupported action: ${action}`);
    if (!params || typeof params !== 'object' || Array.isArray(params)) {
      throw new Error(`Event ${index} needs a params object`);
    }
    if (action === 'SLIDE' && (!Number.isFinite(params.fromX) || !Number.isFinite(params.toX))) {
      throw new Error(`Event ${index} SLIDE needs numeric fromX and toX`);
    }
    if (action === 'DROP' && (!Number.isFinite(params.x) || !Number.isFinite(params.y))) {
      throw new Error(`Event ${index} DROP needs numeric x and y`);
    }
    if ((action === 'POSE_SWAP' || action === 'SCENE_CUT') &&
        (!hasTarget(params.hide) || !hasTarget(params.show) ||
         (params.bounceTarget && !hasTarget(params.bounceTarget)))) {
      throw new Error(`Event ${index} ${action} has missing hide/show/bounce target`);
    }
    if (action === 'SET' && (!params.props || typeof params.props !== 'object')) {
      throw new Error(`Event ${index} SET needs props`);
    }
    if (action === 'TWEEN' && (!params.to || typeof params.to !== 'object')) {
      throw new Error(`Event ${index} TWEEN needs to`);
    }
    if (action === 'FROM_TO' && (!params.from || !params.to)) {
      throw new Error(`Event ${index} FROM_TO needs from and to`);
    }
  }

  function compile(spec, compositionId) {
    if (!spec || spec.schemaVersion !== '1.0' || !Number.isFinite(spec.durationSec) ||
        spec.durationSec <= 0 || !Array.isArray(spec.events) || !Array.isArray(spec.initial)) {
      throw new Error('Motif event spec must contain initial and events arrays');
    }
    const tl = gsap.timeline({ paused: true });
    for (const item of spec.initial) {
      if (!hasTarget(item.target)) {
        throw new Error(`Missing initial-state target: ${item.target}`);
      }
      gsap.set(item.target, item.props || {});
    }
    spec.events.forEach((event, index) => validateEvent(event, index, spec.durationSec));
    const sorted = [...spec.events].sort((a, b) => a.time - b.time);
    for (const event of sorted) {
      const { time, target, action, params = {} } = event;
      if (primitiveNames.has(action)) {
        window.MotifMotion[action](tl, target, time, params);
      } else if (action === 'SET') {
        tl.set(target, params.props || {}, time);
      } else if (action === 'TWEEN') {
        tl.to(target, { ...(params.to || {}), duration: params.duration ?? 0.3,
          ease: params.ease || 'power2.out' }, time);
      } else if (action === 'FROM_TO') {
        tl.fromTo(target, params.from || {}, { ...(params.to || {}),
          duration: params.duration ?? 0.3, ease: params.ease || 'power2.out',
          immediateRender: false }, time);
      } else if (action === 'PULSE') {
        const peak = params.peak ?? 1;
        const rise = params.rise ?? 0.1;
        const fall = params.fall ?? 0.16;
        tl.to(target, { opacity: peak, duration: rise, ease: 'power2.out' }, time);
        tl.to(target, { opacity: 0, duration: fall, ease: 'power2.in' }, time + rise);
      } else if (action === 'CAPTION_REPLACE') {
        // A single caption slot: clear every previous card before showing the
        // next one. Cards keep their fixed center and baseline in the SVG.
        tl.set('.caption-card', { opacity: 0, scale: 1 }, time);
        tl.set(target, { opacity: 1, scale: 1 }, time);
      } else if (action === 'POSE_SWAP' || action === 'SCENE_CUT') {
        tl.set(params.hide, { opacity: 0 }, time);
        tl.set(params.show, { opacity: 1 }, time);
        if (params.bounceTarget) {
          window.MotifMotion.BOUNCE(tl, params.bounceTarget, time, {
            height: params.height ?? 16, duration: params.duration ?? 0.28
          });
        }
      }
    }
    window.__timelines[compositionId] = tl;
    tl.seek(0);
    return tl;
  }

  window.MotifEventEngine = { compile, actions: [...allActions] };
})();
