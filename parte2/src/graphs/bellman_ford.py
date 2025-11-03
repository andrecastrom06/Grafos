import json
import time
import tracemalloc
from graph import build_directed_graph 

def bellman_ford(graph, start):
    tracemalloc.start()
    start_time = time.time()

    dist = {n: float('inf') for n in graph}
    pred = {n: None for n in graph}
    dist[start] = 0

    for _ in range(len(graph) - 1):
        for u in graph:
            if dist[u] == float('inf'):
                continue
            for v, w, log in graph[u]:
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    pred[v] = (u, log, w)

    has_neg = False
    for u in graph:
        if dist[u] == float('inf'):
            continue
        for v, w, _ in graph[u]:
            if dist[u] + w < dist[v]:
                has_neg = True
                print(f"Ciclo negativo detectado: {u} -> {v}")
                break
        if has_neg:
            break

    exec_time = time.time() - start_time
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    peak_memory_kb = peak / 1024

    return dist, pred, has_neg, exec_time, peak_memory_kb


def reconstruir_caminho(pred, origem, destino):
    path, flights, weights = [], [], []
    cur = destino
    while cur and cur in pred and pred[cur]:
        path.insert(0, cur)
        prev_node, log, w = pred[cur]
        flights.insert(0, log)
        weights.insert(0, w)
        cur = prev_node
    
    if cur == origem:
        path.insert(0, origem)
    
    if not path or path[0] != origem:
        return [], [], [] 
        
    return path, flights, weights


def main():
    print("--- Iniciando busca com Bellman-Ford ---")

    csv_file_path = '../../data/flight_filtrado.csv'
    output_json_file = '../../out/percurso_voo_bellman_ford.json'

    min_nos_no_caminho = 0

    graph = build_directed_graph(csv_file_path)
    if not graph:
        print("ERRO: O grafo está vazio. Verifique 'flight_filtrado.csv'.")
        return

    found_examples = []
    all_countries = list(graph.keys())
    total_countries = len(all_countries)

    print(f"Iniciando cálculo de Bellman-Ford para {total_countries} países de origem...")

    for i, src_country in enumerate(all_countries):
        
        print(f"  Calculando caminhos a partir de: {src_country} ({i+1}/{total_countries})")

        dist, pred, has_neg, bf_exec_time, bf_peak_memory = bellman_ford(graph, src_country)
        
        if has_neg:
            print(f"    ALERTA: Ciclo negativo detectado em caminhos a partir de {src_country}")

        for dst_country in all_countries:
            if src_country == dst_country:
                continue
                
            if dist[dst_country] == float('inf'):
                continue
                
            path, flights, weights = reconstruir_caminho(pred, src_country, dst_country)
            
            if path and len(path) >= min_nos_no_caminho:
                dist_val = dist[dst_country]
                
                found_examples.append((
                    dist_val, path, flights, weights, 
                    src_country, dst_country, 
                    bf_exec_time, bf_peak_memory
                ))

    print(f"\nCálculo de caminhos concluído. Total de {len(found_examples)} caminhos encontrados.")

    json_results_list = []
    for i, ex in enumerate(found_examples):
        cost, path, flights, weights, src_found, dst_found, exec_time, peak_memory_kb = ex
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
        print(f"\nArquivo JSON salvo com {len(json_results_list)} exemplos em '{output_json_file}'.")
    except Exception as e:
        print(f"ERRO ao salvar o arquivo JSON: {e}")


if __name__ == "__main__":
    main()