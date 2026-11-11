
# Middleware در NexelPy

این سند توضیح می‌دهد middleware چیست، چطور در NexelPy کار می‌کند، و چطور می‌توانید middleware خودتان را اضافه کنید.

---

## ۱. Middleware چیست؟

Middleware یک لایه‌ی نازک است که **قبل از** رسیدن درخواست به route (view) و **بعد از** آماده شدن پاسخ، اجرا می‌شود.

### چرخه‌ی یک درخواست

```
Client → [Middleware 1] → [Middleware 2] → [Middleware 3] → Route (View) → Response
                                                                              ↓
Client ← [Middleware 1] ← [Middleware 2] ← [Middleware 3] ← Response ←──────┘
```

هر middleware می‌تواند:
- درخواست را **رد کند** (مثلاً اگر احراز هویت نشده → 401).
- درخواست را **تغییر دهد** (مثلاً اضافه کردن `user` به `scope`).
- پاسخ را **تغییر دهد** (مثلاً اضافه کردن هدر امنیتی).
- درخواست را **بدون تغییر** به middleware بعدی پاس دهد.

### مثال‌های واقعی

| Middleware | کار |
|---|---|
| Auth | چک کردن توکن لاگین. اگر نبود → 401 |
| Session | خواندن کوکی و رمزگشایی آن. اضافه کردن `session` به `scope` |
| CSRF | چک کردن توکن CSRF در درخواست‌های POST |
| Rate Limit | محدود کردن تعداد درخواست‌ها |
| Logging | ثبت درخواست‌ها |
| CORS | اضافه کردن هدرهای CORS |

---

## ۲. چطور در NexelPy کار می‌کند؟

NexelPy از یک registry (ثبت‌کننده) استفاده می‌کند. وقتی شما یک middleware می‌سازید، با دکوریتور `@Middleware` آن را ثبت می‌کنید. سپس NexelPy در `MainAppBuilder.__init__` همه‌ی middlewareهای ثبت‌شده را می‌خواند، ترتیب آن‌ها را بر اساس وابستگی (`after`) حل می‌کند، و به Starlette اضافه می‌کند.

### جریان کار

```
1. شما @Middleware(name="auth", after="session") را می‌نویسید.
2. با import شدن فایل، MiddlewareRegistry پر می‌شود.
3. Nexelpy(__file__) اجرا می‌شود.
4. MainAppBuilder.__init__ → MiddlewareRegistry().get_ordered() را می‌خواند.
5. middlewareها به ترتیب به Starlette اضافه می‌شوند.
6. middleware_stack بازسازی می‌شود.
```

---

## ۳. نوشتن اولین Middleware

### ساختار پایه

```python
from nexelpy import Middleware


@Middleware(name="my_middleware")
class MyMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # 1. کد قبل از درخواست
        await self.app(scope, receive, send)
        # 2. کد بعد از درخواست
```

### اجزای این کلاس

| جزء | توضیح |
|---|---|
| `@Middleware(name=..., after=...)` | دکوریتور ثبت. `name` نام یکتای middleware (برای ارجاع). `after` نام middlewareای که این یکی باید **بعد از** آن اجرا شود. |
| `__init__(self, app)` | Starlette این کلاس را با `app` (middleware بعدی) می‌سازد. شما `app` را ذخیره می‌کنید. |
| `async def __call__(self, scope, receive, send)` | این متد ASGI است. Starlette آن را برای هر درخواست صدا می‌زند. |
| `await self.app(scope, receive, send)` | درخواست را به middleware بعدی (یا route) پاس می‌دهد. |

### `__call__` چطور کار می‌کند؟

`__call__` یک تابع ASGI است. Starlette آن را با سه آرگومان صدا می‌زند:

| آرگومان | نوع | توضیح |
|---|---|---|
| `scope` | `dict` | اطلاعات درخواست (مثل `path`, `method`, `headers`, `state`, `app`). |
| `receive` | `async callable` | تابعی برای دریافت داده (مثل بدنه‌ی درخواست). |
| `send` | `async callable` | تابعی برای ارسال پاسخ. |

**نکته‌ی مهم:** شما `await self.app(scope, receive, send)` را صدا می‌زنید. این کار درخواست را به middleware بعدی (یا route) پاس می‌دهد. اگر این خط را ننویسید، درخواست هرگز به route نمی‌رسد و کاربر پاسخی نمی‌گیرد.

---

## ۴. مثال ۱: Middleware ساده (Logging)

```python
from nexelpy import Middleware
from rich.console import Console

console = Console()


@Middleware(name="logger")
class LoggingMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            console.print(f"[blue]{scope['method']}[/blue] {scope['path']}")
        await self.app(scope, receive, send)
```

این middleware هر درخواست را در ترمینال چاپ می‌کند.

---

## ۵. مثال ۲: Middleware با تغییر `scope` (تزریق state)

```python
from nexelpy import Middleware


@Middleware(name="greeter")
class GreeterMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            scope.setdefault("state", {})
            scope["state"]["greeting"] = "Hello from middleware!"
        await self.app(scope, receive, send)
```

در view:

```python
@Route("/")
async def home():
    x = View(__file__)
    greeting = await x.REQUEST.state("greeting")
    x.p(greeting)
    return x.RESPONSE()
```

---

## ۶. مثال ۳: Middleware با رد کردن درخواست

```python
from nexelpy import Middleware
from starlette.responses import PlainTextResponse


@Middleware(name="auth")
class AuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        if not scope["path"].startswith("/protected"):
            return await self.app(scope, receive, send)

        headers = dict(scope.get("headers", []))
        token = headers.get(b"x-auth-token", b"").decode()

        if token != "secret":
            response = PlainTextResponse("Unauthorized", status_code=401)
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)
```

**نکته:** وقتی می‌خواهید درخواست را رد کنید، یک `Response` می‌سازید و آن را با `await response(scope, receive, send)` می‌فرستید. سپس `return` می‌کنید تا `self.app` صدا زده نشود.

---

## ۷. وابستگی (ترتیب)

### `after`

اگر middleware شما به middleware دیگری نیاز دارد، از `after` استفاده کنید:

```python
@Middleware(name="auth", after="session")
class AuthMiddleware:
    ...
```

این یعنی: «`AuthMiddleware` باید **بعد از** `SessionMiddleware` اجرا شود.»

### چرا مهم است؟

فرض کنید `SessionMiddleware` کوکی را می‌خواند و `scope["state"]["session"]` را پر می‌کند. `AuthMiddleware` می‌خواهد از `session` بخواند. اگر `AuthMiddleware` **قبل از** `SessionMiddleware` اجرا شود، `session` خالی است و auth کار نمی‌کند.

با `after="session"`، تضمین می‌شود که `AuthMiddleware` بعد از `SessionMiddleware` اجرا شود.

### خطا در وابستگی

اگر `after` به middleware ناموجود اشاره کند (مثلاً `after="ss"` که وجود ندارد):

```
14:32:15 (nexelpy Middleware Error)
         Cannot resolve middleware order. This is usually caused by:
           - A circular dependency (A after B, B after A)
           - A missing 'after' target (the referenced middleware is not registered/imported)
         Unresolved middlewares: ['auth (after: ss)']
```

برنامه متوقف می‌شود. باید مطمئن شوید که middleware مورد نظر import شده است.

### حلقه (Circular Dependency)

اگر A بعد از B باشد و B بعد از A:

```
14:32:15 (nexelpy Middleware Error)
         Cannot resolve middleware order...
         Unresolved middlewares: ['a (after: b)', 'b (after: a)']
```

---

## ۸. ثبت و اجرا

### چطور middleware ثبت می‌شود؟

با دکوریتور `@Middleware`. وقتی فایل import می‌شود، `@Middleware` middleware را در `MiddlewareRegistry` ثبت می‌کند.

```python
# main.py
from nexelpy import Nexelpy
import my_middleware   # ← ثبت middleware
import views           # ← ثبت routeها

app = Nexelpy(__file__)

if __name__ == "__main__":
    app.run()
```

**نکته‌ی مهم:** `import my_middleware` باید **قبل از** `Nexelpy(__file__)` باشد. چون `Nexelpy.__init__` `MiddlewareRegistry` را می‌خواند.

### چطور middleware اجرا می‌شود؟

`MainAppBuilder.__init__`:
1. `MiddlewareRegistry().get_ordered()` را صدا می‌زند.
2. middlewareها را به Starlette اضافه می‌کند.
3. `middleware_stack` را بازسازی می‌کند.

از آن به بعد، Starlette middlewareها را برای هر درخواست اجرا می‌کند.

---

## ۹. ترتیب اجرای middleware

### Starlette چطور middlewareها را اجرا می‌کند؟

Starlette middlewareهایی که با `add_middleware` اضافه می‌شوند را **معکوس** اجرا می‌کند. یعنی:

```python
self.add_middleware(A)
self.add_middleware(B)
self.add_middleware(C)
```

ترتیب اجرا: `C → B → A → Route → A → B → C`

**چرا؟** چون هر middleware، middleware بعدی را در `self.app` صدا می‌زند. `C` که آخرین اضافه شده، اولین middleware است که اجرا می‌شود.

### `get_ordered` چطور ترتیب را برمی‌گرداند؟

`get_ordered` middlewareها را به ترتیبی برمی‌گرداند که **باید در لیست `add_middleware` قرار بگیرند**. یعنی اول `session`، بعد `auth`، بعد `csrf` (در صورت وجود). سپس `MainAppBuilder` آن‌ها را به همان ترتیب `add_middleware` می‌کند. Starlette آن‌ها را **معکوس** اجرا می‌کند. پس در عمل، `csrf` اول اجرا می‌شود، بعد `auth`، بعد `session`.

**نکته:** این طراحی درست است. `get_ordered` ترتیب «لایه‌بندی» را برمی‌گرداند (کدام middleware به کدام نیاز دارد)، و Starlette ترتیب «اجرا» را خودش می‌سازد (معکوس).

---

## ۱۰. یک middleware کامل (قالب)

```python
from nexelpy import Middleware
from starlette.responses import PlainTextResponse


@Middleware(name="my_middleware", after="session")
class MyMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # فقط برای HTTP
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        # 1. قبل از درخواست
        # (مثلاً خواندن session، چک کردن auth)
        session = scope.get("state", {}).get("session", {})
        if not session.get("user_id"):
            response = PlainTextResponse("Please login", status_code=401)
            await response(scope, receive, send)
            return

        # 2. پاس دادن به middleware بعدی
        await self.app(scope, receive, send)

        # 3. بعد از درخواست (اختیاری)
        # (مثلاً اضافه کردن هدر به پاسخ - اما send قبلاً صدا زده شده!)
```

**نکته‌ی مهم:** اگر می‌خواهید پاسخ را تغییر دهید (مثلاً هدر اضافه کنید)، باید `send` را wrap کنید:

```python
async def __call__(self, scope, receive, send):
    async def send_wrapper(message):
        if message["type"] == "http.response.start":
            headers = dict(message.get("headers", []))
            headers[b"x-custom"] = b"value"
            message["headers"] = list(headers.items())
        await send(message)

    await self.app(scope, receive, send_wrapper)
```

---

## ۱۱. اشتباهات رایج

### ❌ فراموش کردن `await self.app(...)`

```python
async def __call__(self, scope, receive, send):
    # ... (بدون await self.app)
```

**نتیجه:** درخواست هرگز به route نمی‌رسد. کاربر پاسخی نمی‌گیرد.

### ❌ `return` بدون `await response(...)`

```python
if not authorized:
    return PlainTextResponse("Unauthorized", status_code=401)
```

**نتیجه:** Starlette خطا می‌دهد. باید `await response(scope, receive, send)` را صدا بزنید.

### ❌ `after` به middleware ناموجود

```python
@Middleware(name="auth", after="nonexistent")
```

**نتیجه:** `MiddlewareError` و توقف برنامه.

### ❌ import نکردن middleware

```python
# main.py
from nexelpy import Nexelpy
# import my_middleware  ← فراموش شده
app = Nexelpy(__file__)
```

**نتیجه:** middleware هرگز ثبت نمی‌شود و اجرا نمی‌شود.

### ❌ نوشتن `async def` برای `__init__`

```python
async def __init__(self, app):  # اشتباه
    ...
```

**نتیجه:** `__init__` نمی‌تواند `async` باشد. `__call__` است که `async` است.

---

## ۱۲. سؤالات متداول

### چرا `__call__` باید `async` باشد؟

چون Starlette (و ASGI) از `async/await` استفاده می‌کند. اگر `async` نباشد، Starlette خطا می‌دهد.

### `app` در `__init__` چیست؟

`app` همان middleware بعدی (یا route) است. Starlette آن را با `app=next_middleware` می‌سازد.

### چرا `scope["type"] != "http"`؟

چون Starlette ممکن است middleware را برای WebSocket یا lifespan هم صدا بزند. اگر می‌خواهید فقط روی HTTP کار کنید، این چک لازم است.

### اگر بخواهم middleware را غیرفعال کنم؟

فایل middleware را import نکنید. یا `after` را به middlewareای بدهید که وجود ندارد (که خطا می‌دهد). یا `MiddlewareRegistry().clear()` را صدا بزنید (که همه را پاک می‌کند).

### آیا می‌توانم middleware را بعد از `Nexelpy(__file__)` import کنم؟

**نه.** باید قبل از `Nexelpy(__file__)` باشد. چون `MainAppBuilder.__init__` `MiddlewareRegistry` را می‌خواند. اگر بعد از آن import کنید، middleware ثبت می‌شود اما `MainAppBuilder` آن را نمی‌بیند.

---

## ۱۳. جمع‌بندی

| مورد | نکته |
|---|---|
| تعریف | `@Middleware(name="...", after="...")` |
| ساخت | `def __init__(self, app): self.app = app` |
| اجرا | `async def __call__(self, scope, receive, send): ...` |
| پاس دادن | `await self.app(scope, receive, send)` |
| رد کردن | `response = PlainTextResponse(...); await response(scope, receive, send); return` |
| ترتیب | `after="session"` (بعد از session) |
| ثبت | `import my_middleware` قبل از `Nexelpy(__file__)` |
| خطا | `MiddlewareError` (چاپ با rich + `sys.exit(1)`) |

با این الگو، می‌توانید هر middlewareای بنویسید: auth، rate limit، logging، CORS، و هر چیز دیگری.
```

