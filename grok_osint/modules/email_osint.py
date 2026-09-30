"""Email OSINT Module - Advanced Public Intelligence (Ethical Only)"""

import asyncio
import re
from dataclasses import dataclass, field
from typing import Any, Optional
from urllib.parse import quote

import dns.resolver
import httpx
from rich.console import Console
from rich.table import Table

from ..core.utils import md5_hash, print_info, print_success, print_warning
from ..core.validator import EmailValidator, EmailValidationResult

console = Console()


@dataclass
class EmailOSINTResult:
    email: str
    validation: EmailValidationResult
    mx_records: list[str] = field(default_factory=list)
    has_mx: bool = False
    gravatar: dict[str, Any] = field(default_factory=dict)
    account_checks: list[dict] = field(default_factory=list)
    paste_hits: list[dict] = field(default_factory=list)
    username_guesses: list[str] = field(default_factory=list)
    social_profiles: list[dict] = field(default_factory=list)
    dorks: list[dict] = field(default_factory=list)
    breach_hints: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    raw: dict = field(default_factory=dict)


class EmailOSINT:
    """Advanced Ethical Email OSINT using only public sources."""

    def __init__(self, timeout: float = 12.0, api_keys: Optional[dict] = None, deep: bool = True):
        self.timeout = timeout
        self.api_keys = api_keys or {}
        self.deep = deep
        self.validator = EmailValidator()
        self.headers = {
            "User-Agent": "GrokOSINT/1.1 (Ethical Research; +https://github.com/sayan9168/GrokOSINT)",
            "Accept": "application/json, text/plain, */*",
        }

    def run(self, email: str) -> EmailOSINTResult:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(self.run_async(email))

    async def run_async(self, email: str) -> EmailOSINTResult:
        validation = self.validator.validate(email)
        result = EmailOSINTResult(email=email, validation=validation)

        if not validation.is_valid:
            result.notes.append(f"Invalid email: {validation.reason}")
            return result

        print_info(f"Analyzing email: {validation.email}")

        local = validation.local_part
        result.username_guesses = self._guess_usernames(local)

        tasks = [
            self._check_mx(validation.domain),
            self._check_gravatar(validation.email),
            self._generate_social_links(validation),
            self._generate_search_dorks(validation),
            self._check_public_pastes(validation.email),
        ]

        if self.deep:
            tasks.append(self._run_account_checks(validation))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        idx = 0
        mx = results[idx]; idx += 1
        gravatar = results[idx]; idx += 1
        social = results[idx]; idx += 1
        dorks = results[idx]; idx += 1
        pastes = results[idx]; idx += 1
        accounts = results[idx] if self.deep else []

        if not isinstance(mx, Exception):
            result.mx_records = mx.get("records", [])
            result.has_mx = mx.get("has_mx", False)
        if not isinstance(gravatar, Exception):
            result.gravatar = gravatar
        if not isinstance(social, Exception):
            result.social_profiles = social
        if not isinstance(dorks, Exception):
            result.dorks = dorks
        if not isinstance(pastes, Exception):
            result.paste_hits = pastes
        if self.deep and not isinstance(accounts, Exception):
            result.account_checks = accounts

        if self.api_keys.get("hibp"):
            try:
                breaches = await self._check_hibp(validation.email)
                result.breach_hints = breaches
            except Exception as e:
                result.notes.append(f"HIBP check failed: {e}")

        if validation.is_gmail:
            result.notes.append("Gmail detected → Consider GHunt for Google Account deep dive (photos, reviews, maps)")
        if validation.is_disposable:
            result.notes.append("⚠ Disposable / temporary email domain detected — low trust")
        if not result.has_mx:
            result.notes.append("No MX records found — domain may not accept mail")
        if result.paste_hits:
            result.notes.append(f"Found {len(result.paste_hits)} public paste mention(s)")
        if any(a.get("found") for a in result.account_checks):
            found = [a["name"] for a in result.account_checks if a.get("found")]
            result.notes.append(f"Possible accounts found on: {', '.join(found)}")

        return result

    def _guess_usernames(self, local: str) -> list[str]:
        base = re.sub(r"[^a-zA-Z0-9._-]", "", local)
        guesses = {base}
        if "." in base:
            parts = base.split(".")
            guesses.add("".join(parts))
            guesses.add("_".join(parts))
            guesses.add(parts[0])
        if "_" in base:
            parts = base.split("_")
            guesses.add("".join(parts))
            guesses.add(".".join(parts))
        no_num = re.sub(r"\d+$", "", base)
        if no_num and no_num != base:
            guesses.add(no_num)
        return sorted(list(guesses))[:8]

    async def _check_mx(self, domain: str) -> dict:
        try:
            answers = dns.resolver.resolve(domain, "MX")
            records = sorted([str(r.exchange).rstrip(".") for r in answers])
            return {"has_mx": True, "records": records}
        except Exception:
            return {"has_mx": False, "records": []}

    async def _check_gravatar(self, email: str) -> dict:
        hash_ = md5_hash(email)
        profile_url = f"https://www.gravatar.com/{hash_}.json"
        avatar_url = f"https://www.gravatar.com/avatar/{hash_}?d=404&s=200"

        async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers, follow_redirects=True) as client:
            has_avatar = False
            try:
                r = await client.head(avatar_url)
                has_avatar = r.status_code == 200
            except Exception:
                pass

            profile = {}
            if has_avatar:
                try:
                    r = await client.get(profile_url)
                    if r.status_code == 200:
                        data = r.json()
                        entry = data.get("entry", [{}])[0]
                        profile = {
                            "display_name": entry.get("displayName"),
                            "about": entry.get("aboutMe"),
                            "location": entry.get("currentLocation"),
                            "urls": [u.get("value") for u in entry.get("urls", [])],
                            "photos": [p.get("value") for p in entry.get("photos", [])],
                        }
                except Exception:
                    pass

        return {
            "has_gravatar": has_avatar,
            "hash": hash_,
            "avatar_url": avatar_url if has_avatar else None,
            "profile_url": f"https://gravatar.com/{hash_}" if has_avatar else None,
            "profile": profile,
        }

    async def _run_account_checks(self, validation: EmailValidationResult) -> list[dict]:
        results = []
        email = validation.email

        async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers, follow_redirects=False) as client:
            try:
                r = await client.get(f"https://api.github.com/search/users?q={quote(email)}+in:email")
                if r.status_code == 200:
                    data = r.json()
                    found = data.get("total_count", 0) > 0
                    items = data.get("items", [])[:3]
                    results.append({
                        "name": "GitHub",
                        "found": found,
                        "details": [i.get("login") for i in items] if found else [],
                        "url": f"https://github.com/search?q={quote(email)}+in%3Aemail&type=users"
                    })
                else:
                    results.append({"name": "GitHub", "found": False, "details": [], "url": ""})
            except Exception:
                results.append({"name": "GitHub", "found": False, "details": [], "url": ""})

            try:
                r = await client.get(f"https://keybase.io/_/api/1.0/user/lookup.json?email={quote(email)}")
                if r.status_code == 200:
                    data = r.json()
                    found = data.get("them") is not None and len(data.get("them", [])) > 0
                    usernames = [u.get("basics", {}).get("username") for u in data.get("them", [])] if found else []
                    results.append({
                        "name": "Keybase",
                        "found": found,
                        "details": usernames,
                        "url": f"https://keybase.io/{usernames[0]}" if usernames else "https://keybase.io"
                    })
                else:
                    results.append({"name": "Keybase", "found": False, "details": [], "url": ""})
            except Exception:
                results.append({"name": "Keybase", "found": False, "details": [], "url": ""})

        return results

    async def _check_public_pastes(self, email: str) -> list[dict]:
        hits = []
        async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
            try:
                r = await client.get(f"https://psbdmp.ws/api/v3/search/{quote(email)}")
                if r.status_code == 200:
                    data = r.json()
                    if isinstance(data, list):
                        for item in data[:5]:
                            hits.append({
                                "source": "psbdmp",
                                "id": item.get("id"),
                                "date": item.get("time"),
                                "url": f"https://pastebin.com/{item.get('id')}" if item.get("id") else None
                            })
            except Exception:
                pass
        return hits

    async def _generate_social_links(self, validation: EmailValidationResult) -> list[dict]:
        email = validation.email
        local = validation.local_part
        platforms = [
            ("GitHub Users", f"https://github.com/search?q={quote(email)}+in%3Aemail&type=users"),
            ("GitHub Code", f"https://github.com/search?q=%22{quote(email)}%22&type=code"),
            ("X / Twitter", f"https://x.com/search?q={quote(email)}&f=user"),
            ("LinkedIn", f"https://www.linkedin.com/search/results/all/?keywords={quote(email)}"),
            ("Facebook", f"https://www.facebook.com/search/top?q={quote(email)}"),
            ("Instagram (guess)", f"https://www.instagram.com/{quote(local)}/"),
            ("Reddit", f"https://www.reddit.com/search/?q={quote(email)}"),
            ("TikTok", f"https://www.tiktok.com/search?q={quote(local)}"),
            ("Google", f"https://www.google.com/search?q=%22{quote(email)}%22"),
            ("DuckDuckGo", f"https://duckduckgo.com/?q=%22{quote(email)}%22"),
        ]
        return [{"platform": p[0], "url": p[1]} for p in platforms]

    async def _generate_search_dorks(self, validation: EmailValidationResult) -> list[dict]:
        email = validation.email
        local = validation.local_part
        return [
            {"name": "Exact email", "query": f'"{email}"'},
            {"name": "Email + password style", "query": f'"{email}" (password OR pass OR pwd OR credential OR login)'},
            {"name": "Paste sites", "query": f'site:pastebin.com OR site:ghostbin.com OR site:hastebin.com OR site:rentry.co "{email}"'},
            {"name": "Documents", "query": f'"{email}" (filetype:pdf OR filetype:doc OR filetype:docx OR filetype:xls OR filetype:xlsx)'},
            {"name": "Username variants", "query": f'"{local}" (email OR mail OR contact OR @)'},
            {"name": "Social profiles", "query": f'"{email}" (site:twitter.com OR site:x.com OR site:linkedin.com OR site:facebook.com)'},
        ]

    async def _check_hibp(self, email: str) -> list[str]:
        key = self.api_keys.get("hibp")
        if not key:
            return []
        url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
        headers = {**self.headers, "hibp-api-key": key}
        async with httpx.AsyncClient(timeout=self.timeout, headers=headers) as client:
            r = await client.get(url, params={"truncateResponse": "false"})
            if r.status_code == 200:
                data = r.json()
                return [f"{b.get('Name')} ({b.get('BreachDate')}) - {b.get('PwnCount', '?')} accounts" for b in data]
            elif r.status_code == 404:
                return ["No breaches found in HIBP"]
            return [f"HIBP returned status {r.status_code}"]

    def display(self, result: EmailOSINTResult):
        table = Table(title=f"📧 Email OSINT → {result.email}", show_header=True, header_style="bold magenta")
        table.add_column("Field", style="cyan", width=18)
        table.add_column("Value", style="white")

        v = result.validation
        table.add_row("Valid Format", "✓ Yes" if v.is_valid else "✗ No")
        table.add_row("Local Part", v.local_part)
        table.add_row("Domain", v.domain)
        table.add_row("Gmail", "Yes ✓" if v.is_gmail else "No")
        table.add_row("Disposable", "⚠ Yes" if v.is_disposable else "No")
        table.add_row("Has MX", "✓ Yes" if result.has_mx else "✗ No")
        if result.mx_records:
            table.add_row("MX Records", ", ".join(result.mx_records[:4]))

        g = result.gravatar
        table.add_row("Gravatar", "✓ Found" if g.get("has_gravatar") else "Not found")
        if g.get("profile", {}).get("display_name"):
            table.add_row("Display Name", g["profile"]["display_name"])
        if g.get("profile_url"):
            table.add_row("Gravatar URL", g["profile_url"])

        console.print(table)

        if result.username_guesses:
            console.print("\n[bold]👤 Username Guesses:[/bold]")
            console.print("  " + ", ".join(result.username_guesses))

        if result.account_checks:
            console.print("\n[bold]🔎 Account Existence Checks:[/bold]")
            for a in result.account_checks:
                status = "[green]FOUND[/green]" if a.get("found") else "[dim]not found[/dim]"
                extra = f" → {', '.join(a.get('details', []))}" if a.get("details") else ""
                console.print(f"  • {a['name']}: {status}{extra}")

        if result.paste_hits:
            console.print("\n[bold red]📋 Public Paste Mentions:[/bold red]")
            for p in result.paste_hits:
                console.print(f"  • {p.get('source')} | {p.get('date')} | {p.get('url')}")

        if result.social_profiles:
            console.print("\n[bold]🔗 Quick Social / Search Links:[/bold]")
            for s in result.social_profiles[:8]:
                console.print(f"  • {s['platform']}: {s['url']}")

        if result.dorks:
            console.print("\n[bold]🔍 Google Dorks (copy-paste):[/bold]")
            for d in result.dorks:
                console.print(f"  • {d['name']}: [dim]{d['query']}[/dim]")

        if result.breach_hints:
            console.print("\n[bold red]🛡 Breach Intelligence (HIBP):[/bold red]")
            for b in result.breach_hints:
                console.print(f"  • {b}")

        if result.notes:
            console.print("\n[bold yellow]Notes:[/bold yellow]")
            for n in result.notes:
                console.print(f"  • {n}")
