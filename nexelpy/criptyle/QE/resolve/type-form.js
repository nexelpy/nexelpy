import { qsa } from '../core/dom-query.js';
import { SKIP } from '../core/skip.js';

// ["@@form", selector]
export function resolveForm(arr, context) {
  const [, selector] = arr;

  let form;
  if (selector === 'this') {
    form = context.element;
  } else {
    form = qsa(selector)[0];
  }

  if (!form) return SKIP;

  const data = {};
  const fields = form.querySelectorAll('input, select, textarea');

  for (const el of fields) {
    const name = el.name;
    if (!name) continue;
    if (el.disabled) continue;

    if (el.type === 'checkbox' || el.type === 'radio') {
      if (!el.checked) continue;
      if (name in data) {
        if (!Array.isArray(data[name])) data[name] = [data[name]];
        data[name].push(el.value);
      } else {
        data[name] = el.value;
      }
      continue;
    }

    if (el.tagName === 'SELECT' && el.multiple) {
      data[name] = [...el.selectedOptions].map(o => o.value);
      continue;
    }

    if (el.type === 'file') continue;

    data[name] = el.value;
  }

  return data;
}