
import sys
import os
from pathlib import Path

# Add project root to path
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

def debug():
    print("Checking NetworkX availability...")
    try:
        import networkx
        print(f"NetworkX version: {networkx.__version__}")
        print(f"NetworkX path: {networkx.__file__}")
    except ImportError as e:
        print(f"FAILED to import networkx directly: {e}")

    print("\nImporting hive.utils.memory_graph...")
    try:
        from hive.utils import memory_graph
        print(f"memory_graph.nx is: {memory_graph.nx}")
        
        from hive.utils.memory_graph import memory
        print(f"memory.graph is: {memory.graph}")
        
    except Exception as e:
        print(f"Error importing memory_graph: {e}")

if __name__ == "__main__":
    debug()
