import heapq
import json
import time
import tracemalloc 
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
    print("--- Iniciando busca por rotas 'todos para todos' ---")
    
    csv_file_path = '../../data/flight_filtrado.csv'
    output_json_file = '../../out/percurso_voo_dijkstra_todos_para_todos.json'
    
    paises_desejados = [
        "Algeria", "Argentina", "Australia", "Austria", "Brazil", "Belgium",
        "Chile", "Columbia", "Dublin", "Egypt", "France", "Germany", "Greece",
        "India", "Peru", "Rome", "Qatar", "Spain", "Turkey", "United Arab Emirates",
        "United Kingdom", "Canada", "China", "Portugal", "Russia", "South Korea",
        "United States", "Zurich", "Vietnam", "Denmark", "Ethiopia", "Indonesia",
        "Kenya", "Japan", "Morocco", "Mexico", "Norway", "Philippines", "Malaysia",
        "South Africa", "Singapore", "Thailand", "Taiwan", "Italy", "Netherlands",
        "Panama", "Sweden"
    ]
    
    adj = build_directed_graph(csv_file_path)
    
    if not adj:
        print("ERRO: O grafo está vazio. Verifique 'flight_filtrado.csv'.")
        return
    
    paises_no_grafo = set(adj.keys())
    paises_para_buscar = [p for p in paises_desejados if p in paises_no_grafo]
    
    paises_nao_encontrados = [p for p in paises_desejados if p not in paises_no_grafo]
    if paises_nao_encontrados:
        print(f"ATENÇÃO: Os seguintes países da lista não foram encontrados no grafo e serão ignorados:")
        print(f"  {', '.join(paises_nao_encontrados)}")

    print(f"\nIniciando busca de caminhos entre {len(paises_para_buscar)} países...")

    found_examples = []
    total_rotas_calculadas = 0

    for src_country in paises_para_buscar:
        for dst_country in paises_para_buscar:
            if src_country == dst_country:
                continue
            
            total_rotas_calculadas += 1
            tracemalloc.start() 
            start_time = time.time()  
            cost, path, flights, weights = dijkstra(adj, src_country, dst_country)
            exec_time = time.time() - start_time
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop() 
            peak_memory_kb = peak / 1024  

            if cost != float('inf'):
                found_examples.append((cost, path, flights, weights, src_country, dst_country, exec_time, peak_memory_kb))
                
                if len(found_examples) % 100 == 0:
                    print(f"  ... {len(found_examples)} rotas válidas encontradas...")


    print(f"\nBusca concluída. {total_rotas_calculadas} rotas potenciais verificadas.")
    print(f"{len(found_examples)} rotas válidas (com caminho) foram encontradas.")

    json_results_list = []
    for i, example_data in enumerate(found_examples):
        cost, path, flights, weights, src_found, dst_found, exec_time, peak_memory_kb = example_data
        
        resultado_json = {
            "exemplo_num": i + 1,
            "origem": src_found,
            "destino": dst_found,
            "custo_total_minutos": cost,
            "tempo_execucao_segundos": exec_time,
            "peak_memory_kb": peak_memory_kb, 
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
        print(f"\n✅ Arquivo JSON salvo com {len(json_results_list)} rotas em '{output_json_file}'.")
    except Exception as e:
        print(f"ERRO ao salvar o arquivo JSON: {e}")

if __name__ == "__main__":
    main()