import time
from collections import deque

def bfs(adj, start):
    """
    Executa a busca em largura (BFS) em um grafo dirigido.

    Retorna:
      - ordem de visita
      - níveis (distâncias em camadas)
      - ciclos detectados
      - tempo de execução
    """
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
