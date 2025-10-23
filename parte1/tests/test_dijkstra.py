import unittest
import heapq

def dijkstra(adj, src, dst):
    if src not in adj or dst not in adj:
        return float('inf'), [], [], []
    dist = {n: float('inf') for n in adj}
    prev = {n: None for n in adj}
    prev_street = {n: None for n in adj}
    prev_weight = {n: None for n in adj}  
    dist[src] = 0
    pq = [(0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == dst: break
        if d > dist[u]: continue
        for v, w, log in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v], prev[v], prev_street[v], prev_weight[v] = nd, u, log, w
                heapq.heappush(pq, (nd, v))
    if dist[dst] == float('inf'):
        return float('inf'), [], [], []
    path, streets, weights, cur = [], [], [], dst
    while cur:
        path.append(cur)
        if prev_street[cur]:
            streets.append(prev_street[cur])
            weights.append(prev_weight[cur])
        cur = prev[cur]
    path.reverse()
    streets.reverse()
    weights.reverse()
    return dist[dst], path, streets, weights

class TestDijkstra(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Configura um grafo de teste único (mock) para todos os testes.
        O formato (vizinho, peso, metadata) é o mesmo.
        """
        cls.mock_adj = {
            'A': [('B', 2, 'Rua A-B'), ('C', 10, 'Rua A-C')],
            'B': [('C', 3, 'Rua B-C')],
            'C': [],
            'D': [('E', 1, 'Rua D-E')],
            'E': []
        }
        cls.mock_adj.setdefault('A', [])
        cls.mock_adj.setdefault('B', [])
        cls.mock_adj.setdefault('C', [])
        cls.mock_adj.setdefault('D', [])
        cls.mock_adj.setdefault('E', [])


    def test_shortest_path_multi_step(self):
        print("\nTestando: test_shortest_path_multi_step (A -> C)")
        src, dst = 'A', 'C'
        
        cost, path, streets, weights = dijkstra(self.mock_adj, src, dst)
        
        self.assertEqual(cost, 5, "O custo deve ser 5 (via 'B')")
        self.assertEqual(path, ['A', 'B', 'C'], "O caminho deve ser ['A', 'B', 'C']")
        self.assertEqual(streets, ['Rua A-B', 'Rua B-C'], "As ruas devem corresponder ao caminho")
        self.assertEqual(weights, [2, 3], "Os pesos devem corresponder ao caminho")

    def test_shortest_path_direct(self):
        print("\nTestando: test_shortest_path_direct (A -> B)")
        src, dst = 'A', 'B'
        
        cost, path, streets, weights = dijkstra(self.mock_adj, src, dst)
        
        self.assertEqual(cost, 2)
        self.assertEqual(path, ['A', 'B'])
        self.assertEqual(streets, ['Rua A-B'])
        self.assertEqual(weights, [2])

    def test_no_path_found(self):
        print("\nTestando: test_no_path_found (A -> D)")
        src, dst = 'A', 'D'
        
        cost, path, streets, weights = dijkstra(self.mock_adj, src, dst)
        
        self.assertEqual(cost, float('inf'))
        self.assertEqual(path, [])
        self.assertEqual(streets, [])
        self.assertEqual(weights, [])

    def test_invalid_source_node(self):
        print("\nTestando: test_invalid_source_node (Z -> A)")
        src, dst = 'Z', 'A'
        
        cost, path, _, _ = dijkstra(self.mock_adj, src, dst)
        
        self.assertEqual(cost, float('inf'))
        self.assertEqual(path, [])

    def test_invalid_destination_node(self):
        print("\nTestando: test_invalid_destination_node (A -> Z)")
        src, dst = 'A', 'Z'
        
        cost, path, _, _ = dijkstra(self.mock_adj, src, dst)
        
        self.assertEqual(cost, float('inf'))
        self.assertEqual(path, [])

    def test_path_to_self(self):
        print("\nTestando: test_path_to_self (A -> A)")
        src, dst = 'A', 'A'
        
        cost, path, streets, weights = dijkstra(self.mock_adj, src, dst)
        
        self.assertEqual(cost, 0)
        self.assertEqual(path, ['A'])
        self.assertEqual(streets, [])
        self.assertEqual(weights, [])


if __name__ == '__main__':
    print("--- Executando Testes de Unidade para Dijkstra (Versão Bairros) ---")
    unittest.main()