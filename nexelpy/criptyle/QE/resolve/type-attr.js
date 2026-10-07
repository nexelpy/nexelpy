import { resolveBySelector, resolveMultiKey } from './selector-resolver.js';
import { SKIP } from '../core/skip.js';
import { readValue } from '../core/read-write.js';

// @@attr.key (string)
export function resolveAttrString(arg, context) {
  const key = arg.slice(7);
  const el = context.element;
  if (!el) return SKIP;

  const value = readValue(el, 'attr', key);
  return value === null ? SKIP : value;
}

// ["@@attr.key", selector, expr?]
export function resolveAttrArray(arr, context) {
  const [typeKey, selector, expr] = arr;
  const keysStr = typeKey.slice(7);
  const keys = keysStr.split(/[\s,]+/).filter(k => k);

  if (!keys.length) {
    throw new Error('@@attr: no keys');
  }

  if (keys.length === 1) {
    return resolveBySelector('attr', keys[0], selector, expr, context);
  }

  return resolveMultiKey('attr', keys, selector, expr, context);
}