# BFS, DFS, Dijkstra, Bellman–Ford

import heapq
import json
from graph import build_game_graph 

def create_adjacency_list(edge_list_with_genre):
    
    adj = {}
    for u, v, w, genre in edge_list_with_genre:
        adj.setdefault(u, []).append((v, w, genre))
        adj.setdefault(v, []).append((u, w, genre))
    return adj

def dijkstra(adj, src, dst):
    if src not in adj or dst not in adj:
        return float('inf'), [], [], []
    
    dist = {n: float('inf') for n in adj}
    prev = {n: None for n in adj}
    prev_street = {n: None for n in adj}
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
                prev_street[v] = log 
                prev_weight[v] = w
                heapq.heappush(pq, (nd, v))
                
    if dist[dst] == float('inf'):
        return float('inf'), [], [], []
        
    path, streets, weights = [], [], []
    cur = dst
    
    while cur:
        path.append(cur)
        if prev_street[cur]: 
            streets.append(prev_street[cur])
            weights.append(prev_weight[cur])
        cur = prev[cur]
        
    path.reverse()
    streets.reverse()
    weights.reverse()
    
    return dist[dst], path, streets, weights

def main():
    
    print("--- Iniciando busca de caminho no Grafo de Jogos Steam ---")
    
    csv_file_path = '../../data/steam_filtrado.csv'
    src_game = "Counter-Strike"
    dst_game = "Ricochet" 

    nodes_data, edge_list = build_game_graph(csv_file_path)
    
    print("\nCriando lista de adjacência para o algoritmo...")
    adj = create_adjacency_list(edge_list)
    print("Lista de adjacência criada.")

    if src_game not in adj:
        print(f"\nERRO: Jogo de origem '{src_game}' não foi encontrado ou não tem arestas.")
        return 
    if dst_game not in adj:
        print(f"\nERRO: Jogo de destino '{dst_game}' não foi encontrado ou não tem arestas.")
        return

    print(f"\nBuscando menor caminho de '{src_game}' para '{dst_game}'...")
    
    cost, path, genres, weights = dijkstra(adj, src_game, dst_game)
    
    print("\n--- RESULTADO DA BUSCA (Console) ---")
    
    resultado_json = {
        "no_de_saida": src_game,
        "no_de_entrada": dst_game,
        "caminho": None, 
        "peso": None     
    }
    
    if cost == float('inf'):
        print(f"Não foi encontrado um caminho conectando '{src_game}' e '{dst_game}'.")
        resultado_json["caminho"] = "Nenhum caminho encontrado"
        resultado_json["peso"] = "INF"
    else:
        print(f"Caminho encontrado!")
        print(f"Custo total (Popularidade): {cost:.2f}")
        print(f"\nPercurso do Caminho ({len(path)} nós):")
        print(" -> ".join(path))    
        print(f"\nEtapas da Conexão ({len(genres)} arestas):")
        for i in range(len(genres)):
            print(f"  {i+1}. De '{path[i]}' para '{path[i+1]}'")
            print(f"     Gênero em comum: {genres[i]}")
            print(f"     Peso da aresta: {weights[i]:.2f}")
            
        resultado_json["caminho"] = path
        resultado_json["peso"] = cost

    output_json_file = '../../out/dijkstra.json'
    print(f"\n--- SALVANDO ARQUIVO JSON ---")
    print(f"Salvando resultado em '{output_json_file}'...")
    
    try:
        with open(output_json_file, 'w', encoding='utf-8') as f:
            json.dump(resultado_json, f, ensure_ascii=False)
        print("Arquivo JSON salvo com sucesso.")
    except Exception as e:
        print(f"ERRO ao salvar o arquivo JSON: {e}")

if __name__ == '__main__':
    main()