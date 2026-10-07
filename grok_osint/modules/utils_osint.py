"""Utils: permutations, hash ID, link packs, scan history."""
import hashlib, json, re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

def username_permutations(base: str, max_out: int = 40) -> list:
    base = re.sub(r"[^a-zA-Z0-9._-]", "", (base or "").strip().lower())
    if not base: return []
    out = {base}
    parts = [p for p in re.split(r"[._-]", base) if p]
    if len(parts) >= 2:
        out.update(["".join(parts), ".".join(parts), "_".join(parts), parts[0], parts[-1], parts[0]+parts[-1]])
    for y in ("2024", "2025", "2026", "1", "123"):
        out.add(base + y)
    return sorted([x for x in out if 2 <= len(x) <= 30])[:max_out]

def email_permutations(first: str, last: str, domain: str = "gmail.com", max_out: int = 25) -> list:
    first = re.sub(r"[^a-z]", "", (first or "").lower())
    last = re.sub(r"[^a-z]", "", (last or "").lower())
    domain = (domain or "gmail.com").lower()
    if not first: return []
    patterns = [first]
    if last:
        patterns += [f"{first}.{last}", f"{first}_{last}", f"{first}{last}", f"{first[0]}{last}", f"{last}.{first}"]
    return [f"{p}@{domain}" for p in patterns if p][:max_out]

HASH_PATTERNS = [
    (r"^[a-fA-F0-9]{32}$", "MD5"), (r"^[a-fA-F0-9]{40}$", "SHA-1"),
    (r"^[a-fA-F0-9]{64}$", "SHA-256"), (r"^[a-fA-F0-9]{128}$", "SHA-512"),
    (r"^\$2[aby]?\$\d{2}\$", "bcrypt"), (r"^\$argon2", "Argon2"),
]

def identify_hash(value: str) -> dict:
    v = (value or "").strip()
    matches = [n for p, n in HASH_PATTERNS if re.search(p, v)]
    return {"possible_types": matches or ["Unknown"], "lookup_links": [
        {"name": "CrackStation", "url": "https://crackstation.net/"},
        {"name": "Google", "url": f"https://www.google.com/search?q=%22{quote(v)}%22"},
    ], "note": "Identify only — no cracking"}

def quick_hashes(text: str) -> dict:
    b = (text or "").encode()
    return {"md5": hashlib.md5(b).hexdigest(), "sha1": hashlib.sha1(b).hexdigest(), "sha256": hashlib.sha256(b).hexdigest()}

def reverse_image_links(image_url: str = ""):
    q = quote(image_url) if image_url else ""
    return [
        {"name": "Google Lens", "url": f"https://lens.google.com/uploadbyurl?url={q}" if image_url else "https://lens.google.com/upload"},
        {"name": "Yandex", "url": f"https://yandex.com/images/search?rpt=imageview&url={q}" if image_url else "https://yandex.com/images/"},
        {"name": "TinEye", "url": f"https://tineye.com/search?url={q}" if image_url else "https://tineye.com/"},
    ]

def social_search_pack(query: str):
    q = quote(query or "")
    return [{"name": n, "url": u} for n, u in [
        ("Google", f"https://www.google.com/search?q=%22{q}%22"),
        ("X/Twitter", f"https://x.com/search?q={q}"),
        ("LinkedIn", f"https://www.linkedin.com/search/results/all/?keywords={q}"),
        ("Facebook", f"https://www.facebook.com/search/top?q={q}"),
        ("Reddit", f"https://www.reddit.com/search/?q={q}"),
        ("GitHub", f"https://github.com/search?q={q}&type=users"),
        ("YouTube", f"https://www.youtube.com/results?search_query={q}"),
    ]]

def breach_paste_links(email_or_query: str):
    q = quote(email_or_query or "")
    return [
        {"name": "HIBP", "url": "https://haveibeenpwned.com/"},
        {"name": "IntelX", "url": f"https://intelx.io/?s={q}"},
        {"name": "Pastebin Google", "url": f"https://www.google.com/search?q=site%3Apastebin.com+{q}"},
        {"name": "GitHub code", "url": f"https://github.com/search?q={q}&type=code"},
    ]

def history_path(base_dir="reports"):
    p = Path(base_dir); p.mkdir(parents=True, exist_ok=True)
    return p / "scan_history.jsonl"

def append_history(entry: dict, base_dir="reports"):
    entry = dict(entry); entry.setdefault("ts", datetime.now(timezone.utc).isoformat())
    with open(history_path(base_dir), "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def read_history(limit=50, base_dir="reports"):
    path = history_path(base_dir)
    if not path.exists(): return []
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    out = []
    for line in lines[-limit:]:
        try: out.append(json.loads(line))
        except Exception: pass
    return list(reversed(out))
