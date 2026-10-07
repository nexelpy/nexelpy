import { resolveBySelector } from './selector-resolver.js';

// ["@@text", selector, expr?]
export function resolveText(arr, context) {
  const [, selector, expr] = arr;
  return resolveBySelector('text', 'value', selector, expr, context);
}