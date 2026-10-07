"""Multi-seed Correlator — shared accounts, IPs, domains + merged graph."""
from collections import defaultdict
from .graph import OSINTGraph
from .fullspectrum import FullSpectrum

class Correlator:
    def __init__(self, deep=False, top_sites=200):
        self.deep, self.top_sites = deep, top_sites

    def correlate_seeds(self, seeds):
        fs = FullSpectrum(deep=self.deep, top_sites=self.top_sites)
        results = []
        for s in seeds[:12]:
            s = (s or "").strip()
            if not s: continue
            try:
                r = fs.run(s)
                results.append({"seed": r.seed, "type": r.seed_type, "findings": r.findings, "graph": r.graph, "stats": r.stats})
            except Exception as e:
                results.append({"seed": s, "error": str(e)})
        return self.merge(results)

    def merge(self, results):
        g = OSINTGraph()
        accounts_by_site, ips, domains = defaultdict(list), defaultdict(list), defaultdict(list)
        for r in results:
            if r.get("error"): continue
            seed = r.get("seed") or ""
            g.add_node(f"seed:{seed}", seed, r.get("type") or "unknown", role="seed")
            findings = r.get("findings") or {}
            for acc in (findings.get("username") or {}).get("accounts") or []:
                site = (acc.get("site") or acc.get("name") or "?").lower()
                accounts_by_site[site].append({"seed": seed, "url": acc.get("url") or ""})
                nid = f"account:{site}:{seed}"
                g.add_node(nid, f"{seed}@{site}", "account"); g.add_edge(f"seed:{seed}", nid, "has_account")
            for a in (findings.get("domain") or {}).get("a") or []:
                ips[a].append(seed); g.add_node(f"ip:{a}", a, "ip"); g.add_edge(f"seed:{seed}", f"ip:{a}", "related_ip")
            child = r.get("graph") or {}
            for n in child.get("nodes") or []:
                g.add_node(n["id"], n.get("label") or n["id"], n.get("type") or "entity", **(n.get("props") or {}))
            for e in child.get("edges") or []:
                g.add_edge(e["source"], e["target"], e.get("relation") or "linked")
        shared_sites = {s: v for s, v in accounts_by_site.items() if len({x["seed"] for x in v}) >= 2}
        shared_ips = {ip: v for ip, v in ips.items() if len(set(v)) >= 2}
        return {
            "seeds_processed": len([r for r in results if not r.get("error")]),
            "errors": [r for r in results if r.get("error")],
            "shared_sites": shared_sites, "shared_ips": shared_ips, "shared_domains": {},
            "correlation_hits": len(shared_sites) + len(shared_ips),
            "graph": g.to_dict(),
            "summary": {"unique_sites": len(accounts_by_site), "unique_ips": len(ips), "unique_domains": 0},
        }
