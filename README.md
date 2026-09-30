# 🛡️ GrokOSINT

**Advanced Ethical OSINT Tool for Email (Gmail) + Phone Number Intelligence**

> Publicly available data only • Beautiful terminal UI • JSON + Markdown export

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Ethical Use](https://img.shields.io/badge/Use-Ethical%20Only-red.svg)]()

---

## ⚠️ Ethical & Legal Warning (বাধ্যতামূলক পড়ুন)

```
এই টুল শুধুমাত্র publicly available তথ্য সংগ্রহ করে।
This tool collects ONLY publicly available information.

• শুধু নিজের অ্যাকাউন্ট বা explicit written authorization থাকা টার্গেটে ব্যবহার করুন।
• Stalking, doxxing, harassment, unauthorized investigation = অবৈধ।
• Bangladesh / India / যেকোনো দেশের privacy আইন মেনে চলুন।
• Author কোনো অপব্যবহারের দায় নেয় না।
```

**By using this tool you agree to use it only for authorized, ethical purposes.**

---

## ✨ Features

| Module | Capabilities |
|--------|--------------|
| **Email** | Format validation, MX records, Disposable detection, Gravatar profile, Social search links, Google Dorks, Optional HIBP |
| **Phone** | Full parse (E.164/National/International), Country/Region/Carrier/Line-type/Timezone, Social lookup links, Google Dorks, Optional NumVerify |
| **Combined** | Run both together → unified report |
| **Export** | JSON + Markdown reports automatically |
| **UI** | Rich colored tables, progress spinners, clean CLI |

### Advanced Features
- Async HTTP requests
- Configurable API keys (optional deeper checks)
- Region-aware phone parsing (default BD)
- Ready-to-copy Google Dorks
- One-command full investigation
- Modular architecture (easy to extend)

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/sayan9168/GrokOSINT.git
cd GrokOSINT

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt
# or
pip install -e .
```

### 2. (Optional) Config

```bash
cp config.example.yaml config.yaml
# Edit and add API keys if you have them (HIBP, NumVerify etc.)
```

### 3. Run

```bash
# Email only
python main.py email someone@gmail.com

# Phone only (Bangladesh default)
python main.py phone +8801712345678

# Phone with different region
python main.py phone 9876543210 --region IN

# Both together
python main.py full --email someone@gmail.com --phone +8801712345678

# Skip confirmation (automation)
python main.py email test@example.com --yes --no-export

# About
python main.py about
```

After install with `pip install -e .` you can also use:

```bash
grokosint email someone@gmail.com
grokosint phone +8801xxxxxxxxx
grokosint full -e mail@gmail.com -p +8801xxxxxxxxx
```

---

## 📦 Optional API Keys

| Service | Purpose | Free Tier |
|---------|---------|-----------|
| [Have I Been Pwned](https://haveibeenpwned.com/API/Key) | Breach check | Paid for API |
| [NumVerify](https://numverify.com) | Extra carrier data | 100/month free |
| Hunter.io / EmailRep | Enrichment | Limited free |

Leave empty → tool still works with 100% free public sources.

---

## 📂 Project Structure

```
GrokOSINT/
├── main.py                 # Entry point
├── pyproject.toml
├── requirements.txt
├── config.example.yaml
├── grok_osint/
│   ├── __init__.py
│   ├── cli.py              # Typer CLI
│   ├── core/
│   │   ├── validator.py    # Email + Phone validation
│   │   ├── reporter.py     # JSON / Markdown export
│   │   └── utils.py
│   └── modules/
│       ├── email_osint.py  # Email intelligence
│       └── phone_osint.py  # Phone intelligence
└── reports/                # Generated reports (auto-created)
```

---

## 🛠️ Extending

Want more sources?
1. Add new methods in `email_osint.py` / `phone_osint.py`
2. Call them inside `run_async`
3. Display + export automatically picks them up

Ideas: Holehe integration, Ignorant (WhatsApp/IG), GHunt wrapper, Pastebin deep search, etc.

---

## ⚖️ License

MIT License — free to use, modify, distribute.

**But remember: with great power comes great responsibility.**

---

## 🙏 Credits

- [phonenumbers](https://github.com/daviddrysdale/python-phonenumbers) (libphonenumber)
- [Rich](https://github.com/Textualize/rich) & [Typer](https://github.com/tiangolo/typer)
- OSINT community (Holehe, PhoneInfoga, GHunt inspiration)

---

**Built with ❤️ by [Sayan the researcher](https://github.com/sayan9168)**

*Use it to protect, not to harm.*
