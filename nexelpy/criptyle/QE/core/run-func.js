// Dynamic import + call
export async function runFunc(path, name, ...args) {
  try {
    const module = await import(path);
    const fn = module[name];

    if (typeof fn !== 'function') {
      throw new Error(`"${name}" not found in ${path}`);
    }

    return await fn(...args);
  } catch (err) {
    console.error(`runFunc failed (${path}.${name}): ${err.message}`);
    throw err;
  }
}