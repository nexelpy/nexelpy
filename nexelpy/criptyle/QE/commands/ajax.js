export async function ajax(url, method = 'GET', body = null) {
  const upperMethod = method.toUpperCase();

  const options = {
    method: upperMethod,
    headers: { 'Content-Type': 'application/json' }
  };

  if (body) {
    if (upperMethod === 'GET' || upperMethod === 'HEAD') {
      const query = new URLSearchParams(body).toString();
      url += (url.includes('?') ? '&' : '?') + query;
    } else {
      options.body = JSON.stringify(body);
    }
  }

  const response = await fetch(url, options);

  let data = null;
  const contentType = response.headers.get('content-type') || '';

  try {
    if (contentType.includes('application/json')) {
      data = await response.json();
    } else {
      data = await response.text();
    }
  } catch (err) {
    console.error(`ajax parse error: ${err.message}`);
    data = null;
  }

  return { ok: response.ok, response: data };
}