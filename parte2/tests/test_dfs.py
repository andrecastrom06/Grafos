import unittest
import time

def dfs(adj, start):
    visited = []
    levels = {start: 0}
    cycles = []
    start_time = time.time()

    def dfs_visit(node, depth, ancestors):
        visited.append(node)
        for neighbor, _, _ in adj[node]:
            if neighbor not in visited:
                levels[neighbor] = depth + 1
                dfs_visit(neighbor, depth + 1, ancestors + [node])
            elif neighbor in ancestors:
                cycles.append((node, neighbor))

    dfs_visit(start, 0, [])
    exec_time = time.time() - start_time

    return {
        "algorithm": "DFS",
        "start": start,
        "visited_order": visited,
        "levels": levels,
        "cycles": cycles,
        "execution_time": exec_time
    }

def sample_graph():
    return {
        'A': [('B', 1, ''), ('C', 1, '')],
        'B': [('D', 1, '')],
        'C': [('A', 1, ''), ('D', 1, '')],
        'D': []
    }

class TestDFS(unittest.TestCase):

    def setUp(self):
        self.graph = sample_graph()

    def test_dfs_levels(self):
        result = dfs(self.graph, 'A')
        self.assertEqual(result["levels"]['A'], 0)
        self.assertIn('D', result["levels"])

    def test_dfs_cycle_detection(self):
        result = dfs(self.graph, 'A')
        self.assertGreaterEqual(len(result["cycles"]), 1)

if __name__ == '__main__':
    unittest.main()