import json
from .graph import build_directed_graph
from .bfs import bfs
from .dfs import dfs

def main():
    input_file = '../data/flight_filtrado.csv'
    output_file = '../out/parte2_report.json'

    adj = build_directed_graph(input_file)
    origins = list(adj.keys())[:3]  

    all_results = []

    for origin in origins:
        print(f"\n🔹 Rodando BFS e DFS a partir de '{origin}'...")

        bfs_result = bfs(adj, origin)
        dfs_result = dfs(adj, origin)

        all_results.append({
            "origin": origin,
            "bfs": bfs_result,
            "dfs": dfs_result
        })

        print(f"  BFS: {len(bfs_result['visited_order'])} nós visitados em {bfs_result['execution_time']:.6f}s")
        print(f"  DFS: {len(dfs_result['visited_order'])} nós visitados em {dfs_result['execution_time']:.6f}s")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Resultados salvos em '{output_file}'.")

if __name__ == "__main__":
    main()
