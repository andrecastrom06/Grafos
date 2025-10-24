import time
from collections import deque
import unittest

def bfs(adj, start):
    visited = []
    queue = deque([(start, 0)])  
    seen = {start}
    levels = {start: 0}
    cycles = []

    start_time = time.time()

    while queue:
        node, level = queue.popleft()
        visited.append(node)

        for neighbor, _, _ in adj[node]:
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append((neighbor, level + 1))
                levels[neighbor] = level + 1
            elif neighbor in visited:
                cycles.append((node, neighbor))

    exec_time = time.time() - start_time

    return {
        "algorithm": "BFS",
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
        'C': [('D', 1, ''), ('A', 1, '')],
        'D': []
    }

class TestBFS(unittest.TestCase):

    def setUp(self):
        self.graph = sample_graph()

    def test_bfs_levels(self):
        result = bfs(self.graph, 'A')
        self.assertEqual(result["levels"]['A'], 0)
        self.assertEqual(result["levels"]['B'], 1)
        self.assertGreaterEqual(result["levels"]['D'], 1)

    def test_bfs_cycle_detection(self):
        result = bfs(self.graph, 'A')
        self.assertGreaterEqual(len(result["cycles"]), 1)

if __name__ == '__main__':
    unittest.main()