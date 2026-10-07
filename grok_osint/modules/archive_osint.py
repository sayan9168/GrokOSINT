"""Archive / Wayback OSINT - historical URLs via public CDX API"""

import asyncio
from dataclasses import dataclass, field
from urllib.parse import quote

import httpx


@dataclass
class ArchiveOSINTResult:
    target: str
    snapshots: list[dict] = field(default_factory=list)
    unique_urls: list[str] = field(default_factory=list)
    total: int = 0
    wayback_url: str = ""
    notes: list[str] = field(default_factory=list)


class ArchiveOSINT:
    def __init__(self, timeout: float = 20.0, limit: int = 50):
        self.timeout = timeout
        self.limit = limit
        self.headers = {"User-Agent": "GrokOSINT/2.1 (Ethical Research)"}

    def run(self, target: str) -> ArchiveOSINTResult:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(self.run_async(target))

    async def run_async(self, target: str) -> ArchiveOSINTResult:
        target = (target or "").strip()
        if target.startswith("http"):
            host = target
        else:
            host = target.replace("https://", "").replace("http://", "").split("/")[0]
        result = ArchiveOSINTResult(target=host, wayback_url=f"https://web.archive.org/web/*/{quote(host)}")
        if not host:
            result.notes.append("Invalid target")
            return result
        url = (
            "https://web.archive.org/cdx/search/cdx"
            f"?url={quote(host)}/*&output=json&fl=timestamp,original,statuscode,mimetype"
            f"&collapse=urlkey&limit={self.limit}"
        )
        try:
            async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers, follow_redirects=True) as client:
                r = await client.get(url)
                if r.status_code != 200:
                    result.notes.append(f"CDX HTTP {r.status_code}")
                    return result
                data = r.json()
                if not data or len(data) < 2:
                    result.notes.append("No snapshots found")
                    return result
                seen = set()
                for row in data[1:]:
                    if len(row) < 2:
                        continue
                    ts, original = row[0], row[1]
                    status = row[2] if len(row) > 2 else ""
                    mime = row[3] if len(row) > 3 else ""
                    snap = f"https://web.archive.org/web/{ts}/{original}"
                    result.snapshots.append({"timestamp": ts, "original": original, "status": status, "mimetype": mime, "snapshot_url": snap})
                    if original not in seen:
                        seen.add(original)
                        result.unique_urls.append(original)
                result.total = len(result.snapshots)
                result.notes.append(f"Found {result.total} capture(s), {len(result.unique_urls)} unique URL(s)")
        except Exception as e:
            result.notes.append(f"Archive lookup failed: {e}")
        return result
