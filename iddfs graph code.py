from collections import defaultdict

class Graph:
    def __init__(self):
        self.graph = defaultdict(list)

    def add_edge(self, u, v):
        """Add an edge from u → v (directed graph)"""
        self.graph[u].append(v)

    def dls(self, node, target, limit, path, order):
        """Depth-Limited Search (recursive with expansion order)"""
        order.append(node)  # record visiting node
        if node == target:
            return path, order
        if limit == 0:
            return None, order
        for neighbor in self.graph[node]:
            if neighbor not in path:  # avoid cycles
                result, order = self.dls(neighbor, target, limit - 1, path + [neighbor], order)
                if result:
                    return result, order
        return None, order

    def iddfs(self, start, target, max_depth):
        """Iterative Deepening DFS with expansion order"""
        for depth in range(max_depth + 1):
            print(f"\n Trying with depth limit = {depth}")
            order = []
            result, order = self.dls(start, target, depth, [start], order)
            print("Nodes visited in this depth:", " ".join(order))
            if result:
                return result, order
        return None, order


# -----------------------------
# Example Graph and Run
# -----------------------------
g = Graph()
g.add_edge("A", "B")
g.add_edge("A", "C")
g.add_edge("B", "D")
g.add_edge("B", "E")
g.add_edge("C", "F")
g.add_edge("C", "G")
g.add_edge("D", "H")
g.add_edge("E", "I")

start_node = "A"
target_node = "I"
max_depth = 3

solution, visited_order = g.iddfs(start_node, target_node, max_depth)

if solution:
    print(f"\nPath found within depth {max_depth}: {' -> '.join(solution)}")
    print(f" Full visiting order before finding goal: {' '.join(visited_order)}")
else:
    print(f"\n❌ No path found within depth {max_depth}")
