"""IP OSINT - Geo, ASN, reverse DNS, public reputation links"""

import asyncio
import re
import socket
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import quote

import httpx


@dataclass
class IPOSINTResult:
    ip: str
    valid: bool = False
    version: int = 4
    reverse_dns: list[str] = field(default_factory=list)
    geo: dict = field(default_factory=dict)
    asn: dict = field(default_factory=dict)
    reputation_links: list[dict] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    raw: dict = field(default_factory=dict)


class IPOSINT:
    def __init__(self, timeout: float = 12.0):
        self.timeout = timeout
        self.headers = {"User-Agent": "GrokOSINT/2.0 (Ethical Research)"}

    def run(self, ip: str) -> IPOSINTResult:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(self.run_async(ip))

    async def run_async(self, ip: str) -> IPOSINTResult:
        ip = (ip or "").strip()
        result = IPOSINTResult(ip=ip)
        if not self._is_ip(ip):
            result.notes.append("Invalid IP address")
            return result
        result.valid = True
        result.version = 6 if ":" in ip else 4
        try:
            host, aliases, _ = socket.gethostbyaddr(ip)
            result.reverse_dns = [host] + list(aliases or [])
        except Exception:
            result.reverse_dns = []
        result.geo, result.asn = await self._lookup_geo_asn(ip)
        result.reputation_links = self._rep_links(ip)
        if result.geo.get("country"):
            result.notes.append(f"Location: {result.geo.get('city') or ''} {result.geo.get('region') or ''} {result.geo.get('country')}".strip())
        if result.asn.get("org"):
            result.notes.append(f"ORG/ASN: {result.asn.get('org')} {result.asn.get('asn') or ''}".strip())
        if result.reverse_dns:
            result.notes.append(f"rDNS: {', '.join(result.reverse_dns[:3])}")
        return result

    def _is_ip(self, s: str) -> bool:
        if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", s):
            return all(0 <= int(p) <= 255 for p in s.split("."))
        if ":" in s and re.match(r"^[0-9a-fA-F:]+$", s):
            return True
        return False

    async def _lookup_geo_asn(self, ip: str):
        geo, asn = {}, {}
        async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
            try:
                r = await client.get(f"http://ip-api.com/json/{ip}?fields=status,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,asname,mobile,proxy,hosting")
                if r.status_code == 200:
                    d = r.json()
                    if d.get("status") == "success":
                        geo = {"country": d.get("country"), "country_code": d.get("countryCode"), "region": d.get("regionName"), "city": d.get("city"), "zip": d.get("zip"), "lat": d.get("lat"), "lon": d.get("lon"), "timezone": d.get("timezone"), "isp": d.get("isp"), "org": d.get("org"), "mobile": d.get("mobile"), "proxy": d.get("proxy"), "hosting": d.get("hosting")}
                        asn = {"asn": d.get("as"), "asname": d.get("asname"), "org": d.get("org") or d.get("isp")}
                        return geo, asn
            except Exception:
                pass
        return geo, asn

    def _rep_links(self, ip: str):
        q = quote(ip)
        return [
            {"name": "VirusTotal", "url": f"https://www.virustotal.com/gui/ip-address/{q}"},
            {"name": "AbuseIPDB", "url": f"https://www.abuseipdb.com/check/{q}"},
            {"name": "Shodan", "url": f"https://www.shodan.io/host/{q}"},
            {"name": "Censys", "url": f"https://search.censys.io/hosts/{q}"},
            {"name": "GreyNoise", "url": f"https://viz.greynoise.io/ip/{q}"},
            {"name": "IPInfo", "url": f"https://ipinfo.io/{q}"},
            {"name": "BGPView", "url": f"https://bgpview.io/ip/{q}"},
            {"name": "Google", "url": f"https://www.google.com/search?q=%22{q}%22"},
        ]
