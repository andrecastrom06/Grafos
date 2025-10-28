import time
import json
import tracemalloc
from graph import build_directed_graph

def dfs(adj, start):
    visited = []
    levels = {start: 0}
    cycles = []
    
    tracemalloc.start()
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
    
    current, peak = tracemalloc.get_traced_memory()  
    tracemalloc.stop() 
    peak_memory_kb = peak / 1024  

    return {
        "algorithm": "DFS",
        "start": start,
        "visited_order": visited,
        "levels": levels,
        "cycles": cycles,
        "execution_time": exec_time,
        "peak_memory_kb": peak_memory_kb 
    }

def main():
    input_file = '../../data/flight_filtrado.csv'
    output_file = '../../out/percurso_voo_dfs.json'

    adj = build_directed_graph(input_file)
    origins = list(adj.keys())[:3]  

    all_results = []

    for origin in origins:
        print(f"\n🔹 Rodando DFS a partir de '{origin}'...")

        dfs_result = dfs(adj, origin)
        all_results.append({
            "origin": origin,
            "dfs": dfs_result
        })

        print(f"  DFS: {len(dfs_result['visited_order'])} nós visitados em {dfs_result['execution_time']:.6f}s, pico de memória: {dfs_result['peak_memory_kb']:.2f} KB")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Resultados DFS salvos em '{output_file}'.")

if __name__ == "__main__":
    main()