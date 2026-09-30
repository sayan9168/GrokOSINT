# 🛡️ GrokOSINT v1.2.1

**Advanced Ethical OSINT Tool for Email (Gmail) + Phone Number Intelligence**

> Public data only • CLI + **Flask Web UI** (Termux friendly) • JSON / Markdown / PDF reports

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## ⚠️ Ethical Warning

শুধুমাত্র publicly available data।  
Only use on accounts/numbers you own or have explicit authorization.  
Stalking / doxxing = ILLEGAL.

---

## ✨ Features

- Email OSINT (MX, Gravatar, Account checks, Holehe optional, Pastes, Dorks...)
- Phone OSINT (Carrier, Type, Timezone, Ignorant optional, Apps heuristic...)
- **Flask Web UI** (lightweight, works great on Termux)
- CLI with Rich
- JSON + Markdown + PDF reports
- Optional: Holehe + Ignorant

---

## 🚀 Install (Termux friendly)

```bash
pkg update && pkg upgrade -y
pkg install python git
# Optional but recommended for numpy if needed later
# pkg install python-numpy

git clone https://github.com/sayan9168/GrokOSINT.git
cd GrokOSINT

pip install -r requirements.txt

# Optional deep tools
pip install holehe ignorant
```

---

## Usage

### CLI
```bash
python main.py email someone@gmail.com
python main.py phone +8801712345678
python main.py full -e someone@gmail.com -p +8801712345678
```

### Web UI (Flask - Recommended on Termux)
```bash
python web_app.py
```
তারপর ব্রাউজারে খোলো: **http://127.0.0.1:5000**

(মোবাইল থেকে অন্য ডিভাইস দিয়ে এক্সেস করতে চাইলে একই WiFi-তে থাকো এবং Termux-এ দেখানো IP ব্যবহার করো)

---

## Why Flask instead of Streamlit?

Streamlit needs numpy + heavy dependencies → Termux-এ install কষ্টকর।  
Flask অনেক হালকা এবং Termux-এ পারফেক্ট কাজ করে।

---

## License

MIT — Use ethically.

**Built by [Sayan the researcher](https://github.com/sayan9168)**
