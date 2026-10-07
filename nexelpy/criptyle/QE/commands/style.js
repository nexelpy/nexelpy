import { qsa, withDelay } from '../core/dom-query.js';

export function addStyle(selector, styles, delay = 0) {
  const els = qsa(selector);
  return withDelay(() => {
    els.forEach(el => {
      for (const [key, value] of Object.entries(styles)) {
        el.style[key] = value;
      }
    });
  }, delay);
}

export function removeStyle(selector, key, delay = 0) {
  const els = qsa(selector);
  return withDelay(() => {
    els.forEach(el => { el.style[key] = ''; });
  }, delay);
}

export function setStyle(selector, styles, delay = 0) {
  const els = qsa(selector);
  return withDelay(() => {
    els.forEach(el => {
      el.style.cssText = '';
      for (const [key, value] of Object.entries(styles)) {
        el.style[key] = value;
      }
    });
  }, delay);
}