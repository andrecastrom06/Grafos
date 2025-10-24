import pandas as pd
import sys

def build_directed_graph(csv_path):
    required_cols = ['from_country', 'dest_country', 'flight_number', 'duration_minutes']
    
    adjacency_list = {}
    
    all_nodes = set()
    try:
        df = pd.read_csv(csv_path)
        
        if not all(col in df.columns for col in required_cols):
            print(f"Erro: O arquivo '{csv_path}' deve conter as colunas: {required_cols}")
            sys.exit()
            
    except FileNotFoundError:
        print(f"Erro: Arquivo '{csv_path}' não encontrado.")
        sys.exit()
    except Exception as e:
        print(f"Ocorreu um erro ao ler o CSV: {e}")
        sys.exit()

    print(f"Arquivo '{csv_path}' lido com sucesso. Processando {len(df)} voos...")

    for index, row in df.iterrows():
        try:
            origem = str(row['from_country']).strip()
            destino = str(row['dest_country']).strip()
            voo = str(row['flight_number']).strip()
            
            peso = pd.to_numeric(row['duration_minutes'], errors='coerce')

            if pd.isna(peso) or not origem or not destino:
                print(f"Aviso: Ignorando linha {index} (dados inválidos ou faltando)")
                continue
            all_nodes.add(origem)
            all_nodes.add(destino)
            adjacency_list.setdefault(origem, []).append((destino, peso, voo))
            
        except Exception as e:
            print(f"Aviso: Erro ao processar linha {index}. Erro: {e}")

    for node in all_nodes:
        adjacency_list.setdefault(node, []) 
    print(f"\nGrafo dirigido construído com sucesso.")
    print(f"Total de Nós (países): {len(all_nodes)}")
    
    total_edges = sum(len(edges) for edges in adjacency_list.values())
    print(f"Total de Arestas (voos únicos de origem->destino): {total_edges}")

    return adjacency_list

def main():
    file_path = '../../data/flight_filtrado.csv'
    graph = build_directed_graph(file_path)
    
    print("\n--- AMOSTRA DA LISTA DE ADJACÊNCIA (GRAFO) ---")
    
    if not graph:
        print("O grafo está vazio.")
        return
        
    for origem, arestas in graph.items():
        
        print(f"\nNó (Origem): '{origem}'")
        if not arestas:
            print("  -> (Não possui voos de saída)")
        else:
            print(f"  -> Possui {len(arestas)} voos de saída para:")
            for i, (destino, peso, voo) in enumerate(arestas):
                if i >= 3:
                    print(f"     ... (e mais {len(arestas) - 3})")
                    break
                print(f"     - Destino: '{destino}' (Peso: {peso}, Voo: {voo})")

if __name__ == '__main__':
    main()