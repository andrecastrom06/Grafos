import json
import pandas as pd
from pyvis.network import Network
import matplotlib.pyplot as plt
import streamlit as st
import streamlit.components.v1 as components
from io import BytesIO

st.set_page_config(page_title="Grafo Recife", layout="wide")

# Colunas para centralizar conteúdo
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.title("Projeto Grafos - Recife")
    st.image("../foto_capa.jpg", width=500)

    # -----------------------------
    # Carrega dados
    # -----------------------------
    df_adj = pd.read_csv('../data/adjacencias_bairros.csv')
    adj = {}
    for _, row in df_adj.iterrows():
        u = row['bairro_origem'].strip()
        v = row['bairro_destino'].strip()
        adj.setdefault(u, set()).add(v)
        adj.setdefault(v, set()).add(u)

    with open('../out/percurso_nova_descoberta_setubal.json', encoding='utf-8') as f:
        percurso = json.load(f)

    caminho = percurso['caminho']
    ruas = percurso.get('ruas', [])
    pesos = percurso.get('pesos', [])

    # -----------------------------
    # Dropdown de visualização
    # -----------------------------
    opcao = st.selectbox(
        "Escolha a visualização",
        ["", 
         "Percurso Nova Descoberta → Boa Viagem", 
         "Grau dos bairros", "Top 10 bairros por grau", 
         "Distribuição dos graus"]
    )

    # -----------------------------
    # Funções auxiliares
    # -----------------------------
    def gera_grafo_html(caminho, ruas=None, pesos=None, cor_nos="#1f77b4", cor_arestas="#FF0000", espessura=3):
        net = Network(height="600px", width="100%", directed=True, bgcolor="#ffffff")
        net.barnes_hut()
        for bairro in caminho:
            net.add_node(bairro, label=bairro, color=cor_nos, shape="ellipse")
        for i in range(len(caminho)-1):
            origem = caminho[i]
            destino = caminho[i+1]
            rua = ruas[i] if ruas and i < len(ruas) else ""
            peso = pesos[i] if pesos and i < len(pesos) else ""
            label = f"{rua} ({peso})" if peso else rua
            net.add_edge(origem, destino, label=label, color=cor_arestas, width=espessura)
        path_html = "../out/temp.html"
        net.save_graph(path_html)
        with open(path_html, "r", encoding="utf-8") as f:
            return f.read()

    def plot_to_bytes(fig):
        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        return buf

    # -----------------------------
    # Renderiza visualizações
    # -----------------------------
    if opcao == "Percurso Nova Descoberta → Boa Viagem":
        cor_nos = st.color_picker("Cor dos bairros", "#1f77b4")
        cor_arestas = st.color_picker("Cor do percurso", "#FF0000")
        espessura = st.slider("Espessura das arestas", 1, 10, 3)
        st.subheader("Percurso interativo")
        html = gera_grafo_html(caminho, ruas, pesos, cor_nos, cor_arestas, espessura)
        components.html(html, height=600, width=800)

    elif opcao == "Grau dos bairros":
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
        path_html = "../out/temp_grau.html"
        net_grau.save_graph(path_html)
        with open(path_html, "r", encoding="utf-8") as f:
            components.html(f.read(), height=600, width=800)

    elif opcao == "Top 10 bairros por grau":
        top10 = sorted(adj.items(), key=lambda x: len(x[1]), reverse=True)[:10]
        top_bairros = set(b for b,_ in top10)
        net_top10 = Network(height="600px", width="100%", directed=False, bgcolor="#ffffff")
        for bairro in top_bairros:
            net_top10.add_node(bairro, label=bairro, color="#1f77b4")
        for u in top_bairros:
            for v in adj[u]:
                if v in top_bairros and u < v:
                    net_top10.add_edge(u, v, color="red", width=2)
        path_html = "../out/temp_top10.html"
        net_top10.save_graph(path_html)
        with open(path_html, "r", encoding="utf-8") as f:
            components.html(f.read(), height=600, width=800)

    elif opcao == "Distribuição dos graus":
        graus = [len(v) for v in adj.values()]
        fig, ax = plt.subplots(figsize=(8,5))
        ax.hist(graus, bins=range(1, max(graus)+2), color='skyblue', edgecolor='black')
        plt.xlabel("Grau do bairro")
        plt.ylabel("Número de bairros")
        plt.title("Distribuição dos graus dos bairros")
        st.image(plot_to_bytes(fig), use_container_width=True)