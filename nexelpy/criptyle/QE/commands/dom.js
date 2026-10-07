
import { qsa, withDelay } from '../core/dom-query.js';
import { runTransition } from '../transitions/index.js';

export function setText(selector, text, delay = 0, transition) {
  const els = qsa(selector);

  els.forEach(el => {
    const doChange = () => { el.textContent = text; };

    if (transition) {
      runTransition(el, transition, delay, doChange);
    } else {
      if (delay > 0) {
        setTimeout(doChange, delay);
      } else {
        doChange();
      }
    }
  });
}

export function appendText(selector, text, delay = 0) {
  const els = qsa(selector);
  return withDelay(() => {
    els.forEach(el => { el.textContent += text; });
  }, delay);
}

export function prependText(selector, text, delay = 0) {
  const els = qsa(selector);
  return withDelay(() => {
    els.forEach(el => { el.textContent = text + el.textContent; });
  }, delay);
}

export function setHtml(selector, html, delay = 0) {
  const els = qsa(selector);
  return withDelay(() => {
    els.forEach(el => { el.innerHTML = html; });
  }, delay);
}

export function appendHtml(selector, html, delay = 0) {
  const els = qsa(selector);
  return withDelay(() => {
    els.forEach(el => { el.insertAdjacentHTML('beforeend', html); });
  }, delay);
}

export function prependHtml(selector, html, delay = 0) {
  const els = qsa(selector);
  return withDelay(() => {
    els.forEach(el => { el.insertAdjacentHTML('afterbegin', html); });
  }, delay);
}

export function setValue(selector, value, delay = 0) {
  const els = qsa(selector);
  return withDelay(() => {
    els.forEach(el => { el.value = value; });
  }, delay);
}