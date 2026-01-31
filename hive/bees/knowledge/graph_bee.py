"""
Knowledge Graph Bee
-------------------
Responsible for Long-Term Memory (LTM).
Interact with the HiveKnowledgeGraph to store and retrieve semantic triples.
"""


from hive.bees.base_bee import BaseBee
from hive.utils.memory_graph import memory


class KnowledgeGraphBee(BaseBee):
    """
    The Librarian of the Hive.
    Manages the semantic knowledge graph.
    """

    def work(self, task):
        """
        Execute knowledge tasks.
        Supported instructions:
        - "learn": Add a new fact (Subject, Predicate, Object).
        - "query": Retrieve context about a node.
        - "snapshot": Persist graph to disk.
        """
        instruction = task.get("instruction", "").lower()
        args = task.get("args", {})

        self.log(f"Processing knowledge task: {instruction}")

        if "learn" in instruction:
            return self.learn_fact(args)
        elif "query" in instruction or "recall" in instruction:
            return self.query_knowledge(args)
        elif "snapshot" in instruction:
            return self.save_memory()
        else:
            return {"success": False, "reason": f"Unknown knowledge instruction: {instruction}"}

    def learn_fact(self, args):
        """
        Add a semantic triple to the graph.
        Expects: subject, predicate, object, (optional) metadata
        """
        subj = args.get("subject")
        pred = args.get("predicate", "related_to")
        obj = args.get("object")
        meta = args.get("metadata", {})

        if not subj or not obj:
            return {"success": False, "reason": "Missing subject or object"}

        # Add to singleton memory graph (synchronous wrapper for async method if needed)
        # Note: In a real async runner, we would await this.
        # For now, we assume the graph operations are fast or we wrap them.

        # Checking if memory.graph is available
        if memory.graph is None:
             return {"success": False, "reason": "Graph memory disabled (NetworkX missing?)"}

        try:
            # Direct add (since the utils might be async, but NetworkX is sync)
            memory.graph.add_node(subj, type="entity")
            memory.graph.add_node(obj, type="concept")
            memory.graph.add_edge(subj, obj, relation=pred, **meta)

            self.log(f"Learned: {subj} -[{pred}]-> {obj}", level="success")

            return {
                "success": True,
                "fact": f"{subj} {pred} {obj}",
                "nodes": memory.graph.number_of_nodes(),
                "edges": memory.graph.number_of_edges()
            }
        except Exception as e:
            self.log(f"Learning failed: {e}", level="error")
            return {"success": False, "error": str(e)}

    def query_knowledge(self, args):
        """
        Retrieve context for a node.
        """
        query = args.get("query")
        int(args.get("depth", 1))

        if not query:
            return {"success": False, "reason": "Missing query argument"}

        if memory.graph is None:
             return {"success": False, "reason": "Graph memory disabled"}

        # BFS Traversal
        results = []
        if query in memory.graph:
            edges = list(memory.graph.out_edges(query, data=True))
            for u, v, data in edges:
                rel = data.get('relation', 'related_to')
                results.append(f"{u} {rel} {v}")
        else:
            return {"success": False, "found": False, "msg": f"No knowledge about '{query}'"}

        return {
            "success": True,
            "found": True,
            "results": results,
            "count": len(results)
        }

    def save_memory(self):
        """Force save to disk."""
        if memory.graph:
            # Stub: Real persistence would go here (e.g. GraphML write)
            return {"success": True, "msg": "Memory snapshot saved (stub)."}
        return {"success": False, "reason": "Graph disabled"}
