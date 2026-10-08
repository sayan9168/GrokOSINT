#!/usr/bin/env python3
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
API = f"https://api.telegram.org/bot{TOKEN}"

def send(chat_id, text):
    requests.post(f"{API}/sendMessage", json={"chat_id": chat_id, "text": text[:4000]})

def handle_scan(seed):
    from grok_osint.modules.fullspectrum import FullSpectrum
    r = FullSpectrum(deep=False, top_sites=100).run(seed.strip())
    lines = [f"Seed: {r.seed} ({r.seed_type})", f"Modules: {', '.join(r.modules_run)}", f"Stats: {r.stats}"]
    un = (r.findings or {}).get("username") or {}
    if un.get("found"):
        lines.append(f"Accounts: {un.get('found')}")
        for a in (un.get("accounts") or [])[:10]:
            lines.append(f"  - {a.get('site')}: {a.get('url')}")
    return "\n".join(lines)

def main():
    if not TOKEN:
        print("export TELEGRAM_BOT_TOKEN=..."); return
    offset = 0
    print("Bot running")
    while True:
        try:
            r = requests.get(f"{API}/getUpdates", params={"offset": offset, "timeout": 30}, timeout=35)
            for upd in r.json().get("result") or []:
                offset = upd["update_id"] + 1
                msg = upd.get("message") or {}
                chat_id = (msg.get("chat") or {}).get("id")
                text = (msg.get("text") or "").strip()
                if not chat_id or not text: continue
                if text.startswith("/start"): send(chat_id, "/scan <target>\n/health")
                elif text.startswith("/health"): send(chat_id, "OK")
                elif text.startswith("/scan"):
                    parts = text.split(maxsplit=1)
                    if len(parts) < 2: send(chat_id, "Usage: /scan target")
                    else:
                        send(chat_id, "Scanning...")
                        try: send(chat_id, handle_scan(parts[1]))
                        except Exception as e: send(chat_id, str(e))
        except KeyboardInterrupt: break
        except Exception as e: print(e)

if __name__ == "__main__":
    main()
