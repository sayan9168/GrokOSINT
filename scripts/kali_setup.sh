#!/usr/bin/env bash
set -e
echo "[*] GrokOSINT Kali/Debian setup"
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git whois nmap exiftool dnsutils
cd "$(dirname "$0")/.."
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
pip install holehe maigret ignorant theHarvester 2>/dev/null || true
echo "[+] Run: source .venv/bin/activate && python web_app.py"
