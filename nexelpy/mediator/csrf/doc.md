
# مستندات فنی: CSRF (Cross-Site Request Forgery) در NexelPy

این سند توضیح می‌دهد که سیستم محافظت در برابر CSRF در NexelPy چگونه کار می‌کند، از چه الگوریتم‌هایی استفاده می‌کند، چگونه با سشن کلاینت یکپارچه می‌شود و محدودیت‌های آن چیست.

---

## ۱. نمای کلی (Overview)

NexelPy از یک الگوی کاملاً **Stateless** و مبتنی بر **Signed Double-Submit Cookie** (کوکی دوگانه‌ی امضا شده) برای محافظت در برابر CSRF استفاده می‌کند. این یعنی:

- هیچ توکنی روی سرور ذخیره نمی‌شود.
- هیچ دیتابیس یا کش اضافه‌ای نیاز نیست.
- توکن با استفاده از **HMAC-SHA۲۵۶** امضا می‌شود و می‌تواند به شناسه‌ی سشن کاربر یا یک شناسه‌ی تصادفی برای کاربران مهمان گره بخورد.
- توکن به طور خودکار در هدر `X-CSRF-ClientSide` و کوکی `csrf_clientSide` قرار می‌گیرد.
- اعتبارسنجی هم برای درخواست‌های AJAX (از طریق هدر) و هم برای فرم‌های سنتی HTML (از طریق بدنه‌ی فرم) انجام می‌شود.

این سیستم با معماری «سشن سمت کلاینت» نکسل‌پای کاملاً هماهنگ است و به هیچ زیرساخت اضافی نیاز ندارد.

> **نکته:** نام‌های `csrf_clientSide` و `X-CSRF-ClientSide` به عمد انتخاب شده‌اند تا با نام‌های رزرو شده‌ی `csrf_token` و `X-CSRF-Token` (که ممکن است توسط کتابخانه‌های دیگر یا خود کاربر استفاده شوند) تداخل نداشته باشند.

---

## ۲. اجزای اصلی

| جزء | مسئولیت |
|---|---|
| `CSRFManager` | تولید توکن امضا شده و اعتبارسنجی آن (با HMAC-SHA۲۵۶) |
| `CSRFMiddleware` | تولید توکن اولیه، تزریق به `scope`، و اعتبارسنجی درخواست‌های `POST` |
| `CookiesManager.set_csrf_clientSide` | تنظیم `max_age`، انتخاب کلید اتصال (binding) و بازتولید توکن |
| `CookiesManager._set_csrf_clientSide_cookie_and_header` | ست کردن توکن در هدر پاسخ و کوکی‌ها |
| `PluginBuilder.csrf_token` | دسترسی راحت به توکن در ویوها (`x.csrf_token`) |
| کوکی `csrf_clientSide` | حامل توکن برای اعتبارسنجی |
| کوکی `random_key` (یا هر نام دلخواه) | حامل شناسه‌ی یکتای مهمان برای اتصال توکن |

---

## ۳. الگوریتم تولید توکن (Token Generation)

### ۳-۱. ساختار Payload

هر توکن از سه بخش تشکیل شده است که با `:` از هم جدا می‌شوند و سپس با یک `.` به امضا متصل می‌شوند:

```
[nonce] : [timestamp] : [session_binding] . [signature]
```

| بخش | توضیح |
|---|---|
| `nonce` | یک رشته‌ی تصادفی ۳۲ کاراکتری که تضمین می‌کند هر توکن منحصربه‌فرد است. |
| `timestamp` | زمان تولید توکن (Unix timestamp) برای کنترل انقضا. |
| `session_binding` | رشته‌ای که توکن را به کاربر گره می‌زند (می‌تواند `user_id`، هش کل سشن، یا یک شناسه‌ی مهمان باشد). |
| `signature` | امضای HMAC-SHA۲۵۶ روی سه بخش بالا با استفاده از **کلید امضای Fernet** (کلید سشن). |

### ۳-۲. حالت‌های اتصال (Binding)

توسعه‌دهنده می‌تواند در هر ویو با استفاده از `set_csrf_clientSide` تعیین کند که توکن به چه چیزی گره بخورد:

۱. **اتصال به کل سشن (`binding_key=None`):** هش کل دیکشنری سشن به عنوان `session_binding` استفاده می‌شود. اگر هر داده‌ای در سشن تغییر کند، توکن باطل می‌شود.
۲. **اتصال به یک کلید خاص (`binding_key="user_id"`):** فقط مقدار آن کلید در سشن (مثلاً `user_id`) به عنوان `session_binding` استفاده می‌شود. این بهترین گزینه برای کاربران لاگین‌شده است.
۳. **اتصال به شناسه‌ی مهمان (`binding_key="random_key"` یا هر نام دیگر):** اگر کلید در سشن وجود نداشته باشد، سیستم یک شناسه‌ی تصادفی (۱۶ بایت) تولید می‌کند، آن را در یک کوکی با همان نام (`random_key`) ذخیره می‌کند و توکن را به آن گره می‌زند. این گزینه امنیت کاربران مهمان را تضمین می‌کند.

---

## ۴. اعتبارسنجی توکن (Token Verification)

متد `CSRFManager.verify_token` سه مرحله را بررسی می‌کند:

۱. **بررسی اتصال:** آیا `session_binding` با مقدار فعلی (بر اساس `binding_key`) مطابقت دارد؟ (جلوگیری از سرقت توکن بین کاربران مختلف)
۲. **بررسی امضا:** آیا HMAC محاسبه‌شده با امضای موجود در توکن یکسان است؟ (جلوگیری از جعل)
۳. **بررسی زمان:** آیا `timestamp` از `max_age` فراتر رفته است؟ (جلوگیری از استفاده‌ی مجدد)

اگر هر کدام شکست بخورد، خطای **۴۰۳ Forbidden** برگردانده می‌شود.

---

## ۵. جریان کار (Flow)

### ۵-۱. تولید اولیه
میان‌افزار `CSRFMiddleware` در هر درخواست، اگر توکنی در `scope` نباشد، یک توکن پیش‌فرض تولید می‌کند. سپس `CookiesManager._set_csrf_clientSide_cookie_and_header` در هنگام ساخت پاسخ، توکن را در هدر `X-CSRF-ClientSide` و کوکی `csrf_clientSide` قرار می‌دهد.

### ۵-۲. استفاده در فرم سنتی HTML
توسعه‌دهنده توکن را از `x.set_csrf_clientSide()` می‌گیرد و در فیلد مخفی قرار می‌دهد:

```python
x = View(__file__)
token = x.set_csrf_clientSide(max_age=3600, binding_key="random_key")

with x.form(action="/submit", method="POST"):
    x.input(type="hidden", name="csrf_clientSide_token", value=token)
    x.input(type="text", name="username")
    x.button("Submit")

return x.RESPONSE()
```

### ۵-۳. استفاده در AJAX
توکن از هدر `X-CSRF-ClientSide` خوانده می‌شود و در درخواست بعدی ارسال می‌گردد:

```javascript
fetch('/api/submit', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRF-ClientSide': document.querySelector('meta[name="csrf_clientSide"]').content
    },
    body: JSON.stringify({...})
})
```

---

## ۶. هماهنگی با سشن کلاینت

- **کلید امضا:** همان کلید Fernet که برای رمزنگاری سشن استفاده می‌شود، برای امضای CSRF نیز به کار می‌رود. تغییر کلید Fernet، تمام توکن‌های CSRF را باطل می‌کند.
- **چرخش خودکار:** اگر توکن به `user_id` گره خورده باشد، با لاگین یا لاگ‌اوت کاربر، `user_id` تغییر می‌کند و توکن‌های قبلی به طور خودکار باطل می‌شوند. نیازی به چرخش دستی نیست.
- **`max_age`:** مقدار پیش‌فرض ۷۲۰۰ ثانیه (۲ ساعت) است. کاربر می‌تواند با `x.set_csrf_clientSide(max_age=...)` آن را تغییر دهد. این مقدار هم روی کوکی (برای مرورگر) و هم روی `timestamp` (برای سرور) اعمال می‌شود.

---

## ۷. امنیت در برابر حملات رایج

| حمله | دفاع |
|---|---|
| **جعل توکن** | امضای HMAC-SHA۲۵۶ با کلید مخفی |
| **سرقت توکن بین کاربران** | گره خوردن به `session_binding` (user_id یا شناسه مهمان) |
| **استفاده‌ی مجدد بعد از انقضا** | `timestamp` و بررسی `max_age` |
| **Brute Force** | `nonce` تصادفی ۳۲ کاراکتری (۱۲۸ بیت) |
| **Timing Attack** | استفاده از `hmac.compare_digest` (مقایسه‌ی زمان-ثابت) |
| **XSS (دزدیدن کوکی)** | `httponly=True` روی کوکی‌ها (جاوااسکریپت نمی‌تواند آن‌ها را بخواند) |
| **CSRF (درخواست از سایت دیگر)** | توکن باید با هدر یا بدنه‌ی فرم ارسال شود؛ درخواست cross-site نمی‌تواند هدر سفارشی اضافه کند |

---

## ۸. تنظیمات و سفارشی‌سازی

### ۸-۱. تنظیم `max_age` و `binding_key`
توسعه‌دهنده در هر ویو می‌تواند تصمیم بگیرد:

```python
# Bind to user_id (best for logged-in users)
x.set_csrf_clientSide(max_age=3600, binding_key="user_id")

# Bind to a random guest ID (best for guests)
x.set_csrf_clientSide(max_age=3600, binding_key="random_key")

# Bind to the entire session (default)
x.set_csrf_clientSide(max_age=3600)
```

### ۸-۲. `httponly` و `samesite`
به طور پیش‌فرض `httponly=True` و `samesite="strict"` هستند. این تنظیمات امنیت را به حداکثر می‌رسانند و برای اکثر پروژه‌ها مناسب‌اند.

---

## ۹. محدودیت‌ها

- **چند تب:** توکن در همه‌ی تب‌های یک مرورگر یکسان است (چون بر اساس سشن یا شناسه مهمان است). این رفتار امن و مدیریت آن ساده است.
- **تغییر سشن:** اگر کاربر در یک تب لاگین کند، توکن تب‌های دیگر (که با شناسه مهمان تولید شده بودند) باطل می‌شوند. کاربر باید صفحه را رفرش کند.
- **نیاز به ارسال توکن:** برای AJAX، توکن باید در هدر ارسال شود. برای فرم‌های سنتی، توکن در فیلد مخفی قرار می‌گیرد.

---

## ۱۰. جدول خلاصه‌ی امنیت

| ویژگی | مکانیزم | وضعیت |
|---|---|---|
| تولید توکن تصادفی | `secrets.token_hex(16)` | ✅ |
| امضای توکن | HMAC-SHA۲۵۶ | ✅ |
| اتصال به سشن | `session_binding` (کل سشن، `user_id`، یا شناسه مهمان) | ✅ |
| انقضا | `timestamp` + `max_age` | ✅ |
| مقایسه‌ی زمان-ثابت | `hmac.compare_digest` | ✅ |
| پشتیبانی از AJAX | هدر `X-CSRF-ClientSide` | ✅ |
| پشتیبانی از فرم سنتی | فیلد مخفی `csrf_clientSide_token` | ✅ |
| امنیت کاربران مهمان | شناسه تصادفی در کوکی (مثل `random_key`) | ✅ |
| نیاز به دیتابیس | ندارد (Stateless) | ✅ |

---

## ۱۱. مثال کامل

```python
from nexelpy import Nexelpy, View, Route

app = Nexelpy(__file__)

@Route("/form", methods=["GET"])
async def show_form():
    x = View(__file__, title="Form")

    # Use random_key for guest security
    token = x.set_csrf_clientSide(max_age=3600, binding_key="random_key")

    with x.form(action="/submit", method="POST"):
        x.input(type="hidden", name="csrf_clientSide_token", value=token)
        x.input(type="text", name="username", placeholder="Enter your name")
        x.button("Submit")

    return x.RESPONSE()

@Route("/submit", methods=["POST"])
async def handle_submit():
    x = View(__file__, title="Result")
    username = await x.REQUEST.form("username")
    x.h2("Form Submitted Successfully!")
    x.p(f"Username: {username}")
    return x.RESPONSE()
```

**نتیجه:**
- صفحه‌ی `/form` یک فرم با توکن مخفی و یک کوکی `random_key` نشان می‌دهد.
- اگر توکن دستکاری شود، خطای `403 CSRF token invalid or expired` برمی‌گردد.
- اگر توکن سالم باشد، به `/submit` منتقل می‌شود.

---

## ۱۲. جمع‌بندی

سیستم CSRF در NexelPy:

- **امن** است (HMAC + nonce تصادفی + اتصال انعطاف‌پذیر به سشن/مهمان + httponly + samesite).
- **Stateless** است (بدون دیتابیس).
- **قابل تنظیم** است (`max_age` و `binding_key` در هر ویو).
- **پشتیبانی کامل از AJAX و فرم سنتی** را دارد.
- **با سشن کلاینت کاملاً یکپارچه** است.
- **بدون تداخل با نام‌های رزرو شده** (استفاده از پیشوند `clientSide`).

این سیستم برای اکثر پروژه‌های وب (از وبلاگ تا پنل ادمین) کاملاً کافی و امن است.


