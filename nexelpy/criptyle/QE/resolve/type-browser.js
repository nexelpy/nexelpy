import { SKIP } from '../core/skip.js';

// @@cookie.key
export function resolveCookie(arg, context) {
  const key = arg.slice(9);
  const match = document.cookie.match(
    new RegExp(`(?:^|;\\s*)${key}=([^;]*)`)
  );

  if (!match) {
    console.warn(`Cookie "${key}" not found (may be HttpOnly)`);
    return SKIP;
  }

  return decodeURIComponent(match[1]);
}

// @@location.key
export function resolveLocation(arg, context) {
  const key = arg.slice(11);
  const value = location[key];
  return value === undefined ? SKIP : value;
}