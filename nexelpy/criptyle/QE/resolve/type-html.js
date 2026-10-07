import { resolveBySelector } from './selector-resolver.js';

// ["@@html", selector, expr?]
export function resolveHtml(arr, context) {
  const [, selector, expr] = arr;
  return resolveBySelector('html', 'value', selector, expr, context);
}