# 🛡️ GrokOSINT v1.3.0

**Advanced Ethical OSINT Tool for Email + Phone Number Intelligence**

> Public data only • CLI + **Flask Web UI** (Termux friendly) • JSON / Markdown / PDF reports

---

## ⚠️ Ethical Warning

Only use on accounts/numbers you own or have **explicit authorization**.  
Stalking / doxxing is **illegal**.

---

## ✨ Features (v1.3)

### Email OSINT
- Validation, disposable detection, Gmail detection
- MX / A / NS / SPF records
- Gravatar profile + avatar
- Username guessing + multi-platform username checks
- Account existence: GitHub, Keybase, About.me, GitLab, Reddit + more
- Holehe integration (120+ platforms) when installed
- Public paste search (psbdmp)
- Google / DuckDuckGo / Bing dorks
- HIBP support (optional API key)
- Rich social & search quick links

### Phone OSINT
- libphonenumber validation (E.164, carrier, line type, timezone)
- Possible apps heuristic (WhatsApp, Telegram, Signal, country-specific)
- Ignorant integration (WhatsApp / IG / Snapchat) when installed
- Public lookup links (Truecaller, NumLookup, WhitePages, etc.)
- Social search links + Google dorks

### Output
- Beautiful Flask Web UI (English)
- CLI with Rich
- Auto JSON + Markdown + PDF reports

---

## Install (Termux recommended)

```bash
pkg update && pkg upgrade -y
pkg install python git
git clone https://github.com/sayan9168/GrokOSINT.git
cd GrokOSINT
pip install -r requirements.txt

# Optional deep tools
pip install holehe ignorant
```

---

## Usage

### Web UI
```bash
python web_app.py
```
Open: **http://127.0.0.1:5000**

### CLI
```bash
python main.py email someone@gmail.com
python main.py phone +8801712345678
python main.py full -e someone@gmail.com -p +8801712345678
```

---

## License

MIT — Use ethically.

**Built by [Sayan the researcher](https://github.com/sayan9168)**
