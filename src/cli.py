import json
from pyvis.network import Network
import webbrowser
import os

def main():
    with open('../out/percurso_nova_descoberta_setubal.json', encoding='utf-8') as f:
        percurso = json.load(f)

    caminho = percurso['caminho']
    ruas = percurso.get('ruas', [])

    net = Network(height="600px", width="100%", directed=True, bgcolor="#ffffff")
    net.barnes_hut()

    for bairro in caminho:
        net.add_node(bairro, label=bairro, color="#1f77b4", shape="ellipse")

    for i in range(len(caminho) - 1):
        origem = caminho[i]
        destino = caminho[i + 1]
        rua = ruas[i] if i < len(ruas) else ""
        peso = percurso.get("pesos", [])[i] if "pesos" in percurso else ""
        label = f"{rua} ({peso})" if peso else rua
        net.add_edge(origem, destino,
                    label=label,
                    color="red",
                    width=3)



    net.save_graph("../out/arvore_percurso.html")
    print("Arquivo salvo")

    net.save_graph("../out/arvore_percurso.html")
    webbrowser.open(f"file://{os.path.abspath('../out/arvore_percurso.html')}")


if __name__ == "__main__":
    main()