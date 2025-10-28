import sys
import time
import tracemalloc  # <-- ADICIONADO

def bellman_ford(graph, start_node):
    """
    Executa o algoritmo de Bellman-Ford a partir de um nó de origem.
    
    Retorna:
        tuple: (dist, pred, has_negative_cycle, execution_time, peak_memory_kb) # <-- ADICIONADO
    """
    tracemalloc.start()  # <-- ADICIONADO
    start_time = time.perf_counter()
    
    # 1. Inicialização
    dist = {node: float('inf') for node in graph}
    pred = {node: None for node in graph}
    
    # Verifica se o nó de origem realmente existe no grafo
    if start_node not in dist:
        print(f"Erro: Nó de origem '{start_node}' não encontrado no grafo.", file=sys.stderr)
        current, peak = tracemalloc.get_traced_memory()  # <-- ADICIONADO
        tracemalloc.stop()  # <-- ADICIONADO
        return {}, {}, False, 0.0, peak / 1024  # <-- ADICIONADO

    dist[start_node] = 0
    num_nodes = len(graph)

    # 2. Relaxamento das Arestas (V-1 vezes)
    for _ in range(num_nodes - 1):
        for u in graph:
            if dist[u] == float('inf'):
                continue
            for v, weight in graph[u].items():
                if dist[u] + weight < dist[v]:
                    dist[v] = dist[u] + weight
                    pred[v] = u

    # 3. Detecção de Ciclo Negativo
    has_negative_cycle = False
    for u in graph:
        if dist[u] == float('inf'):
            continue
        for v, weight in graph[u].items():
            if dist[u] + weight < dist[v]:
                has_negative_cycle = True
                break 
        if has_negative_cycle:
            break

    end_time = time.perf_counter()
    execution_time = end_time - start_time
    
    current, peak = tracemalloc.get_traced_memory()  # <-- ADICIONADO
    tracemalloc.stop()  # <-- ADICIONADO
    peak_memory_kb = peak / 1024  # <-- ADICIONADO
    
    return dist, pred, has_negative_cycle, execution_time, peak_memory_kb  # <-- MODIFICADO