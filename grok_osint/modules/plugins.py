"""Plugin loader — drop .py into plugins/."""
import importlib.util, sys
from pathlib import Path

def plugins_dir():
    root = Path(__file__).resolve().parents[2]
    d = root / "plugins"
    d.mkdir(parents=True, exist_ok=True)
    return d

def load_plugins():
    loaded = []
    pdir = plugins_dir()
    if str(pdir) not in sys.path:
        sys.path.insert(0, str(pdir.parent))
    for path in sorted(pdir.glob("*.py")):
        if path.name.startswith("_"): continue
        try:
            spec = importlib.util.spec_from_file_location(f"plugins.{path.stem}", path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            meta = getattr(mod, "PLUGIN", None) or {}
            run = getattr(mod, "run", None)
            if not meta and not run: continue
            loaded.append({"id": meta.get("id") or path.stem, "name": meta.get("name") or path.stem,
                           "description": meta.get("description") or "", "file": str(path), "run": run})
        except Exception as e:
            loaded.append({"id": path.stem, "name": path.stem, "error": str(e), "file": str(path)})
    return loaded

def run_plugin(plugin_id, target):
    for p in load_plugins():
        if p.get("id") == plugin_id and callable(p.get("run")):
            try:
                return {"ok": True, "plugin": plugin_id, "result": p["run"](target)}
            except Exception as e:
                return {"ok": False, "plugin": plugin_id, "error": str(e)}
    return {"ok": False, "error": "Plugin not found"}
