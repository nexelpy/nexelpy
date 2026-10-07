import { qsa } from '../core/dom-query.js';

// ============================================
// Animation presets
// ============================================
const ANIMATIONS = {
  fade: {
    in:  [{ opacity: 0 }, { opacity: 1 }],
    out: [{ opacity: 1 }, { opacity: 0 }]
  },
  zoom: {
    in:  [{ opacity: 0, transform: 'scale(0.8)' }, { opacity: 1, transform: 'scale(1)' }],
    out: [{ opacity: 1, transform: 'scale(1)' }, { opacity: 0, transform: 'scale(0.8)' }]
  },
  slideDown: {
    in:  [{ opacity: 0, transform: 'translateY(-60px)' }, { opacity: 1, transform: 'translateY(0)' }],
    out: [{ opacity: 1, transform: 'translateY(0)' }, { opacity: 0, transform: 'translateY(-60px)' }]
  },
  slideUp: {
    in:  [{ opacity: 0, transform: 'translateY(60px)' }, { opacity: 1, transform: 'translateY(0)' }],
    out: [{ opacity: 1, transform: 'translateY(0)' }, { opacity: 0, transform: 'translateY(60px)' }]
  },
  slideLeft: {
    in:  [{ opacity: 0, transform: 'translateX(-60px)' }, { opacity: 1, transform: 'translateX(0)' }],
    out: [{ opacity: 1, transform: 'translateX(0)' }, { opacity: 0, transform: 'translateX(-60px)' }]
  },
  slideRight: {
    in:  [{ opacity: 0, transform: 'translateX(60px)' }, { opacity: 1, transform: 'translateX(0)' }],
    out: [{ opacity: 1, transform: 'translateX(0)' }, { opacity: 0, transform: 'translateX(60px)' }]
  },
  none: {
    in:  null,
    out: null
  }
};

// ============================================
// showModal
// ============================================

export function showModal(selector, delay = 0, duration = 0, type = 'none', closeOnBackdrop = true) {
  qsa(selector).forEach(el => {
    if (!(el instanceof HTMLDialogElement)) return;
    if (el.open) return;

    el.showModal();

    // Animate
    const preset = ANIMATIONS[type] || ANIMATIONS.none;
    if (preset.in && duration > 0) {
      el.animate(preset.in, {
        duration,
        delay,
        easing: 'ease',
        fill: 'forwards'
      });
    }

    // Close on backdrop
    if (closeOnBackdrop !== false && closeOnBackdrop !== 'false') {
      el.addEventListener('click', function handler(e) {
        if (e.target === el) {
          hideModal(selector, 0, duration, type);
          el.removeEventListener('click', handler);
        }
      });
    }
  });
}

// ============================================
// hideModal
// ============================================

export function hideModal(selector, delay = 0, duration = 0, type = 'none') {
  qsa(selector).forEach(el => {
    if (!(el instanceof HTMLDialogElement) || !el.open) return;

    const preset = ANIMATIONS[type] || ANIMATIONS.none;

    if (!preset.out || duration === 0) {
      el.close();
      return;
    }

    const anim = el.animate(preset.out, {
      duration,
      delay,
      easing: 'ease',
      fill: 'forwards'
    });

    anim.finished.then(() => el.close());
  });
}