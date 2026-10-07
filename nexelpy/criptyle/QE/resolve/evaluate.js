import { resolve, SKIP } from './index.js';
import { evalExpr } from '../core/expr-eval.js';

// Evaluate a single condition
// condition = ["@@attr.counter", "this", "{counter > 7}"]
export async function evaluateSingleCondition(condition, context) {
  if (!Array.isArray(condition)) return false;

  const [source, selector, expr] = condition;

  // Resolve value (handles @@attr, @@timer, @@input, ...)
  const value = await resolve([source, selector], context);
  if (value === SKIP) return false;

  // Extract key from source ("@@timer.s" → "s", "@@attr.counter" → "counter")
  const key = source.replace(/^@@\w+\./, '');

  // Remove template brackets { } if present
  const cleanExpr = String(expr).replace(/[{}]/g, '').trim();

  if (!cleanExpr) return false;

  // Evaluate
  const result = evalExpr(cleanExpr, { [key]: value });
  return Boolean(result.value);
}