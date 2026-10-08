# 🛡️ GrokOSINT

### Advanced Ethical OSINT Platform for Email, Phone, Username & IP Intelligence

**Public-source only · Case management · Correlation graphs · CLI + Web + Streamlit**

[![CI](https://github.com/sayan9168/GrokOSINT/actions/workflows/ci.yml/badge.svg)](https://github.com/sayan9168/GrokOSINT/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Ethical](https://img.shields.io/badge/Focus-Authorized%20Research%20Only-0B7285)](#disclaimer)

> Local-first OSINT toolkit designed for **authorized research**, security analysts, and ethical investigators.  
> No private account access. No credential harvesting. Pure public data.

---

## 💡 Why GrokOSINT?

Most OSINT tools are either too basic (single-purpose scripts) or too heavy (Maltego-style desktops).  
GrokOSINT sits in the middle:

| Generation | Style | Limitation |
|------------|-------|------------|
| 1.0 | Manual tabs / browser | Slow & unstructured |
| 2.0 | CLI scripts (holehe, maigret…) | Fragmented, no cases |
| 3.0 | Heavy GUI (Maltego, SpiderFoot) | Resource heavy, steep learning |
| **4.0 — GrokOSINT** | **Cases + Graph + CLI + Web + CI** | **Fast, modular, reproducible** |

---

## ✨ Features

### Intelligence Modules
- **Email OSINT** — breach checks, account existence (via holehe/maigret integration), DNS, MX, social profiles
- **Phone OSINT** — carrier, country, type, possible social links (phonenumbers + enrichment)
- **Username OSINT** — multi-platform presence scanning
- **IP OSINT** — geolocation, ASN, reverse DNS, open ports context
- **Archive OSINT** — historical web snapshots & related data
- **Full-spectrum pipeline** — chain multiple modules into one investigation

### Investigation Workspace
- **Cases** — persistent investigation containers with notes & metadata
- **Correlation / Graph** — link entities across email, phone, username, IP
- **Timeline** — chronological view of findings
- **Compare** — side-by-side target analysis
- **Playbooks** — reusable investigation recipes
- **Batch mode** — process many targets at once
- **Export suite** — Markdown, HTML, PDF, JSON reports

### Interfaces
- **CLI** (`grokosint`) — rich terminal experience with Typer + Rich
- **Web App** (Flask) — clean browser UI
- **Streamlit App** — interactive dashboard
- **Docker** ready + `docker-compose`

### Engineering
- Plugin system
- Progress tracking
- Configurable rate limits / proxies / OPSEC mode
- CI/CD with GitHub Actions (tests + Docker + releases)
- Type-safe (Pydantic)

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/sayan9168/GrokOSINT.git
cd GrokOSINT

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Recommended extra scanners
pip install holehe maigret ignorant
```

### 2. Configuration

```bash
cp config.example.yaml config.yaml
# Edit config.yaml — add optional API keys (HIBP, Shodan) if you have them
```

### 3. Run

**CLI**
```bash
# After pip install -e .
grokosint --help

# Or directly
python -m grok_osint.cli --help
```

**Web UI**
```bash
python web_app.py
# Open http://127.0.0.1:5000
```

**Streamlit Dashboard**
```bash
streamlit run streamlit_app.py
```

**Docker**
```bash
docker compose up --build
```

---

## 📂 Project Structure

```text
GrokOSINT/
├── grok_osint/
│   ├── cli.py                 # Typer CLI entrypoint
│   ├── core/                 # Reporter, validator, utils
│   └── modules/              # Intelligence modules
│       ├── email_osint.py
│       ├── phone_osint.py
│       ├── username_osint.py
│       ├── ip_osint.py
│       ├── cases.py
│       ├── correlator.py
│       ├── graph.py
│       ├── pipeline.py
│       └── …
├── web_app.py               # Flask web interface
├── streamlit_app.py         # Streamlit dashboard
├── templates/               # Web UI templates
├── plugins/                 # Extensible plugins
├── scripts/                 # Kali setup, Telegram bot helper
├── tests/
├── Dockerfile + docker-compose.yml
└── config.example.yaml
```

---

## 📝 Example Workflow

```bash
# Create a new case
grokosint case create "Investigation-Alpha"

# Run email intelligence
grokosint email target@example.com --case Investigation-Alpha

# Run phone intelligence
grokosint phone +919876543210 --case Investigation-Alpha

# Correlate everything in the case
grokosint correlate --case Investigation-Alpha

# Export full report
grokosint export --case Investigation-Alpha --format pdf
```

---

## 🔒 Disclaimer

GrokOSINT is built **strictly for authorized, ethical, and legal use**.

- Only public data sources are used
- No private account access, no credential stuffing, no exploitation
- Users are solely responsible for complying with local laws and platform ToS
- The author assumes no liability for misuse

**Authorized research only.**

---

## 👥 Contributing

Pull requests are welcome. For major changes, please open an issue first.

```bash
pip install -e ".[dev]"
pytest
```

---

## 📄 License

MIT License © [Sayan Mahata](https://github.com/sayan9168) (Sayan the researcher)

---

<div align="center">

**Built with ⚙️ by [Sayan the researcher](https://github.com/sayan9168)**  
[Portfolio](https://sayan9168.github.io) · [Sayanox](https://github.com/sayan9168/sayanox)

</div>
