import { resolve, SKIP } from './resolve/index.js';
import { commandsMap } from './commands/index.js';
import { ajax } from './commands/ajax.js';
import { runFunc } from './core/run-func.js';
import { evaluateSingleCondition } from './resolve/evaluate.js';

// ============================================
// wait
// ============================================
function wait(ms) {
  return new Promise(r => setTimeout(r, ms));
}

// ============================================
// If/Elif/Else
// ============================================

async function runIfChain(list, startIndex, context) {
  let i = startIndex;
  let handled = false;

  while (i < list.length) {
    const [action, ...args] = list[i];

    if (action === 'if') {
      if (handled) break;
      const bodyEnd = findBodyEnd(list, i + 1);
      if (await evaluateCondition(args, context)) {
        await runEffects(list.slice(i + 1, bodyEnd), context);
        handled = true;
      }
      i = bodyEnd;
      continue;
    }

    if (action === 'elif') {
      if (handled) break;
      const bodyEnd = findBodyEnd(list, i + 1);
      if (await evaluateCondition(args, context)) {
        await runEffects(list.slice(i + 1, bodyEnd), context);
        handled = true;
      }
      i = bodyEnd;
      continue;
    }

    if (action === 'else') {
      if (handled) break;
      const bodyEnd = findBodyEnd(list, i + 1);
      await runEffects(list.slice(i + 1, bodyEnd), context);
      handled = true;
      i = bodyEnd;
      continue;
    }

    if (action === 'endCondition') {
      return i;
    }

    break;
  }

  return i - 1;
}

// ============================================
// For loop
// ============================================

async function runForLoop(list, startIndex, context) {
  const [, varStr, sourceExpr] = list[startIndex];

  // Resolve source
  const source = await resolve(sourceExpr, context);
  if (source === SKIP) {
    console.error(`for: source "${sourceExpr}" returned SKIP`);
    return startIndex;
  }

  // Parse var names
  const varNames = String(varStr).split(',').map(s => s.trim()).filter(Boolean);

  if (!varNames.length) {
    console.error(`for: no variable names`);
    return startIndex;
  }

  // Find body
  const bodyEnd = findBodyEnd(list, startIndex + 1);
  const body = list.slice(startIndex + 1, bodyEnd);

  // ============================================
  // ۱. تولید لیست
  // ============================================
  const newList = [];

  // ---- Array ----
  if (Array.isArray(source)) {
    if (varNames.length !== 1) {
      console.error(`for: array requires 1 variable, got ${varNames.length}`);
      return bodyEnd - 1;
    }

    const varName = varNames[0];

    for (let i = 0; i < source.length; i++) {
      context.loop = { [varName]: source[i], index: i };

      for (const [action, ...args] of body) {
        const resolvedArgs = await Promise.all(
          args.map(arg => resolve(arg, context))
        );
        newList.push([action, ...resolvedArgs]);
      }
    }
  }
  // ---- Object ----
  else if (source && typeof source === 'object') {
    if (varNames.length !== 2) {
      console.error(`for: object requires 2 variables (k,v), got ${varNames.length}`);
      return bodyEnd - 1;
    }

    const [keyName, valName] = varNames;
    const entries = Object.entries(source);

    for (let i = 0; i < entries.length; i++) {
      const [k, v] = entries[i];
      context.loop = { [keyName]: k, [valName]: v, index: i };

      for (const [action, ...args] of body) {
        const resolvedArgs = await Promise.all(
          args.map(arg => resolve(arg, context))
        );
        newList.push([action, ...resolvedArgs]);
      }
    }
  }
  // ---- Invalid ----
  else {
    console.error(`for: source must be array or object`);
    return bodyEnd - 1;
  }

  // Clear loop
  context.loop = null;

  // ============================================
  // ۲. ران لیست تولیدشده
  // ============================================
  await runEffects(newList, context, { resolved: true });

  return bodyEnd - 1;
}

// ============================================
// findBodyEnd
// ============================================

function findBodyEnd(list, startIndex) {
  let i = startIndex;

  while (i < list.length) {
    const [action] = list[i];

    if (
      action === 'if' ||
      action === 'elif' ||
      action === 'else' ||
      action === 'endCondition'
    ) {
      break;
    }

    i++;
  }

  return i;
}

// ============================================
// Evaluate condition with and/or
// ============================================

async function evaluateCondition(args, context) {
  const parts = [];

  for (const part of args) {
    if (part === 'and' || part === 'or') {
      parts.push({ type: 'op', value: part });
    } else {
      const result = await evaluateSingleCondition(part, context);
      parts.push({ type: 'cond', value: Boolean(result) });
    }
  }

  if (!parts.length) return false;

  // Stage 1: and
  let i = 1;
  while (i < parts.length) {
    if (parts[i].type === 'op' && parts[i].value === 'and') {
      const left = parts[i - 1].value;
      const right = parts[i + 1].value;
      parts.splice(i - 1, 3, { type: 'cond', value: left && right });
      i = 1;
    } else {
      i += 2;
    }
  }

  // Stage 2: or
  let result = parts[0].value;
  for (let i = 1; i < parts.length; i += 2) {
    if (parts[i].value === 'or') {
      result = result || parts[i + 1].value;
    }
  }

  return result;
}

// ============================================
// runEffects
// ============================================

export async function runEffects(effects, context = {}, options = {}) {
  const { resolved = false } = options;

  // Default context
  context.ok = context.ok ?? true;
  context.response = context.response ?? null;
  context.loop = context.loop ?? null;

  const list = Array.isArray(effects[0]) ? effects : [effects];
  let pending = [];

  for (let i = 0; i < list.length; i++) {
    const effect = list[i];
    const [action, ...args] = effect;

    // ---- if ----
    if (action === 'if') {
      i = await runIfChain(list, i, context);
      continue;
    }

    // ---- endCondition ----
    if (action === 'endCondition') {
      continue;
    }

    // ---- for ----
    if (action === 'for') {
      i = await runForLoop(list, i, context);
      continue;
    }

    // ---- then ----
    if (action === 'then') {
      await Promise.all(pending);
      pending = [];
      continue;
    }

    // ---- wait ----
    if (action === 'wait') {
      await wait(args[0] || 0);
      continue;
    }

    // ---- ajax ----
    if (action === 'ajax') {
      try {
        let finalArgs;
        if (resolved) {
          finalArgs = args;
        } else {
          finalArgs = await Promise.all(
            args.map(arg => resolve(arg, context))
          );
          if (finalArgs.some(a => a === SKIP)) continue;
        }

        const result = await ajax(...finalArgs);
        context.ok = result.ok;
        context.response = result.response;
      } catch (err) {
        context.ok = false;
        context.response = null;
        console.error(`Ajax error: ${err.message}`);
      }
      continue;
    }

    // ---- runFunc ----
    if (action === 'runFunc') {
      try {
        let finalArgs;
        if (resolved) {
          finalArgs = args;
        } else {
          finalArgs = await Promise.all(
            args.map(arg => resolve(arg, context))
          );
          if (finalArgs.some(a => a === SKIP)) continue;
        }

        await runFunc(...finalArgs);
      } catch (err) {
        console.error(`runFunc error: ${err.message}`);
      }
      continue;
    }

    // ---- @@attr / @@input as standalone effect ----
    if (
      typeof action === 'string' &&
      (action.startsWith('@@attr.') || action.startsWith('@@input.'))
    ) {
      try {
        await resolve(effect, context);
      } catch (err) {
        console.error(`Resolve error in "${action}": ${err.message}`);
      }
      continue;
    }

    // ---- normal command ----
    const fn = commandsMap[action];
    if (typeof fn !== 'function') {
      console.error(`Command "${action}" not found`);
      continue;
    }

    try {
      let finalArgs;
      if (resolved) {
        finalArgs = args.map(arg =>
          arg === 'this' ? context.element : arg
        );
      } else {
        const resolvedArgs = await Promise.all(
          args.map(arg => resolve(arg, context))
        );
        if (resolvedArgs.some(a => a === SKIP)) continue;
        finalArgs = resolvedArgs.map(arg =>
          arg === 'this' ? context.element : arg
        );
      }

      const result = fn(...finalArgs);
      if (result instanceof Promise) {
        pending.push(result);
      }
    } catch (err) {
      console.error(`Error in "${action}": ${err.message}`);
    }
  }

  await Promise.all(pending);
}