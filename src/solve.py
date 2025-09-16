#construção dos json /out

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

    def ordem(self):
        return len(self.adj)

    def tamanho(self):
        return sum(len(viz) for viz in self.adj.values())//2

    def densidade(self):
        V = self.ordem()
        E = self.tamanho()
        if V < 2:
            return 0
        return (2 * E) / (V * (V - 1))
    
    def subgrafo(self, vertices):
        sg = Grafo()
        vertices_set = set(vertices)
        for u in vertices_set:
            if u in self.adj:
                for v, logradouro in self.adj[u]:
                    if v in vertices_set and u < v:
                        sg.adicionar_aresta(u, v, logradouro)
        return sg


df = pd.read_csv("../data/adjacencias_bairros.csv")  

grafo = Grafo()

for _, row in df.iterrows():
    grafo.adicionar_aresta(row["bairro_origem"], row["bairro_destino"], row["logradouro"])

with open("../out/recife_global.json", "w") as f:
    f.write("{\n")
    f.write("  \"Ordem\": " + str(grafo.ordem()) + ",\n")
    f.write("  \"Tamanho\": " + str(grafo.tamanho()) + ",\n")
    f.write("  \"Densidade\": " + str(grafo.densidade()) + "\n")
    f.write("}")

df_microrregiao = pd.read_csv("../data/bairros_unique.csv")

resultados = []
for micro, grupo in df_microrregiao.groupby("microrregiao"):
    bairros = grupo["bairro"].tolist()
    sg = grafo.subgrafo(bairros)
    resultados.append({
        "microrregiao": int(micro),
        "ordem": sg.ordem(),
        "tamanho": sg.tamanho(),
        "densidade": round(sg.densidade(), 4)
    })

with open("../out/microrregioes.json", "w", encoding="utf-8") as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)

ego_resultados = []
for bairro in grafo.adj.keys():
    viz = grafo.vizinhos(bairro)
    ego_vertices = [bairro] + viz
    sg = grafo.subgrafo(ego_vertices)

    ego_resultados.append({
        "bairro": bairro,
        "grau": len(viz),
        "ordem_ego": sg.ordem(),
        "tamanho_ego": sg.tamanho(),
        "densidade_ego": round(sg.densidade(), 4)
    })

df_ego = pd.DataFrame(ego_resultados)
with open("../out/ego_bairros.json", "w", encoding="utf-8") as f:
    json.dump(ego_resultados, f, ensure_ascii=False, indent=2)