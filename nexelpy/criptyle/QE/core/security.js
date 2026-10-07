// Dangerous patterns to block
const DANGEROUS = /\b(eval|Function|constructor|__proto__|prototype|import|require|process|globalThis)\b/;

// Allowed characters in expression (after var replacement)
const ALLOWED = /^[\w\s+\-*/%().,<>=!&|?:[\]'"]+$/;

// Check if expression is safe to eval
export function isSafeExpr(expr) {
  if (typeof expr !== 'string') return false;
  if (DANGEROUS.test(expr)) return false;
  if (!ALLOWED.test(expr)) return false;
  return true;
}