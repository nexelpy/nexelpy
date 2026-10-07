import { parseTemplate } from '../core/template-parser.js';
import { evalExpr } from '../core/expr-eval.js';

// Evaluate template with vars
// Returns { value, store }
export function evalTemplate(template, vars) {
  const parts = parseTemplate(template);

  // No expr → raw text
  if (!parts.some(p => p.type === 'expr')) {
    return { value: template, store: null };
  }

  // Single expr → return raw value
  if (parts.length === 1 && parts[0].type === 'expr') {
    return evalExpr(parts[0].value, vars);
  }

  // Mixed → string concat
  const jsParts = [];
  let lastStore = null;

  for (const part of parts) {
    if (part.type === 'text') {
      jsParts.push(JSON.stringify(part.value));
      continue;
    }

    const r = evalExpr(part.value, vars);
    if (r.store) {
      vars[r.store.key] = r.store.value;
      lastStore = r.store;
    }
    jsParts.push(JSON.stringify(r.value));
  }

  const expr = jsParts.join(' + ');
  const value = Function(`return (${expr})`)();

  return { value, store: lastStore };
}