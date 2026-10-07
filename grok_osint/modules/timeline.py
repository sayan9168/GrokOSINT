"""Timeline from Wayback / CT events."""

def build_timeline(spectrum_or_archive):
    events = []
    findings = spectrum_or_archive.get("findings") or spectrum_or_archive
    arch = findings.get("archive") or {}
    snapshots = arch.get("snapshots") or spectrum_or_archive.get("snapshots") or []
    for s in snapshots[:50]:
        ts = str(s.get("timestamp") or "")
        events.append({"when": _wb_to_iso(ts) or ts, "kind": "wayback", "title": "Archived URL",
                       "detail": s.get("original") or "", "url": s.get("snapshot_url") or ""})
    for c in ((findings.get("domain") or {}).get("ct_sample") or [])[:20]:
        events.append({"when": "", "kind": "certificate", "title": "CT name",
                       "detail": c.get("name") if isinstance(c, dict) else str(c), "url": ""})
    events.sort(key=lambda e: e.get("when") or "9999")
    return events

def _wb_to_iso(ts):
    if not ts or len(ts) < 8: return ""
    try:
        return f"{ts[0:4]}-{ts[4:6]}-{ts[6:8]}T{ts[8:10] if len(ts)>=10 else '00'}:{ts[10:12] if len(ts)>=12 else '00'}:{ts[12:14] if len(ts)>=14 else '00'}Z"
    except Exception:
        return ""
