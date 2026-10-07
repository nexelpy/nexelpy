export async function fade(el, args, doChange) {
  const [duration = 300, custom] = args;
  const half = duration / 2;
  const originalColor = getComputedStyle(el).color;

  // Out
  const outAnim = el.animate([
    {},
    { color: 'transparent', ...(custom || {}) }
  ], {
    duration: half,
    fill: 'forwards'
  });

  await outAnim.finished;
  outAnim.cancel();   // ← اضافه شد

  doChange();

  // In
  await el.animate([
    { color: 'transparent', ...(custom || {}) },
    { color: originalColor, ...(custom || {}) }
  ], {
    duration: half,
    fill: 'forwards'
  }).finished;

  el.getAnimations().forEach(a => a.cancel());
}