export function qsa(selector) {
  if (selector instanceof Element) return [selector];
  if (typeof selector === 'string') return document.querySelectorAll(selector);
  return [];
}

export function withDelay(run, delay = 0) {
  if (delay > 0) {
    return new Promise(resolve => {
      setTimeout(() => {
        run();
        resolve();
      }, delay);
    });
  }
  run();
}