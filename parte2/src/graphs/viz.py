import streamlit as st
import json
import networkx as nx
from pyvis.network import Network
import tempfile
import os

# ===================================================
# 🧠 Função para gerar grafo a partir de JSON genérico
# ===================================================
def gerar_grafo(json_path: str, algoritmo: str):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    G = nx.DiGraph()
    exemplos = data if isinstance(data, list) else [data]

    # === Dijkstra / Bellman-Ford (têm "etapas") ===
    if "etapas" in exemplos[0]:
        for exemplo in exemplos:
            for etapa in exemplo.get("etapas", []):
                G.add_edge(
                    etapa["de"],
                    etapa["para"],
                    label=f"{etapa['voo']} ({etapa['duration_minutes']} min)",
                    weight=etapa["duration_minutes"]
                )

    # === BFS / DFS (têm "visited_order" e "cycles") ===
    elif algoritmo in ["BFS", "DFS"]:
        for exemplo in exemplos:
            resultado = exemplo.get(algoritmo.lower(), {})
            ordem = resultado.get("visited_order", [])
            ciclos = resultado.get("cycles", [])
            for i in range(len(ordem) - 1):
                G.add_edge(ordem[i], ordem[i+1], label=f"Passo {i+1}")
            for c in ciclos:
                G.add_edge(c[0], c[1], label="Ciclo", color="#FF007F")

    else:
        raise ValueError("Formato de JSON desconhecido")

    # ==============================
    # 🎨 Estilo futurista preto e azul
    # ==============================
    net = Network(
        height="720px",
        width="100%",
        bgcolor="#000000",
        font_color="#00BFFF",
        directed=True
    )

    net.barnes_hut(
        gravity=-25000,
        central_gravity=0.3,
        spring_length=120,
        spring_strength=0.05
    )

    for node in G.nodes:
        net.add_node(
            node,
            label=node,
            color="#0A84FF",
            size=18,
            title=f"Nó: {node}"
        )

    for u, v, data_edge in G.edges(data=True):
        net.add_edge(
            u,
            v,
            label=data_edge.get("label", ""),
            color=data_edge.get("color", "#33A1FD"),
            width=2,
            arrows="to"
        )

    tmp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".html").name
    net.save_graph(tmp_path)
    return tmp_path


# ===================================================
# 🚀 Interface principal do Streamlit
# ===================================================
def main():
    st.set_page_config(page_title="Visualizador de Grafos", layout="wide")

    # CSS futurista
    st.markdown("""
        <style>
        .stApp {
            background: radial-gradient(circle at 10% 20%, #000000 0%, #001A33 100%);
            color: #00BFFF;
        }
        h1, h2, h3 {
            color: #33A1FD !important;
            text-shadow: 0 0 12px #007BFF;
        }
        .stSelectbox label, .stInfo {
            color: #00BFFF !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("💠 Visualizador Futurista de Grafos")
    st.write("Explore os resultados dos algoritmos BFS, DFS, Dijkstra e Bellman-Ford.")

    algoritmos = {
        "BFS": "../../out/percurso_voo_bfs.json",
        "DFS": "../../out/percurso_voo_dfs.json",
        "Dijkstra": "../../out/percurso_voo_dijkstra.json",
        "Bellman-Ford": "../../out/percurso_voo_bellman_ford.json"
    }

    algoritmo = st.selectbox("Selecione o algoritmo:", list(algoritmos.keys()))
    json_path = algoritmos[algoritmo]

    if not os.path.exists(json_path):
        st.error(f"❌ Arquivo não encontrado: {os.path.abspath(json_path)}")
        st.stop()

    st.info(f"Renderizando grafo gerado pelo algoritmo **{algoritmo}**...")

    try:
        graph_path = gerar_grafo(json_path, algoritmo)
    except Exception as e:
        st.error(f"Erro ao gerar o grafo: {e}")
        st.stop()

    with open(graph_path, "r", encoding="utf-8") as f:
        html = f.read()

    st.components.v1.html(html, height=750, scrolling=True)

    st.markdown("---")
    st.caption("🛰️ Projeto de Grafos — Visual Futurista Preto e Azul | PyVis + Streamlit")


if __name__ == "__main__":
    main()
