import streamlit as st
import json
import networkx as nx
from pyvis.network import Network
import tempfile
import os


def create_networkx_graph(data: list, algoritmo: str) -> nx.DiGraph:
    """
    Lê os dados (lista de exemplos) e cria o objeto DiGraph do NetworkX.
    Modificado para aceitar uma lista de dados, não um caminho de arquivo.
    """
    G = nx.DiGraph()
    exemplos = data if isinstance(data, list) else [data]

    if not exemplos:
        return G

    if "etapas" in exemplos[0] and "origem" in exemplos[0]:
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
            etapas = exemplo.get("etapas", [])

            voo_map = {(e["de"], e["para"]): e.get("voo", "—") for e in etapas}

            for i in range(len(ordem) - 1):
                u, v = ordem[i], ordem[i + 1]
                nome_voo = voo_map.get((u, v), "—")
                G.add_edge(
                    u, v,
                    label=f"{nome_voo} (Passo {i+1})",
                    title=f"Voo: {nome_voo} | Passo {i+1}"
                )

            for c in ciclos:
                G.add_edge(
                    c[0], c[1],
                    label="Ciclo",
                    color="#FF007F",
                    title="Ciclo Detectado"
                )
    else:
        st.warning(f"Formato de dados não reconhecido para o algoritmo {algoritmo}.")

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

    tmp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".html").name
    net.save_graph(tmp_path)
    return tmp_path



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

    st.title("Visualizador dos vôos")
    st.write("Explore dinamicamente os resultados dos algoritmos de grafos com estilo neon ⚡")

    st.markdown("### ⚙️ Escolha o algoritmo para visualizar")
    
    algoritmos = {
        "BFS": "../out/percurso_voo_bfs.json",
        "DFS": "../out/percurso_voo_dfs.json",
        "Dijkstra": "../out/percurso_voo_dijkstra_todos_para_todos.json", # CORRIGIDO
        "Bellman-Ford": "../out/percurso_voo_bellman_ford.json"
    }
    


    algoritmo = st.selectbox("Selecione o algoritmo:", [""] + list(algoritmos.keys()), index=0)

    if algoritmo == "":
        st.info("👈 Escolha um algoritmo acima para iniciar a visualização.")
        st.stop()

    json_path = algoritmos[algoritmo]
    
    if not os.path.exists(json_path):
        st.error(f"❌ Arquivo não encontrado: {json_path}")
        st.write(f"Caminho absoluto verificado: {os.path.abspath(json_path)}")
        st.error(f"Verifique se o arquivo '{algoritmos[algoritmo]}' existe na pasta 'out'.")
        st.stop()


    physics_config = {
        "gravity": -25000,
        "central_gravity": 0.3,
        "spring_length": 140,
        "spring_strength": 0.05
    }

    origem = None
    destino = None
    G = nx.DiGraph() 
    data = [] 

    
    if algoritmo in ["Dijkstra", "Bellman-Ford"]:
        st.sidebar.markdown(f"<div class='highlight-box'><h3>✈️ Seleção de Rota ({algoritmo} Pré-calculado)</h3>", unsafe_allow_html=True)

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f) 

        all_origins = sorted(list(set(ex.get("origem") for ex in data if "origem" in ex)))
        all_destinations = sorted(list(set(ex.get("destino") for ex in data if "destino" in ex)))
        
        all_nodes = set()
        for ex in data:
            for etapa in ex.get("etapas", []):
                all_nodes.add(etapa["de"])
                all_nodes.add(etapa["para"])
        
        G.add_nodes_from(sorted(list(all_nodes)))

        origem = st.sidebar.selectbox("Aeroporto de Origem:", [""] + all_origins, key="origem_select")
        destino = st.sidebar.selectbox("Aeroporto de Destino:", [""] + all_destinations, key="destino_select")

        st.sidebar.markdown("</div>", unsafe_allow_html=True)
        
        if not origem or not destino:
            st.info(" Selecione uma origem e um destino no sidebar para visualizar um caminho.")
        
        elif origem == destino:
            st.warning(" O aeroporto de origem e destino são iguais. Escolha dois diferentes.")
        
        else:
            matching_example = next((ex for ex in data if ex['origem'] == origem and ex['destino'] == destino), None)
            
            if matching_example:
                G = create_networkx_graph([matching_example], algoritmo) 
                
                path = matching_example['caminho']
                length = matching_example['custo_total_minutos']

                st.success(f" Caminho pré-calculado de **{origem}** até **{destino}** ({algoritmo}):")
                st.info(" → ".join(path))
                st.metric("Duração total (min)", f"{length:.1f}")

                # Lógica de destaque
                edges_in_path = list(zip(path[:-1], path[1:]))
                for (u, v) in G.edges():
                    if (u, v) in edges_in_path:
                        G[u][v]["color"] = "#FFD700" 
                        G[u][v]["width"] = 4
                
                if origem in G.nodes:
                    G.nodes[origem]["color"] = "#00FF88" 
                    G.nodes[origem]["size"] = 25
                if destino in G.nodes:
                    G.nodes[destino]["color"] = "#FF3366" 
                    G.nodes[destino]["size"] = 25

            else:
                st.error(f"❌ Nenhum caminho pré-calculado encontrado de {origem} para {destino} no arquivo JSON.")


    elif algoritmo in ["BFS", "DFS"]:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        G = create_networkx_graph(data, algoritmo)
        
        mostrar_ciclos = st.checkbox("Mostrar arestas de ciclos", value=True)
        if not mostrar_ciclos:
            edges_to_remove = [(u, v) for u, v, data in G.edges(data=True)
                               if "Ciclo" in data.get("label", "")]
            G.remove_edges_from(edges_to_remove)


    st.sidebar.subheader(" Métricas do Grafo (Visão Atual)")
    col1, col2 = st.sidebar.columns(2)
    col1.metric("Nós (Aeroportos)", G.number_of_nodes())
    col2.metric("Arestas (Voos)", G.number_of_edges())

    graph_path = create_pyvis_html(G, physics_config, f"{algoritmo}-{origem}-{destino}")

    with open(graph_path, "r", encoding="utf-8") as f:
        html = f.read()

    st.components.v1.html(html, height=750, scrolling=False)

    st.markdown("---")
    st.caption("Projeto de grafos parte dois")


if __name__ == "__main__":
    main()