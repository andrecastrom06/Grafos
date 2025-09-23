import json
import pandas as pd
from pyvis.network import Network
import matplotlib.pyplot as plt
import streamlit as st
import streamlit.components.v1 as components
from io import BytesIO

# Configuração da página
st.set_page_config(
    page_title="Grafo Recife", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem !important;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.5rem !important;
        color: #2e86ab;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }
    .stSelectbox div div div {
        border-radius: 10px !important;
    }
    .stButton button {
        border-radius: 10px !important;
        background-color: #1f77b4 !important;
        color: white !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# PRIMEIRO: Carregar os dados antes de usar no sidebar
@st.cache_data
def load_data():
    df_adj = pd.read_csv('../data/adjacencias_bairros.csv')
    df_info = pd.read_csv('../data/bairros_unique.csv')  
    
    # Criar dicionário de adjacências
    adj = {}
    for _, row in df_adj.iterrows():
        u = row['bairro_origem'].strip()
        v = row['bairro_destino'].strip()
        adj.setdefault(u, set()).add(v)
        adj.setdefault(v, set()).add(u)
    
    # Calcular densidade
    densidade = {}
    for bairro, vizinhos in adj.items():
        k = len(vizinhos)
        if k <= 1:
            densidade[bairro] = 0
        else:
            links = sum(1 for u in vizinhos for v in vizinhos if u != v and v in adj[u]) / 2
            densidade[bairro] = links / (k*(k-1)/2)
    
    # Carregar percurso
    with open('../out/percurso_nova_descoberta_setubal.json', encoding='utf-8') as f:
        percurso = json.load(f)
    
    return df_adj, df_info, adj, densidade, percurso

# Carregar dados
df_adj, df_info, adj, densidade, percurso = load_data()

caminho = percurso['caminho']
ruas = percurso.get('ruas', [])
pesos = percurso.get('pesos', [])

# AGORA podemos calcular totais para o sidebar
total_bairros = len(df_info)
total_arestas = sum(len(v) for v in adj.values()) // 2

# Sidebar para informações e controles
with st.sidebar:
    
    # Informações gerais
    st.markdown("### 📊 Informações do Grafo")
    
    col_metric1, col_metric2 = st.columns(2)
    with col_metric1:
        st.metric("Total de Bairros", total_bairros)
    with col_metric2:
        st.metric("Total de Conexões", total_arestas)
    
    st.markdown("---")

# Layout principal
col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    st.markdown('<h1 class="main-header">Projeto Grafos - Recife</h1>', unsafe_allow_html=True)
    
    # Container da imagem de capa
    with st.container():
        st.image("../foto_capa.jpg", use_column_width=True)
        st.markdown("---")

    # Container de seleção de visualização
    with st.container():
        st.markdown("### 📈 Selecione o tipo de visualização")
        opcao = st.selectbox(
            "Escolha a visualização:",
            ["", 
             "Percurso Nova Descoberta → Boa Viagem", 
             "Grau dos bairros",
             "Top 10 bairros por grau", 
             "Distribuição dos graus",
             "Buscar por bairro"],
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # Função auxiliar
    def plot_to_bytes(fig):
        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", dpi=300, transparent=True)
        buf.seek(0)
        return buf

    # Visualizações
    if opcao == "Percurso Nova Descoberta → Boa Viagem":
        st.markdown('<h2 class="sub-header">Percurso Interativo</h2>', unsafe_allow_html=True)
        
        with st.expander("Personalizar Aparência", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                cor_nos = st.color_picker("Cor dos bairros", "#1f77b4")
            with col2:
                cor_arestas = st.color_picker("Cor do percurso", "#FF6B6B")
            with col3:
                espessura = st.slider("Espessura das arestas", 1, 10, 3)

        # Informações do percurso
        col_info1, col_info2, col_info3 = st.columns(3)
        with col_info1:
            st.metric("Bairros no percurso", len(caminho))
        with col_info2:
            total_pesos = sum(pesos) if pesos else 0
            st.metric("Peso total", f"{total_pesos:.1f} ")
        with col_info3:
            st.metric("Trechos", len(ruas))

        # Rede interativa
        net = Network(height="600px", width="100%", directed=True, bgcolor="#ffffff", font_color="#333333")
        net.barnes_hut()
        
        for bairro in caminho:
            net.add_node(bairro, label=bairro, color=cor_nos, shape="ellipse", size=25)
        
        for i in range(len(caminho)-1):
            origem = caminho[i]
            destino = caminho[i+1]
            rua = ruas[i] if ruas and i < len(ruas) else ""
            peso = pesos[i] if pesos and i < len(pesos) else ""
            label = f"{rua} ({peso}km)" if peso else rua
            net.add_edge(origem, destino, label=label, color=cor_arestas, width=espessura)

        html = net.generate_html()
        components.html(html, height=600, scrolling=True)

    elif opcao == "Grau dos bairros":
        st.markdown('<h2 class="sub-header">📊 Grau dos Bairros</h2>', unsafe_allow_html=True)
        
        with st.expander("Sobre esta visualização", expanded=False):
            st.info("""
            - **Cores**: Intensidade varia conforme o grau (número de conexões)
            - **Tooltip**: Passe o mouse sobre os bairros para ver informações detalhadas
            - **Grau**: Número de bairros adjacentes
            - **Densidade ego**: Mede a conectividade entre os vizinhos diretos
            """)

        net = Network(height="700px", width="100%", directed=False, bgcolor="#ffffff")
        net.barnes_hut()

        max_degree = max(len(v) for v in adj.values())
        for bairro, vizinhos in adj.items():
            grau = len(vizinhos)
            micro = df_info.loc[df_info['bairro'] == bairro, 'microrregiao'].values[0] \
                    if bairro in df_info['bairro'].values else "N/A"
            dens = densidade.get(bairro, 0)
            tooltip = f"Bairro: {bairro}; Grau: {grau}; Microrregião: {micro}; Densidade ego: {dens:.2f}"

            # Gradiente de cor baseado no grau
            intensity = int(255 * (grau / max_degree))
            color_hex = f'rgb({100 + intensity}, {150}, {200 + intensity//2})'

            net.add_node(bairro, label=bairro, title=tooltip, color=color_hex, size=20 + grau)

        for u, vizinhos in adj.items():
            for v in vizinhos:
                if u < v:
                    net.add_edge(u, v, color="rgba(100,100,100,0.3)")

        html = net.generate_html()
        components.html(html, height=700, scrolling=True)

    elif opcao == "Top 10 bairros por grau":
        st.markdown('<h2 class="sub-header">🏆 Top 10 Bairros Mais Conectados</h2>', unsafe_allow_html=True)
        
        top10 = sorted(adj.items(), key=lambda x: len(x[1]), reverse=True)[:10]
        
        # Tabela informativa
        st.dataframe(
            pd.DataFrame([
                {
                    'Posição': i+1, 
                    'Bairro': bairro, 
                    'Grau': len(vizinhos),
                    'Microrregião': df_info.loc[df_info['bairro'] == bairro, 'microrregiao'].values[0] 
                    if bairro in df_info['bairro'].values else "N/A"
                }
                for i, (bairro, vizinhos) in enumerate(top10)
            ]),
            use_container_width=True
        )

        top_bairros = set(b for b,_ in top10)
        net_top10 = Network(height="600px", width="100%", directed=False, bgcolor="#ffffff")
        
        for bairro in top_bairros:
            grau = len(adj[bairro])
            net_top10.add_node(bairro, label=bairro, color="#FF6B6B", size=30, 
                             title=f"Grau: {grau}")
        
        for u in top_bairros:
            for v in adj[u]:
                if v in top_bairros and u < v:
                    net_top10.add_edge(u, v, color="#4ECDC4", width=3)

        html = net_top10.generate_html()
        components.html(html, height=600, scrolling=True)

    elif opcao == "Distribuição dos graus":
        st.markdown('<h2 class="sub-header">📈 Distribuição dos Graus</h2>', unsafe_allow_html=True)
        
        graus = [len(v) for v in adj.values()]
        
        col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
        with col_stats1:
            st.metric("Grau Médio", f"{sum(graus)/len(graus):.1f}")
        with col_stats2:
            st.metric("Grau Máximo", max(graus))
        with col_stats3:
            st.metric("Grau Mínimo", min(graus))
        with col_stats4:
            st.metric("Mediana", f"{sorted(graus)[len(graus)//2]:.1f}")

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        
        # Histograma
        ax1.hist(graus, bins=range(1, max(graus)+2), color='#4ECDC4', edgecolor='black', alpha=0.7)
        ax1.set_xlabel("Grau do bairro")
        ax1.set_ylabel("Número de bairros")
        ax1.set_title("Distribuição dos graus dos bairros")
        ax1.grid(True, alpha=0.3)
        
        # Boxplot
        ax2.boxplot(graus, vert=True, patch_artist=True, 
                   boxprops=dict(facecolor="#FF6B6B", alpha=0.7))
        ax2.set_ylabel("Grau")
        ax2.set_title("Boxplot da distribuição de graus")
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        st.pyplot(fig)

    elif opcao == "Buscar por bairro":
        st.markdown('<h2 class="sub-header">🔍 Ego-grafo do Bairro</h2>', unsafe_allow_html=True)
        
        col_search1, col_search2 = st.columns([2, 1])
        with col_search1:
            bairro_escolhido = st.selectbox("Selecione um bairro:", sorted(adj.keys()))
        
        if bairro_escolhido:
            vizinhos = adj[bairro_escolhido]
            
            # Estatísticas do bairro selecionado
            grau_central = len(vizinhos)
            micro_central = df_info.loc[df_info['bairro'] == bairro_escolhido, 'microrregiao'].values[0] \
                            if bairro_escolhido in df_info['bairro'].values else "N/A"
            dens_central = densidade.get(bairro_escolhido, 0)
            
            col_stats = st.columns(4)
            with col_stats[0]:
                st.metric("Grau", grau_central)
            with col_stats[1]:
                st.metric("Densidade Ego", f"{dens_central:.2f}")
            with col_stats[2]:
                st.metric("Microrregião", micro_central)
            with col_stats[3]:
                st.metric("Vizinhos Diretos", len(vizinhos))

            net = Network(height="600px", width="100%", directed=False, bgcolor="#ffffff")
            net.barnes_hut()

            # Bairro central
            tooltip_central = f"Bairro: {bairro_escolhido}<br>Grau: {grau_central}<br>Microrregião: {micro_central}<br>Densidade ego: {dens_central:.2f}"
            net.add_node(bairro_escolhido, label=bairro_escolhido, title=tooltip_central, 
                        color="#FF6B6B", size=40, font={'size': 20})

            # Vizinhos
            for v in vizinhos:
                grau = len(adj[v])
                micro = df_info.loc[df_info['bairro'] == v, 'microrregiao'].values[0] \
                        if v in df_info['bairro'].values else "N/A"
                dens = densidade.get(v, 0)
                tooltip = f"Bairro: {v}<br>Grau: {grau}<br>Microrregião: {micro}<br>Densidade ego: {dens:.2f}"
                net.add_node(v, label=v, title=tooltip, color="#4ECDC4", size=25)
                net.add_edge(bairro_escolhido, v, color="gray", width=2)

            html = net.generate_html()
            components.html(html, height=600, scrolling=True)
