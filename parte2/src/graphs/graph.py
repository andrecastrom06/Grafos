import pandas as pd
import itertools
import sys
from collections import defaultdict

nodes_data = {}
edge_list = []

try:
    df = pd.read_csv("../../data/steam_filtrado.csv")

    required_cols = ['name', 'genres', 'positive_ratings', 'negative_ratings']
    if not all(col in df.columns for col in required_cols):
        print(f"Erro: O arquivo 'steam_filtrado.csv' deve conter as colunas: {required_cols}")
        sys.exit()

except FileNotFoundError:
    print("Erro: Arquivo 'steam_filtrado.csv' não encontrado.")
    sys.exit()
except Exception as e:
    print(f"Ocorreu um erro ao ler o CSV: {e}")
    sys.exit()
print(f"Arquivo 'steam_filtrado.csv' lido com sucesso. Total de {len(df)} registros.")

print("\nProcessando Nós (Vértices)...")
for index, row in df.iterrows():
    nome = row['name']
    
    if nome in nodes_data:
        continue
        
    try:
        pos_ratings = pd.to_numeric(row['positive_ratings'], errors='coerce')
        neg_ratings = pd.to_numeric(row['negative_ratings'], errors='coerce')

        if pd.isna(pos_ratings): pos_ratings = 0
        if pd.isna(neg_ratings): neg_ratings = 0

        peso_base_no = max(0, pos_ratings - neg_ratings)
        
        nodes_data[nome] = {
            'genres': row['genres'],
            'base_weight': peso_base_no
        }
    except Exception as e:
        print(f"Aviso: Ignorando linha {index} ('{nome}') devido a dados inválidos. Erro: {e}")

print(f"Total de {len(nodes_data)} Nós únicos criados.")

print("\nOtimização: Agrupando nós por gênero...")
nodes_by_genre = defaultdict(list)

for node_name, data in nodes_data.items():
    genre = data['genres']
    if pd.notna(genre):
        nodes_by_genre[genre].append(node_name)

print(f"Nós agrupados em {len(nodes_by_genre)} gêneros únicos.")

print("\nProcessando Arestas (Conexões) - Modo Otimizado...")

total_genres = len(nodes_by_genre)
arestas_criadas_total = 0

for i, (genre, nodes_in_genre) in enumerate(nodes_by_genre.items()):
    
    num_nodes_in_genre = len(nodes_in_genre)
    
    print(f"  [Gênero {i+1}/{total_genres}] Processando: '{genre}' (contém {num_nodes_in_genre} nós)")

    if num_nodes_in_genre < 2:
        continue
    pares_no_genero = itertools.combinations(nodes_in_genre, 2)
    
    arestas_neste_genero = 0
    for node1, node2 in pares_no_genero:
        data_node1 = nodes_data[node1]
        data_node2 = nodes_data[node2]
        peso_aresta = (data_node1['base_weight'] + data_node2['base_weight']) / 2
        
        edge_list.append((node1, node2, peso_aresta))
        arestas_neste_genero += 1
    
    if arestas_neste_genero > 0:
        print(f"    -> Criadas {arestas_neste_genero} arestas para o gênero '{genre}'.")
    
    arestas_criadas_total += arestas_neste_genero


print(f"\nProcessamento de arestas concluído.")
print(f"Total de {arestas_criadas_total} Arestas criadas.")
print("\n--- Visualização do Grafo (Sem bibliotecas de grafo) ---")

print("\n--- AMOSTRA DE NÓS (VÉRTICES) ---")
for i, (nome, data) in enumerate(nodes_data.items()):
    if i >= 5:
        break
    print(f"Nó: {nome} | Atributos: {data}")

print(f"\n--- AMOSTRA DE ARESTAS (CONEXÕES) ---")
if not edge_list:
    print("Nenhuma aresta foi criada (nenhum jogo compartilha o mesmo gênero).")
else:
    for i, (n1, n2, peso) in enumerate(edge_list):
        if i >= 10:
            break
        print(f"Aresta: ({n1}, {n2}) | Peso: {peso:.2f} | Gênero: {nodes_data[n1]['genres']}")