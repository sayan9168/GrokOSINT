"""OSINT Pipeline — chain modules from one seed (email/domain/ip/username)."""

import asyncio
import re
from dataclasses import dataclass, field


@dataclass
class PipelineResult:
    seed: str
    seed_type: str
    steps: list[dict] = field(default_factory=list)
    summary: dict = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)


class OSINTPipeline:
    def __init__(self, deep: bool = True, top_sites: int = 300):
        self.deep = deep
        self.top_sites = top_sites

    def detect_type(self, seed: str) -> str:
        s = (seed or "").strip()
        if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", s) or (":" in s and re.match(r"^[0-9a-fA-F:]+$", s)):
            return "ip"
        if "@" in s and "." in s.split("@")[-1]:
            return "email"
        host = s.replace("https://", "").replace("http://", "").split("/")[0]
        if re.match(r"^[\w.-]+\.[a-zA-Z]{2,}$", host):
            return "domain"
        return "username"

    def run(self, seed: str) -> PipelineResult:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(self.run_async(seed))

    async def run_async(self, seed: str) -> PipelineResult:
        seed = (seed or "").strip()
        stype = self.detect_type(seed)
        result = PipelineResult(seed=seed, seed_type=stype)
        result.notes.append(f"Detected type: {stype}")
        if stype == "email":
            await self._email(seed, result)
        elif stype == "domain":
            await self._domain(seed, result)
        elif stype == "ip":
            await self._ip(seed, result)
        else:
            await self._user(seed, result)
        result.summary = {"seed": seed, "type": stype, "steps_completed": len(result.steps),
                          "findings": sum(1 for s in result.steps if s.get("findings"))}
        return result

    async def _email(self, email, result):
        from .email_osint import EmailOSINT
        from .domain_osint import DomainOSINT
        from .username_osint import UsernameOSINT
        er = await EmailOSINT(deep=self.deep).run_async(email)
        result.steps.append({"module": "EmailOSINT", "findings": True, "data": {
            "valid": er.validation.is_valid, "gmail": er.validation.is_gmail, "mx": er.has_mx,
            "holehe": len(er.holehe_results), "notes": er.notes[:8]}})
        if er.validation.domain:
            dr = await DomainOSINT(check_subs=True, max_subs=25).run_async(er.validation.domain)
            result.steps.append({"module": "DomainOSINT", "findings": bool(dr.a_records), "data": {
                "domain": er.validation.domain, "a": dr.a_records[:5], "subs": len(dr.subdomains), "ct": len(dr.ct_certs)}})
        local = er.validation.local_part or email.split("@")[0]
        if local and self.deep:
            ur = UsernameOSINT(top_sites=self.top_sites, timeout=180).run(local)
            result.steps.append({"module": "UsernameOSINT", "findings": ur.total_found > 0, "data": {
                "username": local, "checked": ur.total_checked, "found": ur.total_found,
                "accounts": ur.found_accounts[:20]}})

    async def _domain(self, domain, result):
        from .domain_osint import DomainOSINT
        from .archive_osint import ArchiveOSINT
        from .ip_osint import IPOSINT
        domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
        dr = await DomainOSINT(check_subs=True).run_async(domain)
        result.steps.append({"module": "DomainOSINT", "findings": bool(dr.a_records), "data": {
            "a": dr.a_records, "mx": dr.mx_records, "subs": dr.subdomains[:15], "ct": len(dr.ct_certs)}})
        ar = await ArchiveOSINT(limit=30).run_async(domain)
        result.steps.append({"module": "ArchiveOSINT", "findings": ar.total > 0, "data": {
            "snapshots": ar.total, "urls": ar.unique_urls[:15], "wayback": ar.wayback_url}})
        if dr.a_records:
            ipr = await IPOSINT().run_async(dr.a_records[0])
            result.steps.append({"module": "IPOSINT", "findings": ipr.valid, "data": {"ip": ipr.ip, "geo": ipr.geo, "asn": ipr.asn}})

    async def _ip(self, ip, result):
        from .ip_osint import IPOSINT
        ipr = await IPOSINT().run_async(ip)
        result.steps.append({"module": "IPOSINT", "findings": ipr.valid, "data": {
            "geo": ipr.geo, "asn": ipr.asn, "rdns": ipr.reverse_dns, "links": ipr.reputation_links[:6]}})

    async def _user(self, username, result):
        from .username_osint import UsernameOSINT
        ur = UsernameOSINT(top_sites=self.top_sites, timeout=200).run(username.lstrip("@"))
        result.steps.append({"module": "UsernameOSINT", "findings": ur.total_found > 0, "data": {
            "checked": ur.total_checked, "found": ur.total_found, "accounts": ur.found_accounts[:30]}})
