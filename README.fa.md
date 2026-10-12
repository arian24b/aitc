# aitc

[English](README.md)

شمارندهٔ توکن برای مدل‌های هوش مصنوعی. تعداد توکن‌های یک متن، یک فایل یا ورودی pipe را می‌شمارد و هزینهٔ آن را روی API چند مدل معروف تخمین می‌زند. دو فایل را هم می‌تواند با هم مقایسه کند.

## ویژگی‌ها

- توکن‌ها را از `--text`، `--file` یا stdin می‌شمارد.
- هزینهٔ ورودی را برای شش مدل در یک جدول تخمین می‌زند.
- `--diff` تغییر توکن و هزینه را بین دو فایل نشان می‌دهد.
- `--live-prices` قیمت روز را از OpenRouter می‌خواند و اگر درخواست شکست بخورد، به جدول داخلی برمی‌گردد.

## طرز کار

`aitc` ورودی را با [tiktoken](https://github.com/openai/tiktoken) و رمزگذاری `cl100k_base` توکن‌بندی می‌کند و تعداد را در قیمت ورودی هر یک میلیون توکن هر مدل ضرب می‌کند. قیمت‌های داخلی ثابت‌هایی در `tokencount.py` هستند. با `--live-prices` درخواستی به `https://openrouter.ai/api/v1/models` می‌رود (مهلت ۳ ثانیه) و قیمت `prompt` مدل‌های مطابق خوانده می‌شود؛ خروجی می‌گوید قیمت‌ها زنده بوده‌اند یا از جدول داخلی آمده‌اند. هیچ داده‌ای جز همین درخواست از شبکه رد نمی‌شود.

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

نمونهٔ خروجی:

```text
$ aitc --text "Hello world"
Tokens: 2

Model (input cost)  Cost
GPT-4o              $0.000005
GPT-4o mini         $0.000000
Claude Sonnet 4.5   $0.000006
Claude Haiku 4.5    $0.000002
Gemini 1.5 Pro      $0.000002
Gemini 1.5 Flash    $0.000000
```

```text
$ aitc --diff old.txt new.txt
File 1: old.txt                        →        4 tokens
File 2: new.txt                        →        7 tokens
Delta:  +3 tokens  (+75.0%)

Model (cost delta)  Delta
GPT-4o              +$0.000007
...
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

## عیب‌یابی

- `File not found: ...` با کد خروج ۱: مسیری که به `--file` یا `--diff` داده‌اید وجود ندارد.
- `[prices: fallback (live fetch failed)]`: به OpenRouter دسترسی نبوده یا پاسخ غیرمنتظره بوده و قیمت‌های داخلی به کار رفته‌اند.
- شمارش فقط برای مدل‌های OpenAI که از `cl100k_base` استفاده می‌کنند دقیق است؛ ردیف‌های Claude و Gemini تقریبی‌اند. قیمت‌های داخلی ممکن است قدیمی شده باشند.

## توسعه

```bash
uv sync
uv run ruff check . && uv run ruff format --check .
uv build
```

## مجوز

MIT
