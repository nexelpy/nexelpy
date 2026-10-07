import { qsa, withDelay } from '../core/dom-query.js';

export function setAttr(selector, name, value = '', delay = 0) {
  const els = qsa(selector);
  return withDelay(() => {
    els.forEach(el => { el.setAttribute(name, value); });
  }, delay);
}

export function setAttrs(selector, attrs, delay = 0) {
  const els = qsa(selector);
  return withDelay(() => {
    els.forEach(el => {
      for (const [key, value] of Object.entries(attrs)) {
        el.setAttribute(key, value);
      }
    });
  }, delay);
}

export function removeAttr(selector, name, delay = 0) {
  const els = qsa(selector);
  return withDelay(() => {
    els.forEach(el => { el.removeAttribute(name); });
  }, delay);
}

export function setProps(selector, name, delay = 0) {
  const els = qsa(selector);
  return withDelay(() => {
    els.forEach(el => { el.setAttribute(name, ''); });
  }, delay);
}

export function removeProps(selector, name, delay = 0) {
  const els = qsa(selector);
  return withDelay(() => {
    els.forEach(el => { el.removeAttribute(name); });
  }, delay);
}

export function toggleProps(selector, name, delay = 0) {
  const els = qsa(selector);
  return withDelay(() => {
    els.forEach(el => {
      if (el.hasAttribute(name)) {
        el.removeAttribute(name);
      } else {
        el.setAttribute(name, '');
      }
    });
  }, delay);
}