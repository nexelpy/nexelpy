export function findDebounce(effects) {
  const list = Array.isArray(effects?.[0]) ? effects : [effects];

  for (const effect of list) {
    if (Array.isArray(effect) && effect[0] === 'debounceEvent') {
      const ms = Number(effect[1]);
      return Number.isFinite(ms) && ms > 0 ? ms : 300;
    }
  }

  return null;
}

export function debounceEvent() {
  return true;
}
