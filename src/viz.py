import pandas as pd
from pyvis.network import Network
import matplotlib.pyplot as plt
from collections import deque
import os
import webbrowser

df = pd.read_csv('../data/adjacencias_bairros.csv')
adj = {}
for _, row in df.iterrows():
    u = row['bairro_origem'].strip()
    v = row['bairro_destino'].strip()
    adj.setdefault(u, set()).add(v)
    adj.setdefault(v, set()).add(u)

# Mapa de cores por grau do bairro (mais conexões = cor mais intensa).
net_grau = Network(height="600px", width="100%", directed=False, bgcolor="#ffffff")
max_degree = max(len(v) for v in adj.values())
for bairro, vizinhos in adj.items():
    degree = len(vizinhos)
    color_intensity = int(255 * (degree / max_degree))
    color_hex = f'#{255-color_intensity:02x}{color_intensity:02x}80'
    net_grau.add_node(bairro, label=bairro, color=color_hex)
for u, vizinhos in adj.items():
    for v in vizinhos:
        if u < v:
            net_grau.add_edge(u, v)
net_grau.save_graph("../out/_grau.html")


# Ranking de densidade de ego-subrede por microrregião (barra).
densidade = {}
for bairro, vizinhos in adj.items():
    k = len(vizinhos)
    if k <= 1:
        densidade[bairro] = 0
    else:
        links = sum(1 for u in vizinhos for v in vizinhos if u != v and v in adj[u]) / 2
        densidade[bairro] = links / (k*(k-1)/2)

sorted_bairros = sorted(densidade.items(), key=lambda x: x[1], reverse=True)

bairros, valores = zip(*sorted_bairros)
plt.figure(figsize=(10,6))
plt.bar(bairros, valores, color='purple')
plt.xticks(rotation=45, ha='right')
plt.ylabel("Densidade da ego-subrede")
plt.title("Ranking de densidade de ego-subrede por bairro")
plt.tight_layout()
plt.savefig("../out/_densidade.png", dpi=300)
plt.close()

# Subgrafo dos 10 bairros com maior grau (graph view).
top10 = sorted(adj.items(), key=lambda x: len(x[1]), reverse=True)[:10]
top_bairros = set(b for b,_ in top10)
net_top10 = Network(height="600px", width="100%", directed=False, bgcolor="#ffffff")
for bairro in top_bairros:
    net_top10.add_node(bairro, label=bairro, color="#1f77b4")
for u in top_bairros:
    for v in adj[u]:
        if v in top_bairros and u < v:
            net_top10.add_edge(u, v, color="red", width=2)
net_top10.save_graph("../out/_top10.html")

# Distribuição dos graus (histograma).
plt.figure(figsize=(8,5))
graus = [len(v) for v in adj.values()]
plt.hist(graus, bins=range(1, max(graus)+2), color='skyblue', edgecolor='black')
plt.xlabel("Grau do bairro")
plt.ylabel("Número de bairros")
plt.title("Distribuição dos graus dos bairros")
plt.tight_layout()
plt.savefig("../out/_histograma.png", dpi=300)
plt.close()

# Árvore BFS a partir de um polo (Recife "Antigo") para visualizar camadas (níveis).
def bfs_tree(adj, root):
    visited = {root}
    queue = deque([(root, 0)])
    tree_edges = []
    levels = {root: 0}
    while queue:
        node, lvl = queue.popleft()
        for neighbor in adj[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, lvl+1))
                tree_edges.append((node, neighbor))
                levels[neighbor] = lvl+1
    return tree_edges, levels

edges, levels = bfs_tree(adj, "Recife")
plt.figure(figsize=(10,6))
pos = {}
y_gap = 1
for node, lvl in levels.items():
    pos[node] = (lvl, -list(levels.keys()).index(node)*y_gap)
for u,v in edges:
    x_values = [pos[u][0], pos[v][0]]
    y_values = [pos[u][1], pos[v][1]]
    plt.plot(x_values, y_values, color='red', linewidth=1)
for node, (x, y) in pos.items():
    plt.scatter(x, y, s=200, color='#1f77b4')
    plt.text(x, y, node, fontsize=8, ha='center', va='center', color='white')
plt.axis('off')
plt.title("Árvore BFS a partir do Recife Antigo")
plt.tight_layout()
plt.savefig("../out/_bfs.png", dpi=300)
plt.close()

# ---------------------------
# HTML combinado com dropdown
# ---------------------------
with open("../out/insights.html", "w", encoding="utf-8") as f:
    f.write("""
<html>
<head>
<title>Insights Grafo Recife</title>
</head>
<body>
<h2>Escolha a visualização:</h2>
<select id="graficoSelect" onchange="showGraph()">
<option value="">-- Escolha uma visualização --</option>
<option value="grau">Grau dos bairros</option>
<option value="densidade">Densidade da ego-subrede</option>
<option value="top10">Top 10 bairros por grau</option>
<option value="histograma">Distribuição dos graus</option>
<option value="bfs">Árvore BFS a partir do Recife Antigo</option>
</select>

<div id="grau" style="display:none">
<iframe src="_grau.html" width="100%" height="600px" frameborder="0"></iframe>
</div>
<div id="densidade" style="display:none">
<iframe src="_densidade.png" width="100%" height="600px" frameborder="0"></iframe>
</div>
<div id="top10" style="display:none">
<iframe src="_top10.html" width="100%" height="600px" frameborder="0"></iframe>
</div>
<center>
<div id="histograma" style="display:none">
<img src="_histograma.png" width="60%">
</div>
</center>
<div id="bfs" style="display:none">
<img src="_bfs.png" width="100%">
</div>

<script>
function showGraph(){
    let val = document.getElementById('graficoSelect').value;
    ['grau','densidade','top10','histograma','bfs'].forEach(id=>{
        document.getElementById(id).style.display = 'none';
    });
    if(val) document.getElementById(val).style.display = 'block';
}
</script>

</body>
</html>
""")

print("HTML combinado gerado")
webbrowser.open(f"file://{os.path.abspath('../out/insights.html')}")