import time
import tracemalloc  
from collections import deque
from graph import build_directed_graph
import json

def bfs(adj, start):
    visited = []
    queue = deque([(start, 0)])  
    seen = {start}
    levels = {start: 0}
    cycles = []

    tracemalloc.start()  
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
    
    current, peak = tracemalloc.get_traced_memory()  
    tracemalloc.stop()  
    peak_memory_kb = peak / 1024  

    return {
        "algorithm": "BFS",
        "start": start,
        "visited_order": visited,
        "levels": levels,
        "cycles": cycles,
        "execution_time": exec_time,
        "peak_memory_kb": peak_memory_kb  
    }

def main():
    input_file = '../../data/flight_filtrado.csv'
    output_file = '../../out/percurso_voo_bfs.json'

    adj = build_directed_graph(input_file)
    origins = list(adj.keys())[:3]  

    all_results = []

    for origin in origins:
        print(f"\n🔹 Rodando BFS a partir de '{origin}'...")

        bfs_result = bfs(adj, origin)
        all_results.append({
            "origin": origin,
            "bfs": bfs_result
        })

        print(f"  BFS: {len(bfs_result['visited_order'])} nós visitados em {bfs_result['execution_time']:.6f}s, pico de memória: {bfs_result['peak_memory_kb']:.2f} KB")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Resultados BFS salvos em '{output_file}'.")

if __name__ == "__main__":
    main()