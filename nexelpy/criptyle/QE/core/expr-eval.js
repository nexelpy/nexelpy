import { FUNC_NAMES, FUNC_VALUES } from './math-funcs.js';
import { isNumeric } from './read-write.js';
import { isSafeExpr } from './security.js';

// Evaluate expression with vars
// Returns { value, store }
export function evalExpr(expr, vars) {
  if (typeof expr !== 'string') {
    return { value: expr, store: null };
  }

  // Detect store: key op= rhs
  const storeMatch = expr.match(/^(\w+)\s*([+\-*/%]?=)\s*(.+)$/);

  if (storeMatch && !/[=!<>]=/.test(storeMatch[2])) {
    const [, key, op, valExpr] = storeMatch;
    const currentValue = vars[key];
    const isNum = isNumeric(currentValue);

    const rhs = evalSimple(valExpr, vars);

    let newValue;

    if (op === '+=' && !isNum) {
      newValue = String(currentValue) + String(rhs);
    } else {
      const n = Number(currentValue);
      const r = Number(rhs);
      switch (op) {
        case '+=': newValue = n + r; break;
        case '-=': newValue = n - r; break;
        case '*=': newValue = n * r; break;
        case '/=': newValue = n / r; break;
        case '%=': newValue = n % r; break;
        case '=':  newValue = rhs; break;
        default:   newValue = rhs;
      }
    }

    return {
      value: newValue,
      store: { key, value: newValue }
    };
  }

  // Simple eval
  const value = evalSimple(expr, vars);
  return { value, store: null };
}

// Eval simple expression (no store)
function evalSimple(expr, vars) {
  // Wrap vars in _vars namespace
  const wrapped = wrapVars(expr, vars);

  if (!isSafeExpr(wrapped)) {
    throw new Error(`Unsafe expression: ${wrapped}`);
  }

  try {
    return Function(
      '_vars',
      ...FUNC_NAMES,
      `return (${wrapped})`
    )(vars, ...FUNC_VALUES);
  } catch (err) {
    throw new Error(`Eval error: ${err.message} (expr: ${wrapped})`);
  }
}

// Wrap bare keys in _vars namespace
// "i.name" → "_vars.i.name"
// "s < 10" → "_vars.s < 10"
function wrapVars(expr, vars) {
  let result = expr;

  // Sort keys by length desc to avoid partial matches
  const keys = Object.keys(vars).sort((a, b) => b.length - a.length);

  for (const key of keys) {
    // Match word boundaries, but not if already prefixed with _vars. or .
    const pattern = new RegExp(`(?<![\\w.$])${key}\\b`, 'g');
    result = result.replace(pattern, `_vars.${key}`);
  }

  return result;
}