import { routeResolve, NOT_FOUND } from './router.js';
import { SKIP } from '../core/skip.js';
import { runFunc } from '../core/run-func.js';
import { evalTemplate } from './template.js';

// Main resolver
export async function resolve(arg, context) {
  // runFunc (returns value)
  if (Array.isArray(arg) && arg[0] === 'runFunc') {
    const [, path, name, ...args] = arg;
    const resolvedArgs = await Promise.all(
      args.map(a => resolve(a, context))
    );
    return await runFunc(path, name, ...resolvedArgs);
  }

  // Try router
  const routed = await routeResolve(arg, context);
  if (routed !== NOT_FOUND) return routed;

  // String — template-eval if `{...}` and loop context
  if (typeof arg === 'string') {
    if (arg.includes('{') && context.loop) {
      const result = evalTemplate(arg, context.loop);
      return result.value;
    }
    return arg;
  }

  // Primitive
  if (arg == null || typeof arg !== 'object') return arg;

  // Array
  if (Array.isArray(arg)) {
    const resolved = await Promise.all(
      arg.map(item => resolve(item, context))
    );
    if (resolved.some(r => r === SKIP)) return SKIP;
    return resolved;
  }

  // Object
  const result = {};
  for (const [key, value] of Object.entries(arg)) {
    const resolved = await resolve(value, context);
    if (resolved === SKIP) return SKIP;
    result[key] = resolved;
  }
  return result;
}

// Re-export SKIP
export { SKIP } from '../core/skip.js';