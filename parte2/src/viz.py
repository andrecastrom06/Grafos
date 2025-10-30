import streamlit as st
import json
import networkx as nx
from pyvis.network import Network
import tempfile
import os

# --- Funções de Geração do Grafo (Refatoradas) ---

@st.cache_data  # Cacheia a leitura do JSON e criação do grafo NetworkX
def create_networkx_graph(json_path: str, algoritmo: str) -> nx.DiGraph:
    """Lê o JSON e cria o objeto DiGraph do NetworkX."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    G = nx.DiGraph()
    exemplos = data if isinstance(data, list) else [data]

    # Lógica para grafos de caminhos (Dijkstra, Bellman-Ford)
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

    # Lógica para grafos de percurso (BFS, DFS)
    elif algoritmo in ["BFS", "DFS"]:
        for exemplo in exemplos:
            resultado = exemplo.get(algoritmo.lower(), {})
            ordem = resultado.get("visited_order", [])
            ciclos = resultado.get("cycles", [])
            for i in range(len(ordem) - 1):
                G.add_edge(ordem[i], ordem[i+1], label=f"Passo {i+1}", title=f"Passo {i+1}")
            # Destaca ciclos
            for c in ciclos:
                G.add_edge(c[0], c[1], label="Ciclo", color="#FF007F", title="Ciclo Detectado")

    else:
        raise ValueError(f"Formato de JSON desconhecido ou não suportado para o algoritmo {algoritmo}.")

    return G


# --- CORREÇÃO APLICADA AQUI ---
@st.cache_data  # Cacheia a renderização do HTML (rápido ao mudar sliders)
def create_pyvis_html(_G: nx.DiGraph, physics_config: dict, cache_key: str) -> str:
    """
    Cria a visualização do PyVis a partir de um grafo NetworkX.
    _G (com underscore) é ignorado pelo cache do Streamlit.
    cache_key (string simples) força o cache a recarregar quando o algoritmo muda.
    """
    
    net = Network(
        height="750px",
        width="100%",
        bgcolor="#000000",
        font_color="#00BFFF",
        directed=True,
        notebook=False # Importante para o Streamlit
    )

    # Adiciona nós com estilo (usando _G)
    for node in _G.nodes:
        net.add_node(
            node,
            label=node,
            color="#0A84FF",
            size=18,
            title=f"Aeroporto: {node}",
            font={"size": 14, "color": "#FFFFFF", "face": "Consolas"}
        )

    # Adiciona arestas com estilo (usando _G)
    for u, v, data_edge in _G.edges(data=True):
        net.add_edge(
            u,
            v,
            label=data_edge.get("label", ""),
            color=data_edge.get("color", "#33A1FD"),
            width=2,
            arrows="to",
            title=data_edge.get("title", data_edge.get("label", "")) # Tooltip melhorado
        )

    # --- MELHORIA: Opções de física e interação ---
    # Usa os valores dos sliders passados pelo 'physics_config'
    net.barnes_hut(
        gravity=physics_config["gravity"],
        central_gravity=physics_config["central_gravity"],
        spring_length=physics_config["spring_length"],
        spring_strength=physics_config["spring_strength"],
        damping=0.09,
        overlap=0
    )
    
    # --- MELHORIA: Adiciona botões de controle nativos do PyVis ---
    net.show_buttons(filter_=['physics'])
    
    # Salva em um arquivo temporário
    tmp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".html").name
    net.save_graph(tmp_path)
    return tmp_path

# --- Interface do Streamlit (main) ---

def main():
    st.set_page_config(page_title="Visualizador de Grafos", layout="wide", initial_sidebar_state="expanded")

    # --- MELHORIA: CSS aprimorado (incluindo a sidebar) ---
    st.markdown("""
        <style>
        /* Fundo principal */
        .stApp {
            background: radial-gradient(circle at 10% 20%, #000000 0%, #001A33 100%);
            color: #00BFFF;
        }
        
        /* Títulos */
        h1, h2, h3 {
            color: #33A1FD !important;
            text-shadow: 0 0 12px #007BFF;
            font-family: 'Consolas', 'Courier New', monospace;
        }
        
        /* Sidebar */
        .stSidebar {
            background-color: rgba(0, 10, 20, 0.8) !important;
            backdrop-filter: blur(5px);
        }
        
        /* Textos e widgets */
        .stSelectbox label, .stInfo, .stSlider label, .stMetric label, .stMetric value {
            color: #00BFFF !important;
            font-family: 'Consolas', 'Courier New', monospace;
        }
        .stMetric value {
            color: #FFFFFF !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- Conteúdo Principal ---
    st.title("💠 Visualizador Futurista de Grafos")
    st.write("Explore dinamicamente os resultados dos algoritmos de grafos.")

    # --- MELHORIA: Controles na Sidebar ---
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
    st.sidebar.subheader("Ajustes de Física (Barnes-Hut)")

    # --- MELHORIA: Sliders para controle da física ---
    physics_config = {
        "gravity": st.sidebar.slider("Gravidade (Atração)", -50000, 0, -25000, step=1000),
        "central_gravity": st.sidebar.slider("Gravidade Central", 0.0, 1.0, 0.3, step=0.05),
        "spring_length": st.sidebar.slider("Comprimento da Mola", 50, 500, 120, step=10),
        "spring_strength": st.sidebar.slider("Força da Mola", 0.01, 0.2, 0.05, step=0.01)
    }
    
    st.sidebar.markdown("---")

    # --- Lógica de Renderização ---
    
    if not os.path.exists(json_path):
        st.error(f"❌ Arquivo não encontrado: {os.path.abspath(json_path)}")
        st.info("Verifique se o caminho do JSON está correto e se o arquivo existe.")
        st.stop()

    st.info(f"Renderizando grafo para **{algoritmo}**... Use os controles na sidebar para ajustar a física.")

    try:
        # 1. Cria o grafo NetworkX (cacheado)
        G = create_networkx_graph(json_path, algoritmo)

        # --- MELHORIA: Exibe Métricas do Grafo ---
        st.sidebar.subheader("📊 Métricas do Grafo")
        col1, col2 = st.sidebar.columns(2)
        col1.metric("Nós (Aeroportos)", G.number_of_nodes())
        col2.metric("Arestas (Voos)", G.number_of_edges())
        
        # 2. Cria o HTML do PyVis (cacheado)
        # --- CORREÇÃO APLICADA AQUI ---
        # Passa 'algoritmo' como a 'cache_key' para o cache funcionar corretamente
        graph_path = create_pyvis_html(G, physics_config, algoritmo)
        
        # 3. Lê o HTML e exibe
        with open(graph_path, "r", encoding="utf-8") as f:
            html = f.read()

        st.components.v1.html(html, height=750, scrolling=False)

    except Exception as e:
        st.error(f"Erro ao gerar o grafo: {e}")
        st.exception(e) # Mostra o stacktrace para debug
        st.stop()

    st.markdown("---")
    st.caption("🛰️ Projeto de Grafos — Visual Futurista Preto e Azul | PyVis + Streamlit")


if __name__ == "__main__":
    main()