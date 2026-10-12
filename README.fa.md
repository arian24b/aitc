# aitc

[English](README.md)

شمارندهٔ توکن برای مدل‌های هوش مصنوعی. تعداد توکن‌های یک متن، یک فایل یا ورودی pipe را می‌شمارد و هزینهٔ آن را روی API چند مدل معروف تخمین می‌زند. دو فایل را هم می‌تواند با هم مقایسه کند.

## نصب

پایتون ۳٫۱۲ تا ۳٫۱۵.

```bash
uv tool install aitc      # یا: pipx install aitc، pip install aitc
```

از روی کلون: `uv sync && uv run aitc --text "Hello"`.

## استفاده

`aitc` یک دستور دارد، `count`، که به‌طور پیش‌فرض اجرا می‌شود. پس `aitc --text ...` با `aitc count --text ...` یکی است.

```bash
aitc --text "Your text here"           # متن مستقیم
aitc --file README.md                  # یک فایل
echo "Your text here" | aitc           # stdin
aitc --diff old.txt new.txt            # تفاوت توکن و هزینهٔ دو فایل
aitc --text "Hello" --live-prices      # قیمت روز از OpenRouter
aitc                                   # در ترمینال و بدون ورودی: متن را می‌پرسد
```

گزینه‌های `count`:

| گزینه | کار |
|---|---|
| `-t`، `--text TEXT` | متنی که باید شمرده شود |
| `-f`، `--file FILE` | فایلی که باید شمرده شود |
| `-d`، `--diff FILE FILE` | مقایسهٔ دو فایل |
| `--live-prices` | به‌جای جدول داخلی، قیمت را از OpenRouter می‌گیرد |

ترتیب خواندن ورودی: اول `--text`، بعد `--file`، بعد stdin. هزینه‌ها برای توکن‌های ورودی و به دلار است و برای این مدل‌ها نشان داده می‌شود: GPT-4o، GPT-4o mini، Claude Sonnet 4.5، Claude Haiku 4.5، Gemini 1.5 Pro و Gemini 1.5 Flash. شمارش با رمزگذاری `cl100k_base` انجام می‌شود؛ برای مدل‌های خانوادهٔ دیگر عدد تقریبی است.

## دستورهای مشترک

این ابزار روی [cfuicli](https://github.com/arian24b/cfui) ساخته شده و ظاهر و رفتارش با بقیهٔ ابزارهای این مجموعه یکی است.

```bash
aitc help [command]     # راهنما؛ -h روی هر دستور کار می‌کند
aitc version            # نسخه و مخزن گیت (همچنین: -v)
aitc update [--check]   # به‌روزرسانی خود ابزار؛ --check فقط نسخه‌ها را مقایسه می‌کند
aitc -q ...             # حالت آرام: بدون بنر و یادداشت (یا AITC_QUIET=1)
```

- اگر گزینهٔ اجباری جا افتاده باشد و ابزار را در ترمینال اجرا کرده باشید، مقدارش را می‌پرسد. در pipe یا CI با پیام `--flag is required. Pass --flag <value> or run interactively.` متوقف می‌شود (کد خروج ۲).
- خطاها در یک کادر قرمز روی stderr و با کد خروج غیرصفر نمایش داده می‌شوند. با Ctrl-C کد خروج ۱۳۰ است.
- رنگ فقط در ترمینال استفاده می‌شود. با `NO_COLOR=1` خاموش می‌شود.

## توسعه

```bash
uv sync
uv run ruff check . && uv run ruff format --check .
uv build
```

## مجوز

MIT
