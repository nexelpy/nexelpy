



#  NexelPy

### A full web app. One language. HTML, CSS, JavaScript, Database — all in Python.

**"We are not code workers, we are developers."**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Starlette](https://img.shields.io/badge/Built%20on-Starlette-purple.svg)](https://starlette.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)



---

## 😩 The Familiar Story

You have an idea. A web app. You need to start:

```
Project structure, venv, dependencies...
Pick a framework
For JS: webpack? vite? esbuild?
Template engine?
Forms, validation, routing...
```

**Three hours have passed. You don't have a single page yet.**

And when you want to bring code from your previous project into this one — you have to repeat the entire setup.

---

## 🎯 NexelPy Breaks This Cycle

NexelPy asks a simple question: **"Why should we learn a separate language and tool for every layer of the web?"**

Then it answers: **You don't have to.**

```python
from nexelpy import Nexelpy, Route, View

app = Nexelpy(__file__)

@app.route("/")
async def home():
    x = View(__file__, title="NexelPy")
    x.h1("hello world from nexelpy")
    return x.RESPONSE()

if __name__ == "__main__":
    app.run()
```

That's it. `python main.py`. A complete web app, no build tools, no config.

---

## ✨ Five Things That Give You Time Back

### 1. 🚀 Auto-Routing — Without a Single Extra Import

**This is one of the most compelling parts of NexelPy.**

In other frameworks, for every view you have to:
1. Create a `views.py` file.
2. **Import** it in `urls.py` or `app.py`.
3. **Manually** add the path to a map.

In NexelPy:

```python
# views/users.py
from nexelpy import Route, View

@Route("/users")
async def users():
    x = View(__file__)
    x.h1("Users")
    return x.RESPONSE()
```

Just create `views/users.py`. NexelPy scans, finds `@Route`, and registers the route on startup. **No central imports, no URL maps, no boilerplate.**

As your project grows, you organize files into any folders you want. NexelPy finds them all.

---

### 2. 🧩 Plugins = Regular Python Code

**This is the biggest difference between NexelPy and any other framework.**

In other frameworks, "plugin" means a magical concept: config-driven, interface-based, hook-based. In NexelPy, **a plugin is just a module or a folder of Python code.**

Copy the folder into your project, import it, and use it. That's it.

```python
# views/navbar.py
from nexelpy import Plugin

async def navbar():
    x = Plugin(__file__)
    with x.div():
        with x.ul():
            with x.li(): x.a("Home", href="/")
            with x.li(): x.a("Users", href="/users")
            with x.li(): x.a("About", href="/about")
            with x.li(): x.a("Contact", href="/contact")
    return x.RESPONSE()
```

```python
# views/home.py
from nexelpy import Route, View
from views.navbar import navbar

@Route("/")
async def home():
    x = View(__file__, title="NexelPy")
    await x.importPlugin(navbar())
    x.h1("hello world from nexelpy")
    return x.RESPONSE()
```

Plugins have access to every capability of a web page:

- ✅ Can be a **middleware** (`@Middleware`)
- ✅ Full access to the **request** object
- ✅ Can **redirect**, **set cookies**, **return JSON**
- ✅ Can use **View**, **Nextyle**, **Nexcript**
- ✅ Can be a reusable **View fragment**

**Meaning: anything you write in a view, you can write in a plugin.** No new API to learn.

#### Why This Matters

In raw HTML, if you have a "user card" and want to use it across 5 pages, **you copy the code 5 times**. Or you have to learn a template engine.

In NexelPy, **you break your View code into separate files**. Each section is a file, a testable, reusable function. Just like any other Python code.

You can even use plugins written by other developers instead of writing your own. Plugins have a **marketplace** at [nexelpy.net](https://nexelpy.net). You can download a login form with client and server-side validation that has been tested and debugged by a developer, and use it by copying it into your project.

---

### 3. 🗂️ Static File Serving — No Mounting, No Restrictions

In every other framework:

- Static files must be in a specific folder (`static/`).
- You must `mount` that folder.
- You must prefix your paths (`/static/...`).

In NexelPy, HTML, CSS, and JavaScript files are served directly **from anywhere in your project**.

For other static files, create a folder named `static` anywhere in your project — its contents are served statically without dealing with mounts. **Any `static` folder in the project is valid for the server.**

NexelPy supports both relative and absolute paths.

> **This structure means no architecture is forced upon the developer.** The developer or team decides what architecture and structure to use. For small projects, you can dump files flat in the root, or for large projects, put each prefix in its own directory.

---

### 4. 🎨 CSS in Python — `Nextyle`

Write CSS right where you write your Python code. The `.css` file is generated automatically.

```python
# views/home.py
from nexelpy import Nextyle

with Nextyle(__file__) as y:
    y.select("body").background_color("#1a1a2e").color("#eee")
    y.select(".card").padding("4px", sm="8px", md="12px", lg="20px")\
        .hover().box_shadow("0 8px 24px rgba(0,0,0,0.3)")
```

Output:

```css
/* views/home.css */
body {
    background-color: #1a1a2e;
    color: #eee;
}

.card {
    padding: 4px;
}

.card:hover {
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
}

@media (min-width: 640px) {
    .card { padding: 8px; }
}

@media (min-width: 768px) {
    .card { padding: 12px; }
}

@media (min-width: 1024px) {
    .card { padding: 20px; }
}
```

Everything is available: media queries (`sm`, `md`, `lg`, `xl`, `ul`), keyframes, `@layer`, `@container`, `@scope`, `@font-face`, `@supports`, `@property`, variables. No build step, no new syntax.

---

### 5. 🧠 JavaScript and TypeScript in Python — `Nexcript`

```python
from nexelpy import Nexcript

with Nexcript(__file__) as s:
    s.add_script("""
        alert("hello Nexcript")
    """)
```

The `.js` file is generated automatically. **TypeScript is also supported** — NexelPy detects it and compiles it for you.

---

## ⚡ QuickEvent — Reactive Without JavaScript

Define behaviors with HTML attributes. Not a single line of JS.

```python
from nexelpy import Route, View

@Route("/quickevent")
async def home():
    x = View(__file__, title="QuickEvent Demo")
    x.button("click me", click=["setText", "#my-paragraph", "hello world!"])
    x.p("click the button", id="my-paragraph")
    return x.RESPONSE()
```

Content updates, classes, Ajax requests, animations, modals, accordions, conditional logic. XSS protection with DOMPurify.

[QuickEvent full documentation →](https://github.com/NexeLinstance/quickevent)

---

## 🛡️ Why Trust NexelPy?

NexelPy is built on **Starlette** — one of the most mature and fastest ASGI frameworks for Python.

| Feature | Starlette (NexelPy) | Other Frameworks |
|---|---|---|
| **Async-native (ASGI)** | ✅ | ❌ (WSGI, limited async) |
| **WebSocket** | ✅ Native | ⚠️ Requires separate channel |
| **HTTP/2** | ✅ | ⚠️ |
| **Request speed** | 🥇 Fastest | 🐢 Slower |
| **Overhead** | Negligible | Medium to high |

Starlette **outperforms most Python frameworks** in benchmarks. NexelPy is built on this foundation and **has no extra middleware in the kernel** — so every request in NexelPy is as fast as a pure Starlette request.

### What We **Don't** Do (And Why It Matters)

- ❌ **Regenerate CSS/JS on every request** — NexelPy doesn't. Only on startup.
- ❌ **Re-read AST on every request** — NexelPy doesn't. Only in `__init__`.
- ❌ **Use a slow template engine** — NexelPy doesn't have one. It's a string builder.

**If Starlette is fast enough for you, NexelPy is too.**

---

## 🏗️ Mental Model

In traditional frameworks, you have a separate tool for each layer. In NexelPy, everything is one language:

```
NexelPy
├── @Route()        ← Routes (auto-discovered)
├── View()          ← HTML
├── Nextyle         ← CSS
├── Nexcript        ← JS / TS
├── QuickEvent      ← Reactive behaviors
├── @Middleware     ← Middle layers
├── Plugins         ← Your Python code
└── Headers         ← Backend security headers
```

All in harmony, all in one language, all in one project.

---

## 🗄️ Database

NexelPy is integrated with **Piccolo ORM** — a modern, async, and fast ORM for Python. Both are async, and the integration with NexelPy is seamless and painless.

```python
from nexelpy import Route, View
from piccolo.columns.column_types import Varchar
from piccolo.engine.sqlite import SQLiteEngine
from piccolo.table import Table

DB = SQLiteEngine()

class Band(Table, db=DB):
    name = Varchar()

@Route("/")
async def home():
    x = View(__file__, title="NexelPy")
    bands = await Band.select()
    for band in bands:
        x.p(f"name: {band['name']}")
    return x.RESPONSE()
```

---

## 💡 What NexelPy **Doesn't** Do (And Why It's Fine)

- **No built-in authentication.** An official plugin is on the way.
- **No admin panel.** It's planned.
- **The plugin ecosystem is just starting.** It will grow over time.

**Scale:** NexelPy is built on Starlette. If Starlette works for you, NexelPy works for you (`uvicorn main:app --workers 4` in production).

---

## 🚀 Getting Started

```bash
pip install nexelpy
```

```python
# main.py
from nexelpy import Nexelpy, Route, View

app = Nexelpy(__file__)

@app.route("/")
async def home():
    x = View(__file__, title="NexelPy")
    x.h1("hello world from nexelpy")
    return x.RESPONSE()

if __name__ == "__main__":
    app.run()
```

```bash
python main.py
```

**Browser → `http://127.0.0.1:8000`**

**That's it.** Auto-reloader (`.py` only), beautiful error pages in dev, everything ready.

---

## 📈 Project Status

| Area | Status |
|---|---|
| Routing, View, Nextyle, Nexcript | ✅ Stable |
| QuickEvent | ✅ Stable |
| Plugin & Middleware System | ✅ Stable |
| Piccolo ORM | ✅ Integrated |
| Header Builder (Security) | ✅ Stable |
| Full Documentation | 🚧 In progress |
| Plugin Marketplace | 🚧 On nexelpy.net |
| Authentication (Official Plugin) | 🚧 Coming soon |

---

## 🤝 Contributing

Writing a plugin? Have an idea? NexelPy was designed for plugin extensibility from the start, and we welcome contributions.

Share your plugins with others. Your code can be a tiny card, a full page, or an entire website. It can be a security tool or an SEO helper.

[💬 GitHub Discussions](https://github.com/nexelpy/nexelpy/discussions)

---

## 📄 License

MIT

<div align="center">
<sub>Built for developers who are tired of too many tools.</sub>
</div>
```
