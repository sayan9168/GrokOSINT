"""OSINT Playbooks — guided investigation runbooks."""
from typing import Any

def get_playbooks() -> list:
    return [
        {"id": "person_email", "name": "Person from Email", "difficulty": "medium", "seed": "email",
         "description": "Email → accounts, domain, username, breaches",
         "steps": ["Validate + MX", "Holehe", "Maigret on local-part", "Domain DNS/CT/Wayback", "Breach links", "Graph export"],
         "builtin": "fullspectrum", "cmds": ["holehe EMAIL --only-used", "maigret LOCAL --top-sites 500 --html"]},
        {"id": "person_username", "name": "Person from Username", "difficulty": "easy", "seed": "username",
         "description": "Exhaustive username footprint",
         "steps": ["Permutations", "Maigret 500-1000", "Social Analyzer", "Social link pack", "Graph"],
         "builtin": "fullspectrum", "cmds": ["maigret USER --top-sites 1000 --html", "sherlock USER"]},
        {"id": "org_domain", "name": "Organization / Domain", "difficulty": "medium", "seed": "domain",
         "description": "DNS, subs, CT, archive, tech, IPs",
         "steps": ["Domain OSINT", "Subdomains + CT", "Wayback", "IP pivot", "Subfinder/Amass", "httpx"],
         "builtin": "fullspectrum", "cmds": ["subfinder -d DOMAIN -all | httpx -title", "amass enum -d DOMAIN"]},
        {"id": "ip_host", "name": "IP / Host Intelligence", "difficulty": "easy", "seed": "ip",
         "description": "Geo, ASN, rDNS, reputation",
         "steps": ["IP OSINT", "VT/Shodan/AbuseIPDB", "rDNS pivot", "Authorized nmap"],
         "builtin": "fullspectrum", "cmds": ["shodan host IP", "nmap -sV IP"]},
        {"id": "phone_lead", "name": "Phone Number Lead", "difficulty": "medium", "seed": "phone",
         "description": "Carrier + messenger signals",
         "steps": ["Phone OSINT", "Ignorant", "Public lookup links"],
         "builtin": "phone", "cmds": ["ignorant CC NUMBER"]},
        {"id": "batch_watchlist", "name": "Batch Watchlist", "difficulty": "medium", "seed": "mixed",
         "description": "Many targets at once", "steps": ["List targets", "Batch shallow", "Deep on hits"],
         "builtin": "batch", "cmds": []},
    ]

def get_playbook(pid: str):
    for p in get_playbooks():
        if p["id"] == pid: return p
    return None
