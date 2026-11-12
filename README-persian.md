
<div align="center">

# 🐍 NexelPy

### یک وب‌اپ کامل. یک زبان. HTML، CSS، JavaScript، Database — همه در پایتون.

**"We are not code workers, we are developers."**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Starlette](https://img.shields.io/badge/Built%20on-Starlette-purple.svg)](https://starlette.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)

</div>

---

## 😩 داستان آشنا

یک ایده دارید. یک وب‌اپ. باید شروع کنید:

```
ساختار پروژه، venv، dependency...
یک فریم‌ورک انتخاب کن
برای JS: webpack؟ vite؟ esbuild؟
template engine؟
فرم‌ها، validation، routing...
```

**سه ساعت گذشته. هنوز یک صفحه ندارید.**

بعد که بخواهید کد را از پروژه‌ی قبلی به این یکی بیاورید — کل setup تکرار می‌شود.

---

## 🎯 NexelPy این چرخه را قطع می‌کند

NexelPy یک سؤال ساده می‌پرسد: **«چرا برای هر لایه از وب باید یک زبان و یک ابزار جدا یاد بگیریم؟»**

پس پاسخ می‌دهد: **لازم نیست.**

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

همین. `python main.py`. یک وب‌اپ کامل، بدون build tool، بدون config.

---

## ✨ پنج چیزی که به شما زمان برمی‌گرداند

### ۱. 🚀 Routing خودکار — بدون یک خط import اضافه

**این یکی از جذاب‌ترین بخش‌های NexelPy است.**

در فریم‌ورک‌های دیگر برای هر view باید:
1. یک فایل `views.py` بسازید.
2. آن را در `urls.py` یا `app.py` **import** کنید.
3. مسیر را **دستی** به یک map اضافه کنید.

در NexelPy:

```python
# views/users.py
from nexelpy import Route, View

@Route("/users")
async def users():
    x = View(__file__)
    x.h1("Users")
    return x.RESPONSE()
```

فایل `views/users.py` را بسازید. NexelPy در startup خودش اسکن می‌کند، `@Route` را پیدا می‌کند، route را ثبت می‌کند. **هیچ import مرکزی، هیچ URL map، هیچ boilerplate.**

پروژه‌ی شما هرچقدر بزرگ‌تر بشود، فایل‌ها را در پوشه‌های دلخواه تقسیم می‌کنید. NexelPy همه را پیدا می‌کند.

---

### ۲. 🧩 پلاگین‌ها = کد پایتون معمولی

**این بزرگ‌ترین تفاوت NexelPy با هر فریم‌ورک دیگری است.**

در بقیه‌ی فریم‌ورک‌ها، «پلاگین» یعنی یک مفهوم جادویی: config-driven، interface-based، hook-based. در NexelPy، **پلاگین فقط یک ماژول یا یک پوشه از کد پایتون است.**

کپی پوشه در پروژه، import و استفاده. همین.

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

پلاگین به همه‌ی امکانات یک صفحه‌ی وب دسترسی دارد:

- ✅ می‌تواند **middleware** باشد (`@Middleware`)
- ✅ به **request** کامل دسترسی دارد
- ✅ می‌تواند **redirect** کند، **cookie** ست کند، **JSON** برگرداند
- ✅ می‌تواند از **View**، **Nextyle**، **Nexcript** استفاده کند
- ✅ می‌تواند یک **View fragment** قابل استفاده‌ی مجدد باشد

**یعنی: هر چیزی که در یک view می‌نویسید، در یک پلاگین هم می‌نویسید.** بدون API جدید.

#### چرا این مهم است؟

در HTML خام، اگر یک «کارت کاربر» دارید و می‌خواهید در ۵ صفحه استفاده کنید، **کد را ۵ بار کپی می‌کنید**. یا باید از template engine استفاده کنید.

در NexelPy، **کد View را به فایل‌های جدا می‌شکنید**. هر بخش یک فایل، یک تابع قابل تست و قابل استفاده‌ی مجدد. مثل هر کد پایتون دیگر.

حتی می‌توانید خودتان پلاگین ننویسید و از پلاگین‌های نوشته‌شده توسط دولوپرهای دیگر استفاده کنید. پلاگین‌ها یک **marketplace** در [nexelpy.net](https://nexelpy.net) دارند. می‌توانید یک فرم لاگین با validation در سمت کلاینت و بک‌اند که تست و دیباگ شده توسط یک دولوپر را دانلود کنید و با کپی کردن از آن استفاده کنید.

---

### ۳. 🗂️ سرو فایل‌های استاتیک — بدون mount، بدون محدودیت

در همه‌ی فریم‌ورک‌های دیگر:

- فایل‌های استاتیک باید در یک پوشه‌ی خاص (`static/`) باشند.
- باید آن پوشه را `mount` کنید.
- باید مسیرها را با prefix (`/static/...`) بنویسید.

در NexelPy، فایل‌های HTML، CSS، JavaScript **در هر جای پروژه** به صورت مستقیم سرو می‌شوند.

برای فایل‌های استاتیک دیگر، هر جای پروژه یک فولدر به نام `static` ایجاد کنید — محتوای درونش به صورت استاتیک سرو می‌شود بدون درگیر شدن با mount کردن. **پوشه‌های `static` در پروژه برای سرور معتبر هستند.**

NexelPy آدرس نسبی و مطلق را پشتیبانی می‌کند.

> **این ساختار باعث می‌شود هیچ معماری به دولوپر تحمیل نشود.** دولوپر یا تیم برنامه‌نویس تعیین می‌کند که از چه معماری و ساختاری استفاده کند. برای پروژه‌های کوچک می‌تواند فایل‌ها را تخت در روت بریزد، یا برای پروژه‌های بزرگ هر prefix را در یک دایرکتوری جدا بنویسد.

---

### ۴. 🎨 CSS در پایتون — `Nextyle`

CSS را همان‌جا که کد پایتون می‌نویسید بنویسید. فایل `.css` خودش ساخته می‌شود.

```python
# views/home.py
from nexelpy import Nextyle

with Nextyle(__file__) as y:
    y.select("body").background_color("#1a1a2e").color("#eee")
    y.select(".card").padding("4px", sm="8px", md="12px", lg="20px")\
        .hover().box_shadow("0 8px 24px rgba(0,0,0,0.3)")
```

خروجی:

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

همه‌چیز در دسترس: media queries (`sm`, `md`, `lg`, `xl`, `ul`)، keyframes، `@layer`، `@container`، `@scope`، `@font-face`، `@supports`، `@property`، variables. بدون build step، بدون سینتکس جدید.

---

### ۵. 🧠 JavaScript و TypeScript در پایتون — `Nexcript`

```python
from nexelpy import Nexcript

with Nexcript(__file__) as s:
    s.add_script("""
        alert("hello Nexcript")
    """)
```

فایل `.js` خودکار تولید می‌شود. **TypeScript هم پشتیبانی می‌شود** — NexelPy خودش تشخیص می‌دهد و کامپایل می‌کند.

---

## ⚡ QuickEvent — Reactive بدون JavaScript

رفتارها را با attribute HTML تعریف کنید. بدون یک خط JS.

```python
from nexelpy import Route, View

@Route("/quickevent")
async def home():
    x = View(__file__, title="QuickEvent Demo")
    x.button("click me", click=["setText", "#my-paragraph", "hello world!"])
    x.p("click the button", id="my-paragraph")
    return x.RESPONSE()
```

تغییر محتوا، کلاس، ارسال Ajax، انیمیشن، مودال، آکاردئون، منطق شرطی. امنیت XSS با DOMPurify.

[مستندات کامل QuickEvent →](https://github.com/NexeLinstance/quickevent)

---

## 🛡️ چرا به NexelPy اعتماد کنیم؟

NexelPy روی **Starlette** بنا شده — یکی از بالغ‌ترین و سریع‌ترین فریم‌ورک‌های ASGI پایتون.

| ویژگی | Starlette (NexelPy) | Other Frameworks |
|---|---|---|
| **Async-native (ASGI)** | ✅ | ❌ (WSGI، async محدود) |
| **WebSocket** | ✅ بومی | ⚠️ نیاز به کانال جدا |
| **HTTP/2** | ✅ | ⚠️ |
| **سرعت request** | 🥇 بالاترین | 🐢 کندتر |
| **Overhead** | ناچیز | متوسط تا بالا |

Starlette در بنچمارک‌ها **سریع‌تر از اغلب فریم‌ورک‌های پایتونی** است. NexelPy روی این پایه ساخته شده و **هیچ middleware اضافه‌ای در kernel ندارد** — پس هر request در NexelPy به اندازه‌ی یک request خالص Starlette سریع است.

### چه چیزهایی **نمی‌کنیم** (و چرا مهم است)

- ❌ **تولید مجدد CSS/JS در هر request** — NexelPy نمی‌کند. فقط در startup.
- ❌ **خواندن مجدد AST در هر request** — NexelPy نمی‌کند. فقط در `__init__`.
- ❌ **استفاده از template engine کند** — NexelPy ندارد. String builder است.

**اگر Starlette برای شما کافی است، NexelPy هم هست.**

---

## 🏗️ مدل ذهنی

در فریم‌ورک‌های سنتی، برای هر لایه یک ابزار جدا دارید. در NexelPy، همه یک زبان هستند:

```
NexelPy
├── @Route()        ← روت‌ها (auto-discovered)
├── View()          ← HTML
├── Nextyle         ← CSS
├── Nexcript        ← JS / TS
├── QuickEvent      ← رفتار reactive
├── @Middleware     ← لایه‌های میانی
├── Plugins         ← کد پایتون شما
└── Headers         ← هدرهای امنیتی در بک‌اند
```

همه هماهنگ، همه در یک زبان، همه در یک پروژه.

---

## 🗄️ دیتابیس

NexelPy با **Piccolo ORM** یکپارچه است — یک ORM مدرن، async، و سریع برای پایتون. هر دو async هستند و ارتباطش با NexelPy بسیار راحت و بدون دردسر است.

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

## 💡 آنچه NexelPy **نمی‌کند** (و چرا مشکلی نیست)

- **Authentication آماده ندارد.** یک پلاگین رسمی در راه است.
- **Admin panel ندارد.** در برنامه است.
- **اکوسیستم پلاگین تازه شروع شده.** در آینده گسترده‌تر می‌شود.

**مقیاس:** NexelPy روی Starlette است. اگر Starlette برای شما جواب می‌دهد، NexelPy هم جواب می‌دهد (`uvicorn main:app --workers 4` در production).

---

## 🚀 شروع

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

**مرورگر → `http://127.0.0.1:8000`**

**همین.** reloader خودکار (فقط `.py`)، error page زیبا در dev، همه‌چیز آماده.

---

## 📈 وضعیت پروژه

| بخش | وضعیت |
|---|---|
| Routing، View، Nextyle، Nexcript | ✅ پایدار |
| QuickEvent | ✅ پایدار |
| سیستم پلاگین و Middleware | ✅ پایدار |
| Piccolo ORM | ✅ یکپارچه |
| Header Builder (امنیت) | ✅ پایدار |
| مستندات کامل | 🚧 در حال آماده‌سازی |
| Marketplace پلاگین | 🚧 در سایت nexelpy.net |
| Authentication (پلاگین رسمی) | 🚧 به زودی |

---

## 🤝 مشارکت

پلاگین می‌نویسید؟ ایده دارید؟ NexelPy از ابتدا برای پلاگین‌پذیری طراحی شده و از مشارکت استقبال می‌کند.

پلاگین‌های خودتان را با دیگران به اشتراک بگذارید. کد شما می‌تواند یک کارد کوچک باشد تا یک صفحه‌ی کامل، تا یک وب‌سایت کامل. می‌تواند یک ابزار برای امنیت باشد یا کمک به سئو.

[💬 GitHub Discussions](https://github.com/nexelpy/nexelpy/discussions)

---

## 📄 لایسنس

MIT

<div align="center">
<sub>ساخته شده برای توسعه‌دهندگانی که از ابزارهای زیاد خسته شده‌اند.</sub>
</div>
```
