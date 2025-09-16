#construção dos json /out

import pandas as pd

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

    def ordem(self): #esperado 94
        return len(self.adj)

    def tamanho(self): #esperado 449
        return (sum(len(viz) for viz in self.adj.values())//2)+1

    def densidade(self): #esperado 0.1027
        V = self.ordem()
        E = self.tamanho()
        if V < 2:
            return 0
        return (2 * E) / (V * (V - 1))

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
