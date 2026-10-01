/* Motif v1 motion vocabulary. All actions write to a paused, seekable GSAP timeline. */
window.MotifMotion = {
  POP_IN(tl, target, at, { duration = 0.28, scale = 1, overshoot = 1.13 } = {}) {
    tl.fromTo(target, { opacity: 0, scale: 0.25 },
      { opacity: 1, scale: scale * overshoot, duration: duration * 0.68, ease: 'power3.out', immediateRender: false }, at);
    tl.to(target, { scale, duration: duration * 0.32, ease: 'power2.inOut' }, at + duration * 0.68);
  },
  POP_OUT(tl, target, at, { duration = 0.2 } = {}) {
    tl.to(target, { scale: 0.2, opacity: 0, duration, ease: 'power2.in' }, at);
  },
  SLIDE(tl, target, at, { fromX, toX, fromY = 0, toY = 0, duration = 0.6, ease = 'power2.inOut' }) {
    tl.fromTo(target, { x: fromX, y: fromY },
      { x: toX, y: toY, duration, ease, immediateRender: false }, at);
  },
  DROP(tl, target, at, { x, y, duration = 0.4, rotation = 12 } = {}) {
    tl.to(target, { x, y, rotation, duration: duration * 0.82, ease: 'power2.in' }, at);
    tl.to(target, { y: y - 15, scaleY: 0.88, scaleX: 1.06, duration: duration * 0.10, ease: 'power2.out' }, at + duration * 0.82);
    tl.to(target, { y, scaleY: 1, scaleX: 1, duration: duration * 0.08, ease: 'power2.in' }, at + duration * 0.92);
  },
  STAMP(tl, target, at, { duration = 0.42, fromY = -180 } = {}) {
    tl.fromTo(target, { y: fromY, scale: 1.12, opacity: 0 },
      { y: 13, scale: 0.92, opacity: 1, duration: duration * 0.52, ease: 'power3.in', immediateRender: false }, at);
    tl.to(target, { y: -12, scale: 1.045, duration: duration * 0.23, ease: 'power2.out' }, at + duration * 0.52);
    tl.to(target, { y: 0, scale: 1, duration: duration * 0.25, ease: 'power2.inOut' }, at + duration * 0.75);
  },
  BOUNCE(tl, target, at, { height = 17, duration = 0.25 } = {}) {
    tl.to(target, { y: -height, duration: duration * 0.47, ease: 'power2.out' }, at);
    tl.to(target, { y: 0, duration: duration * 0.53, ease: 'power2.in' }, at + duration * 0.47);
  },
  WOBBLE(tl, target, at, { angle = 6, duration = 0.42 } = {}) {
    tl.to(target, { rotation: angle, duration: duration * .24, ease: 'power2.out' }, at);
    tl.to(target, { rotation: -angle * .57, duration: duration * .28, ease: 'power2.inOut' }, at + duration * .24);
    tl.to(target, { rotation: angle * .24, duration: duration * .23, ease: 'power2.inOut' }, at + duration * .52);
    tl.to(target, { rotation: 0, duration: duration * .25, ease: 'power2.out' }, at + duration * .75);
  },
  SHAKE(tl, target, at, { distance = 13, duration = 0.32 } = {}) {
    tl.to(target, { x: -distance, duration: duration * .22, ease: 'power1.inOut' }, at);
    tl.to(target, { x: distance * .82, duration: duration * .27, ease: 'power1.inOut' }, at + duration * .22);
    tl.to(target, { x: -distance * .38, duration: duration * .27, ease: 'power1.inOut' }, at + duration * .49);
    tl.to(target, { x: 0, duration: duration * .24, ease: 'power1.out' }, at + duration * .76);
  },
  SQUASH(tl, target, at, { amount = .87, duration = .18 } = {}) {
    tl.to(target, { scaleY: amount, scaleX: 2 - amount, duration: duration * .45, ease: 'power2.in' }, at);
    tl.to(target, { scaleY: 1, scaleX: 1, duration: duration * .55, ease: 'back.out(1.7)' }, at + duration * .45);
  },
  STRETCH(tl, target, at, { amount = 1.1, duration = .18 } = {}) {
    tl.to(target, { scaleY: amount, scaleX: 2 - amount, duration: duration * .45, ease: 'power2.out' }, at);
    tl.to(target, { scaleY: 1, scaleX: 1, duration: duration * .55, ease: 'power2.inOut' }, at + duration * .45);
  },
  CAMERA_PUSH(tl, target, at, { scale = 1.05, duration = .7 } = {}) {
    tl.to(target, { scale, duration, ease: 'power2.inOut' }, at);
  },
  CAMERA_PULL(tl, target, at, { scale = 1, duration = .55 } = {}) {
    tl.to(target, { scale, duration, ease: 'power2.inOut' }, at);
  }
};
