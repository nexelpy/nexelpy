
# مستندات فنی: Session سمت کلاینت (Client-Side Session)

این سند توضیح می‌دهد که مکانیزم سشن در NexelPy چطور کار می‌کند، از چه لایه‌های رمزنگاری استفاده می‌کند، چطور امنیت را تضمین می‌کند و محدودیت‌هایش چیست.

---

## ۱. نمای کلی (Overview)

NexelPy از یک سشن **کاملاً سمت کلاینت (Stateless)** استفاده می‌کند. این یعنی:

- هیچ داده‌ای از سشن روی سرور ذخیره نمی‌شود.
- هیچ دیتابیس، کش یا حافظه‌ای برای نگهداری سشن‌ها لازم نیست.
- تمام داده‌ها در یک **کوکی رمزنگاری‌شده** روی مرورگر کاربر ذخیره می‌شوند.
- سرور فقط می‌تواند کوکی را **رمزگشایی** کند و بخواند، اما نمی‌تواند آن را تغییر دهد بدون اینکه کلید را داشته باشد.

این مدل برای پروژه‌هایی که نمی‌خواهند زیرساخت اضافی (Redis, DB) نگه دارند، ایده‌آل است. اما محدودیت‌هایی دارد که در بخش «محدودیت‌ها» توضیح داده می‌شود.

---

## ۲. اجزای اصلی

| جزء | مسئولیت |
|---|---|
| `ClientSession` | رمزنگاری و رمزگشایی داده‌ها با Fernet |
| `CookiesManager.set_session_clientSide` | ساخت داده، رمزنگاری و ست کردن کوکی |
| `NexelpySessionMiddleware` | خواندن کوکی از هر درخواست و رمزگشایی آن در scope |
| `RequestProxy.session_clientSide` | دسترسی راحت به داده‌ی سشن در هر جای handler |
| کوکی `session_clientSide` | حامل توکن رمزنگاری‌شده |

---

## ۳. الگوریتم رمزنگاری (Cryptography)

### ۳-۱. کتابخانه
از `cryptography.fernet` استفاده می‌شود. Fernet یک «دستور پخت» رمزنگاری سطح بالا (High-level Recipe) است که چند لایه امنیتی را با هم ترکیب می‌کند.

### ۳-۲. ساختار کلید (Key)

کلید مخفی یک رشته‌ی **۳۲ بایتی base64-encoded** است که در `Nexelpy.__init__` تولید می‌شود:

```python
secretKey = Fernet.generate_key()  # 32 bytes, base64-encoded
```

اگر کاربر `secretKey` را پاس ندهد، هر بار اجرای اپ یک کلید تصادفی جدید ساخته می‌شود (که یعنی تمام سشن‌های قبلی باطل می‌شوند). در production باید `secretKey` را از یک منبع پایدار (مثلاً environment variable) بخوانید:

```python
app = Nexelpy(__file__, secretKey=os.environ["SECRET_KEY"].encode())
```

### ۳-۳. ساختار توکن Fernet

هر توکن Fernet این ساختار را دارد:

```
[Version: 1 byte] [Timestamp: 8 bytes] [IV: 16 bytes] [Ciphertext] [HMAC: 32 bytes]
```

| بخش | اندازه | نقش |
|---|---|---|
| Version | ۱ بایت | نسخه‌ی فرمت (فعلاً `0x80`) |
| Timestamp | ۸ بایت | زمان ساخت توکن (Unix timestamp) |
| IV (Initialization Vector) | ۱۶ بایت | تصادفی، برای هر پیام متفاوت |
| Ciphertext | متغیر | داده‌ی رمزنگاری‌شده با AES-128-CBC |
| HMAC-SHA256 | ۳۲ بایت | امضای یکپارچگی توکن |

### ۳-۴. الگوریتم‌های استفاده‌شده

- **AES-128-CBC** برای محرمانگی (Confidentiality)
- **HMAC-SHA256** برای یکپارچگی و احراز اصالت (Integrity & Authentication)
- **PKCS7 Padding** برای تکمیل بلوک‌های AES

### ۳-۵. چرا Fernet امن است؟

- **IV تصادفی برای هر پیام:** دو سشن با داده‌ی یکسان، دو توکن کاملاً متفاوت تولید می‌کنند.
- **Authenticate-before-decrypt:** قبل از رمزگشایی، HMAC بررسی می‌شود. اگر کسی حتی یک بیت را تغییر دهد، HMAC شکست می‌خورد و `InvalidToken` برگردانده می‌شود. این جلوی حملات Padding Oracle و Bit-Flipping را می‌گیرد.
- **Constant-time comparison:** مقایسه‌ی HMAC به صورت زمان-ثابت انجام می‌شود تا حملات Timing از بین بروند.

---

## ۴. ساختار Payload

داده‌ی کاربر (مثلاً `{"user_id": 42, "role": "admin"}`) به این شکل بسته‌بندی می‌شود:

```python
payload = {
    "_exp": int(time.time()) + max_age,   # absolute expiry timestamp
    "data": data,                          # user's session data
}
```

سپس به JSON تبدیل و رمزنگاری می‌شود:

```python
token = fernet.encrypt(json.dumps(payload).encode()).decode()
```

**نکته:** فیلد `_exp` زمان مطلق انقضا را نگه می‌دارد. این جدا از TTL خود Fernet است (که در `decrypt` با `ttl=None` غیرفعال شده تا session بتواند بیش از ۶۰ ثانیه عمر کند).

---

## ۵. رمزگشایی (Decryption)

در هر درخواست، `NexelpySessionMiddleware`:

1. هدر `Cookie` را می‌خواند.
2. اگر کوکی `session_clientSide` وجود داشت، مقدارش را می‌گیرد.
3. با `Fernet` رمزگشایی می‌کند:

```python
raw = fernet.decrypt(token.encode(), ttl=None)  # disable Fernet's built-in TTL
payload = json.loads(raw)
```

4. بررسی می‌کند که `_exp` منقضی نشده باشد:

```python
if payload["_exp"] and time.time() > payload["_exp"]:
    return {}   # session expired
```

5. اگر همه‌چیز OK بود، داده را در `scope["state"]["session_clientSide"]` می‌گذارد تا در handler قابل دسترسی باشد.

اگر هر کدام از این مراحل شکست بخورد (توکن خراب، HMAC نامعتبر، منقضی، JSON نامعتبر)، مقدار `{}` برمی‌گردد — یعنی «کاربر مهمان».

---

## ۶. محدودیت مدت (Lifetime) و هماهنگی با `max_age`

### ۶-۱. مکانیزم دوگانه

عمر سشن توسط **دو چیز** کنترل می‌شود:

| لایه | کنترل | نتیجه‌ی انقضا |
|---|---|---|
| کوکی (`Set-Cookie: Max-Age=X`) | مرورگر | مرورگر کوکی را حذف می‌کند |
| `_exp` در payload | سرور | سرور توکن را رد می‌کند |

### ۶-۲. چرا هماهنگ‌اند؟

در `set_session_clientSide`:

```python
encrypted = ClientSession.encrypt(data, max_age=max_age)
self.set_Cookie("session_clientSide", encrypted, max_age=max_age, ...)
```

هر دو از یک `max_age` استفاده می‌کنند. پس:
- تا لحظه‌ی `_exp` → هم مرورگر کوکی را دارد، هم سرور قبول می‌کند. ✅
- بعد از `_exp` → مرورگر کوکی را حذف می‌کند (اگر از `Max-Age` استفاده شده)، و سرور هم رد می‌کند. ✅

### ۶-۳. سقف سخت (Hard Cap)

در `ClientSession`:

```python
MAX_TTL = 3600 * 24 * 30  # 30 days
```

اگر کاربر `max_age` بزرگتری بدهد، به ۳۰ روز محدود می‌شود. این جلوی `max_age=10*365*24*3600` (۱۰ سال) را می‌گیرد.

### ۶-۴. آیا باید TTL و Max-Age همیشه برابر باشند؟

بله. اگر TTL سرور کمتر باشد، کاربر قبل از اینکه مرورگر کوکی را پاک کند، session از دست می‌دهد. اگر TTL بیشتر باشد، کوکی می‌رود ولی توکن هنوز معتبر است (که اگر کسی کوکی را کپی کرده باشد، می‌تواند از آن استفاده کند). پس هماهنگی ضروری است.

---

## ۷. HTTP در مقابل HTTPS و `Secure` Flag

### ۷-۱. مشکل HTTP

کوکی `Secure` یعنی: «مرورگر این کوکی را فقط روی اتصال HTTPS ارسال کن.» اگر اپ روی `http://127.0.0.1:8000` اجرا شود:

- مرورگر کوکی را **ذخیره** می‌کند.
- اما در درخواست بعدی **ارسال نمی‌کند**.
- نتیجه: session در هر درخواست خالی است.

### ۷-۲. حل در NexelPy

در `set_session_clientSide`:

```python
if secure is None:
    app = get_request().scope.get("app")
    secure = getattr(app, "session_secure", True)
```

و `session_secure` در `Nexelpy`:
- در `__init__`: `True` (برای prod)
- در `run`: `False` (چون `run` یعنی dev روی HTTP)

پس:
- **در dev:** `secure=False` → کوکی روی HTTP هم ارسال می‌شود. ✅
- **در prod:** `secure=True` → کوکی فقط روی HTTPS ارسال می‌شود. ✅

### ۷-۳. نکته‌ی مهم
اگر اپ را در production پشت یک Reverse Proxy (Nginx, Cloudflare) با HTTPS اجرا کنید، کوکی `Secure` کار می‌کند حتی اگر خود اپ روی HTTP داخلی باشد (چون مرورگر فقط HTTPS می‌بیند). پس `secure=True` در prod همیشه درست است.

---

## ۸. چرخش (Rotation) — جلوگیری از Session Fixation

### ۸-۱. حمله‌ی Session Fixation چیست؟

1. مهاجم یک session معتبر می‌سازد و کوکی آن را می‌گیرد.
2. مهاجم قربانی را مجبور می‌کند با آن کوکی وارد شود (از طریق XSS یا لینک مخرب).
3. قربانی لاگین می‌کند. اگر session ID عوض نشود، مهاجم با همان کوکی به حساب قربانی دسترسی دارد.

### ۸-۲. چطور NexelPy از آن جلوگیری می‌کند؟

Fernet هر بار یک **IV تصادفی** تولید می‌کند. پس هر بار که `set_session_clientSide` صدا زده شود، ciphertext کاملاً متفاوت است — حتی اگر داده‌ی سشن دقیقاً یکسان باشد.

**نتیجه:** اگر بعد از لاگین، `set_session_clientSide` را دوباره صدا بزنید، کوکی جدید ساخته می‌شود. مهاجم که کوکی قدیمی را دارد، نمی‌تواند از آن استفاده کند (چون session جدید با ciphertext جدید جایگزین شده).

### ۸-۳. توصیه

بعد از هر تغییر در وضعیت احراز هویت (login, privilege change, password change) دوباره صدا بزنید:

```python
# after successful login
x.set_session_clientSide(user_id=user.id, role=user.role)
```

این کار به طور خودکار «چرخش» را انجام می‌دهد.

---

## ۹. مرگ (Kill) سشن

### ۹-۱. سمت کلاینت (توصیه‌شده)

کاربر برای لاگ‌اوت:

```python
x.delete_Cookie("session_clientSide")
```

این کوکی را از مرورگر حذف می‌کند. درخواست بعدی بدون کوکی می‌رود و سرور session خالی برمی‌گرداند.

### ۹-۲. سمت سرور (غیرممکن به تنهایی)

چون session stateless است، سرور نمی‌تواند کوکی کاربر دیگر را حذف کند. اگر مدیر بخواهد یک کاربر را logout کند:

- **راه اول:** کلید Fernet را عوض کنید. اما این **همه‌ی** کاربران را logout می‌کند.
- **راه دوم:** یک ست لیست سیاه (Blacklist) از توکن‌های باطل‌شده نگه دارید. اما این نیاز به دیتابیس یا کش دارد — که کل مزیت stateless بودن را از بین می‌برد.
- **راه سوم:** `max_age` کوتاه انتخاب کنید (مثلاً ۱ ساعت). کاربر هر ساعت باید دوباره لاگین کند، ولی حداکثر ۱ ساعت می‌تواند از کوکی دزدیده‌شده استفاده کند.

**توصیه:** برای اپ‌های معمولی، `max_age` کوتاه (۱-۲ ساعت) و چرخش مکرر کافی است. برای اپ‌های حساس (بانک، پنل ادمین)، باید به server-side session مهاجرت کنید.

---

## ۱۰. محدودیت اندازه (Size Limit)

کوکی مرورگر حداکثر **۴۰۹۶ بایت** است. توکن Fernet برای داده‌ی معمولی (`{"user_id": 42, "role": "admin"}`) حدود ۲۰۰-۳۰۰ بایت است. اما اگر داده‌ی زیادی در session بگذارید:

```python
if len(encrypted) > 3800:
    raise ValueError("session payload too large; keep session data small")
```

این خط جلوی شکست بی‌صدا را می‌گیرد. اگر مرورگر کوکی بزرگ‌تر از ۴KB را رد کند، session شما در ظاهر «کار می‌کند» ولی در عمل هیچ‌وقت ذخیره نمی‌شود.

**توصیه:** فقط شناسه‌های ضروری (user_id, role) را در session بگذارید. داده‌های حجیم (لیست permissionها، سبد خرید) را در دیتابیس نگه دارید.

---

## ۱۱. همان-درخواستی (Same-Request Read)

یکی از امکانات NexelPy این است که بعد از `set_session_clientSide` در همان درخواست هم می‌توانید session را بخوانید:

```python
x.set_session_clientSide(user_id=42)
uid = await x.REQUEST.session_clientSide("user_id")  # 42 (same request!)
```

### چرا این کار می‌کند؟

در `set_session_clientSide`:

```python
request.scope.setdefault("state", {})
request.scope["state"]["session_clientSide"] = dict(data)
```

data را مستقیماً در scope می‌گذارد. پس `session_clientSide()` که از `scope["state"]["session_clientSide"]` می‌خواند، همان داده را می‌بیند.

### چرا این مهم است؟

در حالت عادی (بدون این مکانیزم)، `session_clientSide()` فقط از کوکی ورودی می‌خواند، و در همان درخواست که کوکی هنوز به مرورگر نرفته، خالی برمی‌گردد. این رفتار برای توسعه‌دهنده گیج‌کننده است. NexelPy این را حل می‌کند.

---

## ۱۲. امنیت HMAC و دستکاری

### ۱۲-۱. سناریوی حمله

مهاجم کوکی `session_clientSide` را می‌گیرد و می‌خواهد `role: "user"` را به `role: "admin"` تغییر دهد.

### ۱۲-۲. چرا نمی‌تواند؟

- داده رمزنگاری‌شده است (AES-128-CBC). بدون کلید نمی‌تواند آن را رمزگشایی کند.
- حتی اگر یک بیت را تغییر دهد، HMAC-SHA256 تشخیص می‌دهد که توکن دستکاری شده و `InvalidToken` برمی‌گرداند.
- نتیجه: `decrypt` مقدار `{}` برمی‌گرداند (session خالی).

پس **HMAC-SHA256 تضمین می‌کند که فقط سروری که کلید را دارد می‌تواند session معتبر بسازد.**

---

## ۱۳. کلید Fernet — مدیریت در Production

### ۱۳-۱. ذخیره‌سازی امن

کلید را **هرگز** در کد سخت‌کد نکنید. از environment variable استفاده کنید:

```python
import os
secret = os.environ["NEXELPY_SECRET_KEY"].encode()
app = Nexelpy(__file__, secretKey=secret)
```

### ۱۳-۲. تولید کلید

یک بار با پایتون تولید کنید:

```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

و در `.env` یا secret manager ذخیره کنید.

### ۱۳-۳. چرخش کلید (Key Rotation)

اگر کلید لو رفت، باید:
1. کلید جدید تولید کنید.
2. اپ را با کلید جدید restart کنید.
3. تمام sessionهای قبلی باطل می‌شوند (کاربران باید دوباره لاگین کنند).

اگر می‌خواهید چرخش نرم داشته باشید (بعضی sessionها هنوز معتبر بمانند)، باید `MultiFernet` با چند کلید استفاده کنید. اما این پیچیدگی اضافه دارد و برای اکثر پروژه‌ها لازم نیست.

---

## ۱۴. رونوشت (Replay)

### ۱۴-۱. آیا می‌توان توکن را دوباره استفاده کرد؟

**بله، تا وقتی `_exp` منقضی نشده.** Fernet خودش timestamp دارد و TTL پیش‌فرض ۶۰ ثانیه‌اش را در `decrypt` غیرفعال کردیم (`ttl=None`). پس توکن تا لحظه‌ی `_exp` قابل استفاده است.

### ۱۴-۲. پیامد

اگر کسی کوکی را بدزدد (مثلاً از طریق XSS یا Wi-Fi عمومی)، می‌تواند تا انقضای `_exp` از آن استفاده کند. این محدودیت **ذاتی** session سمت کلاینت است.

### ۱۴-۳. کاهش ریسک

- **HTTPS اجباری:** جلوی Sniffing روی شبکه را می‌گیرد.
- **HttpOnly:** جلوی دزدیدن کوکی از JavaScript (XSS) را می‌گیرد. `set_session_clientSide` به‌طور پیش‌فرض `httponly=True` می‌گذارد.
- **SameSite=strict:** جلوی CSRF را می‌گیرد.
- **`_exp` کوتاه:** کاهش پنجره‌ی حمله.

---

## ۱۵. CSRF (Cross-Site Request Forgery)

### ۱۵-۱. خطر

اگر مهاجم کاربر را مجبور کند درخواستی به اپ شما بفرستد (مثلاً از طریق یک سایت مخرب)، مرورگر به‌طور خودکار کوکی `session_clientSide` را می‌فرستد. اگر اپ شما این درخواست را معتبر بداند، مهاجم می‌تواند به نام کاربر عمل کند.

### ۱۵-۲. دفاع در NexelPy

`set_session_clientSide` به‌طور پیش‌فرض `samesite="strict"` دارد. این یعنی کوکی **فقط** در درخواست‌هایی فرستاده می‌شود که از همان دامنه شروع شده‌اند. درخواست‌های cross-site (مثل یک `<form>` از سایت دیگر) کوکی را نمی‌فرستند.

### ۱۵-۳. محدودیت

`samesite="strict"` ممکن است با بعضی فلوی OAuth یا لینک‌های ایمیل مشکل داشته باشد (چون کاربر از یک دامنه‌ی دیگر می‌آید). در این حالت، `samesite="lax"` یا یک CSRF token جداگانه لازم است.

---

## ۱۶. جدول خلاصه‌ی امنیت

| ویژگی | مکانیزم | وضعیت |
|---|---|---|
| محرمانگی داده | AES-128-CBC | ✅ |
| یکپارچگی | HMAC-SHA256 | ✅ |
| جلوگیری از replay بعد از expiry | `_exp` در payload | ✅ |
| جلوگیری از دستکاری | HMAC | ✅ |
| جلوگیری از Session Fixation | IV تصادفی Fernet | ✅ (با چرخش بعد از login) |
| جلوگیری از XSS | HttpOnly | ✅ (پیش‌فرض) |
| جلوگیری از Sniffing | Secure flag | ✅ (در prod) |
| جلوگیری از CSRF | SameSite=strict | ✅ (پیش‌فرض) |
| Revoke فوری | ندارد | ❌ (محدودیت ذاتی) |
| محدودیت اندازه | هشدار در ۳۸۰۰ بایت | ✅ |

---

## ۱۷. مثال کامل

```python
from nexelpy import Nexelpy, View, AutoRegister

app = Nexelpy(__file__)

@AutoRegister("/login")
async def login():
    x = View(__file__, title="Login")
    # after verifying credentials
    x.set_session_clientSide(user_id=42, role="admin", max_age=3600)
    x.redirect("/dashboard")
    return x.RESPONSE()

@AutoRegister("/dashboard")
async def dashboard():
    x = View(__file__, title="Dashboard")
    uid, role = await x.REQUEST.session_clientSide("user_id", "role")
    if uid is None:
        return x.redirect("/login")
    x.p(f"Welcome user {uid} (role: {role})")
    return x.RESPONSE()

@AutoRegister("/logout")
async def logout():
    x = View(__file__, title="Logout")
    x.delete_Cookie("session_clientSide")
    x.redirect("/login")
    return x.RESPONSE()
```

---

## ۱۸. چه زمانی به Server-Side Session مهاجرت کنیم؟

اگر به یکی از این نیازها رسیدید، client-side session جوابگو نیست:

- **Revoke فوری:** باید بتوانید «همین حالا کاربر X را logout کنم».
- **Session بزرگ:** بیش از ۴KB داده در session.
- **لیست دستگاه‌های فعال:** «کجا لاگین کرده‌ام؟»
- **Token Rotation مکرر:** برای هر درخواست، token جدید (refresh token pattern).
- **حسابرسی (Audit):** لاگ همه‌ی sessionهای فعال.

در این حالت، باید یک لایه‌ی server-side (Redis, SQLite, DB) اضافه کنید و session ID را در کوکی نگه دارید، نه خود داده را.

---

## ۱۹. جمع‌بندی

Client-side session در NexelPy:

- **امن** است برای اکثر اپ‌های وب (به لطف Fernet + HMAC + IV تصادفی + Secure + HttpOnly + SameSite).
- **بدون زیرساخت** کار می‌کند (بدون Redis، بدون DB، بدون کش).
- **مقیاس‌پذیر** است (چون stateless است، هر تعداد سرور می‌تواند session را بخواند).
- **محدودیت دارد** برای revoke فوری و session بزرگ.

اگر به محدودیت‌ها آگاه باشید و `_exp` منطقی انتخاب کنید (مثلاً ۱-۲ ساعت برای اپ حساس، ۷-۳۰ روز برای «remember me»)، این مدل کاملاً قابل اعتماد است.