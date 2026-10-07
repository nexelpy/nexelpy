// Read value from element based on type
export function readValue(el, type, key) {
  switch (type) {
    case 'attr':
      return el.getAttribute(key);
    case 'input':
      return el[key];
    case 'text':
      return el.textContent;
    case 'html':
      return el.innerHTML;
    case 'data':
      return el.dataset[key];
    default:
      return el.getAttribute(key);
  }
}

// Write value to element based on type
export function writeValue(el, type, key, value) {
  switch (type) {
    case 'attr':
      el.setAttribute(key, value);
      break;
    case 'input':
      el[key] = value;
      break;
    case 'text':
      el.textContent = value;
      break;
    case 'html':
      el.innerHTML = value;
      break;
    case 'data':
      el.dataset[key] = value;
      break;
  }
}

// Check if value is numeric
export function isNumeric(v) {
  if (v === null || v === undefined) return false;
  const n = Number(v);
  return !isNaN(n) && String(v).trim() !== '';
}

// Get nested value from object
export function getPath(obj, path) {
  const parts = path.split('.');
  let value = obj;
  for (const key of parts) {
    if (value == null || typeof value !== 'object') return undefined;
    value = value[key];
  }
  return value;
}