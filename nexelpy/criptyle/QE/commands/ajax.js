function flattenParams(obj, prefix = '') {
  return Object.entries(obj).reduce((acc, [key, val]) => {
    const fullKey = prefix ? `${prefix}[${key}]` : key;
    if (val !== null && typeof val === 'object' && !Array.isArray(val)) {
      Object.assign(acc, flattenParams(val, fullKey));
    } else {
      acc[fullKey] = val;
    }
    return acc;
  }, {});
}

function toAbsolute(href) {
  try {
    return new URL(href, location.href).href;
  } catch {
    return href;
  }
}

function existingAssetUrls() {
  return new Set(
    [...document.querySelectorAll('link[href], script[src]')]
      .map(node => node.href || node.src)
      .filter(Boolean)
  );
}

function appendAsset(node, head, existing) {
  const href = node.getAttribute('href') || node.getAttribute('src');
  if (!href) return;

  const absolute = toAbsolute(href);
  if (existing.has(absolute)) return;

  if (node.tagName === 'LINK') {
    const link = document.createElement('link');
    link.rel = node.getAttribute('rel') || 'stylesheet';
    link.href = href;

    const integrity = node.getAttribute('integrity');
    const crossorigin = node.getAttribute('crossorigin');
    const media = node.getAttribute('media');

    if (integrity) link.integrity = integrity;
    if (crossorigin) link.crossOrigin = crossorigin;
    if (media) link.media = media;

    head.appendChild(link);
  } else if (node.tagName === 'SCRIPT') {
    const script = document.createElement('script');
    script.src = href;

    const type = node.getAttribute('type');
    const integrity = node.getAttribute('integrity');
    const crossorigin = node.getAttribute('crossorigin');

    if (type) script.type = type;
    if (integrity) script.integrity = integrity;
    if (crossorigin) script.crossOrigin = crossorigin;

    script.async = node.hasAttribute('async');
    if (node.hasAttribute('defer')) script.defer = true;
    if (node.hasAttribute('nomodule')) script.noModule = true;

    head.appendChild(script);
  } else {
    return;
  }

  existing.add(absolute);
}

function ensureHeadAssets(links) {
  if (links == null || links === '') return;

  const head = document.head || document.getElementsByTagName('head')[0];
  if (!head) return;

  const existing = existingAssetUrls();

  if (typeof links === 'string') {
    const doc = new DOMParser().parseFromString(links, 'text/html');
    for (const node of doc.querySelectorAll('link[href], script[src]')) {
      appendAsset(node, head, existing);
    }
    return;
  }

  const list = Array.isArray(links) ? links : [links];

  for (const item of list) {
    if (!item) continue;

    if (typeof item === 'string' && /<\s*(link|script)\b/i.test(item)) {
      ensureHeadAssets(item);
      continue;
    }

    const href = typeof item === 'string'
      ? item
      : (item.href || item.src || item.url);

    if (!href) continue;

    const fake = document.createElement(
      (typeof item === 'object' && /css|style/i.test(String(item.type || ''))) ||
      /\.css(\?|#|$)/i.test(href)
        ? 'link'
        : 'script'
    );

    if (fake.tagName === 'LINK') fake.setAttribute('href', href);
    else fake.setAttribute('src', href);

    if (typeof item === 'object') {
      if (item.rel) fake.setAttribute('rel', item.rel);
      if (item.type) fake.setAttribute('type', item.type);
      if (item.integrity) fake.setAttribute('integrity', item.integrity);
      if (item.crossorigin) fake.setAttribute('crossorigin', item.crossorigin);
      if (item.defer) fake.setAttribute('defer', '');
      if (item.async) fake.setAttribute('async', '');
    }

    appendAsset(fake, head, existing);
  }
}

export const ajax = async (url, method = 'GET', body = null) => {
  if (!url || typeof url !== 'string') {
    return { ok: false, response: null };
  }

  const upperMethod = method.toUpperCase();
  let finalUrl = url;
  let fetchBody = null;
  const headers = {};

  if (body) {
    if (upperMethod === 'GET' || upperMethod === 'HEAD') {
      const flat = typeof body === 'object' ? flattenParams(body) : body;
      const params = new URLSearchParams(flat).toString();
      if (params) finalUrl += (url.includes('?') ? '&' : '?') + params;
    } else {
      fetchBody = typeof body === 'object' ? JSON.stringify(body) : String(body);
      headers['Content-Type'] = 'application/json';
    }
  }

  try {
    const res = await fetch(finalUrl, {
      method: upperMethod,
      headers,
      body: fetchBody
    });

    const contentType = res.headers.get('content-type') || '';
    let responseData = null;

    if (contentType.includes('application/json')) {
      try { responseData = await res.json(); } catch { responseData = null; }
    } else {
      responseData = await res.text();
    }

    if (responseData && typeof responseData === 'object') {
      ensureHeadAssets(responseData.QE_links_header);
    }

    return { ok: res.ok, response: responseData };
  } catch (err) {
    console.error('[QE] Fetch failed:', err);
    return { ok: false, response: null };
  }
};
