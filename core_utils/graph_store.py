import json
import os
from typing import Any


class GraphNode:
    def __init__(self, id: str, type: str, content: dict[str, Any]):
        self.id = id
        self.type = type
        self.content = content
        self.edges: list[dict] = []

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "content": self.content,
            "edges": self.edges
        }

class GraphStore:
    """
    Sovereign Graph Memory Implementation (Proto-Cognee).
    Stores knowledge as a directed graph of nodes and edges.
    """

    def __init__(self, storage_path: str = "data/memory_graph.json"):
        self.storage_path = storage_path
        self.nodes: dict[str, GraphNode] = {}
        self._load()

    def add_node(self, node_id: str, node_type: str, content: dict[str, Any] = None):
        """Adds or updates a node in the graph."""
        if content is None:
            content = {}

        if node_id not in self.nodes:
            self.nodes[node_id] = GraphNode(node_id, node_type, content)
        else:
            self.nodes[node_id].content.update(content)

        self._save()

    def add_edge(self, source_id: str, target_id: str, relation: str):
        """Adds a directed edge between nodes."""
        if source_id not in self.nodes:
            self.add_node(source_id, "unknown", {})
        if target_id not in self.nodes:
            self.add_node(target_id, "unknown", {})

        # Avoid duplicates
        for edge in self.nodes[source_id].edges:
            if edge["target"] == target_id and edge["relation"] == relation:
                return

        self.nodes[source_id].edges.append({
            "target": target_id,
            "relation": relation
        })
        self._save()

    def get_related(self, node_id: str, relation: str = None) -> list[str]:
        """Returns IDs of related nodes."""
        if node_id not in self.nodes:
            return []

        related = []
        for edge in self.nodes[node_id].edges:
            if relation is None or edge["relation"] == relation:
                related.append(edge["target"])
        return related

    def _save(self):
        """Persists graph to disk."""
        data = {k: v.to_dict() for k, v in self.nodes.items()}
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)

    def _load(self):
        """Loads graph from disk."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path) as f:
                    data = json.load(f)
                    for k, v in data.items():
                        node = GraphNode(v["id"], v["type"], v["content"])
                        node.edges = v["edges"]
                        self.nodes[k] = node
            except Exception as e:
                print(f"[GraphStore] Load error: {e}")

if __name__ == "__main__":
    # Test
    graph = GraphStore()
    graph.add_node("radio_bee.py", "file", {"path": "hive/bees/system/radio_bee.py"})
    graph.add_node("model_registry.py", "file", {"path": "core_utils/model_registry.py"})
    graph.add_edge("radio_bee.py", "model_registry.py", "imports")

    related = graph.get_related("radio_bee.py")
    print(f"Radio Bee depends on: {related}")
