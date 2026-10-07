"""Unified export — JSON dossier, Markdown, CSV accounts, GEXF graph."""
import csv, io, json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

def export_json(data: dict, path: Optional[str] = None) -> str:
    text = json.dumps(data, indent=2, ensure_ascii=False, default=str)
    if path: Path(path).write_text(text, encoding="utf-8")
    return text

def export_markdown(title: str, seed: str, sections: dict) -> str:
    lines = [f"# {title}", "", f"- **Seed:** `{seed}`", f"- **Generated:** {datetime.now(timezone.utc).isoformat()}", ""]
    for name, body in sections.items():
        lines += [f"## {name}", ""]
        if isinstance(body, (dict, list)):
            lines += ["```json", json.dumps(body, indent=2, ensure_ascii=False, default=str)[:8000], "```"]
        else:
            lines.append(str(body))
        lines.append("")
    return "\n".join(lines)

def export_accounts_csv(accounts: list) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["site", "url", "username", "status"])
    for a in accounts or []:
        w.writerow([a.get("site") or a.get("name") or "", a.get("url") or "", a.get("username") or "", a.get("status") or "found"])
    return buf.getvalue()

def export_gexf(graph: dict) -> str:
    nodes, edges = graph.get("nodes") or [], graph.get("edges") or []
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">',
             '<graph mode="static" defaultedgetype="directed">', "<nodes>"]
    for n in nodes:
        nid = str(n.get("id", "")).replace('"', "")
        lab = str(n.get("label", nid)).replace("&", "&amp;").replace('"', "'")
        lines.append(f'  <node id="{nid}" label="{lab}"/>')
    lines.append("</nodes><edges>")
    for i, e in enumerate(edges):
        s, t = str(e.get("source", "")).replace('"', ""), str(e.get("target", "")).replace('"', "")
        rel = str(e.get("relation", "")).replace('"', "'")
        lines.append(f'  <edge id="{i}" source="{s}" target="{t}" label="{rel}"/>')
    lines.append("</edges></graph></gexf>")
    return "\n".join(lines)

def save_dossier(seed: str, payload: dict, out_dir: str = "reports") -> dict:
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    safe = "".join(c if c.isalnum() or c in "._-@" else "_" for c in seed)[:80]
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    base = out / f"dossier_{safe}_{ts}"
    paths = {}
    Path(str(base)+".json").write_text(export_json(payload), encoding="utf-8"); paths["json"] = str(base)+".json"
    sections = {k: payload.get(k) for k in ("findings", "stats", "modules_run", "notes") if k in payload}
    Path(str(base)+".md").write_text(export_markdown("GrokOSINT Dossier", seed, sections), encoding="utf-8"); paths["markdown"] = str(base)+".md"
    if payload.get("graph"):
        Path(str(base)+".gexf").write_text(export_gexf(payload["graph"]), encoding="utf-8"); paths["gexf"] = str(base)+".gexf"
    accounts = ((payload.get("findings") or {}).get("username") or {}).get("accounts") or []
    if accounts:
        Path(str(base)+"_accounts.csv").write_text(export_accounts_csv(accounts), encoding="utf-8"); paths["csv"] = str(base)+"_accounts.csv"
    return paths
