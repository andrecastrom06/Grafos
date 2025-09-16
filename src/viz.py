# (bônus) visualizações/UX
# tem que corrigir
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

df = pd.read_csv("../data/adjacencias_bairros.csv")  

G = nx.Graph()

for _, row in df.iterrows():
    G.add_edge(row["bairro_origem"], row["bairro_destino"], logradouro=row["logradouro"])

pos = nx.spring_layout(G, seed=42)

nx.draw(G, pos, with_labels=True, node_size=2000, node_color="lightblue", font_size=10)

edge_labels = nx.get_edge_attributes(G, "logradouro")
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

plt.show()