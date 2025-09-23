# (obrigatórios, mínimos)
import pandas as pd
import json
import heapq

def subgraph(adj, allowed_nodes):
    """Filtra o grafo para conter apenas os nós em allowed_nodes"""
    sub = {}
    for u in allowed_nodes:
        if u in adj:
            # mantem apenas vizinhos dentro do conjunto permitido
            sub[u] = [(v, w, log) for v, w, log in adj[u] if v in allowed_nodes]
    return sub

def load_graph(path):
    df = pd.read_csv(path)
    adj = {}
    for _, row in df.iterrows():
        u = str(row['bairro_origem']).strip()
        v = str(row['bairro_destino']).strip()
        w = float(row['peso']) if 'peso' in df.columns else 1.0
        log = str(row['logradouro']).strip() if 'logradouro' in df.columns else ''
        adj.setdefault(u, []).append((v, w, log))
        adj.setdefault(v, []).append((u, w, log))
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
        if u == dst: break
        if d > dist[u]: continue
        for v, w, log in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v], prev[v], prev_street[v], prev_weight[v] = nd, u, log, w
                heapq.heappush(pq, (nd, v))
    if dist[dst] == float('inf'):
        return float('inf'), [], [], []
    path, streets, weights, cur = [], [], [], dst
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
    adj = load_graph('../data/adjacencias_bairros.csv')

    allowed = {"Madalena", "Cordeiro", "Boa Viagem"}

    sub = subgraph(adj, allowed)

    cost, path, streets, weights = dijkstra(sub, "Madalena", "Boa Viagem")

    print("Custo:", cost)
    print("Caminho:", " -> ".join(path))
    print("Ruas:", " -> ".join(streets))

    with open('../out/percurso_subgrafo.json','w',encoding='utf-8') as f:
        json.dump({
            'bairro_X': "Madalena",
            'bairro_Y': "Boa Viagem",
            'custo': cost,
            'caminho': path,
            'ruas': streets,
            'pesos': weights
        }, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()