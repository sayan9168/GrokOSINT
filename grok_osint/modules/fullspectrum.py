"""Full Spectrum god-mode — all modules + graph + 2026 framework cmds."""
import asyncio, re
from dataclasses import dataclass, field
from .graph import OSINTGraph
from .utils_osint import username_permutations, social_search_pack, breach_paste_links, append_history

@dataclass
class FullSpectrumResult:
    seed: str
    seed_type: str
    modules_run: list = field(default_factory=list)
    findings: dict = field(default_factory=dict)
    graph: dict = field(default_factory=dict)
    framework_cmds: list = field(default_factory=list)
    link_packs: dict = field(default_factory=dict)
    permutations: list = field(default_factory=list)
    notes: list = field(default_factory=list)
    stats: dict = field(default_factory=dict)

class FullSpectrum:
    def __init__(self, deep=True, top_sites=500, max_subs=40):
        self.deep, self.top_sites, self.max_subs = deep, top_sites, max_subs

    def detect(self, seed):
        s = (seed or "").strip()
        if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", s) or (":" in s and re.match(r"^[0-9a-fA-F:]+$", s)):
            return "ip"
        if "@" in s and "." in s.split("@")[-1]: return "email"
        host = s.replace("https://", "").replace("http://", "").split("/")[0]
        if re.match(r"^[\w.-]+\.[a-zA-Z]{2,}$", host): return "domain"
        return "username"

    def run(self, seed):
        try: loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
        return loop.run_until_complete(self.run_async(seed))

    async def run_async(self, seed):
        seed = (seed or "").strip()
        stype = self.detect(seed)
        result = FullSpectrumResult(seed=seed, seed_type=stype)
        g = OSINTGraph(); g.add_node(f"seed:{seed}", seed, stype, role="seed")
        if stype == "email": await self._email(seed, result, g)
        elif stype == "domain": await self._domain(seed, result, g)
        elif stype == "ip": await self._ip(seed, result, g)
        else: await self._user(seed, result, g)
        result.link_packs = {"social": social_search_pack(seed), "breach_paste": breach_paste_links(seed)}
        result.graph = g.to_dict()
        result.framework_cmds = self._cmds(seed, stype)
        result.stats = {"modules": len(result.modules_run), "graph_nodes": result.graph["stats"]["nodes"],
                        "graph_edges": result.graph["stats"]["edges"], "permutations": len(result.permutations)}
        result.notes.append(f"Full Spectrum done type={stype} modules={result.stats['modules']}")
        append_history({"kind": "fullspectrum", "seed": seed, "type": stype, "stats": result.stats})
        return result

    async def _email(self, email, result, g):
        from .email_osint import EmailOSINT
        from .domain_osint import DomainOSINT
        from .username_osint import UsernameOSINT
        from .archive_osint import ArchiveOSINT
        local, domain = email.split("@")[0], email.split("@")[-1]
        er = await EmailOSINT(deep=self.deep).run_async(email)
        result.modules_run.append("EmailOSINT")
        result.findings["email"] = {"valid": er.validation.is_valid, "gmail": er.validation.is_gmail,
            "mx": er.has_mx, "holehe_count": len(getattr(er, "holehe_results", []) or []), "notes": er.notes[:10]}
        g.add_node(f"email:{email}", email, "email"); g.add_edge(f"seed:{email}", f"email:{email}", "is")
        if domain:
            dr = await DomainOSINT(check_subs=True, max_subs=self.max_subs).run_async(domain)
            result.modules_run.append("DomainOSINT")
            result.findings["domain"] = {"a": dr.a_records, "mx": dr.mx_records, "subs": dr.subdomains[:20], "ct": len(dr.ct_certs)}
            g.add_node(f"domain:{domain}", domain, "domain"); g.add_edge(f"email:{email}", f"domain:{domain}", "uses_domain")
            for ip in dr.a_records[:5]:
                g.add_node(f"ip:{ip}", ip, "ip"); g.add_edge(f"domain:{domain}", f"ip:{ip}", "resolves_to")
            ar = await ArchiveOSINT(limit=25).run_async(domain)
            result.modules_run.append("ArchiveOSINT")
            result.findings["archive"] = {"total": ar.total, "urls": ar.unique_urls[:15]}
        result.permutations = username_permutations(local)
        if self.deep and local:
            ur = UsernameOSINT(top_sites=self.top_sites, timeout=240).run(local)
            result.modules_run.append("UsernameOSINT")
            result.findings["username"] = {"checked": ur.total_checked, "found": ur.total_found, "accounts": ur.found_accounts[:40]}
            for acc in ur.found_accounts[:40]:
                site = acc.get("site") or "site"
                nid = f"account:{site}:{local}"
                g.add_node(nid, f"{local}@{site}", "account", url=acc.get("url") or "")
                g.add_edge(f"user:{local}", nid, "has_account")

    async def _domain(self, domain, result, g):
        from .domain_osint import DomainOSINT
        from .archive_osint import ArchiveOSINT
        from .ip_osint import IPOSINT
        domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
        dr = await DomainOSINT(check_subs=True, max_subs=self.max_subs).run_async(domain)
        result.modules_run.append("DomainOSINT")
        result.findings["domain"] = {"a": dr.a_records, "mx": dr.mx_records, "subs": dr.subdomains[:30],
            "ct_sample": dr.ct_certs[:20], "spf": dr.has_spf, "tech": dr.tech_hints}
        g.add_node(f"domain:{domain}", domain, "domain")
        for ip in dr.a_records[:5]:
            g.add_node(f"ip:{ip}", ip, "ip"); g.add_edge(f"domain:{domain}", f"ip:{ip}", "resolves_to")
            if self.deep:
                ipr = await IPOSINT().run_async(ip)
                result.findings[f"ip_{ip}"] = {"geo": ipr.geo, "asn": ipr.asn}
        ar = await ArchiveOSINT(limit=40).run_async(domain)
        result.modules_run.append("ArchiveOSINT")
        result.findings["archive"] = {"total": ar.total, "urls": ar.unique_urls[:25], "wayback": ar.wayback_url}

    async def _ip(self, ip, result, g):
        from .ip_osint import IPOSINT
        ipr = await IPOSINT().run_async(ip)
        result.modules_run.append("IPOSINT")
        result.findings["ip"] = {"geo": ipr.geo, "asn": ipr.asn, "rdns": ipr.reverse_dns, "links": ipr.reputation_links}
        g.add_node(f"ip:{ip}", ip, "ip")

    async def _user(self, username, result, g):
        from .username_osint import UsernameOSINT
        username = username.lstrip("@")
        result.permutations = username_permutations(username)
        g.add_node(f"user:{username}", username, "username")
        ur = UsernameOSINT(top_sites=self.top_sites, timeout=300).run(username)
        result.modules_run.append("UsernameOSINT")
        result.findings["username"] = {"checked": ur.total_checked, "found": ur.total_found, "accounts": ur.found_accounts[:50]}
        for acc in ur.found_accounts[:50]:
            site = acc.get("site") or "site"
            nid = f"account:{site}:{username}"
            g.add_node(nid, f"{username}@{site}", "account", url=acc.get("url") or "")
            g.add_edge(f"user:{username}", nid, "has_account")

    def _cmds(self, seed, stype):
        cmds = []
        user = seed.split("@")[0] if "@" in seed else seed
        if stype in ("username", "email"):
            cmds += [
                {"tool": "Maigret", "cmd": f"maigret {user} --top-sites 1000 --html", "why": "3000+ site dossier"},
                {"tool": "Blackbird", "cmd": f"blackbird -u {user}", "why": "Username+email sweep"},
                {"tool": "Social Analyzer", "cmd": f"social-analyzer --username {user}", "why": "1000+ social scoring"},
            ]
        if stype == "email":
            cmds += [{"tool": "Holehe", "cmd": f"holehe {seed} --only-used", "why": "Account map"},
                     {"tool": "GHunt", "cmd": f"ghunt email {seed}", "why": "Google account"}]
        if stype == "domain":
            d = seed.replace("https://", "").replace("http://", "").split("/")[0]
            cmds += [{"tool": "Subfinder", "cmd": f"subfinder -d {d} -all", "why": "Passive subs"},
                     {"tool": "Amass", "cmd": f"amass enum -d {d}", "why": "Deep DNS"},
                     {"tool": "theHarvester", "cmd": f"theHarvester -d {d} -b all", "why": "Public emails/subs"}]
        cmds.append({"tool": "SpiderFoot", "cmd": f"sfcli.py -s {seed}", "why": "200+ modules"})
        return cmds
