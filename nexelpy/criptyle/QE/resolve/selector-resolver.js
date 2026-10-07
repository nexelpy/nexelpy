import { qsa } from '../core/dom-query.js';
import { readValue, writeValue } from '../core/read-write.js';
import { evalTemplate } from './template.js';
import { SKIP } from '../core/skip.js';

// Resolve single key from selector
export function resolveBySelector(type, key, selector, expr, context) {
  // Find elements
  let els;
  if (selector === 'this') {
    els = context.element ? [context.element] : [];
  } else {
    els = qsa(selector);
  }

  if (!els.length) return SKIP;

  // Read values
  const values = [];
  const validEls = [];

  for (const el of els) {
    const v = readValue(el, type, key);
    if (v !== null && v !== undefined) {
      values.push(v);
      validEls.push(el);
    }
  }

  if (!values.length) return SKIP;

  // No expr → raw value
  if (!expr) {
    return values.length === 1 ? values[0] : values;
  }

  // Detect aggregate → use array
  const isAggregate = /\b(sum|sub|min|max|avg|count)\s*\(/.test(expr);

  if (isAggregate) {
    const vars = { [key]: values };
    const result = evalTemplate(expr, vars);
    return result.value;
  }

  // Per element
  const results = [];

  for (let i = 0; i < validEls.length; i++) {
    const vars = { [key]: values[i] };
    const result = evalTemplate(expr, vars);

    if (result.store) {
      writeValue(validEls[i], type, result.store.key, result.store.value);
    }

    results.push(result.value);
  }

  return results.length === 1 ? results[0] : results;
}

// Resolve multiple keys from first element
export function resolveMultiKey(type, keys, selector, expr, context) {
  let els;
  if (selector === 'this') {
    els = context.element ? [context.element] : [];
  } else {
    els = qsa(selector);
  }

  if (!els.length) return SKIP;

  const el = els[0];
  const vars = {};

  for (const key of keys) {
    const v = readValue(el, type, key);
    if (v === null || v === undefined) return SKIP;
    vars[key] = v;
  }

  if (!expr) return vars;

  const result = evalTemplate(expr, vars);

  if (result.store) {
    writeValue(el, type, result.store.key, result.store.value);
  }

  return result.value;
}