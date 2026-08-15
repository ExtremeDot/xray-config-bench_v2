# بنچمارک آی‌پی کلادفلر برای اکسری

ابزاری برای تست
 Cloudflare IP
ها با لینک‌های کانفیگ
 Xray
(
 vless
 /
 vmess
 /
 trojan
)
، امتیازدهی برای وب‌گردی، اینستاگرام و گیمینگ، و خروجی اکسل رتبه‌بندی‌شده.

الهام‌گرفته از پروژه
 ExtremeDot/xray-config-benchmark
با تمرکز روی جابه‌جایی
 IP
کلادفلر، رد سریع
 IP
های مرده، و تست
 relay
واقعی.

---

## قابلیت‌ها

- قرار دادن هر
 Cloudflare IP
به‌جای آدرس سرور کانفیگ و تست از طریق
 SOCKS5
محلی
 Xray
- فیلتر سریع
 (Quick probe)
: رد کردن
 IP
های قطع یا خیلی کند قبل از تست کامل  
  (پیش‌فرض: پینگ بالای
 2000 ms
)
- تست
 baseline
اینترنت مستقیم شما (بدون
 VPN
) برای مقایسه
- تست
 Latency
 /
 Download
 /
 Upload
از طریق
 endpoint
های سرعت کلادفلر
- زمان باز شدن سایت‌های مهم از طریق پروکسی:  
  Google
،
 YouTube
،
 Instagram
،
 GitHub
،
 Cloudflare
،
 Microsoft
- امتیاز
 0 تا 10
برای وب، اینستاگرام، گیمینگ و
 Overall
- جداول
 Top-N
در انتهای اجرا + خروجی
 Excel
+ لاگ زنده
- کنترل تقریباً همه چیز با
 config.json
- محیط گرافیکی با استایل اپل (
 GUI
)
- اجرا از
 CLI
و اسکریپت‌های
 setup
 /
 run
برای ویندوز و لینوکس

---

## شروع سریع

### ویندوز

ابتدا وابستگی‌ها را نصب کنید:

```bat
setup.bat
```

اجرای خط فرمان:

```bat
run.bat
```

**محیط گرافیکی (پیشنهادی):**

```bat
gui.bat
```

یا:

```bat
python gui.py
```

رابط روشن و کارتی، فونت سیستم، رنگ آبی اپل.  
بدون پکیج
 GUI
اضافی (از
 Tkinter
خود پایتون استفاده می‌کند).

### لینوکس / مک

```bash
chmod +x setup.sh run.sh
./setup.sh
./run.sh
```

رابط گرافیکی:

```bash
python3 gui.py
```

### نصب دستی

```bash
pip install -r requirements.txt
python cf_xray_benchmark.py
```

---

## ساختار پروژه

```text
cf-xray-benchmark/
  cf_xray_benchmark.py   # ابزار اصلی خط فرمان
  debug_one.py           # دیباگ یک کانفیگ (بدون تعویض IP)
  gui.py                 # لانچر رابط گرافیکی
  gui_app.py             # رابط با طراحی اپل
  gui.bat                # میانبر GUI در ویندوز
  config.json            # همه تنظیمات
  cfip.txt               # لیست IP / CIDR / دامنه
  links.txt              # لینک‌های کانفیگ
  requirements.txt
  setup.bat / setup.sh   # نصب وابستگی‌ها
  run.bat / run.sh       # اجرای CLI
  README.md              # راهنمای انگلیسی
  README_FA.md           # راهنمای فارسی
  temp/                  # کانفیگ‌های موقت Xray
  results/               # گزارش اکسل
  logs/                  # لاگ اجرا
```

---

## فایل‌هایی که باید پر کنید

### فایل
 links.txt

در هر خط یک لینک اشتراک:

```text
vless://uuid@host:443?security=tls&type=ws&path=/&sni=example.com#MyConfig
# کامنت مجاز است
```

پروتکل‌های پشتیبانی‌شده:

 vless://
 ·
 vmess://
 ·
 trojan://

### فایل
 cfip.txt

در هر خط یک مورد. فرمت‌های مجاز:

```text
# سبک اسکنر (پینگ دانلود - پینگ آپلود - آی‌پی)
1181 - 0 - 172.66.170.97

# آی‌پی ساده
172.66.45.96

# بازه CIDR (به آی‌پی‌های میزبان باز می‌شود؛ سقف 4096)
172.66.170.0/24

# دامنه (با DNS به A record تبدیل می‌شود)
cdn.example.com

# کامنت
# نادیده گرفته می‌شود
```

---

## جریان یک تست

برای هر جفت
 CF IP
+ کانفیگ:

1. ساخت کانفیگ موقت
 Xray
(آدرس سرور با
 IP
کلادفلر عوض می‌شود)
2. روشن شدن
 SOCKS
محلی روی یک پورت آزاد
3. **پروب سریع** با تایم‌اوت کوتاه  
   اگر وصل نشد یا پینگ بیشتر از
   `filter.max_latency_ms`
   بود → وضعیت
   SKIP
   (بدون تست کامل)
4. نمونه‌گیری کامل
 latency
5. دانلود / آپلود (اگر در تنظیمات روشن باشد)
6. پینگ
 relay
به سایت‌های بزرگ (اگر روشن باشد)
7. محاسبه امتیاز وب / اینستاگرام / گیمینگ /
 Overall
(از
 0 تا 10
)

در ابتدای اجرا (اختیاری): تست
 baseline
خط مستقیم اینترنت شما بدون پروکسی.

در پایان: جداول
 Top-N
هر دسته، مقایسه با
 baseline
، فایل
 Excel
و لاگ.

---

## تنظیمات
 config.json

کلیدهایی که با
 `_`
شروع می‌شوند فقط توضیح هستند و برنامه آن‌ها را نادیده می‌گیرد.

| بخش | کاربرد |
|-----|--------|
| `workers` | تعداد تست همزمان (روی ویندوز از `1` شروع کنید) |
| `max_ips` | سقف تعداد IP (`0` = همه) |
| `report_name` | پیشوند نام فایل اکسل و لاگ |
| `clear_temp` | `true` / `false` / `null` (پرسش در پایان) |
| `display.*` | نمایش پیشرفت، نتیجه زنده، فایل لاگ |
| `baseline.enabled` | تست اینترنت مستقیم قبل از پروکسی |
| `filter.enabled` | پروب سریع و رد زودهنگام |
| `filter.max_latency_ms` | رد کردن اگر پینگ اول بالاتر از این باشد (پیش‌فرض **2000**) |
| `filter.quick_timeout_seconds` | تایم‌اوت پروب (پیش‌فرض **3**) |
| `filter.require_exit_ip` | رد کردن وقتی Exit IP خوانده نشود |
| `tests.latency/download/upload` | روشن/خاموش + تعداد نمونه / حجم / تکرار |
| `relay.enabled` و `relay.sites.*` | هر سایت جدا + آدرس |
| `scoring.web/instagram/gaming` | روشن/خاموش بودن هر امتیاز |
| `scoring.overall_weights` | وزن‌های Overall (نرمال می‌شوند) |
| `ranking.top_n` | تعداد ردیف در هر جدول برتر |
| `ranking.show_*_top` | نمایش یا مخفی کردن هر جدول |
| `ranking.compare_with_baseline` | ستون «در مقابل خط مستقیم» |
| `timeouts.http_seconds` | تایم‌اوت HTTP تست‌های کامل |
| `timeouts.xray_startup_seconds` | صبر برای آماده شدن SOCKS |
| `paths.*` | نام فایل‌ها و پوشه‌ها |
| `excel.enabled` | نوشتن فایل results/*.xlsx |

### مثال: اجرای سریع‌تر با فیلتر سخت‌گیر

```json
"workers": 2,
"max_ips": 30,
"filter": {
  "enabled": true,
  "max_latency_ms": 1500,
  "quick_timeout_seconds": 3
},
"baseline": { "enabled": true },
"relay": { "enabled": false },
"ranking": { "top_n": 10 }
```

### مثال: فقط
 latency
و امتیاز وب

```json
"tests": {
  "latency": { "enabled": true, "samples": 5 },
  "download": { "enabled": true, "bytes": 250000, "rounds": 1 },
  "upload": { "enabled": false }
},
"scoring": {
  "web": true,
  "instagram": false,
  "gaming": false
},
"ranking": {
  "show_instagram_top": false,
  "show_gaming_top": false
}
```

---

## خط فرمان
 (CLI)

آرگومان‌های خط فرمان در صورت دادن، روی
 config.json
اولویت دارند:

```bash
python cf_xray_benchmark.py
python cf_xray_benchmark.py workers=2 max_ips=15 clear_temp=false report=myrun
python cf_xray_benchmark.py custom
```

| آرگومان | معنی |
|---------|------|
| `workers=N` | تعداد تست همزمان |
| `max_ips=N` | فقط N هدف اول از cfip.txt |
| `report=NAME` | پیشوند نام فایل |
| `clear_temp=true\|false` | پاک کردن یا نگه داشتن temp/ |
| `custom` | پرسش تعاملی در شروع |

---

## رابط گرافیکی

```bat
gui.bat
```

```bash
python gui.py
```

| کنترل | کار |
|-------|-----|
| Files | مسیر cfip.txt، links.txt، config.json |
| Workers / Max IPs / Report | مشابه CLI |
| Clear temp / Baseline | کلیدهای روشن/خاموش |
| Start / Stop | شروع یا توقف بنچمارک |
| Results | باز کردن پوشه results/ |
| Edit Config | باز کردن config.json |
| Debug One | اجرای debug_one.py |
| Live Output | لاگ رنگی زنده |

طراحی: کارت‌های روشن به سبک اپل، رنگ تأکید
 `#007AFF`
، پنل لاگ تیره.  
پیاده‌سازی در فایل
 gui_app.py
.

---

## دیباگ یک کانفیگ (بدون تعویض
 IP
)

اگر ابزار اصلی خطا داد، اول خود لینک را چک کنید:

```bash
python debug_one.py
python debug_one.py "vless://uuid@host:443?..."
```

اگر لینک را ندهید، اولین خط غیرکامنت
 links.txt
استفاده می‌شود.

### ویندوز: پروسه‌های گیرکرده
 xray

```powershell
Get-Process xray -ErrorAction SilentlyContinue | Stop-Process -Force
```

فایل
 run.bat
و
 GUI
قبل از شروع سعی می‌کنند
 xray.exe
را ببندند.

---

## خروجی‌ها

| مسیر | محتوا |
|------|--------|
| `results/*.xlsx` | نتایج کامل + برگه‌های رتبه‌بندی |
| `logs/*.log` | لاگ زنده اجرا |
| `temp/` | کانفیگ JSON هر تست (و FAILED_*.json در صورت خطا) |

### امتیازها (از
 0 تا 10
)

| بازه | معنی |
|------|------|
| 9–10 | عالی |
| 7–8 | خوب |
| 5–6 | متوسط |
| 3–4 | ضعیف |
| 0–2 | خیلی ضعیف |

**Overall** ترکیبی وزن‌دار از وب + اینستاگرام + گیمینگ است  
(وزن‌ها در
 config.json
).

صفحهٔ پایانی همچنین نشان می‌دهد:

- وضعیت
 baseline
خط مستقیم شما (اگر روشن باشد)
- پنج (یا
 N
) مورد برتر برای وب / اینستاگرام / گیمینگ /
 Overall
- بهترین
 IP
هر دسته
- درصد سرعت دانلود پروکسی نسبت به خط مستقیم

---

## پیش‌نیازها

- پایتون
 **3.9+**
- پکیج‌های داخل
 requirements.txt
:

```text
requests[socks]
openpyxl
colorama
```

- باینری
 xray
 /
 xray.exe
(اگر نباشد خودکار دانلود می‌شود)
- دسترسی شبکه به
 endpoint
های سرعت کلادفلر و سایت‌های
 relay

---

## نکات کاربردی

1. روی ویندوز با
   `workers=1`
   شروع کنید؛ بعد از پایداری، عدد را بالا ببرید.
2. اگر آنتی‌ویروس استارت
   xray
   را کند یا مسدود می‌کند،
   python.exe
   و
   xray.exe
   را در لیست مجاز بگذارید.
3. با
   `filter.max_latency_ms`
   (مثلاً
   1500
   تا
   2000
   )
   IP
   های بد سریع رد می‌شوند.
4. بازه‌های
   CIDR
   بزرگ گسترش داده می‌شوند ولی سقف دارند؛ با
   `max_ips`
   بیشتر محدود کنید.
5. هنگام دیباگ
   `clear_temp=false`
   بگذارید تا بتوانید
   `temp/FAILED_*.json`
   را ببینید.

---

## اعتبار

روش بنچمارک الهام‌گرفته از  
 ExtremeDot/xray-config-benchmark  
هستهٔ پروکسی:  
 XTLS/Xray-core
