import { qsa } from '../core/dom-query.js';

export function log(value) {
  console.log(value);
}

export function redirect(url) {
  location.href = url;
}

export function reload() {
  location.reload();
}

export function scrollTo(target) {
  if (typeof target === 'number') {
    window.scrollTo({ top: target, behavior: 'smooth' });
  } else {
    const el = qsa(target)[0];
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  }
}

export function focus(selector) {
  const el = qsa(selector)[0];
  if (el) el.focus();
}