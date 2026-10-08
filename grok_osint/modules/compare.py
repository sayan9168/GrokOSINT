"""Compare two scan dossiers."""

def compare_results(a: dict, b: dict) -> dict:
    fa = a.get("findings") or a
    fb = b.get("findings") or b

    def _sites(findings):
        un = findings.get("username") or {}
        return {(x.get("site") or x.get("name") or "").lower() for x in (un.get("accounts") or []) if x}

    def _ips(findings):
        dom = findings.get("domain") or {}
        s = set(dom.get("a") or [])
        if findings.get("ip") and findings["ip"].get("ip"):
            s.add(findings["ip"]["ip"])
        return s

    sites_a, sites_b = _sites(fa), _sites(fb)
    ips_a, ips_b = _ips(fa), _ips(fb)
    return {
        "sites_only_a": sorted(sites_a - sites_b),
        "sites_only_b": sorted(sites_b - sites_a),
        "sites_shared": sorted(sites_a & sites_b),
        "ips_only_a": sorted(ips_a - ips_b),
        "ips_only_b": sorted(ips_b - ips_a),
        "ips_shared": sorted(ips_a & ips_b),
        "seed_a": a.get("seed"),
        "seed_b": b.get("seed"),
        "stats": {
            "sites_a": len(sites_a),
            "sites_b": len(sites_b),
            "new_in_b": len(sites_b - sites_a),
            "gone_in_b": len(sites_a - sites_b),
        },
    }
