import streamlit as st
import json
import networkx as nx
from pyvis.network import Network
import tempfile
import os

# --- Funções de Geração do Grafo ---

def create_networkx_graph(json_path: str, algoritmo: str) -> nx.DiGraph:
    """Lê o JSON e cria o objeto DiGraph do NetworkX."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    G = nx.DiGraph()
    exemplos = data if isinstance(data, list) else [data]

    if "etapas" in exemplos[0]:
        for exemplo in exemplos:
            for etapa in exemplo.get("etapas", []):
                G.add_edge(
                    etapa["de"],
                    etapa["para"],
                    label=f"{etapa['voo']} ({etapa['duration_minutes']} min)",
                    weight=etapa["duration_minutes"],
                    title=f"Voo: {etapa['voo']}\nDuração: {etapa['duration_minutes']} min"
                )
    elif algoritmo in ["BFS", "DFS"]:
        for exemplo in exemplos:
            resultado = exemplo.get(algoritmo.lower(), {})
            ordem = resultado.get("visited_order", [])
            ciclos = resultado.get("cycles", [])
            for i in range(len(ordem) - 1):
                G.add_edge(ordem[i], ordem[i+1], label=f"Passo {i+1}", title=f"Passo {i+1}")
            for c in ciclos:
                G.add_edge(c[0], c[1], label="Ciclo", color="#FF007F", title="Ciclo Detectado")
    else:
        raise ValueError(f"Formato de JSON desconhecido para o algoritmo {algoritmo}.")

    return G


def create_pyvis_html(G: nx.DiGraph, physics_config: dict, cache_key: str) -> str:
    """Cria a visualização do PyVis."""
    net = Network(
        height="750px",
        width="100%",
        bgcolor="#000000",
        font_color="#00BFFF",
        directed=True,
        notebook=False
    )

    for node, data in G.nodes(data=True):
        net.add_node(
            node,
            label=node,
            color=data.get("color", "#0A84FF"),
            size=data.get("size", 18),
            title=f"Aeroporto: {node}",
            font={"size": 14, "color": "#FFFFFF", "face": "Consolas"}
        )

    for u, v, data_edge in G.edges(data=True):
        net.add_edge(
            u, v,
            label=data_edge.get("label", ""),
            color=data_edge.get("color", "#33A1FD"),
            width=data_edge.get("width", 2),
            arrows="to",
            title=data_edge.get("title", data_edge.get("label", ""))
        )

    net.barnes_hut(
        gravity=physics_config["gravity"],
        central_gravity=physics_config["central_gravity"],
        spring_length=physics_config["spring_length"],
        spring_strength=physics_config["spring_strength"],
        damping=0.09,
        overlap=0
    )

    net.show_buttons(filter_=['physics'])

    tmp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".html").name
    net.save_graph(tmp_path)
    return tmp_path


# --- Interface do Streamlit ---

def main():
    st.set_page_config(page_title="Visualizador de Grafos", layout="wide")

    st.markdown("""
        <style>
        .stApp {
            background: radial-gradient(circle at 10% 20%, #000000 0%, #001A33 100%);
            color: #00BFFF;
        }
        h1, h2, h3 {
            color: #33A1FD !important;
            text-shadow: 0 0 12px #007BFF;
            font-family: 'Consolas', 'Courier New', monospace;
        }
        .stSidebar {
            background-color: rgba(0, 10, 20, 0.85) !important;
            backdrop-filter: blur(6px);
        }
        /* Destaque de seleção de aeroportos */
        .highlight-box {
            border: 1px solid #00BFFF;
            border-radius: 10px;
            padding: 12px;
            margin-bottom: 20px;
            background: rgba(0, 20, 40, 0.7);
            box-shadow: 0 0 15px #007BFF66;
        }
        .stSelectbox label {
            color: #33CCFF !important;
            font-weight: bold;
            text-shadow: 0 0 6px #0099FF;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("💠 Visualizador Futurista de Grafos")
    st.write("Explore dinamicamente os resultados dos algoritmos de grafos com estilo neon.")

    st.sidebar.header("🚀 Controles")
    algoritmos = {
        "BFS": "../out/percurso_voo_bfs.json",
        "DFS": "../out/percurso_voo_dfs.json",
        "Dijkstra": "../out/percurso_voo_dijkstra.json",
        "Bellman-Ford": "../out/percurso_voo_bellman_ford.json"
    }

    algoritmo = st.sidebar.selectbox("Selecione o algoritmo:", list(algoritmos.keys()))
    json_path = algoritmos[algoritmo]

    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Ajustes de Física (Barnes-Hut)")

    physics_config = {
        "gravity": st.sidebar.slider("Gravidade (Atração)", -50000, 0, -25000, step=1000),
        "central_gravity": st.sidebar.slider("Gravidade Central", 0.0, 1.0, 0.3, step=0.05),
        "spring_length": st.sidebar.slider("Comprimento da Mola", 50, 500, 140, step=10),
        "spring_strength": st.sidebar.slider("Força da Mola", 0.01, 0.2, 0.05, step=0.01)
    }

    st.sidebar.markdown("---")

    # Seleção de origem/destino
    origem = destino = None
    if algoritmo in ["Dijkstra", "Bellman-Ford"]:
        st.sidebar.markdown("<div class='highlight-box'><h3>✈️ Seleção de Aeroportos</h3>", unsafe_allow_html=True)

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        nodes = set()
        for exemplo in data if isinstance(data, list) else [data]:
            for etapa in exemplo.get("etapas", []):
                nodes.add(etapa["de"])
                nodes.add(etapa["para"])
        nodes = sorted(list(nodes))

        origem = st.sidebar.selectbox("Aeroporto de Origem:", nodes, key="origem_select")
        destino = st.sidebar.selectbox("Aeroporto de Destino:", nodes, key="destino_select")

        st.sidebar.markdown("</div>", unsafe_allow_html=True)

    # Renderização do grafo
    if not os.path.exists(json_path):
        st.error(f"❌ Arquivo não encontrado: {os.path.abspath(json_path)}")
        st.stop()

    G = create_networkx_graph(json_path, algoritmo)

  # 🚀 Cálculo do caminho mínimo
    if algoritmo in ["Dijkstra", "Bellman-Ford"] and origem and destino:
        # Verifica se origem e destino são iguais
        if origem == destino:
            st.warning("⚠️ O aeroporto de origem e destino são iguais. Escolha dois diferentes.")
        else:
            try:
                if algoritmo == "Dijkstra":
                    path = nx.dijkstra_path(G, origem, destino, weight="weight")
                    length = nx.dijkstra_path_length(G, origem, destino, weight="weight")
                else:
                    path = nx.bellman_ford_path(G, origem, destino, weight="weight")
                    length = nx.bellman_ford_path_length(G, origem, destino, weight="weight")

                st.success(f"✈️ Caminho mínimo de **{origem}** até **{destino}** ({algoritmo}):")
                st.info(" → ".join(path))
                st.metric("Duração total (min)", f"{length:.1f}")

                # Destacar o caminho mínimo
                edges_in_path = list(zip(path[:-1], path[1:]))
                for (u, v) in G.edges():
                    if (u, v) in edges_in_path:
                        G[u][v]["color"] = "#FFD700"  # dourado
                        G[u][v]["width"] = 4
                    else:
                        G[u][v]["color"] = "#444"
                        G[u][v]["width"] = 1

                # Destaque de nós origem/destino
                G.nodes[origem]["color"] = "#00FF88"
                G.nodes[origem]["size"] = 25
                G.nodes[destino]["color"] = "#FF3366"
                G.nodes[destino]["size"] = 25

            except nx.NetworkXNoPath:
                st.error(f"❌ Nenhum caminho encontrado entre {origem} e {destino}.")

    # Métricas
    st.sidebar.subheader("📊 Métricas do Grafo")
    col1, col2 = st.sidebar.columns(2)
    col1.metric("Nós (Aeroportos)", G.number_of_nodes())
    col2.metric("Arestas (Voos)", G.number_of_edges())

    # Criação do HTML (sem cache para atualizar automaticamente)
    graph_path = create_pyvis_html(G, physics_config, f"{algoritmo}-{origem}-{destino}")

    with open(graph_path, "r", encoding="utf-8") as f:
        html = f.read()

    st.components.v1.html(html, height=750, scrolling=False)

    st.markdown("---")
    st.caption("🛰️ Projeto de Grafos — Visual Futurista Preto e Azul | PyVis + Streamlit")


if __name__ == "__main__":
    main()
