"""Phone Number OSINT Module - Advanced Public Intelligence (Ethical Only)"""

import asyncio
from dataclasses import dataclass, field
from typing import Any, Optional
from urllib.parse import quote

import httpx
from rich.console import Console
from rich.table import Table

from ..core.utils import print_info, print_success, print_warning
from ..core.validator import PhoneValidator, PhoneValidationResult

console = Console()


@dataclass
class PhoneOSINTResult:
    original: str
    validation: PhoneValidationResult
    formats: dict[str, str] = field(default_factory=dict)
    dorks: list[dict] = field(default_factory=list)
    social_links: list[dict] = field(default_factory=list)
    possible_apps: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    raw: dict = field(default_factory=dict)


class PhoneOSINT:
    """Advanced Ethical Phone OSINT using phonenumbers + public sources."""

    def __init__(self, default_region: str = "BD", timeout: float = 12.0, api_keys: Optional[dict] = None):
        self.default_region = default_region
        self.timeout = timeout
        self.api_keys = api_keys or {}
        self.validator = PhoneValidator(default_region=default_region)
        self.headers = {
            "User-Agent": "GrokOSINT/1.1 (Ethical Research; +https://github.com/sayan9168/GrokOSINT)"
        }

    def run(self, phone: str, region: Optional[str] = None) -> PhoneOSINTResult:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(self.run_async(phone, region))

    async def run_async(self, phone: str, region: Optional[str] = None) -> PhoneOSINTResult:
        validation = self.validator.validate(phone, region=region)
        result = PhoneOSINTResult(original=phone, validation=validation)

        if not validation.is_valid and not validation.is_possible:
            result.notes.append(f"Invalid / impossible number: {validation.reason}")
            return result

        print_info(f"Analyzing phone: {validation.e164 or phone}")

        result.formats = {
            "E.164": validation.e164 or "",
            "National": validation.national or "",
            "International": validation.international or "",
            "Digits only": "".join(c for c in (validation.national or "") if c.isdigit()),
        }

        result.dorks = self._generate_dorks(validation)
        result.social_links = self._generate_social_links(validation)
        result.possible_apps = self._guess_possible_apps(validation)

        if self.api_keys.get("numverify") and validation.e164:
            try:
                extra = await self._numverify_lookup(validation.e164)
                result.raw["numverify"] = extra
                if extra.get("carrier"):
                    result.notes.append(f"NumVerify Carrier: {extra.get('carrier')} | Line: {extra.get('line_type')}")
            except Exception as e:
                result.notes.append(f"NumVerify failed: {e}")

        if validation.carrier_name:
            result.notes.append(f"Carrier (libphonenumber): {validation.carrier_name}")
        if validation.number_type:
            result.notes.append(f"Line Type: {validation.number_type}")
        if validation.timezones:
            result.notes.append(f"Timezones: {', '.join(validation.timezones)}")
        if validation.country_code == 880:
            result.notes.append("Bangladesh number detected — common operators: Grameenphone, Robi, Banglalink, Teletalk")
        elif validation.country_code == 91:
            result.notes.append("India number detected — common operators: Jio, Airtel, Vi, BSNL")

        result.notes.append("For deeper social presence (WhatsApp/IG/Snap): try 'ignorant' tool with authorization")
        result.notes.append("Truecaller / GetContact may show names but require their apps and share your data")

        return result

    def _guess_possible_apps(self, v: PhoneValidationResult) -> list[str]:
        apps = []
        if v.number_type in ("Mobile", "Fixed or Mobile"):
            apps.extend(["WhatsApp", "Telegram", "Signal", "Viber", "Imo", "Messenger"])
            if v.country_code in (880, 91, 92, 94):
                apps.extend(["Imo", "bKash/Nagad (if BD)"])
        if v.number_type == "VoIP":
            apps.append("Possible VoIP / virtual number")
        return apps

    def _generate_dorks(self, v: PhoneValidationResult) -> list[dict]:
        if not v.e164:
            return []
        e164 = v.e164
        national = v.national or ""
        clean_nat = "".join(c for c in national if c.isdigit())
        return [
            {"name": "Exact E.164", "query": f'"{e164}"'},
            {"name": "Without +", "query": f'"{e164.lstrip("+")}"'},
            {"name": "National format", "query": f'"{national}"'},
            {"name": "Digits only", "query": f'"{clean_nat}"'},
            {"name": "Paste sites", "query": f'site:pastebin.com OR site:ghostbin.com OR site:rentry.co "{e164}" OR "{clean_nat}"'},
            {"name": "Documents", "query": f'"{e164}" OR "{clean_nat}" (filetype:pdf OR filetype:xls OR filetype:xlsx)'},
            {"name": "Social + number", "query": f'"{clean_nat}" (whatsapp OR telegram OR truecaller OR getcontact)'},
        ]

    def _generate_social_links(self, v: PhoneValidationResult) -> list[dict]:
        if not v.e164:
            return []
        e164 = v.e164
        national_digits = "".join(c for c in (v.national or "") if c.isdigit())
        cc = v.country_code or ""
        return [
            {"name": "Google", "url": f"https://www.google.com/search?q=%22{quote(e164)}%22"},
            {"name": "DuckDuckGo", "url": f"https://duckduckgo.com/?q=%22{quote(e164)}%22"},
            {"name": "Truecaller Web", "url": f"https://www.truecaller.com/search/{cc}/{national_digits}"},
            {"name": "Facebook", "url": f"https://www.facebook.com/search/top?q={quote(e164)}"},
            {"name": "LinkedIn", "url": f"https://www.linkedin.com/search/results/all/?keywords={quote(e164)}"},
            {"name": "WhatsApp Click-to-chat", "url": f"https://wa.me/{e164.lstrip('+')}"},
            {"name": "Sync.me", "url": f"https://sync.me/search/?number={quote(e164)}"},
        ]

    async def _numverify_lookup(self, e164: str) -> dict:
        key = self.api_keys.get("numverify")
        if not key:
            return {}
        number = e164.lstrip("+")
        url = f"http://apilayer.net/api/validate?access_key={key}&number={number}&format=1"
        async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
            r = await client.get(url)
            if r.status_code == 200:
                return r.json()
            return {"error": r.status_code}

    def display(self, result: PhoneOSINTResult):
        v = result.validation
        table = Table(title=f"📱 Phone OSINT → {result.original}", show_header=True, header_style="bold magenta")
        table.add_column("Field", style="cyan", width=18)
        table.add_column("Value", style="white")

        table.add_row("Valid", "✓ Yes" if v.is_valid else ("Possible" if v.is_possible else "✗ No"))
        table.add_row("E.164", v.e164 or "-")
        table.add_row("National", v.national or "-")
        table.add_row("International", v.international or "-")
        table.add_row("Country Code", f"+{v.country_code}" if v.country_code else "-")
        table.add_row("Country", v.country_name or "-")
        table.add_row("Region", v.region or "-")
        table.add_row("Carrier", v.carrier_name or "Unknown (libphonenumber)")
        table.add_row("Line Type", v.number_type or "-")
        table.add_row("Timezones", ", ".join(v.timezones) if v.timezones else "-")

        console.print(table)

        if result.possible_apps:
            console.print("\n[bold]📲 Possible Linked Apps (heuristic):[/bold]")
            console.print("  " + ", ".join(result.possible_apps))

        if result.social_links:
            console.print("\n[bold]🔗 Quick Lookup Links:[/bold]")
            for s in result.social_links:
                console.print(f"  • {s['name']}: {s['url']}")

        if result.dorks:
            console.print("\n[bold]🔍 Google Dorks (copy-paste):[/bold]")
            for d in result.dorks:
                console.print(f"  • {d['name']}: [dim]{d['query']}[/dim]")

        if result.notes:
            console.print("\n[bold yellow]Notes:[/bold yellow]")
            for n in result.notes:
                console.print(f"  • {n}")
