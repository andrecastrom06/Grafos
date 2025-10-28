import unittest
import heapq

def dijkstra(adj, src, dst):
    if src not in adj or dst not in adj:
        return float('inf'), [], [], []
    
    dist = {n: float('inf') for n in adj}
    prev = {n: None for n in adj}
    prev_log = {n: None for n in adj} 
    prev_weight = {n: None for n in adj} 
    
    dist[src] = 0
    pq = [(0, src)] 
    
    while pq:
        d, u = heapq.heappop(pq)
        
        if u == dst: 
            break
        if d > dist[u]: 
            continue
        
        for v, w, log in adj[u]:
            nd = d + w
            
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                prev_log[v] = log
                prev_weight[v] = w
                heapq.heappush(pq, (nd, v))
                
    if dist[dst] == float('inf'):
        return float('inf'), [], [], []
        
    path, logs, weights = [], [], []
    cur = dst
    
    while cur:
        path.append(cur)
        if prev_log[cur]: 
            logs.append(prev_log[cur])
            weights.append(prev_weight[cur])
        cur = prev[cur]
        
    path.reverse()
    logs.reverse()
    weights.reverse()
    
    return dist[dst], path, logs, weights


class TestDijkstra(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mock_adj = {
            'A': [('B', 2, 'FL-AB'), ('C', 10, 'FL-AC')],
            'B': [('C', 3, 'FL-BC')],
            'C': [],
            'D': [('E', 1, 'FL-DE')],
            'E': []
        }
        cls.mock_adj.setdefault('A', [])
        cls.mock_adj.setdefault('B', [])
        cls.mock_adj.setdefault('C', [])
        cls.mock_adj.setdefault('D', [])
        cls.mock_adj.setdefault('E', [])


    def test_shortest_path_multi_step(self):
        src, dst = 'A', 'C'
        cost, path, logs, weights = dijkstra(self.mock_adj, src, dst)
        
        self.assertEqual(cost, 5)
        self.assertEqual(path, ['A', 'B', 'C'])
        self.assertEqual(logs, ['FL-AB', 'FL-BC'])
        self.assertEqual(weights, [2, 3])

    def test_shortest_path_direct(self):
        src, dst = 'A', 'B'
        cost, path, logs, weights = dijkstra(self.mock_adj, src, dst)
        
        self.assertEqual(cost, 2)
        self.assertEqual(path, ['A', 'B'])
        self.assertEqual(logs, ['FL-AB'])
        self.assertEqual(weights, [2])

    def test_no_path_found(self):
        src, dst = 'A', 'D'
        cost, path, logs, weights = dijkstra(self.mock_adj, src, dst)
        
        self.assertEqual(cost, float('inf'))
        self.assertEqual(path, [])
        self.assertEqual(logs, [])
        self.assertEqual(weights, [])

    def test_invalid_source_node(self):
        src, dst = 'Z', 'A'
        cost, path, _, _ = dijkstra(self.mock_adj, src, dst)
        
        self.assertEqual(cost, float('inf'))
        self.assertEqual(path, [])

    def test_invalid_destination_node(self):
        src, dst = 'A', 'Z'
        cost, path, _, _ = dijkstra(self.mock_adj, src, dst)
        
        self.assertEqual(cost, float('inf'))
        self.assertEqual(path, [])

    def test_path_to_self(self):
        src, dst = 'A', 'A'
        cost, path, logs, weights = dijkstra(self.mock_adj, src, dst)
        
        self.assertEqual(cost, 0)
        self.assertEqual(path, ['A'])
        self.assertEqual(logs, [])
        self.assertEqual(weights, [])


if __name__ == '__main__':
    unittest.main()