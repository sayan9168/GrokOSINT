"""HIBP + Shodan enrichment from config.yaml keys."""
from pathlib import Path
import httpx, yaml

def load_api_keys():
    for p in (Path("config.yaml"), Path.home() / ".config" / "grokosint" / "config.yaml"):
        if p.exists():
            try:
                return (yaml.safe_load(p.read_text(encoding="utf-8")) or {}).get("api_keys") or {}
            except Exception:
                pass
    return {}

async def hibp_breaches(email, api_key=""):
    key = api_key or load_api_keys().get("hibp") or ""
    if not key:
        return {"ok": False, "error": "No HIBP API key", "breaches": []}
    try:
        async with httpx.AsyncClient(timeout=20.0, headers={"hibp-api-key": key, "user-agent": "GrokOSINT"}) as client:
            r = await client.get(f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}?truncateResponse=false")
            if r.status_code == 404: return {"ok": True, "breaches": [], "count": 0}
            if r.status_code != 200: return {"ok": False, "error": f"HTTP {r.status_code}", "breaches": []}
            data = r.json()
            return {"ok": True, "breaches": data, "count": len(data)}
    except Exception as e:
        return {"ok": False, "error": str(e), "breaches": []}

async def shodan_host(ip, api_key=""):
    key = api_key or load_api_keys().get("shodan") or ""
    if not key:
        return {"ok": False, "error": "No Shodan API key", "data": {}}
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.get(f"https://api.shodan.io/shodan/host/{ip}?key={key}")
            if r.status_code != 200: return {"ok": False, "error": f"HTTP {r.status_code}", "data": {}}
            return {"ok": True, "data": r.json()}
    except Exception as e:
        return {"ok": False, "error": str(e), "data": {}}

def run_hibp_sync(email):
    import asyncio
    try: loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
    return loop.run_until_complete(hibp_breaches(email))

def run_shodan_sync(ip):
    import asyncio
    try: loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
    return loop.run_until_complete(shodan_host(ip))
