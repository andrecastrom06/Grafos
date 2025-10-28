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
        for v, w, _ in graph[u]:
            if dist[u] + w < dist[v]:
                has_neg = True
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
    return path, flights, weights


def main():
    print("--- Iniciando busca com Bellman-Ford ---")

    csv_file_path = '../../data/flight_filtrado.csv'
    output_json_file = '../../out/percurso_voo_bellman_ford.json'

    max_examples_to_find = 5
    target_origin_countries = ['Brazil', 'Chile']
    min_nos_no_caminho = 5

    graph = build_directed_graph(csv_file_path)
    if not graph:
        print("ERRO: O grafo está vazio. Verifique 'flight_filtrado.csv'.")
        return

    valid_origins = [c for c in target_origin_countries if c in graph]
    if not valid_origins:
        print(f"ERRO: Nenhum dos países de origem alvo {target_origin_countries} foi encontrado no grafo.")
        return

    found_examples = []
    all_countries = list(graph.keys())

    for src_country in all_countries:
        if src_country not in target_origin_countries:
            continue
        dist, pred, has_neg, _, _ = bellman_ford(graph, src_country)
        if has_neg:
            print(f"  ALERTA: Ciclo negativo detectado a partir de {src_country}")
        for dst_country in all_countries:
            if src_country == dst_country:
                continue
            if dist[dst_country] == float('inf'):
                continue
            path, flights, weights = reconstruir_caminho(pred, src_country, dst_country)
            if len(path) >= min_nos_no_caminho:
                dist_val, _, has_neg, exec_time, peak_memory_kb = dist, pred, has_neg, _, _
                tracemalloc.start()
                start_time = time.time()
                dist_val = dist[dst_country]
                exec_time = time.time() - start_time
                current, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                peak_memory_kb = peak / 1024
                found_examples.append((dist_val, path, flights, weights, src_country, dst_country, exec_time, peak_memory_kb))
                print(f"  ... Exemplo {len(found_examples)} encontrado: '{src_country}' -> '{dst_country}' ({len(path)-1} passos) em {exec_time:.6f}s, pico de memória: {peak_memory_kb:.2f} KB")
                if len(found_examples) >= max_examples_to_find:
                    break
        if len(found_examples) >= max_examples_to_find:
            break

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
        print(f"\n✅ Arquivo JSON salvo com {len(json_results_list)} exemplos em '{output_json_file}'.")
    except Exception as e:
        print(f"ERRO ao salvar o arquivo JSON: {e}")


if __name__ == "__main__":
    main()