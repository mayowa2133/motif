/* Seek-safe optimization for finite Motif SET/innerHTML frame sequences.
   Agent-authored bounded lookup; delegates timeline ownership to existing engine.
   No clocks, asynchronous work, model code, network or runtime randomness. */
(function () {
  const engine = window.MotifEventEngine;
  if (!engine) throw new Error('Motif event engine must load first');
  engine.compileFrames = function (spec, id) {
    if (spec.schemaVersion !== '1.0' || spec.fps !== 30 ||
        !Number.isFinite(spec.durationSec) || spec.durationSec <= 0 ||
        spec.initial.length !== 1) throw new Error('Invalid finite frame sequence');
    const target = spec.initial[0].target;
    const el = document.querySelector(target);
    const first = spec.initial[0].props.innerHTML;
    if (!el || typeof first !== 'string') throw new Error('Missing frame target/state');
    const frames = [first];
    const count = Math.ceil(spec.durationSec * spec.fps - 1e-6);
    spec.events.forEach(function (e, i) {
      if (e.action !== 'SET' || e.target !== target ||
          Math.abs(e.time - (i + 1) / spec.fps) > 1e-6 ||
          Object.keys(e.params.props).join(',') !== 'innerHTML' ||
          typeof e.params.props.innerHTML !== 'string') {
        throw new Error('Only contiguous explicit SET frame states are supported');
      }
      frames.push(e.params.props.innerHTML);
    });
    if (frames.length !== count) throw new Error('Frame table does not cover duration');
    // The established compiler supplies the only paused timeline. A harmless
    // child opacity lane supplies its full duration; the lookup is idempotent.
    const tl = engine.compile({schemaVersion:'1.0', durationSec:spec.durationSec,
      initial:spec.initial, events:[{time:0,target:target,action:'TWEEN',
      params:{to:{opacity:1},duration:spec.durationSec,ease:'none'}}]}, id);
    let last = -1;
    function applyFrame() {
      const frame = Math.max(0, Math.min(frames.length - 1,
        Math.floor(tl.time() * spec.fps + 1e-5)));
      if (frame !== last) {el.innerHTML = frames[frame];last = frame;}
    }
    tl.eventCallback('onUpdate', applyFrame);
    applyFrame();
    return tl;
  };
})();
