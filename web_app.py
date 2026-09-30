#!/usr/bin/env python3
"""
GrokOSINT Flask Web UI (Termux friendly - no Streamlit/numpy required)
Run: python web_app.py
Then open: http://127.0.0.1:5000
"""

import asyncio
import sys
from pathlib import Path

from flask import Flask, render_template, request, jsonify

sys.path.insert(0, str(Path(__file__).parent))

from grok_osint import __version__
from grok_osint.modules.email_osint import EmailOSINT
from grok_osint.modules.phone_osint import PhoneOSINT
from grok_osint.core.reporter import Reporter

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


@app.route("/")
def index():
    return render_template("index.html", version=__version__)


@app.route("/api/email", methods=["POST"])
def api_email():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip()
    deep = bool(data.get("deep", True))

    if not email or "@" not in email:
        return jsonify({"ok": False, "error": "Valid email required"}), 400

    try:
        osint = EmailOSINT(deep=deep)
        result = run_async(osint.run_async(email))

        out = {
            "ok": True,
            "email": result.email,
            "validation": {
                "is_valid": result.validation.is_valid,
                "local_part": result.validation.local_part,
                "domain": result.validation.domain,
                "is_gmail": result.validation.is_gmail,
                "is_disposable": result.validation.is_disposable,
            },
            "has_mx": result.has_mx,
            "mx_records": result.mx_records,
            "gravatar": result.gravatar,
            "username_guesses": getattr(result, "username_guesses", []),
            "account_checks": getattr(result, "account_checks", []),
            "holehe_results": getattr(result, "holehe_results", []),
            "paste_hits": getattr(result, "paste_hits", []),
            "social_profiles": result.social_profiles,
            "dorks": result.dorks,
            "notes": result.notes,
        }

        reporter = Reporter("reports")
        reporter.export_all(email_result=result, prefix="email_web", pdf=True)
        return jsonify(out)
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/phone", methods=["POST"])
def api_phone():
    data = request.get_json() or {}
    phone = (data.get("phone") or "").strip()
    region = data.get("region", "BD")
    deep = bool(data.get("deep", True))

    if not phone:
        return jsonify({"ok": False, "error": "Phone number required"}), 400

    try:
        osint = PhoneOSINT(default_region=region, deep=deep)
        result = run_async(osint.run_async(phone, region=region))

        v = result.validation
        out = {
            "ok": True,
            "original": result.original,
            "validation": {
                "is_valid": v.is_valid,
                "is_possible": v.is_possible,
                "e164": v.e164,
                "national": v.national,
                "international": v.international,
                "country_code": v.country_code,
                "country_name": v.country_name,
                "region": v.region,
                "carrier": v.carrier_name,
                "number_type": v.number_type,
                "timezones": v.timezones,
            },
            "formats": result.formats,
            "possible_apps": getattr(result, "possible_apps", []),
            "ignorant_results": getattr(result, "ignorant_results", []),
            "social_links": result.social_links,
            "dorks": result.dorks,
            "notes": result.notes,
        }

        reporter = Reporter("reports")
        reporter.export_all(phone_result=result, prefix="phone_web", pdf=True)
        return jsonify(out)
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/full", methods=["POST"])
def api_full():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip()
    phone = (data.get("phone") or "").strip()
    region = data.get("region", "BD")
    deep = bool(data.get("deep", True))

    if not email and not phone:
        return jsonify({"ok": False, "error": "Provide at least email or phone"}), 400

    try:
        email_result = None
        phone_result = None
        out = {"ok": True}

        if email and "@" in email:
            eosint = EmailOSINT(deep=deep)
            email_result = run_async(eosint.run_async(email))
            out["email"] = {
                "input": email_result.email,
                "is_valid": email_result.validation.is_valid,
                "is_gmail": email_result.validation.is_gmail,
                "has_mx": email_result.has_mx,
                "username_guesses": getattr(email_result, "username_guesses", []),
                "account_checks": getattr(email_result, "account_checks", []),
                "holehe_results": getattr(email_result, "holehe_results", []),
                "notes": email_result.notes,
            }

        if phone:
            posint = PhoneOSINT(default_region=region, deep=deep)
            phone_result = run_async(posint.run_async(phone, region=region))
            v = phone_result.validation
            out["phone"] = {
                "input": phone_result.original,
                "is_valid": v.is_valid,
                "e164": v.e164,
                "country": v.country_name,
                "carrier": v.carrier_name,
                "type": v.number_type,
                "possible_apps": getattr(phone_result, "possible_apps", []),
                "ignorant_results": getattr(phone_result, "ignorant_results", []),
                "notes": phone_result.notes,
            }

        reporter = Reporter("reports")
        reporter.export_all(email_result=email_result, phone_result=phone_result, prefix="full_web", pdf=True)
        return jsonify(out)
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


if __name__ == "__main__":
    print(f"\n🛡️  GrokOSINT v{__version__} Web UI")
    print("   Open in browser: http://127.0.0.1:5000")
    print("   (On Termux use: http://127.0.0.1:5000 or your phone IP)\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
