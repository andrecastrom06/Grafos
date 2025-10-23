# algorithms.py

import heapq
import json
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
    print("--- Iniciando busca por rotas longas (>= 4 passos) com origem 'Brazil' ou 'Chile' ---")
    
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
    
    print(f"Países de origem válidos encontrados no grafo: {valid_origins}")

    print(f"\nProcurando {max_examples_to_find} pares (Origem = 'Brazil' ou 'Chile')")
    print(f"onde o melhor caminho tem mais de 3 passos (Nós >= {min_nos_no_caminho})...")
    
    found_examples = [] 
    all_countries = list(adj.keys())
    
    for src_country in all_countries:
        
        if src_country not in target_origin_countries:
            continue

        for dst_country in all_countries:
            if src_country == dst_country:
                continue
                
            cost, path, flights, weights = dijkstra(adj, src_country, dst_country)
            
            if cost != float('inf') and len(path) >= min_nos_no_caminho:
                
                found_examples.append((cost, path, flights, weights, src_country, dst_country))
                print(f"  ... Exemplo {len(found_examples)} encontrado: '{src_country}' -> '{dst_country}' ({len(path) - 1} passos)")
                
                if len(found_examples) >= max_examples_to_find:
                    break 
        
        if len(found_examples) >= max_examples_to_find:
            break 

    print("\n--- RESULTADO DA BUSCA ---")
    
    if not found_examples:
        print(f"Nenhuma rota originada de {target_origin_countries} foi encontrada")
        print(f"com {min_nos_no_caminho - 1} ou mais passos.")
        return

    json_results_list = []

    for i, example_data in enumerate(found_examples):
        cost, path, flights, weights, src_found, dst_found = example_data
        
        print(f"\n--- EXEMPLO {i + 1}/{len(found_examples)} ---")
        
        resultado_json = {
            "exemplo_num": i + 1,
            "origem": src_found,
            "destino": dst_found,
            "custo_total_minutos": cost,
            "caminho": path,
            "etapas": []
        }

        print(f"Rota encontrada de '{src_found}' para '{dst_found}':")
        print(f"Custo total (Duração): {cost:.0f} minutos")
        print(f"Passos (arestas): {len(path) - 1}")
        print(f"\nPercurso do Caminho ({len(path)} países):")
        print(" -> ".join(path))
        print(f"\nEtapas da Viagem ({len(flights)} voos):")

        for j in range(len(flights)):
            etapa = {
                "de": path[j],
                "para": path[j+1],
                "voo": flights[j],
                "duration_minutes": weights[j]
            }
            resultado_json["etapas"].append(etapa)
            
            print(f"  {j+1}. De '{path[j]}' para '{path[j+1]}'")
            print(f"     Voo: {flights[j]}")
            print(f"     Duração: {weights[j]:.0f} min")
        
        json_results_list.append(resultado_json)

    print(f"\n--- SALVANDO ARQUIVO JSON ---")
    print(f"Salvando {len(json_results_list)} exemplos em '{output_json_file}'...")
    
    try:
        with open(output_json_file, 'w', encoding='utf-8') as f:
            json.dump(json_results_list, f, ensure_ascii=False, indent=4) 
        print("Arquivo JSON salvo com sucesso.")
    except Exception as e:
        print(f"ERRO ao salvar o arquivo JSON: {e}")

if __name__ == '__main__':
    main()