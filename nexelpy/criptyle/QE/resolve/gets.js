import { qsa } from '../core/dom-query.js';
import { SKIP } from '../core/skip.js';
import { parseTemplate } from '../core/template-parser.js';
import { evalExpr } from '../core/expr-eval.js';

export const GETS = new Set([
  'getResponse', 'getAttr', 'getText', 'getHtml',
  'getInput', 'getValue', 'getForm', 'getCookie', 'getLocation'
]);


function getPath(obj, path) {
  if (obj == null || !path) return obj;
  return String(path).split('.').reduce((o, k) => (o == null ? undefined : o[k]), obj);
}

function pair(slot) {
  return Array.isArray(slot) ? { key: slot[0], as: slot[1] || slot[0] } : { key: slot, as: null };
}

function takeExpr(rest) {
  const last = rest[rest.length - 1];
  if (typeof last === 'string' && last.includes('{')) {
    rest.pop();
    return last;
  }
  return null;
}

function render(template, vars) {
  const parts = parseTemplate(template);
  if (parts.length === 1 && parts[0].type === 'expr') {
    return evalExpr(parts[0].value, vars).value;
  }
  let result = '';
  for (const p of parts) {
    if (p.type === 'text') {
      result += p.value;
    } else {
      const r = evalExpr(p.value, vars);
      if (r.store) vars[r.store.key] = r.store.value;
      result += r.value == null ? '' : r.value;
    }
  }
  return result;
}

function toArray(nodes) {
  if (!nodes) return [];
  return Array.isArray(nodes) ? nodes : Array.from(nodes);
}

function coerce(value) {
  if (typeof value !== 'string') return value;
  const text = value.trim();
  return /^-?\d+(\.\d+)?$/.test(text) ? Number(text) : value;
}

function collect(nodes, getter) {
  const values = [];
  for (const el of toArray(nodes)) {
    const value = getter(el);
    if (value != null) values.push(coerce(value));
  }
  if (values.length === 0) return null;
  return values.length === 1 ? values[0] : values;
}

function applyOp(current, op, n) {
  if (op === '=') return n;
  const base = typeof current === 'number' ? current : Number(current);
  if (Number.isNaN(base)) return current;
  if (op === '+=') return base + n;
  if (op === '-=') return base - n;
  if (op === '*=') return base * n;
  if (op === '/=') return base / n;
  return current;
}

function remember(context, name, binding) {
  if (!name || !binding) return;
  context.bindings ??= {};
  context.bindings[name] = binding;
}

function writeNodes(nodes, value, writer) {
  const list = toArray(nodes).filter(Boolean);
  if (Array.isArray(value)) {
    list.forEach((el, i) => {
      if (value[i] != null) writer(el, value[i]);
    });
  } else {
    list.forEach(el => writer(el, value));
  }
}

function writeBinding(context, name, next) {
  const binding = context.bindings?.[name];
  if (!binding) return;
  writeNodes(binding.nodes, next, (el, v) => {
    if (binding.type === 'attr') el.setAttribute(binding.attr, String(v));
    else if (binding.type === 'text') el.textContent = String(v);
    else if (binding.type === 'html') el.innerHTML = String(v);
    else if (binding.type === 'input') el.value = String(v);
  });
}

function applyStyle(el, cssText) {
  if (!el?.style) return;
  String(cssText).split(';').forEach(part => {
    const i = part.indexOf(':');
    if (i < 1) return;
    const key = part.slice(0, i).trim();
    const value = part.slice(i + 1).trim();
    if (key && value) el.style.setProperty(key, value);
  });
}

function applyMutations(expr, vars, context) {
  return expr.replace(
    /\{(\w+)\s*(\+=|-=|\*=|\/=|=)\s*(-?\d+(?:\.\d+)?)\s*\}/g,
    (full, varName, op, raw) => {
      if (vars[varName] == null) return full;
      const next = Array.isArray(vars[varName])
        ? vars[varName].map(v => applyOp(v, op, Number(raw)))
        : applyOp(vars[varName], op, Number(raw));
      vars[varName] = next;
      writeBinding(context, varName, next);
      return `{${varName}}`;
    }
  );
}

export async function runUpdate(args, context) {
  context.vars ??= {};
  const vars = context.vars;

  for (const raw of args) {
    if (typeof raw !== 'string') continue;

    const mut = raw.match(/^\{(\w+)\s*(\+=|-=|\*=|\/=|=)\s*(-?\d+(?:\.\d+)?)\s*\}$/);
    if (mut) {
      const [, varName, op, rawNum] = mut;
      if (vars[varName] == null) {
        console.error(`update: "${varName}" is not set`);
        continue;
      }
      const next = Array.isArray(vars[varName])
        ? vars[varName].map(v => applyOp(v, op, Number(rawNum)))
        : applyOp(vars[varName], op, Number(rawNum));
      vars[varName] = next;
      writeBinding(context, varName, next);
      continue;
    }

    const style = raw.match(/^\{style\}([\s\S]+)$/);
    if (style) {
      applyStyle(context.element, style[1]);
      continue;
    }

    const text = raw.match(/^\{text\}([\s\S]*)$/);
    if (text && context.element) {
      context.element.textContent = text[1];
      continue;
    }

    console.error(`update: unknown op "${raw}"`);
  }
}

export async function runGet(arg, context) {
  const [cmd, ...rest] = arg;
  const expr = takeExpr(rest);
  context.vars ??= {};
  const vars = context.vars;

  let value, name;

  if (cmd === 'getResponse') {
    if (!context.ok) return SKIP;
    const spec = pair(rest[0] ?? null);
    value = spec.key == null ? context.response : getPath(context.response, spec.key);
    value = coerce(value);
    name = spec.as || (spec.key ? String(spec.key).split('.').pop() : 'response');
  }
  else if (cmd === 'getText' || cmd === 'getHtml') {
    const spec = pair(rest[0] ?? 'this');
    const nodes = spec.key === 'this' || !spec.key
      ? [context.element]
      : qsa(spec.key);
    value = collect(nodes, el =>
      cmd === 'getText' ? el.textContent : el.innerHTML
    );
    if (value == null) return SKIP;
    name = spec.as || 'value';
    remember(context, name, {
      type: cmd === 'getText' ? 'text' : 'html',
      nodes
    });
  }
  else if (cmd === 'getAttr') {
    const target = pair(rest[0] ?? 'this');
    const keySpec = pair(rest[1]);
    const nodes = target.key === 'this' || !target.key
      ? [context.element]
      : qsa(target.key);
    value = collect(nodes, el => el.getAttribute(keySpec.key));
    if (value == null) return SKIP;
    name = keySpec.as || keySpec.key;
    remember(context, name, { type: 'attr', attr: keySpec.key, nodes });
  }
else if (cmd === 'getInput' || cmd === 'getValue') {
  const spec = pair(rest[0] ?? 'this');
  const nodes = spec.key === 'this' || !spec.key
    ? [context.element]
    : qsa(spec.key);
  value = collect(nodes, el => {
    if (el instanceof HTMLInputElement
      || el instanceof HTMLTextAreaElement
      || el instanceof HTMLSelectElement) return el.value;
    return null;
  });
  if (value == null) return SKIP;
  name = spec.as || 'value';
  remember(context, name, { type: 'input', nodes });
}


  else if (cmd === 'getForm') {
    const spec = pair(rest[0] ?? 'this');
    const form = spec.key === 'this' || !spec.key
      ? context.element
      : qsa(spec.key)[0];
    if (!form) return SKIP;
    value = {};
    form.querySelectorAll('input,select,textarea').forEach(el => {
      if (el.name && !el.disabled && el.type !== 'file') {
        value[el.name] = coerce(el.value);
      }
    });
    Object.assign(vars, value);
    name = spec.as || null;
  }
  else if (cmd === 'getCookie') {
    const spec = pair(rest[0]);
    const m = document.cookie.match(new RegExp(`(?:^|;\\s*)${spec.key}=([^;]*)`));
    if (!m) return SKIP;
    value = coerce(decodeURIComponent(m[1]));
    name = spec.as || spec.key;
  }
  else if (cmd === 'getLocation') {
    const spec = pair(rest[0] ?? 'href');
    value = location[spec.key];
    if (value === undefined) return SKIP;
    name = spec.as || spec.key;
  }
  else return SKIP;

  if (value == null) return SKIP;

  if (name) vars[name] = value;
  if (!expr) return value;

  const rewritten = applyMutations(expr, vars, context);
  return render(rewritten, vars);
}
