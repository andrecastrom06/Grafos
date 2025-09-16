# construção dos json /out

import pandas as pd
import json

class Grafo:
    def __init__(self):
        self.adj = {}

    def adicionar_aresta(self, u, v, logradouro=None):
        if u not in self.adj:
            self.adj[u] = []
        if v not in self.adj:
            self.adj[v] = []
        self.adj[u].append((v, logradouro))
        self.adj[v].append((u, logradouro))

    def vizinhos(self, u):
        return [v for v, _ in self.adj.get(u, [])]
    
    def grau(self, u):
        return len(self.adj.get(u, []))

    def ordem(self):
        return len(self.adj)

    def tamanho(self):
        return sum(len(viz) for viz in self.adj.values()) // 2

    def densidade(self):
        V = self.ordem()
        E = self.tamanho()
        if V < 2:
            return 0
        return (2 * E) / (V * (V - 1))
    
    def subgrafo(self, vertices):
        sg = Grafo()
        for v in vertices:
            if v not in sg.adj:
                sg.adj[v] = []
                
        vertices_set = set(vertices)
        for u in vertices_set:
            if u in self.adj:
                for v, logradouro in self.adj[u]:
                    if v in vertices_set and u < v:
                        sg.adicionar_aresta(u, v, logradouro)
        return sg

df_adjacencias = pd.read_csv("../data/adjacencias_bairros.csv")
df_microrregiao = pd.read_csv("../data/bairros_unique.csv")

grafo = Grafo()

for _, row in df_adjacencias.iterrows():
    grafo.adicionar_aresta(row["bairro_origem"], row["bairro_destino"], row["logradouro"])

for bairro in df_microrregiao['bairro']:
    if bairro not in grafo.adj:
        grafo.adj[bairro] = []
        
dados_globais = {
    "ordem": grafo.ordem(),
    "tamanho": grafo.tamanho(),
    "densidade": round(grafo.densidade(), 4)
}
with open("../out/recife_global.json", "w", encoding="utf-8") as f:
    json.dump(dados_globais, f, ensure_ascii=False, indent=2)

resultados_microrregiao = []
for micro, grupo in df_microrregiao.groupby("microrregiao"):
    bairros = grupo["bairro"].tolist()
    sg = grafo.subgrafo(bairros)
    resultados_microrregiao.append({
        "microrregiao": int(micro),
        "ordem": sg.ordem(),
        "tamanho": sg.tamanho(),
        "densidade": round(sg.densidade(), 4)
    })
with open("../out/microrregioes.json", "w", encoding="utf-8") as f:
    json.dump(resultados_microrregiao, f, ensure_ascii=False, indent=2)

resultados_ego = []
for bairro in sorted(grafo.adj.keys()):
    vizinhos = grafo.vizinhos(bairro)
    ego_vertices = [bairro] + vizinhos
    sg_ego = grafo.subgrafo(ego_vertices)

    resultados_ego.append({
        "bairro": bairro,
        "grau": grafo.grau(bairro),
        "ordem_ego": sg_ego.ordem(),
        "tamanho_ego": sg_ego.tamanho(),
        "densidade_ego": round(sg_ego.densidade(), 4)
    })
df_ego = pd.DataFrame(resultados_ego)
df_ego.to_csv("../out/ego_bairro.csv", index=False, encoding='utf-8')

graus_data = [{"bairro": bairro, "grau": grafo.grau(bairro)} for bairro in sorted(grafo.adj.keys())]
df_graus = pd.DataFrame(graus_data).sort_values(by='grau', ascending=False)
df_graus.to_csv('../out/graus.csv', index=False, encoding='utf-8')

idx_mais_denso = df_ego['densidade_ego'].idxmax()
bairro_mais_denso_info = df_ego.loc[idx_mais_denso]

bairro_maior_grau_info = df_graus.iloc[0]

print(f"Bairro mais denso: {bairro_mais_denso_info['bairro']} (Densidade Ego: {bairro_mais_denso_info['densidade_ego']})")
print(f"Bairro com maior grau: {bairro_maior_grau_info['bairro']} (Grau: {bairro_maior_grau_info['grau']})")

print("\n✅ Análise concluída com sucesso!")