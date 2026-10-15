import { routeResolve, NOT_FOUND } from './router.js';
import { SKIP } from '../core/skip.js';
import { runFunc } from '../core/run-func.js';
import { evalTemplate } from './template.js';
import { GETS, runGet } from './gets.js';

export async function resolve(arg, context) {

  if (Array.isArray(arg) && arg[0] === 'runFunc') {
    const [, path, name, ...args] = arg;
    const resolvedArgs = await Promise.all(
      args.map(a => resolve(a, context))
    );
    return await runFunc(path, name, ...resolvedArgs);
  }

  if (Array.isArray(arg) && GETS.has(arg[0])) {
    return runGet(arg, context);
  }

  const routed = await routeResolve(arg, context);
  if (routed !== NOT_FOUND) return routed;

  if (typeof arg === 'string') {
    if (arg.includes('{') && (context.loop || context.vars)) {
      const scope = { ...(context.vars || {}), ...(context.loop || {}) };
      const result = evalTemplate(arg, scope);

      if (context.loop) {
        for (const key of Object.keys(context.loop)) {
          context.loop[key] = scope[key];
        }
      }

      context.vars ??= {};
      for (const key of Object.keys(scope)) {
        if (!context.loop || !Object.prototype.hasOwnProperty.call(context.loop, key)) {
          context.vars[key] = scope[key];
        }
      }

      return result.value;
    }
    return arg;
  }

  if (arg == null || typeof arg !== 'object') return arg;

  if (Array.isArray(arg)) {
    const resolved = await Promise.all(
      arg.map(item => resolve(item, context))
    );
    if (resolved.some(r => r === SKIP)) return SKIP;
    return resolved;
  }

  const result = {};
  for (const [key, value] of Object.entries(arg)) {
    const resolved = await resolve(value, context);
    if (resolved === SKIP) return SKIP;
    result[key] = resolved;
  }
  return result;
}

export { SKIP } from '../core/skip.js';
