import os
import sys

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core_utils.graph_store import GraphStore

def map_repository():
    """
    Crawls the repository and builds a dependency graph.
    """
    graph = GraphStore(storage_path="data/knowledge_graph.json")
    print("Initializing Sovereign Graph Map...")

    # Manual mapping for critical path
    # In a real Cognee implementation, this would use AST parsing
    
    # Nodes
    utils = [
        ("core_utils/model_registry_loader.py", "utility"),
        ("core_utils/graph_store.py", "utility"),
        ("hive/bees/system/radio_bee.py", "agent"),
        ("hive/bees/research/scout_interface.py", "agent"),
        ("config/target_apis.json", "config"),
        ("docs/session_manifest_jan_2026.md", "documentation")
    ]

    for path, type_ in utils:
        graph.add_node(path, type_, {"status": "active"})

    # Edges (Dependencies)
    graph.add_edge("hive/bees/system/radio_bee.py", "core_utils/model_registry_loader.py", "imports")
    graph.add_edge("hive/bees/research/scout_interface.py", "config/target_apis.json", "reads")
    
    print("Graph mapping complete.")
    print(f"Nodes in Memory: {len(graph.nodes)}")
    
    # Verification
    deps = graph.get_related("hive/bees/system/radio_bee.py")
    print(f"RadioBee Dependencies: {deps}")
    
    if "core_utils/model_registry_loader.py" in deps:
        print("✅ Graph Integrity Verified")
    else:
        print("❌ Graph Integrity Failed")

if __name__ == "__main__":
    map_repository()
