"""Report generation - JSON, Markdown, PDF"""

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
            "version": "1.2.0",
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
                "holehe_results": getattr(email_result, "holehe_results", []),
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
                "ignorant_results": getattr(phone_result, "ignorant_results", []),
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

    def save_pdf(self, data: dict, prefix: str = "report") -> Optional[Path]:
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import mm
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_CENTER
        except ImportError:
            console.print("[yellow]⚠ reportlab not installed — skipping PDF. Run: pip install reportlab[/yellow]")
            return None

        path = self.export_dir / f"{prefix}_{timestamp()}.pdf"
        doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=15*mm, bottomMargin=15*mm)
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="MainTitle", fontSize=18, leading=22, alignment=TA_CENTER, spaceAfter=8, textColor=colors.HexColor("#4a3f8c")))
        styles.add(ParagraphStyle(name="Section", fontSize=13, leading=16, spaceBefore=12, spaceAfter=6, textColor=colors.HexColor("#333399")))
        styles.add(ParagraphStyle(name="Body", fontSize=9, leading=12, spaceAfter=3))
        styles.add(ParagraphStyle(name="Small", fontSize=8, leading=10, textColor=colors.gray))
        styles.add(ParagraphStyle(name="Warn", fontSize=8, leading=10, textColor=colors.red, spaceAfter=8))

        story = []
        story.append(Paragraph("GrokOSINT Report", styles["MainTitle"]))
        story.append(Paragraph(f"Generated: {data.get('generated_at', '')}", styles["Small"]))
        story.append(Paragraph("⚠️ Public data only. Authorized ethical use required.", styles["Warn"]))
        story.append(Spacer(1, 6))

        if "email" in data:
            e = data["email"]
            story.append(Paragraph("📧 Email Intelligence", styles["Section"]))
            rows = [
                ["Input", e.get("input", "")],
                ["Valid", str(e.get("validation", {}).get("is_valid"))],
                ["Domain", e.get("validation", {}).get("domain", "")],
                ["Gmail", str(e.get("validation", {}).get("is_gmail"))],
                ["Disposable", str(e.get("validation", {}).get("is_disposable"))],
                ["Has MX", str(e.get("has_mx"))],
            ]
            t = Table(rows, colWidths=[40*mm, 120*mm])
            t.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f0f8")),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(t)
            story.append(Spacer(1, 6))
            if e.get("username_guesses"):
                story.append(Paragraph(f"<b>Username Guesses:</b> {', '.join(e['username_guesses'])}", styles["Body"]))
            if e.get("account_checks"):
                found = [a["name"] for a in e["account_checks"] if a.get("found")]
                if found:
                    story.append(Paragraph(f"<b>Accounts Found:</b> {', '.join(found)}", styles["Body"]))
            if e.get("holehe_results"):
                story.append(Paragraph(f"<b>Holehe Platforms:</b> {', '.join(e['holehe_results'][:15])}", styles["Body"]))
            if e.get("notes"):
                for n in e["notes"][:6]:
                    story.append(Paragraph(f"• {n}", styles["Body"]))

        if "phone" in data:
            p = data["phone"]
            v = p.get("validation", {})
            story.append(Paragraph("📱 Phone Intelligence", styles["Section"]))
            rows = [
                ["Input", p.get("input", "")],
                ["Valid", str(v.get("is_valid"))],
                ["E.164", str(v.get("e164") or "")],
                ["Country", f"{v.get('country_name', '')} (+{v.get('country_code', '')})"],
                ["Region", str(v.get("region") or "")],
                ["Carrier", str(v.get("carrier") or "")],
                ["Type", str(v.get("number_type") or "")],
                ["Timezones", ", ".join(v.get("timezones") or [])],
            ]
            t = Table(rows, colWidths=[40*mm, 120*mm])
            t.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f0f8")),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(t)
            story.append(Spacer(1, 6))
            if p.get("possible_apps"):
                story.append(Paragraph(f"<b>Possible Apps:</b> {', '.join(p['possible_apps'])}", styles["Body"]))
            if p.get("ignorant_results"):
                story.append(Paragraph(f"<b>Ignorant:</b> {', '.join(p['ignorant_results'])}", styles["Body"]))
            if p.get("notes"):
                for n in p["notes"][:6]:
                    story.append(Paragraph(f"• {n}", styles["Body"]))

        story.append(Spacer(1, 12))
        story.append(Paragraph("Generated by GrokOSINT — https://github.com/sayan9168/GrokOSINT", styles["Small"]))
        doc.build(story)
        console.print(f"[green]✓ PDF saved → {path}[/green]")
        return path

    def _render_markdown(self, data: dict) -> str:
        lines = ["# GrokOSINT Report", f"**Generated:** {data.get('generated_at')}", "", "> ⚠️ Public data only. Ethical & authorized use required.", ""]
        if "email" in data:
            e = data["email"]
            lines.extend(["## 📧 Email Intelligence", f"- **Input:** `{e['input']}`", f"- **Valid:** {e['validation']['is_valid']}", f"- **Domain:** {e['validation']['domain']}", f"- **Gmail:** {e['validation']['is_gmail']}", f"- **Disposable:** {e['validation']['is_disposable']}", f"- **Has MX:** {e['has_mx']}", ""])
            if e.get("username_guesses"):
                lines.append(f"- **Username Guesses:** {', '.join(e['username_guesses'])}")
            if e.get("holehe_results"):
                lines.append("\n### Holehe Platforms")
                for h in e["holehe_results"]:
                    lines.append(f"- {h}")
            if e.get("notes"):
                lines.append("\n### Notes")
                for n in e["notes"]:
                    lines.append(f"- {n}")
        if "phone" in data:
            p = data["phone"]
            v = p["validation"]
            lines.extend(["", "## 📱 Phone Intelligence", f"- **Input:** `{p['input']}`", f"- **Valid:** {v['is_valid']}", f"- **E.164:** `{v.get('e164')}`", f"- **Country:** {v.get('country_name')} (+{v.get('country_code')})", f"- **Carrier:** {v.get('carrier')}", f"- **Type:** {v.get('number_type')}", ""])
            if p.get("possible_apps"):
                lines.append(f"- **Possible Apps:** {', '.join(p['possible_apps'])}")
            if p.get("ignorant_results"):
                lines.append(f"- **Ignorant:** {', '.join(p['ignorant_results'])}")
            if p.get("notes"):
                lines.append("\n### Notes")
                for n in p["notes"]:
                    lines.append(f"- {n}")
        lines.extend(["", "---", "*Generated by [GrokOSINT](https://github.com/sayan9168/GrokOSINT)*"])
        return "\n".join(lines)

    def export_all(self, email_result=None, phone_result=None, prefix: str = "grokosint", pdf: bool = True):
        data = self.to_dict(email_result, phone_result)
        self.save_json(data, prefix)
        self.save_markdown(data, prefix)
        if pdf:
            self.save_pdf(data, prefix)
        return data
