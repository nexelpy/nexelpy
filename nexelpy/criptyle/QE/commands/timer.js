import { qsa } from '../core/dom-query.js';
import { SKIP } from '../core/skip.js';

// ============================================
// State
// ============================================
const timers = new WeakMap();

// ============================================
// Units
// ============================================
const UNIT_KEYS = ['y', 'M', 'w', 'd', 'h', 'm', 's'];

const UNIT_FACTORS = {
  s: 1000,
  m: 60 * 1000,
  h: 60 * 60 * 1000,
  d: 24 * 60 * 60 * 1000,
  w: 7 * 24 * 60 * 60 * 1000,
  M: 30 * 24 * 60 * 60 * 1000,
  y: 365 * 24 * 60 * 60 * 1000
};

// ============================================
// Parse time string
// "1:30"     → 1 minute 30 seconds
// "8:15:00"  → 8 hours 15 minutes
// "y:M:w:d:h:m:s" (7 parts)
// ============================================
function parseTime(str) {
  const parts = String(str).split(':').map(Number);

  if (parts.some(isNaN)) {
    throw new Error(`setTimer: invalid time format "${str}"`);
  }

  if (parts.length > 7) {
    throw new Error(`setTimer: too many parts in "${str}" (max 7)`);
  }

  const result = { s: 0, m: 0, h: 0, d: 0, w: 0, M: 0, y: 0 };
  const offset = UNIT_KEYS.length - parts.length;

  for (let i = 0; i < parts.length; i++) {
    result[UNIT_KEYS[offset + i]] = parts[i];
  }

  let totalMs = 0;
  for (const key of UNIT_KEYS) {
    totalMs += result[key] * UNIT_FACTORS[key];
  }

  return totalMs;
}
// ============================================
// Format ms → { y, M, w, d, h, m, s, ms }
// ============================================
function formatMs(totalMs) {
  let rest = Math.max(0, Math.floor(totalMs));

  const y = Math.floor(rest / UNIT_FACTORS.y);
  rest -= y * UNIT_FACTORS.y;

  const M = Math.floor(rest / UNIT_FACTORS.M);
  rest -= M * UNIT_FACTORS.M;

  const w = Math.floor(rest / UNIT_FACTORS.w);
  rest -= w * UNIT_FACTORS.w;

  const d = Math.floor(rest / UNIT_FACTORS.d);
  rest -= d * UNIT_FACTORS.d;

  const h = Math.floor(rest / UNIT_FACTORS.h);
  rest -= h * UNIT_FACTORS.h;

  const m = Math.floor(rest / UNIT_FACTORS.m);
  rest -= m * UNIT_FACTORS.m;

  const s = Math.floor(rest / 1000);
  rest -= s * 1000;

  return { y, M, w, d, h, m, s, ms: rest };
}

// ============================================
// Get current ms
// ============================================
function getCurrentMs(timer) {
  if (timer.paused || timer.startedAt === null) {
    return timer.currentMs;
  }

  const elapsed = performance.now() - timer.startedAt;

  if (timer.direction === '++') {
    return Math.min(elapsed, timer.duration);
  } else {
    return Math.max(timer.duration - elapsed, 0);
  }
}

// ============================================
// getTimerValue — for @@timer.key
// ============================================
export function getTimerValue(el, key) {
  const timer = timers.get(el);
  if (!timer) return SKIP;

  const ms = getCurrentMs(timer);
  const formatted = formatMs(ms);

  if (!(key in formatted)) return SKIP;

  return formatted[key];
}

// ============================================
// setTimer — only defines the timer
// ============================================
export function setTimer(selector, time, direction = '++') {
  if (!['++', '--'].includes(direction)) {
    console.error(`setTimer: invalid direction "${direction}". Use "++" or "--"`);
    return;
  }

  let totalMs;
  try {
    totalMs = parseTime(time);
  } catch (err) {
    console.error(err.message);
    return;
  }

  qsa(selector).forEach(el => {
    // Skip if timer exists
    if (timers.has(el)) return;

    timers.set(el, {
      duration: totalMs,
      direction,
      currentMs: direction === '++' ? 0 : totalMs,
      startedAt: null,
      paused: true,
      interval: null
    });
  });
}

// ============================================
// playTimer — start or resume
// ============================================
export function playTimer(selector) {
  qsa(selector).forEach(el => {
    const timer = timers.get(el);

    if (!timer) {
      console.error(`playTimer: no timer set on "${selector}"`);
      return;
    }

    if (!timer.paused) return;  // already playing

    timer.paused = false;
    timer.startedAt = performance.now() - (
      timer.direction === '++'
        ? timer.currentMs
        : timer.duration - timer.currentMs
    );

    const tick = () => {
      const ms = getCurrentMs(timer);

      // Check if done
      if (
        (timer.direction === '++' && ms >= timer.duration) ||
        (timer.direction === '--' && ms <= 0)
      ) {
        // Save final value
        timer.currentMs = ms;

        if (timer.interval) {
          clearInterval(timer.interval);
          timer.interval = null;
        }
        timer.paused = true;
        timer.startedAt = null;

        // Fire tick one last time to update display
        el.dispatchEvent(new CustomEvent('tick', { bubbles: true }));
        return;
      }

      // Fire tick
      el.dispatchEvent(new CustomEvent('tick', { bubbles: true }));
    };

    // First tick immediately
    tick();

    // Start interval
    timer.interval = setInterval(tick, 1000);
  });
}

// ============================================
// pauseTimer
// ============================================
export function pauseTimer(selector) {
  qsa(selector).forEach(el => {
    const timer = timers.get(el);

    if (!timer) {
      console.error(`pauseTimer: no timer set on "${selector}"`);
      return;
    }

    if (timer.paused) return;

    timer.currentMs = getCurrentMs(timer);
    timer.paused = true;
    timer.startedAt = null;

    if (timer.interval) {
      clearInterval(timer.interval);
      timer.interval = null;
    }
  });
}

// ============================================
// resetTimer
// ============================================
export function resetTimer(selector) {
  qsa(selector).forEach(el => {
    const timer = timers.get(el);

    if (!timer) {
      console.error(`resetTimer: no timer set on "${selector}"`);
      return;
    }

    if (timer.interval) {
      clearInterval(timer.interval);
      timer.interval = null;
    }

    timer.currentMs = timer.direction === '++' ? 0 : timer.duration;
    timer.startedAt = null;
    timer.paused = true;

    // Fire tick to update display
    el.dispatchEvent(new CustomEvent('tick', { bubbles: true }));
  });
}