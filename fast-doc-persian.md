
# Nexelpy Documentation

## Introduction
Nexelpy یک فریم‌ورک مدرن و سریع است که با تمرکز بر سهولت در توسعه و مدیریت هوشمند منابع طراحی شده است.

---

## Getting Started

### Nexelpy Class
برای ساخت اپلیکیشن اصلی، کلاس `Nexelpy` را ایمپورت کرده و از آن یک نمونه (Instance) بسازید. 

**نکته بسیار مهم:** حتماً باید مسیر فایل جاری یعنی `__file__` را به عنوان ورودی به کلاس پاس دهید. این پارامتر برای مسیر‌یابی داخلی (Path Resolution) و درک ساختار پروژه توسط فریم‌ورک حیاتی است.

```python
from nexelpy import Nexelpy

app = Nexelpy(__file__)

if __name__ == "__main__":
    app.run()
```

### اجرای پروژه (Running the App)
*   **در محیط محلی (Local):** از دستور زیر در ترمینال استفاده کنید:
    `python main.py`
    همچنین می‌توانید از دکمه **Run Python File** در VS Code یا PyCharm استفاده کنید.
*   **نکته فنی:** متد `run()` مخصوص محیط توسعه طراحی شده و قابلیت‌هایی مثل `Auto-reload` و `Debug Mode` را ارائه می‌دهد. برای محیط‌های Production (سرور)، از روش‌های استاندارد جایگزین استفاده کنید.

### 🚀 Deployment (Production)
برای اجرای پروژه در محیط‌های عملیاتی و سرور، توصیه می‌شود از یک ASGI Server مانند **Uvicorn** استفاده کنید تا کارایی و پایداری حداکثری حاصل شود:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```
---

## Core Features

### 🔄 Reloader (Auto-Reload)
ریلودر پس از اجرای پروژه، فایل‌های پایتون را به‌صورت مداوم پایش (Watch) می‌کند. با ذخیره (Save) هر تغییر در کدهای پایتون، پروژه به‌صورت خودکار بازنشانی (Restart) می‌شود تا تغییرات جدید بلافاصله اعمال گردند.

### 📂 Static Files Management
در Nexelpy مدیریت فایل‌های استاتیک بسیار ساده و هوشمند است:
*   **شناسایی خودکار:** نیازی به تعریف دستی مسیرها نیست. هر پوشه‌ای با نام `static` در هر سطحی از پروژه ایجاد شود، محتویات آن مستقیماً سرو (Serve) می‌شود.
*   **پشتیبانی گسترده:** فایل‌های با پسوند `.html` ،`.css` و `.js` حتی اگر خارج از پوشه `static` باشند، به‌صورت خودکار شناسایی و به عنوان فایل استاتیک در دسترس قرار می‌گیرند.

> **⚠️ نکته برای Production:** برای عملکرد بهینه (Performance)، پیشنهاد می‌شود در محیط سرور، فایل‌های استاتیک توسط یک Web Server مانند **Nginx** مدیریت شوند. در صورت عدم تنظیم Nginx،  در لاگ‌ها هشدار می‌دهد که مدیریت فایل‌ها بر عهده خودِ فریم‌ورک است.

---

## Configuration & Parameters

### Nexelpy Initialization
در هنگام ساخت Instance از کلاس `Nexelpy` می‌توانید پارامترهای زیر را تنظیم کنید:

| پارامتر | نوع | اجباری | توضیحات |
| :--- | :--- | :---: | :--- |
| `file` | `str` | ✅ | مسیر فایل اصلی پروژه برای Path Resolution. |
| `mountStatics` | `bool` | ❌ | اگر `True` باشد، Nexelpy فایل‌های استاتیک را سرو می‌کند. |
| `secretKey` | `str` | ❌ | کلید امنیتی برای CSRF و رمزنگاری Sessionها. مقدار پیش‌فرض توسط خود فریم‌ورک ساخته می‌شود. |
| `ignore_watch_dirs` | `str/list`| ❌ | لیست پوشه‌هایی که ریلودر نباید آن‌ها را پایش کند. |

#### پارامتر `secretKey`
این کلید که توسط الگوریتم `Fernet` تولید می‌شود، در تمامی Viewها در دسترس است. 
**هشدار:** در محیط توسعه (Local)، با هر بار ریست شدن پروژه، مقدار این کلید تغییر می‌کند؛ بنابراین اگر Sessionای ست شده باشد، با ریست شدن پروژه باطل خواهد شد.برای جلوگیری از باطل شدن سشن‌ها در هر ریست، متغیر محیطی NEXELPY_SECRET_KEY را در فایل .env ست کنید.

#### پارامتر `ignore_watch_dirs`
اگر در پروژه خود فایل‌هایی تولید یا آپلود می‌کنید که باعث ایجاد حلقه تکرار در ریلودر می‌شود (مثلاً تولید فایل پایتون توسط خود برنامه)، نام آن پوشه‌ها را در این پارامتر وارد کنید تا ریلودر آن‌ها را نادیده بگیرد.

```python
# مثال به صورت تک پوشه
ignore_watch_dirs = "my_folder"

# مثال به صورت لیست
ignore_watch_dirs = ["folder1", "folder2"]
```

### Run Method Parameters
متد `run` برای تنظیمات شبکه در هنگام اجرای اپلیکیشن استفاده می‌شود:

```python
app.run(host="127.0.0.1", port=8000)
```


---

### Routes و View

**مدیریت مسیرها (Routing)**

برای ثبت مسیرها در ماژول main، از دکوریتور `@app.route` استفاده می‌شود. 

```python
from nexelpy import Nexelpy, View

app = Nexelpy(__file__)

@app.route("/")
async def home():
   x = View(__file__, title="Nexelpy")
   x.h2("Hello Nexelpy!")
   return x.RESPONSE()
```

#### پارامترهای دکوریتور `@app.route`
شما می‌توانید با استفاده از پارامترهای زیر، رفتار مسیر را کنترل کنید:

`@app.route(route="/", methods=["GET", "POST"], prefix="/cpanel")`

* **`route`**: مسیر اصلی (Endpoint).
* **`methods`**: لیست متدهای مجاز (Nexelpy فقط از متدهای `GET` و `POST` پشتیبانی می‌کند).
* **`prefix`**
پارامتر prefix (جداسازی منطقی و دسترسی)

استفاده از prefix فراتر از یک تغییر ساده در آدرس URL است. این پارامتر برای ایجاد مرزهای منطقی (Logical Boundaries) در پروژه‌های بزرگ و مقیاس‌پذیر استفاده می‌شود.

تفکیک اپلیکیشن‌ها: در پروژه‌های پیچیده، می‌توانید چندین اپلیکیشن مختلف را با پرفیکس‌های مجزا تعریف کنید (مثلاً /admin برای مدیریت و /api برای سرویس‌ها).
کنترل دسترسی (Access Control): از آنجایی که تمام مشخصات رووت‌ها در request.state.app در دسترس است، پرفیکس به شما اجازه می‌دهد به راحتی سیاست‌های امنیتی را بر اساس پیشوند مسیر اعمال کنید. برای مثال، می‌توانید دسترسی به تمامی مسیرهای زیرمجموعه یک پرفیکس خاص را محدود کنید.
مدیریت در پنل‌های گرافیکی: در پنل‌های مدیریتی (مانند پنل‌های خودکار Nexelpy)، پرفیکس باعث می‌شود که هر اپلیکیشن به عنوان یک موجودیت مجزا شناسایی شده و تنظیمات، دسترسی‌ها و محیط کاربری آن از سایر بخش‌های پروژه کاملاً ایزوله و تفکیک شود.
    * *مثال:* اگر `prefix="/cpanel"` باشد، مسیر نهایی به صورت `example.com/cpanel/` خواهد بود.

> **⚠️ توجه مهم: اجبار به استفاده از `async`**
> فریم‌ورک Nexelpy بر پایه عملیات غیرهمزمان (Asynchronous) بنا شده است. اگر تابعی را بدون کلمه کلیدی `async` تعریف کنید، برنامه با خطای زیر متوقف خواهد شد:
> ```text
> (NexelPy Route Error)
>          handler: home
>          error: Handler must be async (use 'async def').
> ```

---

**کلاس View (نمایش محتوا)**

برای ساخت پاسخ‌های HTML و مدیریت محتوا، از کلاس `View` استفاده می‌شود. در Nexelpy، استفاده از `__file__` یک الگوی ثابت (Pattern) است تا ویو به ساختار فایل‌ها دسترسی داشته باشد.

```python
x = View(__file__, title="Nexelpy")
x.h2("Hello Nexelpy!")
return x.RESPONSE()
```

#### نحوه عملکرد:
1.  **ایجاد اینستنس:** ابتدا یک نمونه از `View` می‌سازید. اولین ورودی حتماً باید `__file__` باشد.
2.  **ساخت محتوا:** با استفاده از متدهای ویو (مانند `h2`, `p`, و...) محتوای خود را اضافه می‌کنید. این اینستنس به تمامی ابزارهای لازم برای مدیریت درخواست‌ها (Request)، پاسخ‌ها (Response) و هدرها مجهز است.
3.  **ارسال پاسخ:** در نهایت با فراخوانی `x.RESPONSE()`، شیء پاسخ نهایی به سمت کلاینت ارسال می‌شود.

#### پارامترهای کلاس `View`
* **`file`**: مسیر فایل جاری برای دسترسی به منابع.
* **`title`**: عنوان (Title) صفحه که در تگ `<title>` قرار می‌گیرد.

---


## ساخت View مستقل از ماژول اصلی

Viewها را می‌توانید در ماژول‌هایی جدا از فایل اصلی پروژه تعریف کنید. برای تعریف Route در این ماژول‌ها، از دکوریتور `@Route` استفاده کنید:

```python
# product.py
from nexelpy import View, Route

@Route("/product")
async def product():
    x = View(__file__, title="Product")
    return x.RESPONSE()
```

### ثبت خودکار Routeها

نیازی به ثبت دستی Route یا واردکردن مستقیم ماژول در `main.py` نیست. هنگام اجرای برنامه، Nexelpy ماژول‌های پایتون پروژه را اسکن می‌کند. پوشه‌هایی که در تنظیمات برنامه‌ی اصلی برای مستثناشدن از اسکن مشخص شده‌اند، بررسی نمی‌شوند.

ماژول‌هایی که در آن‌ها از دکوریتور `@Route` استفاده شده باشد، شناسایی و بارگذاری می‌شوند. با بارگذاری ماژول، دکوریتور اجرا می‌شود و Route مربوطه را به برنامه‌ی اصلی اضافه می‌کند. این سازوکار هم در اجرای محلی و هم در اجرای سرور فعال است.

نام تابع‌های View لازم نیست یکتا باشد؛ Nexelpy برای ثبت Route به نام تابع وابسته نیست.

اسکنر ماژول Main رو اسکن نمیکند .
## ساختار پایه‌ی View

با ساخت یک نمونه از `View`، ساختار اولیه‌ی یک سند HTML شامل تگ‌های `html`، `head` و `body` ایجاد می‌شود:

```python
x = View(__file__, title="Product")
```

پس از ساخت نمونه، می‌توانید عناصر HTML موردنیاز صفحه را ایجاد و به بدنه‌ی سند اضافه کنید.

## ساخت عناصر HTML

از طریق نمونه‌ی `View` می‌توانید با استفاده از نام تگ، عنصر HTML بسازید. برای مثال، `x.h1()` یک عنصر `<h1>` ایجاد می‌کند:

```python
x.h1(
    parent=None,
    text="Hello Nexelpy!",
    props="disabled",
    **attributes
)
```

پارامترهای ساخت عنصر:

- `parent`: عنصر والد. مقدار پیش‌فرض `None` است و در این حالت، عنصر به `body` اضافه می‌شود.
- `text`: متن داخل عنصر.
- `props`: ویژگی‌های بدون مقدار، مانند `disabled`.
- `**attributes`: ویژگی‌های HTML که به‌صورت آرگومان‌های کلیدواژه‌ای فرستاده می‌شوند.

### نمونه

```python
x.button(
    "Click me",
    id="btn",
    Class="bg-red",
    data__number=43,
    props="disabled"
)
```

ویژگی‌های HTML را می‌توانید به‌صورت جفت‌های کلید و مقدار به عنصر بدهید. برای ویژگی `class` از `Class` با حرف بزرگ استفاده کنید تا با کلمه‌ی رزروشده‌ی `class` در پایتون تداخل نداشته باشد.

برای نوشتن خط تیره (`-`) در نام ویژگی‌ها، از دو آندرلاین (`__`) استفاده کنید. برای نمونه، `data__number` به ویژگی `data-number` تبدیل می‌شود.

## تعیین عنصر والد

با پارامتر `parent` می‌توانید مشخص کنید عنصر جدید درون کدام عنصر ساخته شود. مقدار این پارامتر باید یک عنصر متعلق به همان نمونه‌ی `View` باشد. اگر `parent=None` باشد، عنصر به `body` اضافه می‌شود.

```python
container = x.div(Class="container")
x.button("Click me", parent=container, id="btn", Class="bg-red")
```

در این مثال، دکمه درون `div` ساخته می‌شود. ساختار HTML حاصل به این شکل است:

```html
<div class="container"><button id="btn" class="bg-red">Click me</button></div>
```

## ساخت عناصر تو‌در‌تو با `with`

برای ایجاد عناصر تو‌در‌تو، می‌توانید از بلوک‌های `with` استفاده کنید. در این روش، عنصرهای فرزند درون بلوک عنصر والد ساخته می‌شوند:

```python
with x.div(Class="container"):
    x.button("Click me", id="btn", Class="bg-red")

with x.section(Class="container"):
    with x.div():
        with x.button(id="btn", Class="bg-red"):
            x.span("Click me")
```

این شیوه، ساختار پدر و فرزندی عناصر را با تورفتگی کد نشان می‌دهد و نیاز به ساخت متغیر جداگانه برای نگهداری هر عنصر را کاهش می‌دهد.

## افزودن لینک به `head`

برای افزودن عنصرهایی مانند لینک فایل CSS به بخش `head` سند، مقدار `x.headTag` را به‌عنوان والد مشخص کنید:

```python
x.link(parent=x.headTag, rel="stylesheet", href="/style.css")
```

## تگ‌های پایه‌ی ساخته‌شده هنگام مقداردهی اولیه

هنگام ساخت نمونه‌ی `View`، تگ‌های پایه‌ی سند ساخته می‌شوند و از طریق ویژگی‌های زیر در دسترس‌اند:

```python
x.htmlTag
x.headTag
x.bodyTag
```




متد `element` برای ساخت تگ‌های HTML به‌صورت پویا استفاده می‌شود. با ارسال نام تگ در پارامتر `tagName` می‌توانید عناصری بسازید که متد اختصاصی آن‌ها در View وجود ندارد.

پارامتر `parent` مشخص می‌کند عنصر ساخته‌شده در کدام عنصر والد قرار بگیرد. در صورت ارسال `None`، عنصر بدون والد مشخص ایجاد می‌شود.

```python
 x.element(tagName="div", parent=None)
```

برای ساخت تگ‌های مختلف می‌توانید مقدار `tagName` را تغییر دهید:

```python
x.element(tagName="article", parent=None)
x.element(tagName="custom-element", parent=None)
```

متد `element` امکان استفاده از تگ‌های استاندارد HTML و تگ‌های سفارشی را فراهم می‌کند.

### افزودن HTML خام با `raw_html`

متد `raw_html` برای اضافه‌کردن مستقیم یک قطعه HTML به خروجی View استفاده می‌شود. محتوای HTML در پارامتر `html` قرار می‌گیرد و با استفاده از `parent` می‌توان محل قرارگیری آن را مشخص کرد.

```python
@Route("/product")
async def product():
 x = View(__file__, title="product")
 x.raw_html(
 parent=None,
 html="""
 <div class="product">
 <h1>Product title</h1>
 <p>Product description</p>
 </div>
 """
 )
 return x.RESPONSE()
```

در این روش، HTML بدون نیاز به ساخت جداگانه‌ی هر عنصر از طریق متدهایی مانند `x.div()` یا `x.p()` به View اضافه می‌شود.

از `raw_html` می‌توان برای اضافه‌کردن قطعه‌های آماده‌ی HTML یا ساختارهایی استفاده کرد که ایجاد آن‌ها با Element Builder دشوار یا طولانی است. محتوای این متد باید با دقت مدیریت شود؛ زیرا HTML ارسال‌شده به‌صورت مستقیم وارد خروجی می‌شود.

### ساخت فرم‌ها (Forms)
برای ساخت سریع فرم‌های HTML، متدهای `form`، `input` و `submit` در دسترس هستند.

```python
with x.form(action="/submit", method="POST", Class="my-form"):
    x.input(type="text", name="username", placeholder="Enter name")
    x.input(type="password", name="password")
    x.submit("Send Data")
```

#### ریدایرکت کاربر (Redirect)
برای هدایت کاربر به آدرس دیگر، از متد `x.redirect()` استفاده کنید. هنگام فراخوانی این متد، اجرای کد متوقف شده و پاسخ ریدایرکت بلافاصله ارسال می‌شود (نیازی به `return` نیست).

```python
@Route("/admin")
async def admin():
    x = View(__file__)
    
    is_logged_in = await check_auth(x)
    if not is_logged_in:
        # اجرای کد متوقف شده و کاربر به صفحه لاگین می‌رود
        x.redirect("/login", status_code=307)
        
    x.h1("Welcome to Admin Panel")
    return x.RESPONSE()
```
---
## پلاگین‌ها (Plugins)

پلاگین‌ها یکی از قدرتمندترین امکانات Nexelpy هستند که به شما اجازه می‌دهند Viewهای خود را به بخش‌های کوچک‌تر و قابل‌استفاده‌ی مجدد (Reusable) تقسیم کنید. یک پلاگین به تمامی امکانات یک View (مانند مدیریت هد، هدایت مسیر یا Redirect، دسترسی به Request و تنظیم هدرها) دسترسی دارد.

### ساخت یک پلاگین ساده

برای ساخت پلاگین از کلاس `Plugin` استفاده می‌شود (ارسال `__file__` برای تعیین مسیر الزامی است). متد `RESPONSE()` در پلاگین می‌تواند مقادیری را به‌عنوان آرگومان برگرداند تا در View اصلی استفاده شوند:

```python
from nexelpy import Plugin

async def my_plugin():
    x = Plugin(__file__)
    with x.section(Class="container"):
        with x.div():
            with x.button(id="btn", Class="bg-red"):
                x.span("click me")
    return x.RESPONSE("alex", 23)
```

### ساخت پلاگین‌های پارامتریک

می‌توانید توابع پلاگین را با آرگومان دلخواه بنویسید تا عناصر سفارشی بسازید:

```python
async def my_btn(text, id, Class):
    x = Plugin(__file__)
    with x.button(id=id, Class=Class):
        x.span(text)
    return x.RESPONSE()
```

### استفاده از پلاگین در View

برای استفاده از پلاگین‌ها در یک View، از متد `x.importPlugin` استفاده کنید. هنگام فراخوانی پلاگین در متد ایمپورت، استفاده از ک کلیدواژه‌ی `await` الزامی است.

```python
from nexelpy import View, Route
from plugins.btn import my_btn
from plugins.myplug import my_plugin

@Route("/product")
async def product():
    x = View(__file__, title="Product")
    
    # استفاده از پلاگین دکمه
    x.importPlugin(await my_btn(text="click", id="btn3", Class="bg-green"))
    
    # دریافت مقادیر بازگشتی از پلاگین (مانند Name و age)
    Name, age = x.importPlugin(await my_plugin())
    
    return x.RESPONSE()
```

نحوه دریافت مقادیر بازگشتی:

نحوه‌ی دریافت خروجی از تابع importPlugin به تعداد مقادیر بازگشتی از پلاگین بستگی دارد:

اگر پلاگین یک مقدار برگرداند، importPlugin همان مقدار را برمی‌گرداند.
اگر پلاگین بیش از یک مقدار برگرداند، importPlugin آن‌ها را در قالب یک لیست برمی‌گرداند که می‌توانید با استفاده از تکنیک Unpacking (مانند نمونه بالا) آن‌ها را دریافت کنید.

### امکانات پیشرفته در پلاگین‌ها

پلاگین‌ها می‌توانند فایل‌های CSS اختصاصی خود را به بخش `head` صفحه تزریق کنند یا هدرهای HTTP (مانند CSP) را دستکاری کنند. هنگامی که پلاگین به View ایمپورت می‌شود، این تغییرات به‌طور خودکار روی صفحه اعمال می‌شوند:

```python
from nexelpy import Plugin

async def my_btn(text, id, Class):
    x = Plugin(__file__)
    
    # افزودن فایل استایل اختصاصی پلاگین به هدر صفحه
    x.link(parent=x.headTag, rel="stylesheet", href="/plugin_style.css")
    
    with x.button(id=id, Class=Class):
        x.span(text)
        
    # تنظیم Content Security Policy (CSP) در هدرها
    x.Headers.csp.add('default-src', "'self'")
    
    return x.RESPONSE()
```


### مدیریت ریدایرکت (Redirect) در پلاگین‌ها

یکی از ویژگی‌های کلیدی در پلاگین‌های Nexelpy، توانایی انجام ریدایرکت‌های شرطی است. متد `x.redirect()` نیازی به `return` کردن ندارد؛ زیرا به محض اجرا، فرآیند اجرای فعلی (چه در پلاگین و چه در ویو) را متوقف کرده و پاسخ ریدایرکت را مستقیماً به سمت کلاینت ارسال می‌کند.

این ویژگی باعث می‌شود پلاگین بتواند بدون وابستگی به منطق اصلی ویو، جریان برنامه را مدیریت کند. برای مثال، اگر داده‌ای یافت نشد، پلاگین می‌تواند کاربر را به صفحه ورود هدایت کند:

```python
from nexelpy import Plugin

async def get_data_plugin():
    x = Plugin(__file__)
    bands = await Band.select()
    
    if bands:
        for band in bands:
            x.p(f"name: {band['name']}")
    else:
        # در صورت نبود داده، بلافاصله ریدایرکت انجام شده و اجرای بقیه کد متوقف می‌شود
        x.redirect("/login")
    
    # این خط تنها در صورتی اجرا می‌شود که ریدایرکت انجام نشده باشد
    return x.RESPONSE()
```

**نکته فنی:** وقتی `x.redirect()` فراخوانی می‌شود، اجرای بلاک کدی که در آن هستید (در پلاگین یا ویو) متوقف شده و بلافاصله پاسخِ ریدایرکت به مرورگر ارسال می‌شود. بنابراین نیازی نیست حتماً مقدار `x.RESPONSE()` را در همان خط ریدایرکت `return` کنید.


## ویجت‌ها (Widgets)

برای ساخت المان‌های گرافیکی ساده و تکرار شونده که نیازی به مدیریت هدر، استایل‌های اختصاصی، ریدایرکت یا دسترسی به دیتابیس ندارند، استفاده از **Widget** به جای Plugin پیشنهاد می‌شود. 

ویجت‌ها در واقع توابع ساده و همگام (Synchronous) هستند که آبجکتِ ویو یا پلاگین را به عنوان ورودی دریافت کرده و المان‌های HTML مورد نظر را روی آن می‌سازند. استفاده از این روش نسبت به `importPlugin` از نظر پرفورمنس بسیار بهینه‌تر است، زیرا نیازی به فرآیند `await` و مدیریت سنگین Lifecycle پلاگین ندارد.

### ساخت یک ویجت ساده

یک ویجت معمولی باید آبجکتِ سازنده (معمولاً `x`) را در ورودی دریافت کند:

```python
# تعریف ویجت به عنوان یک تابع ساده و سینک
def my_button(obj, text, Class):
   obj.button(text=text, Class=Class)
```

### استفاده از ویجت در View

در اینجا ویجت‌ها را به راحتی و بدون نیاز به `await` در بدنه ویو فراخوانی می‌کنیم:

```python
from nexelpy import View, Route

@Route("/product")
async def product():
   x = View(__file__, title="product")
   
   # فراخوانی ویجت‌ها با پاس دادن آبجکت x
   my_button(obj=x, text="add", Class="bg-green")
   my_button(obj=x, text="delete", Class="bg-red")
   my_button(obj=x, text="edit", Class="bg-yellow")
   
   return x.RESPONSE()
```


## راهنمای متدهای شیء Request

در اینجا لیست تمامی متدها، ورودی‌های قابل قبول و نحوه عملکرد آن‌ها آورده شده است.

### ۱. مدیریت داده‌ها و پارامترها
بسیاری از متد‌های زیر (مانند `args`, `cookies`, `form`, `headers`, `json`, `path_params`, `payload`, `scope`, `state`) از یک الگوی رفتاری واحد پیروی می‌کنند:

*   **بدون آرگومان:** اگر هیچ کلیدی پاس داده نشود، تمامی مقادیر موجود به صورت یک **لیست** برگردانده می‌شوند.
*   **با آرگومان (Key):** اگر کلید مشخصی پاس داده شود، تنها مقدار مربوط به آن کلید برگردانده می‌شود.
*   **با چندین آرگومان (Multiple Keys):** اگر چندین کلید به صورت `*args` پاس داده شود، لیستی از مقادیر مربوط به آن کلیدها برگردانده می‌شود (قابلیت Unpacking).

| متد | عملکرد | مثال |
| :--- | :--- | :--- |
| `args()` | دریافت پارامترهای URL | `name = await x.REQUEST.args("name")` <br> `names = await x.REQUEST.args("name", "age")` |
| `cookies()` | دریافت کوکی‌ها | `val = await x.REQUEST.cookies("session_id")` |
| `form()` | دریافت داده‌های فرم | `val = await x.REQUEST.form("user_id")` |
| `headers()` | دریافت هدرها | `auth = await x.REQUEST.headers("Authorization")` |
| `json()` | دریافت داده‌های JSON | `user = await x.REQUEST.json("user")` |
| `path_params()` | دریافت پارامترهای مسیر | `id = await x.REQUEST.path_params("item_id")` |
| `scope()` | دریافت اطلاعات Scope | `val = await x.REQUEST.scope("key")` |
| `state()` | دریافت داده‌های ذخیره شده | `val = await x.REQUEST.state("key")` |

### ۲. متد ویژه `payload()`
این متد هوشمندترین متد برای دسترسی به داده‌هاست و بر اساس متد HTTP درخواست، منبع داده را انتخاب می‌کند:

*   **ورودی‌ها:** `method` (رشته‌ای مثل `"GET"`, `"POST"`, `"PATH"`, `"JSON"`) و `*keys`.
*   **منطق عملکرد:**
    *   اگر `method="GET"` باشد $\rightarrow$ از `args()` استفاده می‌کند.
    *   اگر `method="POST"` باشد $\rightarrow$ از `form()` استفاده می‌کند.
    *   اگر `method="PATH"` باشد $\rightarrow$ از `path_params()` استفاده می‌کند.
    *   اگر `method="JSON"` باشد $\rightarrow$ از `json()` استفاده می‌کند.
*   **خروجی:** اگر متد ارسالی با نوع درخواست مطابقت نداشته باشد، مقدار `None` برمی‌گرداند.

```python
# مثال کاربردی payload
name = await x.REQUEST.payload("GET", "name")
```

### ۳. سایر متدها و مدیریت وضعیت

| متد | خروجی | توضیحات |
| :--- | :--- | :--- |
| `app()` | `app` instance | دسترسی به نمونه‌ی اصلی اپلیکیشن. |
| `body()` | `bytes` | دریافت بدنه درخواست به صورت بایت. |
| `client()` | `dict` | دریافت مشخصات کلاینت (مرورگر، IP و ...). |
| `method()` | `str` | برگرداندن نوع متد (مثلاً `GET`). |
| `stream()` | `generator` | دریافت بدنه درخواست به صورت استریم. |
| `url()` | `url` object | دریافت اطلاعات کامل URL. |
| `set_state()` | `None` | ذخیره مقدار در `state` (مثلاً `x.REQUEST.set_state(token="abc")`). |





## مدیریت هدرها (HeaderBuilder)

این متدها از طریق `x.headers` در دسترس هستند و برای تنظیم امنیت و رفتار پاسخ (Response) استفاده می‌شوند.
```py
from nexelpy import View, Route


@Route("/product")
async def product():
    x = View(__file__, title="product")
    
    # اضافه کردن منابع مجاز به Content-Security-Policy (درخواست‌کننده، منابع و مبدا)
    x.Headers.csp.add('connect-src', "'self'", "https://api.example.com")
    
    # تنظیم سیاست HSTS برای اجبار استفاده از HTTPS (زمان اعتبار، زیردامنه‌ها، پیش‌بارگذاری)
    x.Headers.hsts(max_age=31536000, include_subdomains=True, preload=True)
    
    # تنظیم سیاست‌های کش مرورگر (نوع کش، حداکثر زمان اعتبار، s_maxage و غیره)
    x.Headers.cache(cache_control="public, immutable", max_age=31536000)
    
    # تنظیم سیاست جلوگیری از Clickjacking (مقادیر: DENY یا SAMEORIGIN)
    x.Headers.frame_options(policy="SAMEORIGIN")
    
    # فعال‌سازی جلوگیری از MIME-sniffing
    x.Headers.content_type_options()
    
    # تنظیم سیاست Referrer-Policy برای ارسال اطلاعات ارجاع‌دهنده
    x.Headers.referrer_Policy(policy="same-origin")
    
    # کنترل دسترسی به قابلیت‌های مرورگر مثل دوربین (نام قابلیت و لیست مجاز)
    x.Headers.permissions_Policy.add('camera', 'https://meet.google.com')
    
    # تنظیم سیاست COOP (Cross-Origin-Opener-Policy)
    x.Headers.cross_origin_opener(policy="same-origin-allow-popups")
    
    # تنظیم سیاست COEP (Cross-Origin-Embedder-Policy)
    x.Headers.cross_origin_embedder(policy="unsafe-none")
    
    # تنظیم سیاست CORP (Cross-Origin-Resource-Policy)
    x.Headers.cross_origin_resource(policy="cross-origin")
    
    # جداسازی کلاستر عامل مبدا (Origin-Agent-Cluster)
    x.Headers.origin_agent_cluster()
    
    # پاکسازی داده‌های سایت در سمت کلاینت (مثل کوکی‌ها و storage)
    x.Headers.clear_site_data('cookies', 'storage')
    
    # اضافه کردن هدرهای دلخواه و خام (زیرخط‌ها به خط تیره تبدیل می‌شوند)
    x.Headers.add_raw_header(
        X_Custom_Header="custom-value",     # X-Custom-Header: custom-value
        X_Another_Header="another-value",   # X-Another-Header: another-value
        X_API_Version="v1.0"                # X-API-Version: v1.0
    )
    
    # پروفایل‌های پیش‌فرض امنیت هدرها
    x.Headers.set_super_strict()  # بالاترین سطح امنیت
    x.Headers.set_strict()        # سطح امنیتی سخت‌گیرانه
    x.Headers.set_normal()        # سطح امنیتی استاندارد و نرمال
    x.Headers.set_relaxed()       # سطح امنیتی آزادتر (توسعه‌ای)

    return x.RESPONSE()
```



## قابلیت Vapi (Ajax-Driven Component Rendering)

یکی از ویژگی‌های منحصربه‌فرد **NexelPy**، سیستم **Vapi** است. این قابلیت برای مدیریت درخواست‌های Ajax طراحی شده تا فرآیند ساخت UI را از سمت کلاینت به سمت سرور منتقل کند.

### مفهوم Vapi
در روش‌های سنتی، پس از دریافت داده از سرور، کلاینت باید با استفاده از JavaScript، داده‌ها را پردازش و المان‌های HTML را بسازد. اما با **Vapi**، تمام فرآیند ساخت کامپوننت‌ها (مانند کارت‌های محصول، لیست‌ها یا بخش‌های پویا) در سمت سرور انجام شده و قطعه‌ی HTML نهایی و آماده به کلاینت ارسال می‌شود. کلاینت تنها وظیفه‌ی `append` کردن این قطعه را بر عهده دارد.

**مثال کاربردی:** در یک سیستم جستجوی محصولات، با تایپ هر کلمه، کلمه به سرور ارسال می‌شود، محصولات مرتبط از دیتابیس استخراج شده، در قالب کارت‌های طراحی شده در سرور ساخته می‌شوند و در نهایت یک سکشن HTML آماده به کلاینت تحویل داده می‌شود.

### مثال پیاده‌سازی

```python
from nexelpy import Vapi, Route

@Route("/send-card-api", methods=["POST"])
async def send():
    # استفاده از Vapi به جای View برای درخواست‌های Ajax
    x = Vapi(__file__)
    
    # دریافت مقدار ورودی از بدنه درخواست
    search_term = await x.REQUEST.payload("POST", "search")
    
    # دریافت محصولات مرتبط از دیتابیس (با فرض استفاده از Piccolo ORM)
    products = await Product.select().where(Product.name == search_term)
    
    # ساخت ساختار HTML در سمت سرور
    for product in products:
        with x.div(Class="product-card"):
            x.img(src=product.urlPic)
            x.h4(f"Product Name: {product.name}")
            x.p(f"Price: {product.price}")
            
    # ارسال پاسخ نهایی شامل قطعه HTML ساخته شده
    return x.RESPONSE(status_code=200)
```

### مزایای اصلی
*   **کاهش بار پردازشی کلاینت:** کلاینت درگیر محاسبات و ساخت DOM سنگین نمی‌شود.
*   **توسعه سریع‌تر:** تمام منطق طراحی UI در یک جا (سمت سرور) متمرکز است.
*   **امنیت بالاتر:** منطق‌های بیزنس و ساختار دقیق داده‌ها در سمت سرور مخفی می‌ماند.
*   **یکپارچگی:** استفاده از همان Syntax همیشگی `x.div`, `x.img` و ... برای ساخت قطعات پویا.





---

### ساختار پاسخ در Vapi (Response Structure)

متد `x.RESPONSE` در کلاس `Vapi` برخلاف `View` معمولی، یک شیء `JSONResponse` برمی‌گرداند. این پاسخ شامل یک دیکشنری JSON است که کلیدهای زیر را در بر می‌گیرد:

| کلید | مبدأ (Source) | توضیحات |
| :--- | :--- | :--- |
| `view` | `bodyTag content` | قطعه HTML تولید شده در سمت سرور که باید در کلاینت `append` شود. |
| `QE_links_header` | `headTag content` | شامل لینک‌های CSS، اسکریپت‌ها و متادیتاهای تزریق شده در `<head>`. |
| `status_message` | آرگومان `status_message` | پیام وضعیت که از متد پاس داده شده است. |
| `**data` (Custom Keys) | آرگومان‌های اضافی (`**kwargs`) | هر کلید و مقداری که کاربر در `RESPONSE` ارسال کند، مستقیماً به این بخش اضافه می‌شود. |

#### مثال ارسال داده‌های اضافی (Custom Data)
کاربر می‌تواند با استفاده از `keyword arguments` (مثل `theme="dark"`)، داده‌های جانبی مورد نیاز برای منطق کلاینت را ارسال کند:

```python
# مثال: ارسال HTML به همراه تنظیمات تم کلاینت
return x.RESPONSE(status_code=200, theme="dark", user_role="admin")
```

**خروجی JSON نهایی در کلاینت به این صورت خواهد بود:**
```json
{
  "view": "<div class='product-card'>...</div>",
  "QE_links_header": "<link rel='stylesheet' href='...'>",
  "status_message": "",
  "theme": "dark",
  "user_role": "admin",
}
```

---




## مدیریت پاسخ‌های API (RestApi)

کلاس `RestApi` برای مدیریت پاسخ‌های استاندارد پروتکل HTTP طراحی شده است. این کلاس تمام سناریوهای رایج ارسال داده را پوشش می‌دهد.

### لیست متدهای پاسخ‌دهی و ساختار آن‌ها

در ادامه، امضای دقیق هر متد و پارامترهای ورودی آن آورده شده است:

#### ۱. `RESPONSE_json`
ارسال داده‌های ساختاریافته در قالب JSON.
*   **امضا:** `x.RESPONSE_json(background_task="", status_code=200, **keywordarg)`
*   **توضیح:** هر آرگومانی که به صورت `key=value` پاس داده شود، مستقیماً به بدنه JSON اضافه می‌شود.

#### ۲. `RESPONSE_file`
ارسال فایل برای دانلود یا نمایش.
*   **امضا:** `x.RESPONSE_file(path="", media_type="", download_name="", background_task="", disposition="attachment", status_code=200)`
*   **توضیح:** از `disposition` برای تعیین حالت دانلود (`attachment`) یا نمایش در مرورگر (`inline`) استفاده می‌شود.

#### ۳. `RESPONSE_text`
ارسال پاسخ متنی ساده.
*   **امضا:** `x.RESPONSE_text(text="", background_task="", status_code=200)`

#### ۴. `RESPONSE_streaming`
ارسال داده‌ها به صورت تکه‌تکه (Streaming) برای فایل‌های حجیم.
*   **امضا:** `x.RESPONSE_streaming(content="", media_type="", background_task="", status_code=200)`

#### ۵. `RESPONSE_no_content`
ارسال پاسخ بدون بدنه (معمولاً برای عملیات‌هایی که نیازی به بازگشت داده ندارند).
*   **امضا:** `x.RESPONSE_no_content(background_task="")`

#### ۶. `RESPONSE_redirect`
هدایت کاربر به یک URL دیگر.
*   **امضا:** `x.RESPONSE_redirect(url="", background_task="", status_code=301)`

#### ۷. `RESPONSE_html`
ارسال فایل HTML خام از روی دیسک.
*   **امضا:** `x.RESPONSE_html(html_path="", background_task="", status_code=200)`

#### ۸. `RESPONSE_html_jinja`
ارسال قالب‌های Jinja2 که نیاز به رندر شدن دارند.
*   **امضا:** `x.RESPONSE_html_jinja(html_path="", background_task="", status_code=200, **keywordarg)`
*   **توضیح:** `keywordarg` متغیرهایی هستند که در قالب HTML جایگذاری می‌شوند.

---

### ⚡ قابلیت Background Tasks (وظایف پس‌زمینه)

پارامتر `background_task` در تمامی متدهای فوق در دسترس است و به شما اجازه می‌دهد عملیاتی را **پس از ارسال پاسخ به کلاینت** اجرا کنید.

#### ویژگی‌ها و نکات فنی:
*   **غیرمسدودکننده (Non-blocking):** استفاده از `asyncio.create_task()` باعث می‌شود پاسخ بلافاصله ارسال شود و تسک در پس‌زمینه اجرا گردد.
*   **مدیریت خطا (Error Handling):** از آنجا که تسک‌ها از چرخه درخواست جدا هستند، حتماً از بلوک `try/except` در داخل تابع تسک استفاده کنید تا از گم شدن خطاها جلوگیری شود.
*   **دسترسی به Context:** توجه داشته باشید که پس از ارسال پاسخ، `Request Context` پاک می‌شود. اگر تابع پس‌زمینه نیاز به اطلاعات درخواست دارد، آن را **قبل از بازگشت پاسخ** استخراج کرده و به عنوان آرگومان به تابع پاس دهید.

#### مثال کاربردی:

```python
import asyncio
from nexelpy import RestApi, Route

async def log_action_task(action_name: str):
    try:
        await asyncio.sleep(2) 
        print(f"Log: {action_name} completed.")
    except Exception as e:
        print(f"Log Error: {e}")

@Route("/api/action", methods=["POST"])
async def perform_action():
    api = RestApi(__file__)
    
    # پاسخ بلافاصله ارسال می‌شود، در حالی که لاگ‌گذاری در پس‌زمینه انجام می‌شود
    return api.RESPONSE_json(
        status=True, 
        message="Action started", 
        background_task=log_action_task("User_Click_Action")
    )
```
---

## مدیریت کوکی‌ها (Cookies)

کلاس‌های `View`، `Plugin` و `RestApi` به متدهای آماده‌ای برای تنظیم و حذف کوکی‌ها دسترسی دارند. این متدها کوکی‌ها را در پاسخ نهایی (Response) تزریق می‌کنند.

```python
# تنظیم کوکی (مثلاً در یک ویو یا پلاگین)
x.set_Cookie(
    key="session_id", 
    value="abc123", 
    max_age=3600, 
    httponly=True, 
    secure=True
)

# حذف کوکی
x.delete_Cookie("session_id")
```
**نکته:** متد `delete_Cookie` می‌تواند چندین کلید را همزمان دریافت کند (مثلاً `x.delete_Cookie("session", "theme")`).


---
#### رمزنگاری داده‌ها با CryptoHelper
برای امنیت داده‌های حساس (مثل توکن‌ها یا شناسه کاربر)، می‌توانید از کلاس `CryptoHelper` استفاده کنید که به صورت خودکار از `secretKey` پروژه استفاده می‌کند.

```python
from nexelpy import CryptoHelper, View

@Route("/auth")
async def auth():
    x = View(__file__)
    
    crypto = CryptoHelper()
    
    # رمزنگاری یک دیکشنری
    token = crypto.encrypt(user_id=42, role="admin")
    
    # رمزگشایی (در صورت دستکاری یا انقضا، None برمی‌گرداند)
    data = crypto.decrypt(token, as_dict=True) 
    
    return x.RESPONSE()
```

---
## مدیریت آدرس‌دهی فایل‌های استاتیک (Static Files Addressing)

در **NexelPy**، مدیریت آدرس فایل‌ها به گونه‌ای طراحی شده که هم از **آدرس‌دهی مطلق (Absolute Pathing)** و هم از **آدرس‌دهی نسبی (Relative Pathing)** به صورت هوشمند پشتیبانی می‌کند. این ویژگی به شما اجازه می‌دهد بدون نگرانی از تغییر ساختار پوشه‌بندی، فایل‌های خود را فراخوانی کنید.

### ۱. آدرس‌دهی مطلق (Absolute Addressing)
در این حالت، آدرس‌دهی از **Root پروژه** (ریشه اصلی) شروع می‌شود. این روش زمانی استفاده می‌شود که می‌خواهید مسیر فایل را از نقطه شروع پروژه مشخص کنید.

**ساختار:** `[Project_Root] / [Folder_Path] / [File_Name]`

**مثال‌ها:**
*   اگر فایل در مسیر `static/pic.png` باشد:
    `example.com/static/pic.png`
*   اگر فایل در مسیر `views/home/script.js` باشد:
    `example.com/views/home/script.js`

---

### ۲. آدرس‌دهی نسبی (Relative Addressing)
این یکی از قدرتمندترین ویژگی‌های NexelPy است. با استفاده از متد `x.url()`، می‌توانید مسیر فایل را **نسبت به موقعیت فایل فعلی (Module Location)** محاسبه کنید. این کار باعث می‌شود اگر یک پوشه را جابجا کردید، آدرس‌دهی‌های داخلی آن خراب نشود.

#### حالت اول: فایل در همان سطح یا زیرپوشه ماژول
*   **موقعیت فایل:** `/views/home/home.py`
*   **موقعیت مقصد:** `/views/home/script.js`
*   **نحوه فراخوانی:**
```python
x.url("./script.js")
```

#### حالت دوم: فایل در زیرپوشه نسبت به ماژول
*   **موقعیت فایل:** `/views/home/home.py`
*   **موقعیت مقصد:** `/views/home/scripts/script.js`
*   **نحوه فراخوانی:**
```python
x.url("./scripts/script.js")
```

### مقایسه سریع

| نوع آدرس‌دهی | مبدأ محاسبه | کاربرد اصلی | مزیت |
| :--- | :--- | :--- | :--- |
| **مطلق (Absolute)** | ریشه پروژه (Root) | فایل‌های عمومی مثل `static` یا `assets` | وضوح بالا در ساختار کلی پروژه |
| **نسبی (Relative)** | موقعیت ماژول فعلی | فایل‌های اختصاصی هر ویو یا ماژول | قابلیت جابجایی آسان ماژول‌ها (Portability) |

---



## آدرس‌دهی فایل‌ها در پاسخ‌ها (File Response Addressing)

هنگام استفاده از متد `x.RESPONSE_file` برای ارسال فایل به کلاینت، سیستم به صورت هوشمند مسیر ورودی را تفسیر می‌کند. شما نیازی به استفاده از `x.url()` برای تولید آدرس ندارید؛ بلکه می‌توانید مستقیماً مسیر را به عنوان ورودی به متد بدهید.

### قوانین تفسیر مسیر (Path Interpretation)

متد `RESPONSE_file` بر اساس وجود یا عدم وجود کاراکتر نقطه (`.`) در ابتدای مسیر، تصمیم می‌گیرد که آدرس را **نسبی** یا **مطلق** در نظر بگیرد:

#### ۱. آدرس‌دهی نسبی (Relative Path)
اگر مسیر با یک نقطه (`.`) شروع شود، آدرس نسبت به **موقعیت فعلی فایل پایتونی** که در حال اجراست، محاسبه می‌شود. این روش برای فایل‌هایی که در کنار ماژول یا در زیرپوشه‌های آن قرار دارند، ایده‌آل است.

*   **مثال ۱ (فایل در کنار ماژول):**
    ```python
    # فایل در همان پوشه‌ای است که این کد در آن قرار دارد
    return x.RESPONSE_file("./data.json")
    ```
*   **مثال ۲ (فایل در زیرپوشه ماژول):**
    ```python
    # فایل در پوشه assets که در کنار ماژول است قرار دارد
    return x.RESPONSE_file("./assets/report.pdf")
    ```

#### ۲. آدرس‌دهی مطلق (Absolute Path)
اگر مسیر با `/` شروع شود (و نقطه نداشته باشد)، آدرس از **ریشه اصلی پروژه (Project Root)** محاسبه می‌شود. این روش برای دسترسی به پوشه‌های عمومی مانند `static` یا `uploads` که در لایه‌های بالاتر پروژه هستند، استفاده می‌شود.

*   **مثال ۱ (پوشه استاتیک در ریشه):**
    ```python
    # فایل در مسیر پروژه/static/logo.png قرار دارد
    return x.RESPONSE_file("/static/logo.png")
    ```
*   **مثال ۲ (دسترسی مستقیم از ریشه):**
    ```python
    # فایل در مسیر پروژه/downloads/manual.pdf قرار دارد
    return x.RESPONSE_file("/downloads/manual.pdf")
    ```

### خلاصه راهنما

| فرمت ورودی | نوع آدرس | مبدأ محاسبه |
| :--- | :--- | :--- |
| `./path/to/file` | **نسبی** | پوشه‌ی فعلیِ ماژول (Current Module Directory) |
| `/path/to/file` | **مطلق** | ریشه‌ی اصلی پروژه (Project Root) |





## تولید اسکریپت‌های سمت کلاینت (Nexcript)

در پروژه‌های سنتی، فایل‌های JavaScript به صورت استاتیک در مرورگر بارگذاری می‌شوند. اما در NexelPy، سرو کردن اسکریپت‌ها و مدیریت آدرس‌دهی فایل‌ها بر عهده سرور است. کلاس **Nexcript** برای حل دو چالش اصلی طراحی شده است:

۱. **مسیریابی هوشمند (Path Resolution):** برخلاف پروژه‌های استاتیک، در سمت سرور مرورگر نمی‌داند فایل JS در کدام پوشه قرار دارد تا آدرس‌های نسبی (مثل `./logo.png`) را حل کند. Nexcript آدرس‌ها را در زمان کامپایل به مسیرهای معتبر تبدیل می‌کند.
۲. **ایزوله‌سازی (Scoping):** با ادغام کدها، نام متغیرها و توابع ممکن است تداخل پیدا کنند. Nexcript به صورت خودکار یک شناسه (Token) یکتا برای هر ماژول تولید می‌کند تا از تداخل جلوگیری شود.

### استفاده پایه از Nexcript

برای ساخت اسکریپت، از یک بلوک `with` استفاده می‌کنید. فایل جاری (`__file__`) برای تشخیص مسیر الزامی است. کدهای شما درون متد `add_script` قرار می‌گیرند.

```python
from nexelpy import Nexcript

# فایل خروجی JS به صورت خودکار در کنار فایل پایتون با پسوند .js ساخته می‌شود
with Nexcript(__file__) as n:
    n.add_script("""
        const el = scoping(); // انتخابگر اتوماتیک اسکوپ‌شده
        const img = url("./assets/logo.png"); // تبدیل به مسیر معتبر
        console.log("Nexcript is ready!");
    """)
```

### روش‌های آدرس‌دهی و Scoping

Nexcript دو تابع سراسری در محیط JS به شما می‌دهد:

*   **`url("./path")`**: مسیرهای نسبی را به مسیرهای مطلق (از ریشه پروژه) تبدیل می‌کند.
*   **`scoping()` یا `scoping(".selector")`**: یک المان DOM را با استفاده از توکن یکتای همان فایل انتخاب می‌کند. این یعنی کدهای شما بدون درگیری با سایر بخش‌های صفحه اجرا می‌شوند.

#### مثال با استفاده از Scoping
```python
with Nexcript(__file__) as n:
    n.add_script("""
        // element را با توجه به اسکوپ این فایل پیدا می‌کند
        const btn = scoping("#my-btn"); 
        btn.addEventListener("click", () => alert("Clicked!"));
    """)
```

### پشتیبانی از TypeScript

اگر Node.js (نسخه 22.6 به بالا) روی سیستم نصب باشد، Nexcript به طور خودکار کدهای TypeScript را تشخیص داده و به JavaScript کامپایل می‌کند. نیازی به تنظیمات اضافه نیست.

```python
with Nexcript(__file__) as n:
    n.add_script("""
        interface User { name: string; }
        const user: User = { name: "Ali" };
        console.log(user.name);
    """)
```

### تعیین مسیر خروجی (Export Path)

به طور پیش‌فرض، فایل JS در کنار فایل پایتون شما با پسوند `.js` ذخیره می‌شود. اگر می‌خواهید آن را در پوشه‌ی دیگری (مثلاً `static/js/`) ذخیره کنید، از پارامتر `export_path` استفاده کنید:

```python
with Nexcript(__file__, export_path="../static/js/app.js") as n:
    n.add_script("console.log('Custom path');")
```

### آدرس‌دهی فایل در View
برای اینکه فایل تولیدشده‌ی JS را به صفحه HTML متصل کنید، از متد `x.url()` استفاده کنید:

```python
x = View(__file__)
x.script(parent=x.headTag, src=x.url("./script.js"))
```
اگر export_path را مقدار دهی نکنید فایل جی اس تولید شده در کنار ماژول پایتون و با همان نام ایجاد میشود <br>
/views/home/homeview.py<br>
/views/home/homeview.js<br>

---




## تولید استایل‌های سمت کلاینت (Nextyle)

**Nextyle** یک ابزار قدرتمند برای تولید کدهای CSS با استفاده از سینتکس پایتون است. این کلاس جایگزین نوشتن فایل‌های CSS خام می‌شود و به شما اجازه می‌دهد استایل‌ها را با استفاده از منطق برنامه‌نویسی (مثل حلقه‌ها و متغیرها) بسازید.

### استفاده پایه از Nextyle

مانند `Nexcript`، با استفاده از یک بلوک `with` و پاس دادن `__file__` شروع می‌شود. فایل CSS تولید شده به صورت خودکار در کنار فایل پایتون با پسوند `.css` ذخیره می‌شود.

```python
from nexelpy import Nextyle

with Nextyle(__file__) as y:
    # انتخاب تگ body و اعمال استایل‌ها
    y.select("body").background_color("#f0f0f0").color("black")
    
    # انتخاب کلاس و اعمال استایل‌ها
    y.select(".card").padding("20px").border("1px solid #ccc")
```

### انتخاب‌گرها (Selectors) و متدهای زنجیره‌ای (Chaining)

در Nextyle می‌توانید متدها را پشت سر هم (زنجیره‌ای) فراخوانی کنید. برای ویژگی‌های CSS که در پایتون با `_` نوشته می‌شوند (مثل `background_color`)، Nextyle به طور خودکار آن‌ها را به فرمت CSS (`background-color`) تبدیل می‌کند.

#### حالت‌های شبه‌کلاس و شبه‌عناصر (Pseudo-classes & Elements)
برای استایل‌دهی به حالت‌های خاص (مثل `hover` یا `focus`)، از متد `hover()`، `focus()` و... استفاده کنید:

```python
y.select(".btn").background_color("blue").color("white")\
    .hover().background_color("red")\
    .active().background_color("green")
```

#### استایل‌دهی به فرزندان
با استفاده از متد `nest` روی یک انتخابگر قبلی، می‌توانید به فرزندان آن استایل دهید:
```python
y.select(".card").padding("10px")
y.select(".card").nest("h2").font_size("24px")
```
نتیجه :
```css
.card {
    padding: 10px;
}

.card h2 {
    font-size: 24px;
}

```

### سیستم Grid و Breakpoints (پاسخ‌گویی)

Nextyle از قابلیت **Mobile-First** پشتیبانی می‌کند. شما می‌توانید با پاس دادن `kwargs` به هر ویژگی، مقادیر مختلفی برای دستگاه‌های مختلف (مانند تبلت و دسکتاپ) تنظیم کنید.

پیش‌فرض‌های بریک‌پوینت در Nextyle (الهام‌گرفته از Bootstrap و Tailwind) عبارتند از:
*   `sm` (موبایل بزرگتر)
*   `md` (تبلت)
*   `lg` (دسکتاپ)
*   `xl` (مانیتور بزرگ)
*   `ul` (Ultra-Large)

```python
# استایل پایه 10px است، در تبلت 20px و در دسکتاپ 30px می‌شود
y.select(".container").padding("10px", md="20px", lg="30px")
```

### استفاده از متغیرها (CSS Variables) و کانتکست‌ها

Nextyle از بلوک‌های `with` برای ایجاد ساختارهای پیچیده CSS استفاده می‌کند:

#### ۱. متغیرهای سراسری (`:root`)
```python
with y.vars(":root"):
    y.add_var(primary_color="#3498db", secondary_color="#e74c3c")
```

#### ۲. مدیا کوئری (Media Queries)
```python
with y.media("(min-width: 1200px)"):
    y.select(".sidebar").display("none")
```

#### ۳. انیمیشن‌ها (Keyframes)
```python
with y.keyframes("fade-in"):
    y.step("0%").opacity("0")
    y.step("100%").opacity("1")
```
(سپس برای استفاده از انیمیشن: `y.select(".box").animation_name("fade-in").animation_duration("2s")`)

#### ۴. فونت‌فیس (@font-face)
```python
with y.font_face("MyFont"):
    y.src(y.url("./fonts/myfont.woff2"), format="woff2")
    y.font_weight("400")
```

### وارد کردن فایل‌های CSS خارجی و کدهای خام

اگر نیاز به استفاده از کتابخانه‌های خارجی (مثل Bootstrap) یا کدهای خام دارید:

```python
# وارد کردن از یک URL
y.import_css(y.url("./bootstrap.min.css"))

# نوشتن CSS خام (که آدرس‌های نسبی درون آن خودکار اصلاح می‌شوند)
y.raw_css("""
    .custom-box {
        background: url("./bg.png");
    }
""")
```

### تعیین مسیر خروجی (Export Path)

به طور پیش‌فرض، فایل CSS در کنار فایل پایتون با همان نام و پسوند `.css` ذخیره می‌شود:
*   `/views/home/homeview.py`
*   `/views/home/homeview.css`

اگر می‌خواهید خروجی را در مسیر دیگری (مثلاً پوشه استاتیک) ذخیره کنید، از پارامتر `export_path` استفاده کنید:

```python
with Nextyle(__file__, export_path="../static/css/style.css") as y:
    y.select("body").margin("0")
```

### اتصال به فایل HTML

برای اعمال استایل تولیدشده در صفحه، کافیست فایل CSS تولید شده را با استفاده از `x.url()` به هد صفحه متصل کنید:

```python
x = View(__file__)
x.link(parent=x.headTag, rel="stylesheet", href=x.url("./homeview.css"))
```




### 🌐 بهینه‌سازی سرو فایل‌های استاتیک با Nginx (اختیاری)

به‌طور پیش‌فرض، NexelPy خودش فایل‌های استاتیک (پوشه `/static/` و فایل‌های با پسوند `.css`، `.js` و `.html`) را مدیریت می‌کند. این رفتار برای محیط توسعه (Local) عالی است، اما اگر پروژه‌ات ترافیک بالایی دارد، توصیه می‌شود برای بهترین کارایی، سرو کردن این فایل‌ها را به یک Web Server مثل **Nginx** بسپاری. Nginx فایل‌های استاتیک را با سرعت بسیار بالاتری سرو می‌کند و هیچ سرباری روی برنامه پایتونی تو ایجاد نمی‌کند.

#### ۱. تنظیمات نمونه برای Nginx

این تنظیمات را در فایل کانفیگ Nginx خود (معمولاً در مسیر `/etc/nginx/sites-available/your_site`) قرار بده. این کانفیگ به Nginx می‌گوید که فایل‌های استاتیک را خودش سرو کند و بقیه درخواست‌ها را به Uvicorn (برنامه پایتون) بفرستد:

```nginx
server {
    listen 80;
    server_name yourdomain.com;  # دامنه خود را جایگزین کنید

    # ۱. سرو فایل‌های استاتیک (CSS, JS, HTML) مستقیماً توسط Nginx
    # درخواست این فایل‌ها هرگز به برنامه پایتون نمی‌رسد
    location ~* \.(css|js|html)$ {
        root /path/to/your/project;  # مسیر ریشه پروژه NexelPy خود را وارد کنید
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # ۲. سرو محتویات پوشه static (تصاویر، فونت‌ها و...)
    location /static/ {
        alias /path/to/your/project/static/;  # مسیر پوشه static پروژه خود را وارد کنید
        expires 30d;
        add_header Cache-Control "public";
        access_log off;
    }

    # ۳. ارسال بقیه درخواست‌ها به برنامه پایتون (Uvicorn)
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

*(حتماً مقادیر `root` و `alias` را با مسیر واقعی پروژه‌ی خودت جایگزین کن).*

#### ۲. غیرفعال کردن سرو استاتیک در NexelPy (اختیاری)

وقتی Nginx برای سرو فایل‌های استاتیک تنظیم شد، می‌توانی به NexelPy بگویی که دیگر خودش این کار را انجام ندهد تا از کار تکراری جلوگیری شود. برای این کار، کافیست در زمان ساخت نمونه، پارامتر `mountStatics=False` را ست کنی:

```python
from nexelpy import Nexelpy

# برای بهترین کارایی در پروداکشن، mountStatics را False کنید
app = Nexelpy(__file__, mountStatics=False)
```

**نکته:** اگر `mountStatics=False` را ست کنی اما Nginx را تنظیم نکنی، سیستم به‌طور خودکار یک هشدار (Warning) در لاگ‌ها ثبت می‌کند تا متوجه شوی فایل‌های استاتیک در دسترس نیستند. این ویژگی باعث می‌شود همیشه از وضعیت استقرار (Deployment) خود مطلع باشی بدون اینکه برنامه از کار بیفتد.