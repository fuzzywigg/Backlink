"""Unit tests for LIVE core_utils.graph_store GraphStore.

Covers node/edge persistence and related-node queries with temp storage —
no network.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core_utils.graph_store import GraphNode, GraphStore


@pytest.mark.unit
class TestGraphNode:
    """GraphNode.to_dict() serialization."""

    def test_to_dict_includes_edges(self) -> None:
        node = GraphNode("n1", "file", {"path": "a.py"})
        node.edges.append({"target": "n2", "relation": "imports"})
        data = node.to_dict()
        assert data == {
            "id": "n1",
            "type": "file",
            "content": {"path": "a.py"},
            "edges": [{"target": "n2", "relation": "imports"}],
        }


@pytest.mark.unit
class TestGraphStore:
    """GraphStore add/query/persist behavior."""

    def test_add_node_and_persist(self, tmp_path: Path) -> None:
        store_path = tmp_path / "mem" / "graph.json"
        store = GraphStore(storage_path=str(store_path))
        store.add_node("bee_a", "bee", {"role": "scout"})

        assert "bee_a" in store.nodes
        assert store.nodes["bee_a"].content["role"] == "scout"
        assert store_path.exists()

        reloaded = json.loads(store_path.read_text(encoding="utf-8"))
        assert reloaded["bee_a"]["type"] == "bee"

    def test_add_node_merges_content(self, tmp_path: Path) -> None:
        store = GraphStore(storage_path=str(tmp_path / "g" / "graph.json"))
        store.add_node("n", "concept", {"a": 1})
        store.add_node("n", "concept", {"b": 2})
        assert store.nodes["n"].content == {"a": 1, "b": 2}

    def test_add_edge_creates_missing_nodes(self, tmp_path: Path) -> None:
        store = GraphStore(storage_path=str(tmp_path / "g" / "graph.json"))
        store.add_edge("src", "dst", "depends_on")
        assert "src" in store.nodes
        assert "dst" in store.nodes
        assert store.get_related("src") == ["dst"]

    def test_add_edge_deduplicates(self, tmp_path: Path) -> None:
        store = GraphStore(storage_path=str(tmp_path / "g" / "graph.json"))
        store.add_node("a", "file")
        store.add_node("b", "file")
        store.add_edge("a", "b", "imports")
        store.add_edge("a", "b", "imports")
        assert len(store.nodes["a"].edges) == 1

    def test_get_related_filters_by_relation(self, tmp_path: Path) -> None:
        store = GraphStore(storage_path=str(tmp_path / "g" / "graph.json"))
        store.add_edge("a", "b", "imports")
        store.add_edge("a", "c", "calls")
        assert store.get_related("a", relation="imports") == ["b"]
        assert set(store.get_related("a")) == {"b", "c"}

    def test_get_related_unknown_node(self, tmp_path: Path) -> None:
        store = GraphStore(storage_path=str(tmp_path / "g" / "graph.json"))
        assert store.get_related("missing") == []

    def test_load_existing_graph(self, tmp_path: Path) -> None:
        store_path = tmp_path / "g" / "graph.json"
        store_path.parent.mkdir(parents=True)
        store_path.write_text(
            json.dumps(
                {
                    "x": {
                        "id": "x",
                        "type": "file",
                        "content": {"k": "v"},
                        "edges": [{"target": "y", "relation": "links"}],
                    },
                    "y": {"id": "y", "type": "file", "content": {}, "edges": []},
                }
            ),
            encoding="utf-8",
        )
        store = GraphStore(storage_path=str(store_path))
        assert store.nodes["x"].content == {"k": "v"}
        assert store.get_related("x", "links") == ["y"]
