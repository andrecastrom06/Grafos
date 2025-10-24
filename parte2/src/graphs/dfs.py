import time

def dfs(adj, start):
    """
    Executa a busca em profundidade (DFS) recursiva em um grafo dirigido.

    Retorna:
      - ordem de visita
      - níveis (profundidade)
      - ciclos detectados
      - tempo de execução
    """
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
