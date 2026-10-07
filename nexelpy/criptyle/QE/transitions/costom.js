export async function custom(el, args, doChange) {
  const [step1, step2, duration = 300] = args;

  // Only step1
  if (step1 && step2 === undefined) {
    await el.animate([
      {},
      step1
    ], {
      duration,
      easing: 'ease',
      fill: 'forwards'
    }).finished;

    // Change content
    if (doChange) doChange();

    el.getAnimations().forEach(a => a.cancel());
    return;
  }

  const half = duration / 2;

  // Step 1
  if (step1) {
    await el.animate([
      {},
      step1
    ], {
      duration: half,
      easing: 'ease',
      fill: 'forwards'
    }).finished;
  }

  // Change content
  if (doChange) doChange();

  // Step 2
  if (step2) {
    await el.animate([
      {},
      step2
    ], {
      duration: half,
      easing: 'ease',
      fill: 'forwards'
    }).finished;
  }

  el.getAnimations().forEach(a => a.cancel());
}