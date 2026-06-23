# HeaderBuilder Documentation

## Overview

`HeaderBuilder` is a powerful class for building HTTP security headers. It is automatically instantiated in the `Page` class and accessed via `x.headers`.

```python
# Usage in project
x = Page()
x.headers.csp.add('default-src', "'self'")
x.headers.hsts(max_age=31536000, include_subdomains=True, preload=True)
x.headers.set_strict()
# Headers are automatically built by Page class
```

---

## Available Builders & Methods

### 1. CSP (Content-Security-Policy)

**Access:**
```python
x.headers.csp
```

**Method:**
```python
def add(self, directive, *sources, origin=True)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `directive` | `str` | CSP directive name |
| `*sources` | `str` | One or more allowed sources |
| `origin` | `bool` | If `True`, converts URLs to origin only |

**Valid Directives:**
```
default-src, script-src, style-src, img-src, connect-src, 
font-src, object-src, media-src, frame-src, frame-ancestors,
base-uri, form-action, manifest-src, worker-src, 
child-src, prefetch-src, navigate-to
```

**Valid Sources:**

| Source | Description |
|--------|-------------|
| `'none'` | Nothing allowed |
| `'self'` | Current domain only |
| `'unsafe-inline'` | Inline scripts/styles allowed |
| `'unsafe-eval'` | eval() function allowed |
| `'strict-dynamic'` | Dynamic scripts allowed |
| `https:` | All HTTPS URLs |
| `http:` | All HTTP URLs |
| `data:` | Inline data (images) |
| `https://example.com` | Specific domain |
| `*.example.com` | All subdomains |

**Examples:**
```python
# Allow only own domain
x.headers.csp.add('default-src', "'self'")

# Scripts from own domain and CDN
x.headers.csp.add('script-src', "'self'", "https://cdnjs.cloudflare.com")

# Styles from own domain and Google Fonts
x.headers.csp.add('style-src', "'self'", "https://fonts.googleapis.com")

# Images from own domain and any HTTPS domain
x.headers.csp.add('img-src', "'self'", "https:")

# Frames only from YouTube
x.headers.csp.add('frame-ancestors', "https://www.youtube.com")

# API connections
x.headers.csp.add('connect-src', "'self'", "https://api.example.com")
```

---

### 2. HSTS (Strict-Transport-Security)

**Method:**
```python
def hsts(self, max_age=31536000, include_subdomains=True, preload=False)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_age` | `int` | `31536000` | Validity in seconds (1 year) |
| `include_subdomains` | `bool` | `True` | Include all subdomains |
| `preload` | `bool` | `False` | Submit to browser preload list |

**Examples:**
```python
# Default (1 year, include subdomains)
x.headers.hsts()

# 2 years
x.headers.hsts(max_age=63072000)

# Without subdomains
x.headers.hsts(include_subdomains=False)

# For preload list
x.headers.hsts(max_age=31536000, include_subdomains=True, preload=True)

# Disable HSTS
x.headers.hsts(max_age=0)
```

---

### 3. Cache-Control

**Method:**
```python
def cache(self, cache_control="no-cache", max_age=31536000, s_maxage="", 
          stale_while_revalidate="", stale_if_error="", extra="")
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `cache_control` | `str` | `"no-cache"` | Main cache-control value |
| `max_age` | `int` | `31536000` | Cache duration in seconds |
| `s_maxage` | `str` | `""` | Max-age for CDN/proxy |
| `stale_while_revalidate` | `str` | `""` | Stale cache allowed time |
| `stale_if_error` | `str` | `""` | Stale cache on error time |
| `extra` | `str` | `""` | Additional cache directives |

**Examples:**
```python
# No caching
x.headers.cache()

# Public cache for 1 year
x.headers.cache(cache_control="public", max_age=31536000)

# Cache with revalidation
x.headers.cache(cache_control="public", max_age=3600, stale_while_revalidate=300)

# For CDN
x.headers.cache(cache_control="public", max_age=3600, s_maxage=86400)

# Static assets
x.headers.cache(cache_control="public, immutable", max_age=31536000)
```

---

### 4. X-Frame-Options

**Method:**
```python
def frame_options(self, policy="DENY")
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `policy` | `str` | `"DENY"` | `DENY` or `SAMEORIGIN` |

**Examples:**
```python
# Prevent all iframes
x.headers.frame_options()

# Allow only same domain
x.headers.frame_options(policy="SAMEORIGIN")
```

---

### 5. X-Content-Type-Options

**Method:**
```python
def content_type_options(self)
```

**Examples:**
```python
# Always enable
x.headers.content_type_options()
```

---

### 6. Referrer-Policy

**Method:**
```python
def referrer_Policy(self, policy="strict-origin-when-cross-origin")
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `policy` | `str` | `"strict-origin-when-cross-origin"` | Referrer policy |

**Valid Values:**
```
no-referrer
no-referrer-when-downgrade
same-origin
origin
strict-origin
origin-when-cross-origin
strict-origin-when-cross-origin (default)
unsafe-url
```

**Examples:**
```python
# Default
x.headers.referrer_Policy()

# Maximum privacy
x.headers.referrer_Policy(policy="no-referrer")

# Same domain only
x.headers.referrer_Policy(policy="same-origin")
```

---

### 7. Permissions-Policy

**Access:**
```python
x.headers.permissions_Policy
```

**Method:**
```python
def add(self, feature, allow_list=None)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `feature` | `str` | Feature name |
| `allow_list` | `str/list/None` | Allowed domains list |

**Valid Features:**
```
geolocation, camera, microphone, usb, fullscreen, payment, 
autoplay, encrypted-media, accelerometer, gyroscope, 
magnetometer, speaker, vibrate, document-domain, 
cross-origin-isolated, midi, clipboard-read, 
clipboard-write, display-capture, gamepad, hid, 
idle-detection, keyboard-map, navigation-override, 
screen-wake-lock, serial, sync-xhr, xr-spatial-tracking
```

**Allow List Values:**

| Value | Description |
|-------|-------------|
| `None` | Blocked `()` |
| `'*'` | All allowed |
| `'self'` | Same domain only |
| `'src'` | Iframe domain only |
| `"https://example.com"` | Specific domain |
| `["a.com", "b.com"]` | List of domains |

**Examples:**
```python
# Block all
x.headers.permissions_Policy.add('geolocation')
x.headers.permissions_Policy.add('camera')
x.headers.permissions_Policy.add('microphone')

# Same domain only
x.headers.permissions_Policy.add('geolocation', 'self')

# All allowed
x.headers.permissions_Policy.add('autoplay', '*')

# Specific domain
x.headers.permissions_Policy.add('camera', 'https://meet.google.com')
```

---

### 8. Cross-Origin-Opener-Policy (COOP)

**Method:**
```python
def cross_origin_opener(self, policy="same-origin")
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `policy` | `str` | `"same-origin"` | Opener policy |

**Valid Values:**
```
unsafe-none                 # No restrictions (insecure)
same-origin-allow-popups    # Allow popups from same origin
same-origin                 # Same origin only (most secure)
```

**Examples:**
```python
# Most secure
x.headers.cross_origin_opener()

# Allow popups
x.headers.cross_origin_opener(policy="same-origin-allow-popups")
```

---

### 9. Cross-Origin-Embedder-Policy (COEP)

**Method:**
```python
def cross_origin_embedder(self, policy="require-corp")
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `policy` | `str` | `"require-corp"` | Embedder policy |

**Valid Values:**
```
unsafe-none        # No restrictions (insecure)
require-corp       # CORS/CORP required (most secure)
credentialless     # Cross-origin resources without cookies
```

**Examples:**
```python
# Most secure
x.headers.cross_origin_embedder()

# No restrictions
x.headers.cross_origin_embedder(policy="unsafe-none")
```

---

### 10. Cross-Origin-Resource-Policy (CORP)

**Method:**
```python
def cross_origin_resource(self, policy="same-origin")
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `policy` | `str` | `"same-origin"` | Resource policy |

**Valid Values:**
```
same-site       # Same site only (includes subdomains)
same-origin     # Same origin only (most secure)
cross-origin    # All domains
```

**Examples:**
```python
# Same origin only
x.headers.cross_origin_resource()

# Same site (includes subdomains)
x.headers.cross_origin_resource(policy="same-site")

# Public
x.headers.cross_origin_resource(policy="cross-origin")
```

---

### 11. Origin-Agent-Cluster

**Method:**
```python
def origin_agent_cluster(self)
```

**Examples:**
```python
# Always enable
x.headers.origin_agent_cluster()
```

---

### 12. Clear-Site-Data

**Method:**
```python
def clear_site_data(self, *types)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `*types` | `str` | Data types to clear |

**Valid Values:**
```
cache                # Clear cache
cookies              # Clear cookies
storage              # Clear localStorage, IndexedDB
executionContexts    # Close execution contexts
*                    # Clear everything
```

**Examples:**
```python
# Clear everything
x.headers.clear_site_data('*')

# Clear cookies only
x.headers.clear_site_data('cookies')

# Clear cookies and cache
x.headers.clear_site_data('cookies', 'cache')

# Clear cookies and storage
x.headers.clear_site_data('cookies', 'storage')
```

---

### 13. Raw Headers

**Method:**
```python
def add_raw_header(self, **headers)
```

**Note:** Underscores (`_`) in keys are automatically converted to dashes (`-`).

**Examples:**
```python
# Custom headers
x.headers.add_raw_header(
    X_Custom_Header="custom-value",
    X_Another_Header="another-value",
    X_API_Version="v1.0"
)

# Converts to:
# X-Custom-Header: custom-value
# X-Another-Header: another-value
# X-API-Version: v1.0
```

---

### 14. Predefined Security Levels

**Methods:**
```python
def set_super_strict(self)
def set_strict(self)
def set_normal(self)
def set_relaxed(self)
```

**Comparison:**

| Level | Method | Use Case | Security |
|-------|--------|----------|----------|
| **Super Strict** | `set_super_strict()` | Banking, admin panels, sensitive data | 🔒 Very High |
| **Strict** | `set_strict()` | User-based websites (default) | 🔒 High |
| **Normal** | `set_normal()` | Blogs, news, public sites | 🔓 Medium |
| **Relaxed** | `set_relaxed()` | Development environment | 🔓 Low |

**Examples:**
```python
# Use security level
x.headers.set_strict()

# Combine with custom settings
x.headers.set_strict()
x.headers.csp.add('script-src', 'https://custom-cdn.com')
x.headers.add_raw_header(X_Custom="value")
```

---

## Complete Examples

### Example 1: Standard User Website
```python
x = Page()
x.headers.set_strict()
x.headers.csp.add('script-src', "'self'", "https://cdnjs.cloudflare.com")
x.headers.csp.add('style-src', "'self'", "https://fonts.googleapis.com")
x.headers.csp.add('img-src', "'self'", "data:", "https:")
```

### Example 2: Website with YouTube Embed
```python
x = Page()
x.headers.set_strict()
x.headers.csp.add('frame-ancestors', "'self'", "https://www.youtube.com")
x.headers.csp.add('script-src', "'self'", "https://www.youtube.com")
x.headers.frame_options(policy="SAMEORIGIN")
```

### Example 3: API with Specific Settings
```python
x = Page()
x.headers.csp.add('default-src', "'none'")
x.headers.csp.add('connect-src', "'self'")
x.headers.cache(cache_control="no-store", max_age=0)
x.headers.cross_origin_resource(policy="same-origin")
```

### Example 4: Combining with Raw Headers
```python
x = Page()
x.headers.set_strict()
x.headers.add_raw_header(
    X_Request_ID="12345",
    X_API_Version="v2.0",
    X_Rate_Limit="100"
)
```

### Example 5: User Logout
```python
x = Page()
x.headers.clear_site_data('*')
x.headers.cache(cache_control="no-store", max_age=0)
```

---

## Important Notes

1. **Automatic Building**: Headers are automatically built by the `Page` class. You don't need to call `build_header()` manually.

2. **Raw Headers Priority**: Raw headers added via `add_raw_header()` take precedence over standard headers.

3. **Automatic Conversion**: Underscores (`_`) in raw header keys are automatically converted to dashes (`-`).

4. **Security Levels**: Always use `set_strict()` as default for production.

5. **CSP**: Always include `'self'` for user-based websites.

6. **HSTS**: Use `31536000` (1 year) for production and `86400` (1 day) for development.

---

## Troubleshooting

### Error: `'NoneType' object has no attribute 'add'`
```python
# ❌ Wrong
x.headers.csp.add()  # CSP not properly initialized

# ✅ Correct
x = Page()
x.headers.csp.add('default-src', "'self'")
```

### Error: `Invalid policy`
```python
# ❌ Wrong
x.headers.frame_options(policy="ALLOW-FROM")  # ALLOW-FROM is deprecated

# ✅ Correct
x.headers.frame_options(policy="SAMEORIGIN")
```

### Headers Not Applied
```python
# ✅ Correct - Page class handles building automatically
x = Page()
x.headers.csp.add('default-src', "'self'")
# Headers are automatically built by Page
```