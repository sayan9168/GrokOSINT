"""Batch OSINT — pipeline across many targets."""
import asyncio
from dataclasses import dataclass, field
from .pipeline import OSINTPipeline
from .utils_osint import append_history

@dataclass
class BatchResult:
    total: int = 0
    completed: int = 0
    results: list = field(default_factory=list)
    notes: list = field(default_factory=list)

class BatchOSINT:
    def __init__(self, deep=False, top_sites=200, max_targets=20):
        self.deep, self.top_sites, self.max_targets = deep, top_sites, max_targets

    def parse_targets(self, text):
        seen, out = set(), []
        for line in (text or "").replace(",", "\n").splitlines():
            t = line.strip()
            if t and not t.startswith("#") and t not in seen:
                seen.add(t); out.append(t)
        return out[:self.max_targets]

    def run(self, text):
        try: loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
        return loop.run_until_complete(self.run_async(text))

    async def run_async(self, text):
        targets = self.parse_targets(text)
        result = BatchResult(total=len(targets))
        if not targets:
            result.notes.append("No targets"); return result
        pipe = OSINTPipeline(deep=self.deep, top_sites=self.top_sites)
        for t in targets:
            try:
                pr = await pipe.run_async(t)
                entry = {"seed": t, "type": pr.seed_type, "steps": len(pr.steps),
                         "findings": pr.summary.get("findings", 0), "summary": pr.summary,
                         "step_modules": [s.get("module") for s in pr.steps]}
                result.results.append(entry)
                append_history({"kind": "batch_item", "seed": t, "type": pr.seed_type})
            except Exception as e:
                result.results.append({"seed": t, "error": str(e)})
            result.completed += 1
        result.notes.append(f"Completed {result.completed}/{result.total}")
        return result
