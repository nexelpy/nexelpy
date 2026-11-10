
# مستندات کامل Nextyle

**تولید CSS با پایتون — به سبک Pythonic، با پشتیبانی از Media Queries، Keyframes، Scoping، و تمام قابلیت‌های مدرن CSS**

---

## فهرست مطالب

1. [معرفی](#۱-معرفی)
2. [نصب و راه‌اندازی](#۲-نصب-و-راهاندازی)
3. [ساختار پایه](#۳-ساختار-پایه)
4. [انتخابگرها (Selectors)](#۴-انتخابگرها-selectors)
5. [ویژگی‌های CSS](#۵-ویژگیهای-css)
6. [شبه‌کلاس‌ها و شبه‌عناصر](#۶-شبهکلاسها-و-شبهعناصر)
7. [Media Queries](#۷-media-queries)
8. [Keyframes و انیمیشن](#۸-keyframes-و-انیمیشن)
9. [Scoping](#۹-scoping)
10. [لایه‌ها (Layers)](#۱۰-لایهها-layers)
11. [Font Face](#۱۱-font-face)
12. [Custom Properties (CSS Variables)](#۱۲-custom-properties-css-variables)
13. [Property (Houdini)](#۱۳-property-houdini)
14. [Scope (CSS @scope)](#۱۴-scope-css-scope)
15. [Starting Style](#۱۵-starting-style)
16. [Page (CSS @page)](#۱۶-page-css-page)
17. [Supports و Container](#۱۷-supports-و-container)
18. [Import و URL](#۱۸-import-و-url)
19. [Raw CSS](#۱۹-raw-css)
20. [ساختار خروجی و فایل CSS](#۲۰-ساختار-خروجی-و-فایل-css)
21. [یکپارچه‌سازی با View](#۲۱-یکپارچهسازی-با-view)
22. [نکات پیشرفته و اشتباهات رایج](#۲۲-نکات-پیشرفته-و-اشتباهات-رایج)
23. [API کامل (مرجع سریع)](#۲۳-api-کامل-مرجع-سریع)

---

## ۱. معرفی

`Nextyle` یک ابزار برای نوشتن CSS با پایتون است. شما به جای نوشتن فایل `.css` جداگانه، استایل‌ها را درون فایل `.py` خود تعریف می‌کنید و `Nextyle` به صورت خودکار یک فایل `.css` کنار همان فایل `.py` تولید می‌کند.

### مزایا
- **تایپ‌سیف**: با IDE خودکار تکمیل می‌شود (autocomplete).
- **Scoping خودکار**: هر فایل استایل، scope مخصوص به خود را دارد تا با فایل‌های دیگر تداخل نکند.
- **Media Queries ساده**: با پارامترهای `sm`, `md`, `lg`, `xl`, `ul` بدون نوشتن دستی `@media`.
- **پشتیبانی از تمام قابلیت‌های مدرن CSS**: `@layer`, `@scope`, `@container`, `@property`, `@font-face`, `@starting-style`, `@page`, `keyframes`.
- **بدون نیاز به build step جداگانه**: با اجرای فایل پایتون، CSS تولید می‌شود.

### وابستگی‌ها
هیچ وابستگی خارجی ندارد؛ فقط از کتابخانه‌ی استاندارد پایتون استفاده می‌کند.

---

## ۲. نصب و راه‌اندازی

`Nextyle` بخشی از NexelPy است و نیازی به نصب جداگانه ندارد:

```python
from nexelpy import Nextyle
```

### اولین فایل استایل

یک فایل به نام `style.py` کنار فایل اصلی پروژه (مثلاً `main.py`) بسازید:

```python
from nexelpy import Nextyle

with Nextyle(__file__) as y:
    y.select("body").background_color("black").color("white")
```

با اجرای این فایل، یک فایل `style.css` در همان پوشه ساخته می‌شود:

```css
body {
    background-color: black;
    color: white;
}
```

> **نکته:** همیشه از `with` استفاده کنید. در غیر این صورت، فایل CSS تولید نمی‌شود.

---

## ۳. ساختار پایه

### `Nextyle(__file__, ...)`

| پارامتر | نوع | پیش‌فرض | توضیح |
|---|---|---|---|
| `file` | `str \| Path` | **الزامی** | مسیر فایل پایتون (`__file__`). |
| `export_path` | `str \| Path \| None` | `None` | مسیر خروجی CSS. پیش‌فرض: کنار فایل پایتون با پسوند `.css`. |
| `layer_order` | `tuple[str, ...]` | `()` | ترتیب `@layer` (مثلاً `("reset", "base", "utilities")`). |
| `**custom_media_queries` | `str` | — | تعریف breakpointهای سفارشی. |

### نمونه

```python
with Nextyle(
    __file__,
    export_path="./dist/styles.css",
    layer_order=("reset", "base", "components", "utilities"),
    phone="@media (max-width: 480px)",
) as y:
    y.select("body").margin("0")
```

---

## ۴. انتخابگرها (Selectors)

### `y.select(selector_name)`

یک انتخابگر جدید می‌سازد و برمی‌گرداند. می‌توانید به صورت زنجیره‌ای، ویژگی‌ها را اضافه کنید.

```python
y.select(".btn").background_color("blue").color("white").padding("10px 20px")
```

### انتخابگرهای پیچیده

```python
y.select(".card > .title").font_weight("bold")
y.select("nav a").text_decoration("none")
y.select("[data-active='true']").border("1px solid green")
y.select("#header .logo").width("100px")
```

### ترکیب با pseudo

```python
y.select(".btn").hover().background_color("darkblue")
y.select("input").focus().outline("2px solid blue")
y.select(".item").first_child().margin_top("0")
```

---

## ۵. ویژگی‌های CSS

تمام ویژگی‌های CSS از طریق `__getattr__` در دسترس هستند. **نام‌ها با زیرخط (`_`) به جای خط تیره (`-`) نوشته می‌شوند.**

| CSS | Python |
|---|---|
| `background-color` | `background_color` |
| `font-size` | `font_size` |
| `margin-top` | `margin_top` |
| `z-index` | `z_index` |

### زنجیره‌سازی

```python
y.select(".box")\
    .background_color("#f0f0f0")\
    .border("1px solid #ccc")\
    .border_radius("8px")\
    .padding("16px")\
    .margin("8px")
```

### مقادیر چندگانه

```python
y.select(".box").margin("10px 20px")          # بالا/پایین، چپ/راست
y.select(".box").padding("10px 20px 15px 25px")  # بالا، راست، پایین، چپ
```

### مقادیر boolean

مقادیر boolean به صورت `true`/`false` در CSS نوشته می‌شوند:

```python
y.select(".element").user_select(True)   # user-select: true; (فقط برای property)
y.select(".card").pointer_events(False)  # pointer-events: false;
```

> **هشدار:** این رفتار برای تمام ویژگی‌های CSS اعمال می‌شود، حتی اگر مقدار boolean معتبر نباشد. در CSS استاندارد، معمولاً `none` و `auto` استفاده می‌شوند.

---

## ۶. شبه‌کلاس‌ها و شبه‌عناصر

### لیست کامل

| Python | CSS |
|---|---|
| `.hover()` | `:hover` |
| `.focus()` | `:focus` |
| `.focus_visible()` | `:focus-visible` |
| `.focus_within()` | `:focus-within` |
| `.active()` | `:active` |
| `.disabled()` | `:disabled` |
| `.enabled()` | `:enabled` |
| `.checked()` | `:checked` |
| `.visited()` | `:visited` |
| `.first_child()` | `:first-child` |
| `.last_child()` | `:last-child` |
| `.first_of_type()` | `:first-of-type` |
| `.last_of_type()` | `:last-of-type` |
| `.before()` | `::before` |
| `.after()` | `::after` |
| `.placeholder()` | `::placeholder` |
| `.selection()` | `::selection` |
| `.marker()` | `::marker` |

### نمونه

```python
y.select(".btn")\
    .background_color("blue")\
    .hover().background_color("darkblue")\
    .active().background_color("navy")\
    .disabled().opacity("0.5")
```

### شبه‌کلاس سفارشی

```python
y.select(".list").pseudo("nth-child(2n+1)").background_color("#f5f5f5")
```

---

## ۷. Media Queries

### Breakpointهای پیش‌فرض

| نام | شرط |
|---|---|
| `sm` | `@media (min-width: 640px)` |
| `md` | `@media (min-width: 768px)` |
| `lg` | `@media (min-width: 1024px)` |
| `xl` | `@media (min-width: 1280px)` |
| `ul` | `@media (min-width: 1536px)` |

### استفاده درون یک انتخابگر

```python
y.select(".text").font_size("14px", sm="16px", md="18px", lg="20px")
```

خروجی:

```css
.text { font-size: 14px; }
@media (min-width: 640px) { .text { font-size: 16px; } }
@media (min-width: 768px) { .text { font-size: 18px; } }
@media (min-width: 1024px) { .text { font-size: 20px; } }
```

### استفاده به عنوان بلوک مستقل

```python
with y.media("(min-width: 1024px)"):
    y.select(".hero").font_size("3rem")
```

خروجی:

```css
@media (min-width: 1024px) {
    .hero { font-size: 3rem; }
}
```

### Media Queries سفارشی

```python
with Nextyle(__file__, phone="@media (max-width: 480px)") as y:
    y.select(".box").padding("8px", phone="4px")
```

---

## ۸. Keyframes و انیمیشن

### تعریف ساده

```python
with y.keyframes("fade-in"):
    y.step("0%").opacity("0")
    y.step("100%").opacity("1")
```

خروجی:

```css
@keyframes fade-in--abc12 {
    0% { opacity: 0; }
    100% { opacity: 1; }
}
```

> **نکته:** نام keyframe به طور خودکار با یک scope_token پسوند داده می‌شود (`fade-in--abc12`) تا با keyframeهای فایل‌های دیگر تداخل نکند.

### استفاده در انیمیشن

```python
with y.keyframes("slide") as anim_name:
    y.step("0%").transform("translateX(-100%)")
    y.step("100%").transform("translateX(0)")

y.select(".modal").animation_name(anim_name).animation_duration("0.3s")
```

### Keyframe بدون Scoping

```python
with y.keyframes("fade-in", scope=False):
    y.step("0%").opacity("0")
```

نام keyframe بدون پسوند می‌ماند: `fade-in`.

### Keyframe با Media Queries

```python
with y.keyframes("responsive-fade"):
    y.step("0%").opacity("0", sm="0.2")
    y.step("100%").opacity("1", sm="0.8")
```

---

## ۹. Scoping

`Scoping` به معنی محدود کردن استایل‌ها به یک محدوده است. `Nextyle` دو حالت ارائه می‌دهد:

### Scoping خودکار

```python
with y.scoping() as scop:
    scop.color("white")
    y.select(".btn").background_color("red")
```

خروجی:

```css
[data-scoping="abc12"] { color: white; }
[data-scoping="abc12"] .btn { background-color: red; }
```

> **نکته:** برای اعمال این scope، باید در HTML یک `div` با `data-scoping` ایجاد کنید. این کار به طور خودکار با `x.scoping()` در `View` انجام می‌شود.

### Scoping دستی

```python
with y.scoping("[data-theme='dark']"):
    y.select(".card").background_color("black").color("white")
```

خروجی:

```css
[data-theme='dark'] .card { background-color: black; color: white; }
```

---

## ۱۰. لایه‌ها (Layers)

`@layer` ترتیب اولویت استایل‌ها را تعیین می‌کند. هر چه لایه‌ی دیرتری تعریف شود، اولویت بالاتری دارد.

```python
with Nextyle(
    __file__,
    layer_order=("reset", "base", "components", "utilities")
) as y:
    with y.layer("reset"):
        y.select("*").margin("0")
        y.select("*, *::before, *::after").box_sizing("border-box")

    with y.layer("base"):
        y.select("body").font_family("sans-serif")

    with y.layer("components"):
        y.select(".btn").padding("10px")
```

خروجی:

```css
@layer reset, base, components, utilities;
@layer reset { ... }
@layer base { ... }
@layer components { ... }
```

---

## ۱۱. Font Face

```python
with y.font_face("MyFont"):
    y.src(y.url("./static/fonts/MyFont.woff2"), format="woff2")
    y.font_weight("400")
    y.font_style("normal")
    y.font_display("swap")
```

خروجی:

```css
@font-face {
    font-family: "MyFont";
    src: url("/static/fonts/MyFont.woff2") format("woff2");
    font-weight: 400;
    font-style: normal;
    font-display: swap;
}
```

### استفاده

```python
y.select("body").font_family("'MyFont', sans-serif")
```

---

## ۱۲. Custom Properties (CSS Variables)

### تعریف متغیر

```python
with y.vars(":root"):
    y.add_var(primary="#3b82f6", secondary="#10b981", spacing="8px")
```

خروجی:

```css
:root {
    --primary: #3b82f6;
    --secondary: #10b981;
    --spacing: 8px;
}
```

### استفاده

```python
y.select(".btn").background_color("var(--primary)")
y.select(".btn").padding("var(--spacing)")
```

---

## ۱۳. Property (Houdini)

`@property` برای تعریف custom property با نوع، مقدار اولیه، و وراثت استفاده می‌شود.

```python
with y.property("--my-color"):
    y.syntax("<color>")
    y.inherits(False)
    y.initial_value("red")
```

خروجی:

```css
@property --my-color {
    syntax: "<color>";
    inherits: false;
    initial-value: red;
}
```

> **نکته:** برای `syntax`، مقدار به طور خودکار با کوتیشن نوشته می‌شود.

---

## ۱۴. Scope (CSS @scope)

`@scope` برای محدود کردن استایل‌ها به یک زیردرخت DOM استفاده می‌شود.

### با یک selector

```python
with y.scope(".card"):
    y.select("p").color("gray")
```

خروجی:

```css
@scope (.card) {
    p { color: gray; }
}
```

### با محدوده‌ی "to"

```python
with y.scope(".card", to=".card-content"):
    y.select("p").color("gray")
```

خروجی:

```css
@scope (.card) to (.card-content) {
    p { color: gray; }
}
```

---

## ۱۵. Starting Style

`@starting-style` برای انیمیشن‌های ورودی (enter animation) استفاده می‌شود.

```python
with y.starting_style():
    y.select(".fade-in").opacity("0")

y.select(".fade-in").transition("opacity 0.3s").opacity("1")
```

خروجی:

```css
@starting-style {
    .fade-in { opacity: 0; }
}
.fade-in { transition: opacity 0.3s; opacity: 1; }
```

---

## ۱۶. Page (CSS @page)

برای استایل‌دهی چاپ (print).

```python
with y.page():
    y.margin("1cm")
    y.size("A4")

with y.page(":first"):
    y.margin_top("2cm")
```

خروجی:

```css
@page {
    margin: 1cm;
    size: A4;
}
@page :first {
    margin-top: 2cm;
}
```

---

## ۱۷. Supports و Container

### `@supports`

برای بررسی پشتیبانی مرورگر از یک ویژگی.

```python
with y.supports("(display: grid)"):
    y.select(".grid").display("grid").gap("1rem")
```

خروجی:

```css
@supports (display: grid) {
    .grid { display: grid; gap: 1rem; }
}
```

### `@container`

برای container queries.

```python
with y.container("(min-width: 400px)", name="card-container"):
    y.select(".card").padding("20px")
```

خروجی:

```css
@container card-container (min-width: 400px) {
    .card { padding: 20px; }
}
```

---

## ۱۸. Import و URL

### `@import`

```python
y.import_css(y.url("./static/fonts.css"))
```

خروجی:

```css
@import url("/static/fonts.css");
```

### `url()`

متد `y.url()` مسیرهای نسبی را به URL مطلق (نسبت به روت پروژه) تبدیل می‌کند.

```python
y.select("body").background_image(y.url("./static/bg.png"))
# → background-image: url("/static/bg.png");
```

**قوانین `url`:**
- مسیرهای نسبی (`./` و `../`) → نسبت به موقعیت فایل `.py` حل می‌شوند.
- مسیرهای مطلق (`/...`) → نسبت به روت پروژه.
- URLهای خارجی (`http://`, `https://`, `//`, `data:`) → دست‌نخورده می‌مانند.

---

## ۱۹. Raw CSS

اگر نیاز به نوشتن CSS خام دارید:

### داخل یک context

```python
y.raw_css("""
    body {
        color: red;
    }
""")
```

### با Media Queries

```python
y.raw_css(
    sm=""".box { padding: 10px; }""",
    md=""".box { padding: 20px; }""",
)
```

### Global Raw CSS (خارج از context)

```python
y.add_global_raw_css("""
    *, *::before, *::after {
        box-sizing: border-box;
    }
""")
```

خروجی raw CSS همیشه در ابتدای فایل CSS (قبل از هر context) قرار می‌گیرد.

---

## ۲۰. ساختار خروجی و فایل CSS

### نحوه‌ی ساخت فایل

- اگر `export_path` داده نشود، فایل خروجی کنار فایل `.py` با پسوند `.css` ساخته می‌شود:
  - `style.py` → `style.css`
- اگر `export_path` داده شود، از آن مسیر استفاده می‌شود.

### ترتیب خروجی

1. `global_raw_css` (اگر وجود داشته باشد)
2. `@layer` order declaration (اگر تعریف شده باشد)
3. تمام contextها به ترتیب تعریف
4. `@import`ها در ابتدای هر context

### `href`

```python
print(y.href)  # → "/style.css"
```

این مقدار را می‌توانید در `View` برای `<link rel="stylesheet">` استفاده کنید.

---

## ۲۱. یکپارچه‌سازی با View

### روش فعلی (دستی)

`Nextyle` را در فایل `.py` خود بسازید و فایل `.css` تولید می‌شود. سپس در `View` لینک کنید:

```python
# style.py
from nexelpy import Nextyle

with Nextyle(__file__) as y:
    y.select("body").background_color("black")

# main.py
from nexelpy import View

@Route("/")
async def index():
    x = View(__file__)
    x.link(rel="stylesheet", href=y.href)
    x.h1("Hello")
    return x.RESPONSE()
```



## ۲۲. نکات پیشرفته و اشتباهات رایج

### ✅ درست

```python
with Nextyle(__file__) as y:
    y.select(".btn").background_color("red")
```

### ❌ اشتباه

```python
y = Nextyle(__file__)  # بدون with → فایل CSS تولید نمی‌شود!
y.select(".btn").background_color("red")
```

### ✅ نام‌گذاری ویژگی‌ها

```python
y.select(".box").background_color("red")    # درست
y.select(".box").background-color("red")     # خطای سینتکس پایتون
```

### ✅ استفاده از `y.url()` برای مسیرها

```python
y.select("body").background_image(y.url("./bg.png"))  # درست
y.select("body").background_image("./bg.png")          # بدون متد یو آر ال مسیر باید مطلق نوشته شود.مسیر نسبی کار نمیکند
```

### ❌ Scoping بدون `View`

اگر `y.scoping()` استفاده می‌کنید، مطمئن شوید که `View` با `x.scoping()` یک `div` با `data-scoping` تولید می‌کند. در غیر این صورت، استایل‌ها اعمال نمی‌شوند.

```python
from nexelpy import View

@Route("/")
async def index():
    x = View(__file__)
    x.link(rel="stylesheet", href=y.href)
    with x.scoping():
        x.h1("Hello")
    return x.RESPONSE()
```

### ✅ استفاده از `layer_order`

```python
with Nextyle(__file__, layer_order=("reset", "base", "components")) as y:
    with y.layer("base"):
        y.select("body").margin("0")
```

### ❌ تعریف چند `Nextyle` روی یک فایل

هر فایل `.py` باید فقط یک `Nextyle` با `__file__` خودش داشته باشد.

### ✅ برای فایل‌های استایل مشترک

اگر استایل مشترک دارید، در یک فایل `common.py` تعریف کنید و از `add_global_raw_css` یا `import_css` در فایل‌های دیگر استفاده کنید.

---

## ۲۳. API کامل (مرجع سریع)

### `Nextyle`

| متد | توضیح |
|---|---|
| `y.select(name)` | انتخابگر جدید |
| `y.media(condition)` | `@media` |
| `y.supports(condition)` | `@supports` |
| `y.container(condition, name=None)` | `@container` |
| `y.layer(name)` | `@layer` |
| `y.font_face(family)` | `@font-face` |
| `y.keyframes(name, scope=True)` | `@keyframes` |
| `y.step(value)` | گام keyframe |
| `y.property(name)` | `@property` |
| `y.vars(selector=":root")` | متغیرهای CSS |
| `y.add_var(**vars)` | افزودن متغیر |
| `y.scope(root, to=None)` | `@scope` |
| `y.scoping(selector=None)` | Scoping (خودکار یا دستی) |
| `y.starting_style()` | `@starting-style` |
| `y.page(selector="")` | `@page` |
| `y.src(*sources)` | `src` در `@font-face` |
| `y.import_css(target)` | `@import` |
| `y.url(path, format=None)` | `url()` |
| `y.raw_css(css=None, **kwargs)` | CSS خام |
| `y.add_global_raw_css(css)` | CSS خام جهانی |
| `y.attr(**kwargs)` | ذخیره attributeها (آینده) |
| `y.generate_css()` | تولید CSS به صورت رشته |
| `y.export()` | ذخیره CSS در فایل |

### `Select`

| متد | توضیح |
|---|---|
| `.pseudo(name)` | شبه‌کلاس سفارشی |
| `.hover()`, `.focus()`, ... | شبه‌کلاس‌های آماده |
| `.__getattr__(name)` | هر ویژگی CSS |

### `KeyframeStep`

| متد | توضیح |
|---|---|
| `._add_prop(prop, value, **kwargs)` | افزودن ویژگی |
| `.__getattr__(name)` | هر ویژگی CSS |

---

## جمع‌بندی

`Nextyle` یک ابزار قدرتمند برای نوشتن CSS با پایتون است که:
- **ساده** است: با `with Nextyle(__file__) as y:` شروع کنید.
- **قدرتمند** است: تمام قابلیت‌های مدرن CSS را پشتیبانی می‌کند.
- **مقیاس‌پذیر** است: scoping خودکار از تداخل جلوگیری می‌کند.
- **Pythonic** است: از ویژگی‌های پایتون برای خوانایی بیشتر استفاده می‌کند.

با رعایت نکات این مستند، می‌توانید استایل‌های پیچیده و حرفه‌ای بسازید، بدون اینکه یک خط CSS خام بنویسید (مگر در موارد خاص).