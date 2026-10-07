import { qsa, withDelay } from '../core/dom-query.js';

export function addClass(selector, className, delay = 0) {
  if (!className) return;
  const els = qsa(selector);
  return withDelay(() => {
    els.forEach(el => { el.classList.add(className); });
  }, delay);
}

export function removeClass(selector, className, delay = 0) {
  if (!className) return;
  const els = qsa(selector);
  return withDelay(() => {
    els.forEach(el => { el.classList.remove(className); });
  }, delay);
}

export function toggleClass(selector, className, delay = 0) {
  if (!className) return;
  const els = qsa(selector);
  return withDelay(() => {
    els.forEach(el => { el.classList.toggle(className); });
  }, delay);
}

export function setClass(selector, className, delay = 0) {
  const els = qsa(selector);
  return withDelay(() => {
    els.forEach(el => { el.className = className; });
  }, delay);
}