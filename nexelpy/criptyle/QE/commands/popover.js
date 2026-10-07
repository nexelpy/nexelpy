import { qsa } from '../core/dom-query.js';

const SIDES = ['top', 'bottom', 'left', 'right'];
const DEFAULT_GAP = '8px';

let counter = 0;
const anchorNames = new WeakMap();

export function popOver(selector, anchor, side = 'bottom', gap = DEFAULT_GAP, closeOnBlur = true) {
  // Validate side
  if (!SIDES.includes(side)) {
    console.error(`popOver: invalid side "${side}"`);
    return;
  }

  // Resolve anchor (Element or selector)
  const anchorEl = anchor instanceof Element
    ? anchor
    : qsa(anchor)[0];

  if (!anchorEl) {
    console.error(`popOver: anchor "${anchor}" not found`);
    return;
  }

  // Assign anchor-name (once)
  let anchorName = anchorNames.get(anchorEl);
  if (!anchorName) {
    anchorName = `--qe-anchor-${++counter}`;
    anchorEl.style.anchorName = anchorName;
    anchorNames.set(anchorEl, anchorName);
  }

  // Normalize closeOnBlur
  const shouldCloseOnBlur = closeOnBlur !== false && closeOnBlur !== 'false';

  qsa(selector).forEach(el => {
    if (!el.hasAttribute('popover')) {
      console.error(`popOver: "${selector}" has no popover attribute`);
      return;
    }

    // Set popover mode
    el.setAttribute('popover', shouldCloseOnBlur ? 'auto' : 'manual');

    // Position via Anchor Positioning
    el.style.positionAnchor = anchorName;
    el.style.positionArea = side;
    el.style.margin = gap;

    if (!el.matches(':popover-open')) {
      el.showPopover();
    }
  });
}

export function popHide(selector) {
  qsa(selector).forEach(el => {
    if (el.matches(':popover-open')) {
      el.hidePopover();
    }
  });
}