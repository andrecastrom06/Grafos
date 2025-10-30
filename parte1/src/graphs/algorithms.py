import pandas as pd
import heapq
import json
import re

def normalize_name(name):
    # remove espaços extras e normaliza caixa
    return re.sub(r'\s+', ' ', str(name).strip().title())

def load_graph(path):
    df = pd.read_csv(path)
    adj = {}
    for _, row in df.iterrows():
        u = normalize_name(row['bairro_origem'])
        v = normalize_name(row['bairro_destino'])
        w = float(row['peso']) if 'peso' in df.columns else 1.0
        log = str(row['logradouro']).strip() if 'logradouro' in df.columns else ''
        
        # adiciona u -> v e v -> u garantido
        adj.setdefault(u, []).append((v, w, log))
        adj.setdefault(v, []).append((u, w, log))
    return adj

def dijkstra(adj, src, dst):
    src, dst = normalize_name(src), normalize_name(dst)
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
    adj = load_graph('../../data/adjacencias_bairros.csv')
    df = pd.read_csv('../../data/enderecos.csv')
    results = []

    for _, r in df.iterrows():
        bx, by = normalize_name(r['bairro_origem']), normalize_name(r['bairro_destino'])
        cost, path, streets, weights = dijkstra(adj, bx, by)
        cost_fmt = round(cost, 2) if cost != float('inf') else 'INF'
        results.append([bx, by, cost_fmt, '->'.join(path), '->'.join(streets)])

    out_df = pd.DataFrame(results, columns=['bairro_X','bairro_Y','custo','caminho','ruas'])
    out_df.to_csv('../../out/distancias_enderecos.csv', index=False)

    cost, path, streets, weights = dijkstra(adj, 'Nova Descoberta', 'Boa Viagem')
    with open('../../out/percurso_nova_descoberta_setubal.json','w',encoding='utf-8') as f:
        json.dump({
            'bairro_X': 'Nova Descoberta',
            'bairro_Y': 'Boa Viagem',
            'custo': round(cost, 2),
            'caminho': path,
            'ruas': streets,
            'pesos': [round(w, 2) for w in weights]
        }, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()