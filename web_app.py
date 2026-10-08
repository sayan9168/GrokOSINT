#!/usr/bin/env python3
"""OSINT Evolution — CI-safe Flask app."""
import sys
from pathlib import Path
from flask import Flask, jsonify, request, render_template

sys.path.insert(0, str(Path(__file__).parent))
from grok_osint import __version__

app = Flask(__name__)
app.secret_key = "grokosint"

@app.route("/api/health")
@app.route("/api/healthz")
def health():
    return jsonify(ok=True, version=__version__, codename="Evolution")

@app.route("/")
def index():
    try:
        return render_template("index.html", version=__version__)
    except Exception:
        return jsonify(ok=True, app="OSINT Evolution", version=__version__)

@app.route("/api/demo")
def demo():
    return jsonify(ok=True, targets={"domain": "example.com", "email": "example@example.com"})

if __name__ == "__main__":
    print(f"OSINT Evolution v{__version__} http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000)
