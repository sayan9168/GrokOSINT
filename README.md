# 🛡️ GrokOSINT v1.4.0

**Advanced Ethical OSINT — Email + Phone + Username (500+ platforms)**

> Public data only · Flask Web UI (Termux friendly) · JSON / Markdown / PDF

---

## ⚠️ Ethical Warning

Only use on accounts/numbers/usernames you **own** or have **explicit authorization**.  
Stalking / doxxing is **illegal**.

---

## Scale

| Module | Platforms (approx) |
|--------|---------------------|
| **Holehe** (email) | ~120 sites |
| **Maigret** (username) | **Top 500** default (up to 3000+) |
| Built-in checks | GitHub, Keybase, Reddit, social links, dorks… |
| **Ignorant** (phone) | WhatsApp / IG / Snapchat (optional) |

Deep email scan = Holehe + Maigret on guessed username → **500–600+ checks**.

---

## Install

```bash
pkg update && pkg upgrade -y   # Termux
pkg install python git
git clone https://github.com/sayan9168/GrokOSINT.git
cd GrokOSINT
pip install -r requirements.txt

# Recommended for large scans:
pip install holehe ignorant maigret
```

---

## Usage

### Web UI
```bash
python web_app.py
```
Open **http://127.0.0.1:5000**

- **Email** — validation, MX, Gravatar, Holehe, Maigret (500 sites on username)
- **Phone** — carrier, apps, public lookups, Ignorant
- **Username** — dedicated **top 500 / 600 / 1000** site scan
- **Full** — email + phone together

### CLI
```bash
python main.py email someone@gmail.com
python main.py phone +8801712345678
```

### Maigret alone (CLI)
```bash
maigret johndoe --top-sites 500
maigret johndoe --top-sites 600
```

---

## Notes

- First Maigret run can take **1–5 minutes** (500 sites).
- Without Maigret installed, username tab still does a small fallback check set.
- Use ethically. MIT License.

**Built by [Sayan the researcher](https://github.com/sayan9168)**
