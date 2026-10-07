"""GrokOSINT Arsenal - Kali-store style OSINT tool catalog (recon only)."""

from typing import Any


def get_arsenal_catalog() -> list[dict[str, Any]]:
    return [
        {"id": "email", "name": "Email OSINT", "category": "Identity", "status": "built-in", "description": "MX, Gravatar, Holehe (~120), pastes, dorks", "kali_like": "holehe, h8mail", "tab": "email"},
        {"id": "phone", "name": "Phone OSINT", "category": "Identity", "status": "built-in", "description": "Carrier, Ignorant, public lookups", "kali_like": "phoneinfoga", "tab": "phone"},
        {"id": "username", "name": "Username Sweep", "category": "Identity", "status": "built-in", "description": "Maigret top 500-1000+ sites", "kali_like": "sherlock, maigret", "tab": "username"},
        {"id": "domain", "name": "Domain Recon", "category": "Network", "status": "built-in", "description": "DNS, SPF/DMARC, subs, Certificate Transparency", "kali_like": "dnsrecon, recon-ng", "tab": "domain"},
        {"id": "ip", "name": "IP Intelligence", "category": "Network", "status": "built-in", "description": "Geo, ASN, rDNS, VT/Shodan links", "kali_like": "dmitry", "tab": "ip"},
        {"id": "archive", "name": "Wayback / Archive", "category": "Historical", "status": "built-in", "description": "Wayback CDX historical URLs", "kali_like": "waybackurls, gau", "tab": "archive"},
        {"id": "holehe", "name": "Holehe", "category": "External", "status": "optional", "description": "Email on 120+ sites", "install": "pip install holehe", "cmd": "holehe email@domain.com --only-used", "kali_like": "holehe"},
        {"id": "maigret", "name": "Maigret", "category": "External", "status": "optional", "description": "Username on 3000+ sites", "install": "pip install maigret", "cmd": "maigret user --top-sites 500", "kali_like": "sherlock"},
        {"id": "ignorant", "name": "Ignorant", "category": "External", "status": "optional", "description": "Phone WhatsApp/IG/Snap", "install": "pip install ignorant", "cmd": "ignorant 8801XXXXXXXXX", "kali_like": "phone OSINT"},
        {"id": "theharvester", "name": "theHarvester", "category": "External", "status": "recommended", "description": "Emails & subdomains from public sources", "install": "pip install theHarvester", "cmd": "theHarvester -d example.com -b all", "kali_like": "theHarvester"},
        {"id": "recon-ng", "name": "recon-ng", "category": "External", "status": "recommended", "description": "Full recon framework", "install": "pip install recon-ng", "cmd": "recon-ng", "kali_like": "recon-ng"},
        {"id": "subfinder", "name": "Subfinder", "category": "External", "status": "recommended", "description": "Passive subdomain discovery", "install": "go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest", "cmd": "subfinder -d example.com", "kali_like": "subfinder"},
        {"id": "nmap", "name": "Nmap", "category": "External", "status": "recommended", "description": "Port scan ONLY with authorization", "install": "pkg install nmap", "cmd": "nmap -sV target", "kali_like": "nmap"},
        {"id": "exiftool", "name": "ExifTool", "category": "External", "status": "recommended", "description": "Image/document metadata", "install": "pkg install exiftool", "cmd": "exiftool file.jpg", "kali_like": "exiftool"},
        {"id": "whois", "name": "WHOIS", "category": "External", "status": "recommended", "description": "Domain registration data", "install": "pkg install whois", "cmd": "whois example.com", "kali_like": "whois"},
        {"id": "spiderfoot", "name": "SpiderFoot", "category": "External", "status": "recommended", "description": "Automated OSINT graph", "install": "pip install spiderfoot", "cmd": "sfcli.py -s example.com", "kali_like": "spiderfoot"},
        {"id": "maltego", "name": "Maltego CE", "category": "External", "status": "link", "description": "Graph link analysis GUI", "install": "https://www.maltego.com/", "cmd": "Maltego CE", "kali_like": "maltego"},
    ]


def get_categories():
    cats = []
    for t in get_arsenal_catalog():
        c = t.get("category", "Other")
        if c not in cats:
            cats.append(c)
    return cats
