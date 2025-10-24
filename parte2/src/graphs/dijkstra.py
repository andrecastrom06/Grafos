import heapq
import json
import time
from graph import build_directed_graph

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

def main():
    print("--- Iniciando busca por rotas longas (>= 4 passos) ---")
    
    csv_file_path = '../../data/flight_filtrado.csv'
    output_json_file = '../../out/percurso_voo_dijkstra.json'
    
    max_examples_to_find = 5
    target_origin_countries = ['Brazil', 'Chile']
    min_nos_no_caminho = 5
    
    adj = build_directed_graph(csv_file_path)
    
    if not adj:
        print("ERRO: O grafo está vazio. Verifique 'flight_filtrado.csv'.")
        return
    
    valid_origins = [c for c in target_origin_countries if c in adj]
    if not valid_origins:
        print(f"ERRO: Nenhum dos países de origem alvo {target_origin_countries} foi encontrado no grafo.")
        return

    found_examples = []
    all_countries = list(adj.keys())

    for src_country in all_countries:
        if src_country not in target_origin_countries:
            continue
        for dst_country in all_countries:
            if src_country == dst_country:
                continue
            
            start_time = time.time()  
            cost, path, flights, weights = dijkstra(adj, src_country, dst_country)
            exec_time = time.time() - start_time  

            if cost != float('inf') and len(path) >= min_nos_no_caminho:
                found_examples.append((cost, path, flights, weights, src_country, dst_country, exec_time))
                print(f"  ... Exemplo {len(found_examples)} encontrado: '{src_country}' -> '{dst_country}' ({len(path)-1} passos) em {exec_time:.6f}s")
                if len(found_examples) >= max_examples_to_find:
                    break
        if len(found_examples) >= max_examples_to_find:
            break

    json_results_list = []
    for i, example_data in enumerate(found_examples):
        cost, path, flights, weights, src_found, dst_found, exec_time = example_data
        
        resultado_json = {
            "exemplo_num": i + 1,
            "origem": src_found,
            "destino": dst_found,
            "custo_total_minutos": cost,
            "tempo_execucao_segundos": exec_time,
            "caminho": path,
            "etapas": []
        }

        for j in range(len(flights)):
            etapa = {
                "de": path[j],
                "para": path[j+1],
                "voo": flights[j],
                "duration_minutes": weights[j]
            }
            resultado_json["etapas"].append(etapa)

        json_results_list.append(resultado_json)

    try:
        with open(output_json_file, 'w', encoding='utf-8') as f:
            json.dump(json_results_list, f, ensure_ascii=False, indent=4)
        print(f"\n✅ Arquivo JSON salvo com {len(json_results_list)} exemplos em '{output_json_file}'.")
    except Exception as e:
        print(f"ERRO ao salvar o arquivo JSON: {e}")

if __name__ == "__main__":
    main()