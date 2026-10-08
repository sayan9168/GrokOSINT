"""Minimal CI tests — must always pass."""
import re

def test_version():
    import grok_osint
    assert re.match(r"\d+\.\d+", getattr(grok_osint, "__version__", "0.0"))

def test_compare():
    from grok_osint.modules.compare import compare_results
    a = {"findings": {"username": {"accounts": [{"site": "github"}]}}}
    b = {"findings": {"username": {"accounts": [{"site": "github"}, {"site": "twitter"}]}}}
    d = compare_results(a, b)
    assert "twitter" in d["sites_only_b"]
    assert "github" in d["sites_shared"]

def test_utils_permute():
    from grok_osint.modules.utils_osint import username_permutations, identify_hash
    assert len(username_permutations("john.doe")) >= 1
    r = identify_hash("d41d8cd98f00b204e9800998ecf8427e")
    assert r.get("possible_types")

def test_graph():
    from grok_osint.modules.graph import OSINTGraph
    g = OSINTGraph()
    g.add_node("a", "A", "email")
    g.add_edge("a", "a", "self")
    assert g.to_dict()["stats"]["nodes"] == 1

def test_pipeline_detect_type():
    from grok_osint.modules.pipeline import OSINTPipeline
    p = OSINTPipeline(deep=False)
    assert p.detect_type("a@b.com") == "email"
    assert p.detect_type("1.2.3.4") == "ip"
