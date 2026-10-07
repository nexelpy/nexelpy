import {
  resolveAttrString,
  resolveAttrArray,
} from './type-attr.js';
import {
  resolveInputString,
  resolveInputArray,
} from './type-input.js';
import { resolveText } from './type-text.js';
import { resolveHtml } from './type-html.js';
import { resolveForm } from './type-form.js';
import { resolveResponse } from './type-response.js';
import { resolveCookie, resolveLocation } from './type-browser.js';
import { SKIP } from '../core/skip.js';
import { resolveTimer } from './type-timer.js';

export const NOT_FOUND = Symbol('not_found');

// Route @@ args to their type handler
export async function routeResolve(arg, context) {
  // @@form
  if (Array.isArray(arg) && arg[0] === '@@form') {
    return resolveForm(arg, context);
  }

  // @@attr
  if (typeof arg === 'string' && arg.startsWith('@@attr.')) {
    return resolveAttrString(arg, context);
  }
  if (Array.isArray(arg) && typeof arg[0] === 'string' && arg[0].startsWith('@@attr.')) {
    return resolveAttrArray(arg, context);
  }

  // @@input
  if (typeof arg === 'string' && arg.startsWith('@@input.')) {
    return resolveInputString(arg, context);
  }
  if (Array.isArray(arg) && typeof arg[0] === 'string' && arg[0].startsWith('@@input.')) {
    return resolveInputArray(arg, context);
  }

  // @@text
  if (Array.isArray(arg) && arg[0] === '@@text') {
    return resolveText(arg, context);
  }

  // @@html
  if (Array.isArray(arg) && arg[0] === '@@html') {
    return resolveHtml(arg, context);
  }

  // @@cookie
  if (typeof arg === 'string' && arg.startsWith('@@cookie.')) {
    return resolveCookie(arg, context);
  }

  // @@location
  if (typeof arg === 'string' && arg.startsWith('@@location.')) {
    return resolveLocation(arg, context);
  }

  // @@response
  if (typeof arg === 'string' && arg.startsWith('@@response')) {
    return resolveResponse(arg.slice(2), context);
  }

// @@timer (array)
if (Array.isArray(arg) && typeof arg[0] === 'string' && arg[0].startsWith('@@timer.')) {
  return resolveTimer(arg, context);
}

  // Unknown @@
  if (typeof arg === 'string' && arg.startsWith('@@')) {
    console.warn(`Unknown @@ type: ${arg}`);
    return SKIP;
  }

  return NOT_FOUND;
}


