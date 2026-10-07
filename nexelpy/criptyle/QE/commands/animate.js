import { qsa } from '../core/dom-query.js';

export function animate(selector, css, delay = 0, duration = 300, ease = 'ease') {
  const promises = [];

  qsa(selector).forEach(el => {
    const anim = el.animate([{}, css], {
      delay,
      duration,
      easing: ease,
      fill: 'forwards'
    });

    promises.push(anim.finished);
  });

  return Promise.all(promises);
}