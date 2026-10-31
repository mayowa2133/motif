// Smoke film: fall (ease in), squash on the contact frame, settle.
Atelier.register({
  render(ctx, env) {
    const { W, H, frame, ease, seg } = env;
    const land = env.moments.land;
    ctx.fillStyle = '#F2E8D5'; ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = '#2B2B2B'; ctx.fillRect(0, 1500, W, 8);
    const fall = ease.inQuad(seg(frame, 0, land));
    const y = 300 + (1500 - 120 - 300) * fall;
    const squash = frame >= land ? 1 - 0.35 * Math.exp(-(frame - land) / 3) * Math.cos((frame - land) / 2) : 1 + 0.25 * fall;
    ctx.save(); ctx.translate(W / 2, frame >= land ? 1500 : y + 120);
    ctx.scale(1 / Math.sqrt(squash), squash);
    ctx.fillStyle = '#E8682A'; ctx.beginPath(); ctx.arc(0, -120, 120, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
  },
});
