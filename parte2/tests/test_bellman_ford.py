import time
import unittest
import tracemalloc

def bellman_ford(graph, start):
    tracemalloc.start()
    start_time = time.time()

    dist = {n: float('inf') for n in graph}
    pred = {n: None for n in graph}
    dist[start] = 0

    for _ in range(len(graph) - 1):
        for u in graph:
            if dist[u] == float('inf'):
                continue
            for v, w, _ in graph[u]:
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    pred[v] = u

    has_neg = False
    for u in graph:
        for v, w, _ in graph[u]:
            if dist[u] + w < dist[v]:
                has_neg = True
                break
        if has_neg:
            break

    exec_time = time.time() - start_time
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "dist": dist,
        "pred": pred,
        "has_negative_cycle": has_neg,
        "execution_time": exec_time,
        "peak_memory_kb": peak / 1024
    }


def sample_graph_no_negative_cycle():
    return {
        'S': [('A', 6, ''), ('B', 5, '')],
        'A': [('C', -2, '')],
        'B': [('A', -2, ''), ('D', 4, '')],
        'C': [('B', 5, ''), ('E', 3, '')],
        'D': [('C', 3, ''), ('E', -1, '')],
        'E': []
    }


def sample_graph_with_negative_cycle():
    return {
        'A': [('B', 1, '')],
        'B': [('C', -1, '')],
        'C': [('A', -1, '')]
    }


class TestBellmanFord(unittest.TestCase):

    def setUp(self):
        self.graph_no_neg = sample_graph_no_negative_cycle()
        self.graph_neg = sample_graph_with_negative_cycle()

    def test_bellman_ford_sem_ciclo_negativo(self):
        result = bellman_ford(self.graph_no_neg, 'S')
        dist = result["dist"]
        pred = result["pred"]

        self.assertFalse(result["has_negative_cycle"])
        self.assertEqual(dist['A'], 3)
        self.assertEqual(dist['C'], 1)
        self.assertEqual(dist['D'], 9)
        self.assertEqual(dist['E'], 4)
        self.assertEqual(pred['E'], 'C')

    def test_bellman_ford_com_ciclo_negativo(self):
        result = bellman_ford(self.graph_neg, 'A')
        self.assertTrue(result["has_negative_cycle"])


if __name__ == '__main__':
    unittest.main()