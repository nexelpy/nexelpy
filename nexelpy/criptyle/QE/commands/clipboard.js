import { qsa } from '../core/dom-query.js';

export async function copyClipboard(selector, value) {
  try {
    await navigator.clipboard.writeText(value);
  } catch (err) {
    console.error(`copyClipboard failed: ${err.message}`);
  }
}

export async function pasteClipboard(selector) {
  try {
    const text = await navigator.clipboard.readText();
    qsa(selector).forEach(el => { el.value = text; });
  } catch (err) {
    console.error(`pasteClipboard failed: ${err.message}`);
  }
}