# 🛡️ GrokOSINT v2.0

**All-in-one Ethical OSINT Platform** — compete with the big toolkits using free/public data.

| Module | Capability |
|--------|------------|
| 📧 **Email** | Validation, MX, Gravatar, Holehe (~120), pastes, dorks |
| 📱 **Phone** | Carrier, type, timezone, Ignorant, public lookups |
| 👤 **Username** | **Maigret top 500–1000+ sites** |
| 🌐 **Domain** | DNS (A/AAAA/MX/NS/TXT), SPF/DMARC, subdomains, CT (crt.sh), WHOIS links |
| 🔢 **IP** | Geo, ASN/ISP, rDNS, VT/Shodan/AbuseIPDB links |

> Public data only · Flask Web UI · CLI · JSON / Markdown / PDF reports

---

## ⚠️ Ethics

Use only with authorization. Stalking / doxxing is illegal.  
Not a replacement for Maltego/SpiderFoot enterprise workflows — a fast, free, Termux-friendly suite.

---

## Install

```bash
git clone https://github.com/sayan9168/GrokOSINT.git
cd GrokOSINT
pip install -r requirements.txt

# Optional power-ups
pip install holehe ignorant maigret
```

## Run

```bash
python web_app.py
# → http://127.0.0.1:5000
```

```bash
python main.py email user@gmail.com
python main.py phone +8801XXXXXXXXX
```

---

## vs big OSINT tools

| Need | GrokOSINT | Classic |
|------|-----------|--------|
| Email account map | Holehe | holehe / h8mail |
| Username @ 500 sites | Maigret | Maigret / Sherlock |
| Domain DNS + CT | Built-in | recon-ng / amass |
| IP geo + rep links | Built-in | ipinfo / VT |
| Mobile / Termux | Yes | Often heavy |
| Cost | Free | Often paid |

---

MIT · Built by [Sayan the researcher](https://github.com/sayan9168)
