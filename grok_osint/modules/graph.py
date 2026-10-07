"""Relationship graph — nodes/edges for Gephi / Maltego-style export."""
from dataclasses import dataclass, field, asdict
import json
from datetime import datetime, timezone

@dataclass
class GraphNode:
    id: str
    label: str
    type: str
    props: dict = field(default_factory=dict)

@dataclass
class GraphEdge:
    source: str
    target: str
    relation: str
    props: dict = field(default_factory=dict)

class OSINTGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = []

    def add_node(self, node_id, label, ntype, **props):
        if node_id not in self.nodes:
            self.nodes[node_id] = GraphNode(id=node_id, label=label, type=ntype, props=props)
        else:
            self.nodes[node_id].props.update(props)

    def add_edge(self, source, target, relation, **props):
        self.edges.append(GraphEdge(source=source, target=target, relation=relation, props=props))

    def to_dict(self):
        types = {}
        for n in self.nodes.values():
            types[n.type] = types.get(n.type, 0) + 1
        return {
            "generated": datetime.now(timezone.utc).isoformat(),
            "tool": "GrokOSINT",
            "nodes": [asdict(n) for n in self.nodes.values()],
            "edges": [asdict(e) for e in self.edges],
            "stats": {"nodes": len(self.nodes), "edges": len(self.edges), "types": types},
        }

    def to_json(self, indent=2):
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
