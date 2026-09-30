# 🛡️ GrokOSINT v1.2.0

**Advanced Ethical OSINT Tool for Email (Gmail) + Phone Number Intelligence**

> Public data only • CLI + Streamlit Web UI • JSON / Markdown / **PDF** reports • Holehe + Ignorant integration

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Ethical Use](https://img.shields.io/badge/Use-Ethical%20Only-red.svg)]()

---

## ⚠️ Ethical & Legal Warning

```
শুধুমাত্র publicly available তথ্য।
Only use on accounts/numbers you own or have explicit written authorization.
Stalking / doxxing / harassment = ILLEGAL.
```

---

## ✨ What's New in v1.2.0

| Feature | Description |
|---------|-------------|
| **Streamlit Web UI** | Beautiful browser interface (`streamlit run streamlit_app.py`) |
| **Holehe Integration** | Optional deep email platform checks (120+ sites) if `holehe` installed |
| **Ignorant Integration** | Optional WhatsApp / Instagram / Snapchat check if `ignorant` installed |
| **PDF Reports** | Professional PDF export via reportlab |
| **More Platforms** | GitHub, Keybase, About.me, Spotify, GitLab, Reddit account checks |
| **Expanded Links** | Medium, Dev.to, Pinterest, TikTok etc. |

---

## 🚀 Quick Start

```bash
git clone https://github.com/sayan9168/GrokOSINT.git
cd GrokOSINT

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Optional deep tools
pip install holehe ignorant
```

### CLI

```bash
python main.py email someone@gmail.com
python main.py phone +8801712345678
python main.py full -e someone@gmail.com -p +8801712345678
python main.py about
```

### Web UI (Streamlit)

```bash
streamlit run streamlit_app.py
```

Open the browser URL shown (usually http://localhost:8501).

---

## Features Overview

**Email:** Validation, MX, Disposable, Gravatar, Account checks (6+ platforms), Username guesses, Holehe (optional), Public pastes, Social links, Google Dorks, HIBP (optional), PDF/JSON/MD export

**Phone:** Full parse, Carrier/Type/Timezone, Possible apps, Ignorant (optional), Social links, Google Dorks, NumVerify (optional), PDF/JSON/MD export

---

## Optional Dependencies

```bash
pip install holehe      # deep email account discovery
pip install ignorant    # WhatsApp / IG / Snapchat phone check
```

Without them the tool still works with all built-in free checks.

---

## License

MIT — Use ethically.

**Built by [Sayan the researcher](https://github.com/sayan9168)**
