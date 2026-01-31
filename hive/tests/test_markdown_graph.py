import shutil
import tempfile
from pathlib import Path

import pytest

from hive.utils.markdown_graph_storage import MarkdownKnowledgeGraph


class TestMarkdownKnowledgeGraph:

    @pytest.fixture
    def temp_graph_dir(self):
        # Create temp dir
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        shutil.rmtree(temp_dir)

    def test_basic_crud(self, temp_graph_dir):
        mkg = MarkdownKnowledgeGraph(temp_graph_dir)

        # 1. Create Entity
        assert mkg.create_entity("Cat")
        assert (Path(temp_graph_dir) / "Cat.md").exists()

        # 2. Add Observation
        mkg.add_observation("Cat", "This is a furry animal.")
        with open(Path(temp_graph_dir) / "Cat.md") as f:
            content = f.read()
            assert "This is a furry animal." in content

        # 3. Add Relationship
        mkg.create_entity("Human")
        # Cat loves Human
        mkg.add_relationship("Cat", "loves", "Human", "very much")

        with open(Path(temp_graph_dir) / "Cat.md") as f:
            content = f.read()
            assert "- loves [[Human]] very much" in content
            assert "## Relationships" in content

    def test_graph_retrieval(self, temp_graph_dir):
        mkg = MarkdownKnowledgeGraph(temp_graph_dir)
        mkg.create_entity("A")
        mkg.create_entity("B")
        mkg.add_relationship("A", "connects_to", "B")

        graph = mkg.get_full_graph()

        assert "A" in graph["entities"]
        assert "B" in graph["entities"]

        rels = graph["relationships"]
        assert len(rels) == 1
        assert rels[0]["source"] == "A"
        assert rels[0]["verb"] == "connects_to"
        assert rels[0]["target"] == "B"

    def test_deletion(self, temp_graph_dir):
        mkg = MarkdownKnowledgeGraph(temp_graph_dir)
        mkg.create_entity("A")
        mkg.create_entity("B")
        mkg.add_relationship("A", "links", "B")

        # Verify link exists
        with open(Path(temp_graph_dir) / "A.md") as f:
            assert "[[B]]" in f.read()

        # Delete B
        mkg.delete_entity("B")
        assert not (Path(temp_graph_dir) / "B.md").exists()

        # Verify link removed from A
        with open(Path(temp_graph_dir) / "A.md") as f:
            assert "[[B]]" not in f.read()
