# BFS, DFS, Dijkstra, Bellman–Ford

import heapq
import json
from graph import build_directed_graph 

def dijkstra(adj, src, dst):
    if src not in adj or dst not in adj:
        print(f"Erro: Origem '{src}' ou Destino '{dst}' não está no grafo.")
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
    
        if u not in adj:
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
    print("--- Iniciando busca de Rota Aérea (Dijkstra) ---")
    
    
    csv_file_path = '../../data/flight_filtrado.csv'
    output_json_file = '../../out/resultado_voo.json'
    src_country = "Algeria"
    dst_country = "Argentina"

    adj = build_directed_graph(csv_file_path)
    
    if src_country not in adj:
        print(f"\nERRO: País de origem '{src_country}' não foi encontrado no grafo.")
        return
    if dst_country not in adj:
        print(f"\nERRO: País de destino '{dst_country}' não foi encontrado no grafo.")
        return

    print(f"\nBuscando rota mais curta (em minutos) de '{src_country}' para '{dst_country}'...")
    
    cost, path, flights, weights = dijkstra(adj, src_country, dst_country)
    
    resultado_json = {
        "origem": src_country,
        "destino": dst_country,
        "custo_total_minutos": cost if cost != float('inf') else "INF",
        "caminho": path if path else "Nenhum caminho encontrado",
        "etapas": []
    }

    print("\n--- RESULTADO DA BUSCA ---")
    if cost == float('inf'):
        print(f"Não foi encontrado um caminho conectando '{src_country}' e '{dst_country}'.")
    else:
        print(f"Rota encontrada!")
        print(f"Custo total (Duração): {cost:.0f} minutos")
        
        print(f"\nPercurso do Caminho ({len(path)} países):")
        print(" -> ".join(path))
        
        print(f"\nEtapas da Viagem ({len(flights)} voos):")
        for i in range(len(flights)):
            etapa = {
                "de": path[i],
                "para": path[i+1],
                "voo": flights[i],
                "duracao_minutos": weights[i]
            }
            resultado_json["etapas"].append(etapa)
            
            print(f"  {i+1}. De '{path[i]}' para '{path[i+1]}'")
            print(f"     Voo: {flights[i]}")
            print(f"     Duração: {weights[i]:.0f} min")

    print(f"\n--- SALVANDO ARQUIVO JSON ---")
    print(f"Salvando resultado em '{output_json_file}'...")
    
    try:
        with open(output_json_file, 'w', encoding='utf-8') as f:
            json.dump(resultado_json, f, ensure_ascii=False, indent=4) 
        print("Arquivo JSON salvo com sucesso.")
    except Exception as e:
        print(f"ERRO ao salvar o arquivo JSON: {e}")

if __name__ == '__main__':
    main()