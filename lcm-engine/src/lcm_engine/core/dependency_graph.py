from typing import List, Dict

class DependencyGraph:
    """
    Extracts and maps dependencies between logical code units.
    """
    def __init__(self):
        self.graph = {}

    def add_node(self, node_id: str, dependencies: List[str]):
        """Register a chunk and what it depends on."""
        self.graph[node_id] = dependencies

    def get_dependencies(self, node_id: str) -> List[str]:
        """Return the immediate dependencies for a node."""
        return self.graph.get(node_id, [])

    def get_all_dependencies(self, node_id: str) -> List[str]:
        """Recursively resolve all dependencies."""
        visited = set()
        
        def dfs(current_node):
            if current_node in visited:
                return
            visited.add(current_node)
            for dep in self.get_dependencies(current_node):
                dfs(dep)
                
        dfs(node_id)
        visited.discard(node_id) # remove self
        return list(visited)

    def to_dict(self) -> Dict[str, List[str]]:
        return self.graph
