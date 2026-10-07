"""Username OSINT - Large-scale platform scan via Maigret (500+ sites default)"""

import json
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class UsernameOSINTResult:
    username: str
    found_accounts: list[dict] = field(default_factory=list)
    total_checked: int = 0
    total_found: int = 0
    maigret_available: bool = False
    notes: list[str] = field(default_factory=list)
    raw_output: str = ""


class UsernameOSINT:
    """Scan username across hundreds of platforms via Maigret (default top 500)."""

    def __init__(self, top_sites: int = 500, timeout: int = 300, tags: Optional[str] = None):
        self.top_sites = top_sites
        self.timeout = timeout
        self.tags = tags

    def is_maigret_available(self) -> bool:
        if shutil.which("maigret"):
            return True
        try:
            import maigret  # noqa: F401
            return True
        except ImportError:
            return False

    def run(self, username: str) -> UsernameOSINTResult:
        username = (username or "").strip().lstrip("@")
        result = UsernameOSINTResult(username=username)
        if not username or len(username) < 2:
            result.notes.append("Invalid username")
            return result

        if not self.is_maigret_available():
            result.notes.append(
                "Maigret not installed. Run: pip install maigret  "
                "Then: maigret USERNAME --top-sites 500"
            )
            result.maigret_available = False
            result.found_accounts = self._fallback_checks(username)
            result.total_found = len(result.found_accounts)
            result.total_checked = 12
            return result

        result.maigret_available = True
        result.notes.append(f"Scanning top {self.top_sites} sites via Maigret (1-5 min)...")
        cmd = [
            "maigret", username,
            "--top-sites", str(self.top_sites),
            "--no-progressbar", "--no-color",
            "--timeout", "15", "-n", "8",
        ]
        if self.tags:
            cmd.extend(["--tags", self.tags])

        try:
            proc = subprocess.run(cmd + ["--json", "simple"], capture_output=True, text=True, timeout=self.timeout)
            out = (proc.stdout or "") + "\n" + (proc.stderr or "")
            result.raw_output = out[:8000]
            accounts = self._parse_maigret_output(out, username)
            if accounts:
                result.found_accounts = accounts
                result.total_found = len(accounts)
                result.total_checked = self.top_sites
                result.notes.append(f"Maigret: {result.total_found} found (top {self.top_sites})")
                return result
        except subprocess.TimeoutExpired:
            result.notes.append(f"Timed out after {self.timeout}s")
        except Exception as e:
            result.notes.append(f"Maigret error: {e}")

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout)
            out = (proc.stdout or "") + "\n" + (proc.stderr or "")
            result.raw_output = out[:8000]
            accounts = self._parse_maigret_output(out, username)
            result.found_accounts = accounts
            result.total_found = len(accounts)
            result.total_checked = self.top_sites
            if accounts:
                result.notes.append(f"Found {result.total_found} on top {self.top_sites} sites")
            else:
                result.notes.append("Maigret ran; no accounts parsed")
        except subprocess.TimeoutExpired:
            result.notes.append("Scan timed out. Try --top-sites 200")
        except Exception as e:
            result.notes.append(f"Scan failed: {e}")
        return result

    def _parse_maigret_output(self, text: str, username: str) -> list[dict]:
        found, seen = [], set()
        for line in text.splitlines():
            line = line.strip()
            m = re.match(r"\[(?:\+|!|x)\]\s*([^:]+):\s*(https?://\S+)", line, re.I)
            if m:
                site, url = m.group(1).strip(), m.group(2).strip()
                if site.lower() not in seen:
                    seen.add(site.lower())
                    found.append({"site": site, "url": url, "username": username, "status": "found"})
                continue
            m2 = re.match(r"\[(?:\+|!)\]\s*(.+)$", line)
            if m2 and "http" not in line.lower():
                site = m2.group(1).strip()
                if len(site) < 60 and site.lower() not in seen:
                    seen.add(site.lower())
                    found.append({"site": site, "url": "", "username": username, "status": "found"})
        return found[:200]

    def _fallback_checks(self, username: str) -> list[dict]:
        import httpx
        results = []
        platforms = [
            ("GitHub", f"https://github.com/{username}", f"https://api.github.com/users/{username}"),
            ("GitLab", f"https://gitlab.com/{username}", None),
            ("Reddit", f"https://www.reddit.com/user/{username}", f"https://www.reddit.com/user/{username}/about.json"),
            ("X/Twitter", f"https://x.com/{username}", None),
            ("Instagram", f"https://www.instagram.com/{username}/", None),
            ("TikTok", f"https://www.tiktok.com/@{username}", None),
            ("YouTube", f"https://www.youtube.com/@{username}", None),
            ("Pinterest", f"https://www.pinterest.com/{username}/", None),
            ("Medium", f"https://medium.com/@{username}", None),
            ("Dev.to", f"https://dev.to/{username}", None),
            ("Keybase", f"https://keybase.io/{username}", None),
            ("About.me", f"https://about.me/{username}", None),
        ]
        try:
            with httpx.Client(timeout=8.0, follow_redirects=True, headers={"User-Agent": "GrokOSINT/1.4"}) as client:
                for name, url, api in platforms:
                    try:
                        r = client.get(api or url)
                        ok = r.status_code == 200
                        if api and name == "GitHub":
                            ok = r.status_code == 200 and "login" in r.text
                        if api and name == "Reddit":
                            ok = r.status_code == 200 and "name" in r.text
                        if ok:
                            results.append({"site": name, "url": url, "username": username, "status": "found"})
                    except Exception:
                        continue
        except Exception:
            pass
        return results
