import { qsa } from '../core/dom-query.js';

// ============================================
// State management
// ============================================

const states = new WeakMap();
const animations = new WeakMap();

function getState(el) {
  if (!states.has(el)) {
    // First time — detect from DOM
    const computed = getComputedStyle(el);
    const collapsed =
      computed.display === 'none' ||
      computed.visibility === 'hidden' ||
      el.offsetHeight === 0;

    states.set(el, { collapsed });
  }
  return states.get(el);
}

function cancelRunning(el) {
  const anim = animations.get(el);
  if (anim) {
    anim.cancel();
    animations.delete(el);
  }
}

function measureHeight(el) {
  // Cancel animation to measure real height
  cancelRunning(el);

  // Force layout
  void el.offsetHeight;

  return el.getBoundingClientRect().height;
}

// ============================================
// slideDown
// ============================================

function slideDownElement(el, duration, delay, ease) {
  const state = getState(el);
  if (!state.collapsed) return Promise.resolve();

  // Capture current visual height (in case of mid-animation)
  const running = animations.get(el);
  const startHeight = running ? el.getBoundingClientRect().height : 0;

  cancelRunning(el);

  // Measure natural height
  const targetHeight = measureHeight(el);

  // Animate
  const anim = el.animate([
    { height: `${startHeight}px`, opacity: 0, overflow: 'hidden' },
    { height: `${targetHeight}px`, opacity: 1, overflow: 'hidden' }
  ], {
    duration,
    delay,
    easing: ease,
    fill: 'forwards'
  });

  animations.set(el, anim);
  state.collapsed = false;

  return anim.finished;
}

// ============================================
// slideUp
// ============================================

function slideUpElement(el, duration, delay, ease) {
  const state = getState(el);
  if (state.collapsed) return Promise.resolve();

  const startHeight = el.getBoundingClientRect().height;

  cancelRunning(el);

  const anim = el.animate([
    { height: `${startHeight}px`, opacity: 1, overflow: 'hidden' },
    { height: '0px', opacity: 0, overflow: 'hidden' }
  ], {
    duration,
    delay,
    easing: ease,
    fill: 'forwards'
  });

  animations.set(el, anim);
  state.collapsed = true;

  return anim.finished;
}

// ============================================
// slideToggle
// ============================================

function slideToggleElement(el, duration, delay, ease) {
  const state = getState(el);

  if (state.collapsed) {
    return slideDownElement(el, duration, delay, ease);
  } else {
    return slideUpElement(el, duration, delay, ease);
  }
}

// ============================================
// Public API
// ============================================

export function slideDown(selector, duration = 300, delay = 0, ease = 'ease') {
  const promises = [];
  qsa(selector).forEach(el => {
    promises.push(slideDownElement(el, duration, delay, ease));
  });
  return Promise.all(promises);
}

export function slideUp(selector, duration = 300, delay = 0, ease = 'ease') {
  const promises = [];
  qsa(selector).forEach(el => {
    promises.push(slideUpElement(el, duration, delay, ease));
  });
  return Promise.all(promises);
}

export function slideToggle(selector, duration = 300, delay = 0, ease = 'ease') {
  const promises = [];
  qsa(selector).forEach(el => {
    promises.push(slideToggleElement(el, duration, delay, ease));
  });
  return Promise.all(promises);
}