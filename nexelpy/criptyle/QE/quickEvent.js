import { runEffects } from './runner.js';

const ALLOWED_EVENTS = [
  'click', 'dblclick',
  'keyup', 'keydown',
  'change', 'input', 'submit',
  'focus', 'blur',
  'mouseenter', 'mouseleave','tick'
];

// ============================================
// Register event listeners
// ============================================

ALLOWED_EVENTS.forEach(eventType => {
  document.addEventListener(eventType, async (e) => {
    const el = e.target instanceof Element ? e.target : e.target.parentElement;
    if (!el) return;

    const target = el.closest(`[${eventType}]`);
    if (!target) return;

    e.preventDefault();

    const effectsStr = target.getAttribute(eventType);
    if (!effectsStr) return;

    let effects;
    try {
      effects = JSON.parse(effectsStr);
    } catch (err) {
      console.error(`Invalid JSON in "${eventType}": ${err.message}`);
      return;
    }

    try {
      await runEffects(effects, {
        element: target,
        event: e
      });
    } catch (err) {
      console.error(`runEffects error: ${err.message}`);
    }
  });
});

// ============================================
// loadDom
// ============================================

async function initLoadDom() {
  const els = document.querySelectorAll('[loadDom]');

  for (const el of els) {
    const effectsStr = el.getAttribute('loadDom');
    if (!effectsStr) continue;

    let effects;
    try {
      effects = JSON.parse(effectsStr);
    } catch (err) {
      console.error(`Invalid JSON in "loadDom": ${err.message}`);
      continue;
    }

    try {
      await runEffects(effects, { element: el });
    } catch (err) {
      console.error(`runEffects error (loadDom): ${err.message}`);
    }
  }
}

if (document.readyState === 'complete') {
  initLoadDom();
} else {
  window.addEventListener('load', initLoadDom);
}