
# مستندات کامل Nexcript

**تبدیل TypeScript به JavaScript با پشتیبانی کامل از import، URL، و scoping — به سبک Pythonic**

---

## فهرست مطالب

1. [معرفی](#۱-معرفی)
2. [نصب و راه‌اندازی](#۲-نصب-و-راهاندازی)
3. [ساختار پایه](#۳-ساختار-پایه)
4. [نوشتن کد](#۴-نوشتن-کد)
5. [تشخیص خودکار TypeScript و JavaScript](#۵-تشخیص-خودکار-typescript-و-javascript)
6. [پیش‌نیازها (Node.js)](#۶-پیشنیازها-nodejs)
7. [مدیریت خودکار URL و Import](#۷-مدیریت-خودکار-url-و-import)
8. [Scoping](#۸-scoping)
9. [یکپارچه‌سازی با View](#۹-یکپارچهسازی-با-view)
10. [سناریوهای خطا و رفتار مورد انتظار](#۱۰-سناریوهای-خطا-و-رفتار-مورد-انتظار)
11. [نکات پیشرفته و اشتباهات رایج](#۱۱-نکات-پیشرفته-و-اشتباهات-رایج)
12. [API کامل (مرجع سریع)](#۱۲-api-کامل-مرجع-سریع)

---

## ۱. معرفی

`Nexcript` یک ابزار برای نوشتن JavaScript و TypeScript به صورت درون‌خطی در فایل‌های پایتون است. شما کد خود را درون یک فایل `.py` می‌نویسید و `Nexcript` به صورت خودکار یک فایل `.js` کنار همان فایل تولید می‌کند.

### مزایا
- **بدون تنظیمات build جداگانه**: با اجرای فایل پایتون، JS تولید می‌شود.
- **تبدیل خودکار TypeScript به JavaScript**: با استفاده از Node.js.
- **مدیریت خودکار مسیرها**: `import`های نسبی، `url()`ها و `scoping`ها به صورت خودکار اصلاح می‌شوند.
- **تشخیص خودکار زبان**: کاربر لازم نیست بگوید کدش TS است یا JS.
- **پشتیبانی از scoping**: هر فایل JS یک scope اختصاصی دارد تا با فایل‌های دیگر تداخل نکند.

### وابستگی‌ها
- پایتون ۳.۸+
- (اختیاری) Node.js 22.6+ برای تبدیل TypeScript.

---

## ۲. نصب و راه‌اندازی

`Nexcript` بخشی از NexelPy است و نیازی به نصب جداگانه ندارد:

```python
from nexelpy import Nexcript
```

### اولین فایل اسکریپت

یک فایل به نام `script.py` کنار فایل اصلی پروژه بسازید:

```python
from nexelpy import Nexcript

with Nexcript(__file__) as n:
    n.raw_script("""
        console.log("Hello, NexelPy!");
    """)
```

با اجرای این فایل، یک فایل `script.js` در همان پوشه ساخته می‌شود:

```javascript
console.log("Hello, NexelPy!");
```

> **نکته:** همیشه از `with` استفاده کنید. در غیر این صورت، فایل JS تولید نمی‌شود.

---

## ۳. ساختار پایه

### `Nexcript(__file__, ...)`

| پارامتر | نوع | پیش‌فرض | توضیح |
|---|---|---|---|
| `file` | `str \| Path` | **الزامی** | مسیر فایل پایتون (`__file__`). |
| `export_path` | `str \| Path \| None` | `None` | مسیر خروجی JS. پیش‌فرض: کنار فایل پایتون با پسوند `.js`. |

### نمونه

```python
with Nexcript(__file__, export_path="./dist/main.js") as n:
    n.raw_script("console.log('Hello');")
```

### مشخصات فایل تولیدشده

- **مسیر پیش‌فرض:** `script.py` → `script.js` (در همان پوشه).
- **`src` (آدرس URL):** به صورت خودکار از روی `project_root` و `export_path` محاسبه می‌شود.
  ```python
  with Nexcript(__file__) as n:
      print(n.src)  # → "/script.js"
  ```

---

## ۴. نوشتن کد

### روش اصلی: `raw_script(code, lang=None)`

```python
with Nexcript(__file__) as n:
    n.raw_script("console.log('Hello');")
    n.raw_script("const x: number = 42;")  # TypeScript (auto-detect)
    n.raw_script("const y = 10;", lang="js")  # Explicit JavaScript
```

### چند بلوک کد

می‌توانید `raw_script` را چند بار صدا بزنید. کدها به ترتیب و با یک خط خالی (`\n\n`) از هم جدا می‌شوند:

```python
with Nexcript(__file__) as n:
    n.raw_script("""
        import { greet } from "./utils.js";
        greet("World");
    """)
    n.raw_script("""
        console.log("Second block");
    """)
```

خروجی:

```javascript
import { greet } from "/utils.js";
greet("World");

console.log("Second block");
```

### کد چندخطی

`inspect.cleandoc` به صورت خودکار indentation اضافی را حذف می‌کند:

```python
n.raw_script("""
    function greet(name) {
        console.log("Hello, " + name);
    }
    greet("World");
""")
```

---

## ۵. تشخیص خودکار TypeScript و JavaScript

`Nexcript` به صورت خودکار تشخیص می‌دهد که کد شما TypeScript است یا JavaScript. کاربر نیازی به تنظیم `lang` ندارد.

### الگوهای تشخیص TypeScript

| الگو | مثال |
|---|---|
| Type annotation | `const x: string = "hi"` |
| Array types | `const arr: string[] = []` |
| Generics | `const arr: Array<number> = []` |
| Interface | `interface User { ... }` |
| Type alias | `type ID = string` |
| Type assertion | `const x = value as string` |
| Non-null assertion | `user!.name` |
| Optional property | `{ name?: string }` |
| Enum | `enum Color { Red, Green }` |
| Type import | `import type { User } from "..."` |
| Function return type | `function foo(): string { ... }` |
| Visibility modifier | `public name: string` |

### استفاده

```python
n.raw_script("const x: number = 42;")  # → TypeScript (auto)
n.raw_script("const y = 42;")          # → JavaScript (auto)
n.raw_script("const z: number = 42;", lang="js")  # → JavaScript (forced)
```

### اگر heuristic اشتباه کند

در موارد نادر (مثلاً JS با کد خاص)، کاربر می‌تواند صریحاً `lang` بدهد:

```python
n.raw_script("const x = { a: 1, b: 2 };", lang="js")  # مطمئن شو JS است
```

---

## ۶. پیش‌نیازها (Node.js)

### برای JavaScript خالص
هیچ پیش‌نیازی ندارد. کد JS بدون Node.js هم تولید می‌شود.

### برای TypeScript
Node.js نسخه **22.6.0 یا بالاتر** الزامی است.

| وضعیت | نتیجه |
|---|---|
| Node.js نصب نیست | ❌ خطا با پیام واضح |
| Node.js < 22.6 | ❌ خطا با پیام واضح |
| Node.js >= 22.6 | ✅ تبدیل موفق |

### نصب Node.js

- **Linux (Ubuntu/Debian):**
  ```bash
  curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
  sudo apt-get install -y nodejs
  ```
- **macOS:**
  ```bash
  brew install node
  ```
- **Windows:**
  از [nodejs.org](https://nodejs.org) دانلود و نصب کنید.

### بررسی نسخه

```bash
node --version
# باید v22.6.0 یا بالاتر باشد
```

---

## ۷. مدیریت خودکار URL و Import

### تبدیل `url(...)`

مسیرهای نسبی درون `url()` به صورت خودکار به URL مطلق (نسبت به روت پروژه) تبدیل می‌شوند:

```python
n.raw_script("""
    const img = url("./images/logo.png");
""")
```

خروجی:

```javascript
const img = "/images/logo.png";
```

**قوانین:**
- `./...` و `../...` → نسبت به موقعیت فایل `.py`.
- `/...` → نسبت به روت پروژه.
- `http://`, `https://`, `//`, `data:` → دست‌نخورده می‌مانند.

### تبدیل `import` و `export`

مسیرهای نسبی درون `import` و `export` هم اصلاح می‌شوند:

```python
n.raw_script("""
    import { greet } from "./utils.js";
    export { hello } from "./helpers.js";
""")
```

خروجی:

```javascript
import { greet } from "/utils.js";
export { hello } from "/helpers.js";
```

**قوانین:**
- اگر مسیر پسوند نداشته باشد (مثل `./utils`)، `.js` اضافه می‌شود.
- مسیرهای مطلق (`/...`) و URLهای خارجی (`http://`, ...) دست‌نخورده می‌مانند.

---

## ۸. Scoping

`Nexcript` از `scoping()` برای محدود کردن کد به یک element خاص استفاده می‌کند.

### استفاده

```python
n.raw_script("""
    const btn = scoping();
    btn.addEventListener("click", () => alert("Hi"));
""")
```

خروجی (با فرض اینکه scope_token = `abc12`):

```javascript
const btn = document.querySelector('[data-scoping="abc12"]');
btn.addEventListener("click", () => alert("Hi"));
```

### نکته مهم

`scoping()` را باید با `scoping()` در `View` جفت کنید:

```python
# در main.py (View)
x = View(__file__)
with x.scoping():
    x.button("Click me")
```

```python
# در script.py (Nexcript)
with Nexcript(__file__) as n:
    n.raw_script("scoping().addEventListener('click', () => alert('Hi'));")
```

### Scoping دستی

```python
n.raw_script("""
    const box = scoping("#my-box");
""")
```

خروجی:

```javascript
const box = document.querySelector('#my-box');
```

---

## ۹. یکپارچه‌سازی با View

### روش فعلی (دستی)

`Nexcript` را در فایل `.py` خود بسازید و فایل `.js` تولید می‌شود. سپس در `View` لینک کنید:

```python
# script.py
from nexelpy import Nexcript

with Nexcript(__file__) as n:
    n.raw_script("console.log('Hello');")

# main.py
from nexelpy import View, Route

@Route("/")
async def index():
    x = View(__file__)
    x.script(src="/script.js")   # لینک به فایل تولیدشده
    x.h1("Hello")
    return x.RESPONSE()
```

### استفاده از `n.src`

`n.src` آدرس URL فایل تولیدشده است:

```python
with Nexcript(__file__) as n:
    n.raw_script("console.log('Hello');")

# در View
x.script(src=n.src)  # → "/script.js"
```

---

## ۱۰. سناریوهای خطا و رفتار مورد انتظار

### خطای TypeScript بدون Node.js

```
RuntimeError: Nexcript requires Node.js >= 22.6.0 to compile TypeScript.
Please install Node.js from nodejs.org.
```

### خطای TypeScript با Node.js قدیمی

```
RuntimeError: Nexcript requires Node.js >= 22.6.0 (found v20.10.0).
Please upgrade Node.js.
```

### خطای تبدیل TypeScript

```
RuntimeError: TypeScript compilation failed: <جزئیات خطا>
```

### خطای مسیر خروجی خارج از پروژه

اگر `export_path` خارج از `project_root` باشد، `PathBuilder` خطا می‌دهد.

---

## ۱۱. نکات پیشرفته و اشتباهات رایج

### ✅ درست

```python
with Nexcript(__file__) as n:
    n.raw_script("console.log('Hello');")
```

### ❌ اشتباه

```python
n = Nexcript(__file__)  # بدون with → فایل JS تولید نمی‌شود!
n.raw_script("console.log('Hello');")
```

### ✅ استفاده از `scoping()` در View و Nexcript

```python
# main.py
with x.scoping():
    x.button("Click")

# script.py
n.raw_script("scoping().addEventListener('click', ...);")
```

### ❌ Scoping فقط در یک طرف

```python
# main.py (بدون x.scoping())
x.button("Click")

# script.py
n.raw_script("scoping()...")  # خطا: عنصر پیدا نمی‌شود
```

### ✅ Import نسبی

```python
n.raw_script("import { x } from './utils';")
# → import { x } from '/utils.js';
```

### ❌ Import با پسوند اشتباه

```python
n.raw_script("import { x } from './utils.ts';")  # .ts نامعتبر در مرورگر
```

### ✅ استفاده از `export_path` برای فایل‌های مشترک

```python
with Nexcript(__file__, export_path="./static/shared.js") as n:
    n.raw_script("// کد مشترک")
```

---

## ۱۲. API کامل (مرجع سریع)

### `Nexcript`

| متد / ویژگی | توضیح |
|---|---|
| `n.raw_script(code, lang=None)` | افزودن یک بلوک کد (auto-detect TS/JS). |
| `n.src` | آدرس URL فایل تولیدشده. |
| `n.file_path` | مسیر مطلق فایل پایتون. |
| `n.project_root` | مسیر روت پروژه (محل `.nexelpy`). |
| `n.current_dir` | مسیر پوشه‌ی فایل پایتون. |
| `n.scope_token` | توکن scoping (یونیک برای هر فایل). |
| `n._export_file` | مسیر مطلق فایل JS. |

### `RuntimeInfo` (Singleton)

| ویژگی | توضیح |
|---|---|
| `info.has_node` | آیا Node.js نصب است؟ |
| `info.node_version` | نسخه‌ی Node.js (مثل `"v22.6.0"`). |
| `info.node_version_ok` | آیا نسخه >= 22.6 است؟ |
| `info.can_transpile_ts` | آیا TypeScript قابل تبدیل است؟ |

### `CodeTransformer` (داخلی)

| متد | توضیح |
|---|---|
| `transform()` | تبدیل `scoping()`، `url()`، `import`/`export`. |

---

## جمع‌بندی

`Nexcript` یک ابزار ساده و قدرتمند برای نوشتن JavaScript و TypeScript درون پایتون است:

- **ساده**: با `with Nexcript(__file__) as n:` شروع کنید.
- **هوشمند**: خودکار TS را از JS تشخیص می‌دهد.
- **خودکار**: `import`، `url()` و `scoping` را مدیریت می‌کند.
- **قابل اعتماد**: پیام‌های خطای واضح برای مسائل Node.js.

با رعایت نکات این مستند، می‌توانید کدهای فرانت‌اند خود را به سادگی در پایتون بنویسید و از مزایای auto-build بهره‌مند شوید.