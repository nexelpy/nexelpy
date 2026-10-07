// Parse template string into parts
// "date is {counter} day ago"
// → [
//     { type: 'text', value: 'date is ' },
//     { type: 'expr', value: 'counter' },
//     { type: 'text', value: ' day ago' }
//   ]
export function parseTemplate(str) {
  if (typeof str !== 'string') {
    return [{ type: 'text', value: str }];
  }

  if (!str.includes('{')) {
    return [{ type: 'text', value: str }];
  }

  const parts = [];
  let current = '';
  let i = 0;

  while (i < str.length) {
    if (str[i] === '{') {
      if (current) {
        parts.push({ type: 'text', value: current });
        current = '';
      }

      const end = str.indexOf('}', i + 1);

      if (end === -1) {
        // No closing brace
        current += str.slice(i);
        break;
      }

      const expr = str.slice(i + 1, end).trim();
      parts.push({ type: 'expr', value: expr });
      i = end + 1;
      continue;
    }

    current += str[i];
    i++;
  }

  if (current) {
    parts.push({ type: 'text', value: current });
  }

  return parts;
}