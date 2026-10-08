import re

def test_version():
    import grok_osint
    assert re.match(r"\d+\.\d+", getattr(grok_osint, "__version__", "0"))

def test_pipeline_detect():
    from grok_osint.modules.pipeline import OSINTPipeline
    p = OSINTPipeline(deep=False)
    assert p.detect_type("user@example.com") == "email"
    assert p.detect_type("8.8.8.8") == "ip"
    assert p.detect_type("example.com") == "domain"
    assert p.detect_type("johndoe") == "username"

def test_username_permutations():
    from grok_osint.modules.utils_osint import username_permutations
    out = username_permutations("john.doe")
    assert len(out) >= 1

def test_hash_identify():
    from grok_osint.modules.utils_osint import identify_hash
    r = identify_hash("d41d8cd98f00b204e9800998ecf8427e")
    assert "MD5" in str(r.get("possible_types"))

def test_compare():
    from grok_osint.modules.compare import compare_results
    a = {"findings": {"username": {"accounts": [{"site": "github"}]}}}
    b = {"findings": {"username": {"accounts": [{"site": "github"}, {"site": "twitter"}]}}}
    d = compare_results(a, b)
    assert "twitter" in d["sites_only_b"]

def test_playbooks():
    from grok_osint.modules.playbooks import get_playbooks
    assert len(get_playbooks()) >= 3

def test_arsenal():
    from grok_osint.modules.arsenal import arsenal_stats
    assert arsenal_stats()["total"] >= 10

def test_graph():
    from grok_osint.modules.graph import OSINTGraph
    g = OSINTGraph()
    g.add_node("a", "A", "email")
    g.add_node("b", "B", "domain")
    g.add_edge("a", "b", "uses")
    assert g.to_dict()["stats"]["nodes"] == 2

def test_plugins_dir():
    from grok_osint.modules.plugins import plugins_dir, load_plugins
    assert plugins_dir().exists()
    assert isinstance(load_plugins(), list)
