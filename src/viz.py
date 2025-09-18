import json
import pandas as pd
from pyvis.network import Network
import matplotlib.pyplot as plt
import streamlit as st
import streamlit.components.v1 as components
from io import BytesIO

st.set_page_config(page_title="Grafo Recife", layout="wide")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.title("Projeto Grafos - Recife")
    st.image("../foto_capa.jpg", width=500)

    df_adj = pd.read_csv('../data/adjacencias_bairros.csv')
    df_info = pd.read_csv('../data/bairros_unique.csv')  

    adj = {}
    for _, row in df_adj.iterrows():
        u = row['bairro_origem'].strip()
        v = row['bairro_destino'].strip()
        adj.setdefault(u, set()).add(v)
        adj.setdefault(v, set()).add(u)

    densidade = {}
    for bairro, vizinhos in adj.items():
        k = len(vizinhos)
        if k <= 1:
            densidade[bairro] = 0
        else:
            links = sum(1 for u in vizinhos for v in vizinhos if u != v and v in adj[u]) / 2
            densidade[bairro] = links / (k*(k-1)/2)

    with open('../out/percurso_nova_descoberta_setubal.json', encoding='utf-8') as f:
        percurso = json.load(f)

    caminho = percurso['caminho']
    ruas = percurso.get('ruas', [])
    pesos = percurso.get('pesos', [])

    opcao = st.selectbox(
        "Escolha a visualização",
        ["", 
         "Percurso Nova Descoberta → Boa Viagem", 
         "Grau dos bairros",
         "Top 10 bairros por grau", 
         "Distribuição dos graus",
         "Buscar por bairro"]  # <<< NOVA OPÇÃO
    )

    def plot_to_bytes(fig):
        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        return buf

    if opcao == "Percurso Nova Descoberta → Boa Viagem":
        cor_nos = st.color_picker("Cor dos bairros", "#1f77b4")
        cor_arestas = st.color_picker("Cor do percurso", "#FF0000")
        espessura = st.slider("Espessura das arestas", 1, 10, 3)
        st.subheader("Percurso interativo")

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

        html = net.generate_html()
        components.html(html, height=600, width=800)

    elif opcao == "Grau dos bairros":
        st.subheader("Grau dos bairros com Tooltip")
        net = Network(height="700px", width="100%", directed=False, bgcolor="#ffffff")
        net.barnes_hut()

        max_degree = max(len(v) for v in adj.values())
        for bairro, vizinhos in adj.items():
            grau = len(vizinhos)
            micro = df_info.loc[df_info['bairro'] == bairro, 'microrregiao'].values[0] \
                    if bairro in df_info['bairro'].values else "N/A"
            dens = densidade.get(bairro, 0)
            tooltip = f"Bairro: {bairro} Grau: {grau} Microrregião: {micro} Densidade ego: {dens:.2f}"

            color_intensity = int(255 * (grau / max_degree))
            color_hex = f'#{255-color_intensity:02x}{color_intensity:02x}80'

            net.add_node(bairro, label=bairro, title=tooltip, color=color_hex)

        for u, vizinhos in adj.items():
            for v in vizinhos:
                if u < v:
                    net.add_edge(u, v)

        html = net.generate_html()
        components.html(html, height=700, width=1000)

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
        html = net_top10.generate_html()
        components.html(html, height=600, width=800)

    elif opcao == "Distribuição dos graus":
        graus = [len(v) for v in adj.values()]
        fig, ax = plt.subplots(figsize=(8,5))
        ax.hist(graus, bins=range(1, max(graus)+2), color='skyblue', edgecolor='black')
        plt.xlabel("Grau do bairro")
        plt.ylabel("Número de bairros")
        plt.title("Distribuição dos graus dos bairros")
        st.image(plot_to_bytes(fig), use_container_width=True)

    elif opcao == "Buscar por bairro":
        st.subheader("Buscar ego-grafo por bairro")
        bairro_escolhido = st.selectbox("Selecione um bairro", sorted(adj.keys()))

        if bairro_escolhido:
            vizinhos = adj[bairro_escolhido]
            net = Network(height="600px", width="100%", directed=False, bgcolor="#ffffff")
            net.barnes_hut()

            # adiciona o bairro central
            grau_central = len(vizinhos)
            micro_central = df_info.loc[df_info['bairro'] == bairro_escolhido, 'microrregiao'].values[0] \
                            if bairro_escolhido in df_info['bairro'].values else "N/A"
            dens_central = densidade.get(bairro_escolhido, 0)
            tooltip_central = f"Bairro: {bairro_escolhido} Grau: {grau_central} Microrregião: {micro_central} Densidade ego: {dens_central:.2f}"
            net.add_node(bairro_escolhido, label=bairro_escolhido, title=tooltip_central, color="red")

            # adiciona os vizinhos
            for v in vizinhos:
                grau = len(adj[v])
                micro = df_info.loc[df_info['bairro'] == v, 'microrregiao'].values[0] \
                        if v in df_info['bairro'].values else "N/A"
                dens = densidade.get(v, 0)
                tooltip = f"Bairro: {v} Grau: {grau} Microrregião: {micro} Densidade ego: {dens:.2f}"
                net.add_node(v, label=v, title=tooltip, color="skyblue")
                net.add_edge(bairro_escolhido, v, color="gray")

            html = net.generate_html()
            components.html(html, height=600, width=800)