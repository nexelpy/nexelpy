import { getPath } from '../core/read-write.js';
import { SKIP } from '../core/skip.js';

// @@response or @@response.key
export function resolveResponse(fullPath, context) {
  if (!context.ok) return SKIP;

  const parts = fullPath.split('.');
  const source = parts[0];

  if (source !== 'response') {
    throw new Error(`Unknown source: ${source}`);
  }

  if (parts.length === 1) {
    // @@response → whole response
    const value = context.response;
    if (value == null || value === '') return SKIP;
    return value;
  }

  // @@response.key.sub
  const path = parts.slice(1).join('.');
  const value = getPath(context.response, path);

  if (value == null || value === '') return SKIP;
  return value;
}