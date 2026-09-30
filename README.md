# 🛡️ GrokOSINT v1.1.0

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

## ✨ What's New in v1.1.0 (Advanced Features)

| Feature | Description |
|---------|-------------|
| **Account Existence Checks** | GitHub + Keybase public lookup for email |
| **Public Paste Search** | psbdmp.ws integration for leaked pastes |
| **Username Guesses** | Smart variants from email local-part |
| **Possible Apps** | Heuristic WhatsApp/Telegram/Imo etc. for phone |
| **Better Dorks** | More targeted Google dorks for email & phone |
| **Region Notes** | Bangladesh & India specific operator hints |
| **Improved Reports** | All new fields exported to JSON + Markdown |

---

## ✨ Full Feature List

| Module | Capabilities |
|--------|--------------|
| **Email** | Format + MX, Disposable detection, Gravatar profile, Account checks (GitHub/Keybase), Public paste hits, Username guesses, Social search links, Google Dorks, Optional HIBP |
| **Phone** | Full parse (E.164/National/International), Country/Region/Carrier/Line-type/Timezone, Possible linked apps, Social lookup links, Google Dorks, Optional NumVerify |
| **Combined** | `full` command runs both → unified report |
| **Export** | Automatic JSON + Markdown reports |
| **UI** | Rich colored tables, progress spinners, clean CLI |

---

## 🚀 Quick Start

```bash
git clone https://github.com/sayan9168/GrokOSINT.git
cd GrokOSINT

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt
# or
pip install -e .
```

### Run

```bash
# Email (with advanced checks)
python main.py email someone@gmail.com

# Phone (Bangladesh default)
python main.py phone +8801712345678

# Phone India
python main.py phone 9876543210 --region IN

# Both together
python main.py full --email someone@gmail.com --phone +8801712345678

# Skip confirmation
python main.py email test@example.com --yes --no-export

# About
python main.py about
```

After `pip install -e .`:

```bash
grokosint email someone@gmail.com
grokosint phone +8801xxxxxxxxx
grokosint full -e mail@gmail.com -p +8801xxxxxxxxx
```

---

## 📦 Optional API Keys

Copy `config.example.yaml` → `config.yaml` and add:

| Service | Purpose |
|---------|---------|
| Have I Been Pwned | Breach check |
| NumVerify | Extra carrier data |

Tool works 100% without any API keys.

---

## 📂 Project Structure

```
GrokOSINT/
├── main.py
├── pyproject.toml
├── requirements.txt
├── config.example.yaml
├── grok_osint/
│   ├── __init__.py
│   ├── cli.py
│   ├── core/
│   │   ├── validator.py
│   │   ├── reporter.py
│   │   └── utils.py
│   └── modules/
│       ├── email_osint.py   # Advanced
│       └── phone_osint.py   # Advanced
└── reports/
```

---

## ⚖️ License

MIT License — free to use, modify, distribute.

**Use it to protect, not to harm.**

---

**Built with ❤️ by [Sayan the researcher](https://github.com/sayan9168)**
