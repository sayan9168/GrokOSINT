#!/usr/bin/env python3
"""GrokOSINT / OSINT Evolution — Flask UI (CI-safe)."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from flask import Flask, render_template, request, jsonify

sys.path.insert(0, str(Path(__file__).parent))

from grok_osint import __version__

app = Flask(__name__)
app.secret_key = "grokosint-ethical-use-only"


def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


@app.route("/api/health")
@app.route("/api/healthz")
def api_health():
    import importlib
    core, optional = {}, {}
    for name in ("flask", "httpx", "yaml", "dns"):
        try:
            importlib.import_module("dns.resolver" if name == "dns" else name)
            core[name] = True
        except Exception:
            core[name] = False
    for name in ("holehe", "maigret", "ignorant"):
        try:
            importlib.import_module(name)
            optional[name] = True
        except Exception:
            optional[name] = False
    return jsonify(ok=True, version=__version__, codename="Evolution", core=core, optional=optional)


@app.route("/")
def index():
    try:
        return render_template("index.html", version=__version__)
    except Exception:
        return jsonify(ok=True, app="OSINT Evolution", version=__version__, ui="template missing")


@app.route("/api/email", methods=["POST"])
def api_email():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip()
    if not email or "@" not in email:
        return jsonify(ok=False, error="Valid email required"), 400
    try:
        from grok_osint.modules.email_osint import EmailOSINT
        result = run_async(EmailOSINT(deep=bool(data.get("deep", True))).run_async(email))
        return jsonify(
            ok=True,
            email=result.email,
            validation={
                "is_valid": result.validation.is_valid,
                "is_gmail": result.validation.is_gmail,
                "domain": result.validation.domain,
            },
            has_mx=result.has_mx,
            mx_records=result.mx_records,
            notes=result.notes,
            holehe_results=getattr(result, "holehe_results", []),
        )
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500


@app.route("/api/phone", methods=["POST"])
def api_phone():
    data = request.get_json() or {}
    phone = (data.get("phone") or "").strip()
    if not phone:
        return jsonify(ok=False, error="Phone required"), 400
    try:
        from grok_osint.modules.phone_osint import PhoneOSINT
        region = data.get("region") or "BD"
        result = run_async(PhoneOSINT(default_region=region).run_async(phone, region=region))
        v = result.validation
        return jsonify(ok=True, e164=v.e164, country=v.country_name, carrier=v.carrier_name, notes=result.notes)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500


@app.route("/api/pipeline", methods=["POST"])
def api_pipeline():
    data = request.get_json() or {}
    seed = (data.get("seed") or data.get("target") or "").strip()
    if not seed:
        return jsonify(ok=False, error="seed required"), 400
    try:
        from grok_osint.modules.pipeline import OSINTPipeline
        r = OSINTPipeline(deep=bool(data.get("deep", False)), top_sites=int(data.get("top_sites") or 100)).run(seed)
        return jsonify(ok=True, seed=r.seed, seed_type=r.seed_type, steps=r.steps, summary=r.summary, notes=r.notes)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500


@app.route("/api/playbooks")
def api_playbooks():
    try:
        from grok_osint.modules.playbooks import get_playbooks
        return jsonify(ok=True, playbooks=get_playbooks(), version=__version__)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500


@app.route("/api/demo")
def api_demo():
    return jsonify(ok=True, targets={"email": "example@example.com", "domain": "example.com", "ip": "1.1.1.1", "username": "github"})


if __name__ == "__main__":
    print(f"OSINT Evolution v{__version__} \u2192 http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
