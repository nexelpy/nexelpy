import { qsa } from '../core/dom-query.js';
import { getTimerValue } from '../commands/timer.js';
import { SKIP } from '../core/skip.js';
import { evalTemplate } from './template.js';

// ["@@timer.key1,key2", selector, expr?]
export async function resolveTimer(arr, context) {
  const [typeKey, selector, expr] = arr;

  // Extract keys: "@@timer.s,m" → ["s", "m"]
  const keysStr = typeKey.slice(8);  // "@@timer." → 8 chars
  const keys = keysStr.split(/[\s,]+/).filter(k => k);

  if (!keys.length) {
    console.error('@@timer: no keys');
    return SKIP;
  }

  // Find timer element
  let els;
  if (selector === 'this') {
    els = [context.element];
  } else {
    els = qsa(selector);
  }

  if (!els.length) return SKIP;

  const el = els[0];

  // Read values
  const vars = {};
  for (const key of keys) {
    const value = getTimerValue(el, key);
    if (value === SKIP) return SKIP;
    vars[key] = value;
  }

  // No expr → raw value (single key) or object (multi key)
  if (!expr) {
    if (keys.length === 1) {
      return vars[keys[0]];
    }
    return vars;
  }

  // Eval template
  const result = evalTemplate(expr, vars);
  return result.value;
}