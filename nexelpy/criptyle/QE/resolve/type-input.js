import { resolveBySelector, resolveMultiKey } from './selector-resolver.js';
import { SKIP } from '../core/skip.js';
import { readValue } from '../core/read-write.js';

// @@input.key (string)
export function resolveInputString(arg, context) {
  const key = arg.slice(8);
  const el = context.element;
  if (!el) return SKIP;

  const value = readValue(el, 'input', key);
  return value === undefined ? SKIP : value;
}

// ["@@input.key", selector, expr?]
export function resolveInputArray(arr, context) {
  const [typeKey, selector, expr] = arr;
  const keysStr = typeKey.slice(8);
  const keys = keysStr.split(/[\s,]+/).filter(k => k);

  if (!keys.length) {
    throw new Error('@@input: no keys');
  }

  if (keys.length === 1) {
    return resolveBySelector('input', keys[0], selector, expr, context);
  }

  return resolveMultiKey('input', keys, selector, expr, context);
}