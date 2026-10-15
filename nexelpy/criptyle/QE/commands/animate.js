import { qsa } from '../core/dom-query.js';

export const animate = async (selector, css, delay = 0, duration = 300, ease = 'ease') => {
    const elements = qsa(selector);
    if (!elements.length) return;

    const animations = elements.map((el) => {
        return el.animate([{}, css], {
            delay: Number(delay) || 0,
            duration: Number(duration) || 300,
            easing: ease || 'ease',
            fill: 'forwards'
        }).finished.catch(() => {});
    });

    await Promise.all(animations);
};
