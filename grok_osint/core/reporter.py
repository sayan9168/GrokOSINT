"""Report generation - JSON, Markdown"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from rich.console import Console

from .utils import ensure_dir, timestamp

console = Console()


class Reporter:
    def __init__(self, export_dir: str = "reports"):
        self.export_dir = ensure_dir(export_dir)

    def to_dict(self, email_result: Any = None, phone_result: Any = None) -> dict:
        data = {
            "tool": "GrokOSINT",
            "version": "1.1.0",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "disclaimer": "Public data only. Authorized ethical use required.",
        }
        if email_result:
            data["email"] = {
                "input": email_result.email,
                "validation": {
                    "is_valid": email_result.validation.is_valid,
                    "local_part": email_result.validation.local_part,
                    "domain": email_result.validation.domain,
                    "is_gmail": email_result.validation.is_gmail,
                    "is_disposable": email_result.validation.is_disposable,
                },
                "mx_records": email_result.mx_records,
                "has_mx": email_result.has_mx,
                "gravatar": email_result.gravatar,
                "account_checks": getattr(email_result, "account_checks", []),
                "paste_hits": getattr(email_result, "paste_hits", []),
                "username_guesses": getattr(email_result, "username_guesses", []),
                "social_profiles": email_result.social_profiles,
                "dorks": email_result.dorks,
                "breach_hints": email_result.breach_hints,
                "notes": email_result.notes,
            }
        if phone_result:
            data["phone"] = {
                "input": phone_result.original,
                "validation": {
                    "is_valid": phone_result.validation.is_valid,
                    "is_possible": phone_result.validation.is_possible,
                    "e164": phone_result.validation.e164,
                    "national": phone_result.validation.national,
                    "international": phone_result.validation.international,
                    "country_code": phone_result.validation.country_code,
                    "country_name": phone_result.validation.country_name,
                    "region": phone_result.validation.region,
                    "carrier": phone_result.validation.carrier_name,
                    "number_type": phone_result.validation.number_type,
                    "timezones": phone_result.validation.timezones,
                },
                "formats": phone_result.formats,
                "dorks": phone_result.dorks,
                "social_links": phone_result.social_links,
                "possible_apps": getattr(phone_result, "possible_apps", []),
                "notes": phone_result.notes,
            }
        return data

    def save_json(self, data: dict, prefix: str = "report") -> Path:
        path = self.export_dir / f"{prefix}_{timestamp()}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        console.print(f"[green]✓ JSON saved → {path}[/green]")
        return path

    def save_markdown(self, data: dict, prefix: str = "report") -> Path:
        path = self.export_dir / f"{prefix}_{timestamp()}.md"
        md = self._render_markdown(data)
        with open(path, "w", encoding="utf-8") as f:
            f.write(md)
        console.print(f"[green]✓ Markdown saved → {path}[/green]")
        return path

    def _render_markdown(self, data: dict) -> str:
        lines = [
            "# GrokOSINT Report",
            f"**Generated:** {data.get('generated_at')}",
            "",
            "> ⚠️ Public data only. Ethical & authorized use required.",
            "",
        ]

        if "email" in data:
            e = data["email"]
            lines.extend([
                "## 📧 Email Intelligence",
                f"- **Input:** `{e['input']}`",
                f"- **Valid:** {e['validation']['is_valid']}",
                f"- **Domain:** {e['validation']['domain']}",
                f"- **Gmail:** {e['validation']['is_gmail']}",
                f"- **Disposable:** {e['validation']['is_disposable']}",
                f"- **Has MX:** {e['has_mx']}",
                "",
            ])
            if e.get("username_guesses"):
                lines.append(f"- **Username Guesses:** {', '.join(e['username_guesses'])}")
            if e.get("account_checks"):
                lines.append("\n### Account Checks")
                for a in e["account_checks"]:
                    status = "FOUND" if a.get("found") else "not found"
                    lines.append(f"- {a['name']}: {status}")
            if e.get("paste_hits"):
                lines.append("\n### Public Pastes")
                for p in e["paste_hits"]:
                    lines.append(f"- {p.get('source')} | {p.get('url')}")
            if e.get("social_profiles"):
                lines.append("\n### Quick Links")
                for s in e["social_profiles"]:
                    lines.append(f"- [{s['platform']}]({s['url']})")
            if e.get("notes"):
                lines.append("\n### Notes")
                for n in e["notes"]:
                    lines.append(f"- {n}")

        if "phone" in data:
            p = data["phone"]
            v = p["validation"]
            lines.extend([
                "",
                "## 📱 Phone Intelligence",
                f"- **Input:** `{p['input']}`",
                f"- **Valid:** {v['is_valid']}",
                f"- **E.164:** `{v.get('e164')}`",
                f"- **Country:** {v.get('country_name')} (+{v.get('country_code')})",
                f"- **Region:** {v.get('region')}",
                f"- **Carrier:** {v.get('carrier')}",
                f"- **Type:** {v.get('number_type')}",
                f"- **Timezones:** {', '.join(v.get('timezones') or [])}",
                "",
            ])
            if p.get("possible_apps"):
                lines.append(f"- **Possible Apps:** {', '.join(p['possible_apps'])}")
            if p.get("social_links"):
                lines.append("### Quick Links")
                for s in p["social_links"]:
                    lines.append(f"- [{s['name']}]({s['url']})")
            if p.get("notes"):
                lines.append("\n### Notes")
                for n in p["notes"]:
                    lines.append(f"- {n}")

        lines.extend([
            "",
            "---",
            "*Generated by [GrokOSINT](https://github.com/sayan9168/GrokOSINT)*",
        ])
        return "\n".join(lines)

    def export_all(self, email_result=None, phone_result=None, prefix: str = "grokosint"):
        data = self.to_dict(email_result, phone_result)
        self.save_json(data, prefix)
        self.save_markdown(data, prefix)
        return data
