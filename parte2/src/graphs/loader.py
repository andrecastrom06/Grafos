# Conteúdo para: src/graphs/loader.py
import csv
import os
import sys

def carregar_grafo_do_csv(path_do_csv: str) -> dict:
    """
    Lê um arquivo CSV de voos (já filtrado) e o transforma 
    em um grafo (dicionário aninhado).

    O formato é: {'PaisOrigem': {'PaisDestino': peso, ...}, ...}

    Se houver múltiplas rotas diretas (arestas paralelas) entre
    dois países no CSV, apenas a rota com o menor 'duration_minutes' (peso)
    será mantida no grafo final.
    """
    
    nodes = set()
    edges_data = [] 

    try:
        with open(path_do_csv, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row.get('from_country') or not row.get('dest_country') or not row.get('duration_minutes'):
                    continue
                    
                source = row['from_country']
                dest = row['dest_country']
                
                try:
                    weight = int(row['duration_minutes'])
                except (ValueError, TypeError):
                    continue 
                
                nodes.add(source)
                nodes.add(dest)
                edges_data.append((source, dest, weight))

    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado em {path_do_csv}", file=sys.stderr)
        return {}
    except Exception as e:
        print(f"Erro ao ler o CSV: {e}", file=sys.stderr)
        return {}

    # 1. Inicializa o grafo com todos os nós (países)
    graph = {node: {} for node in nodes}

    # 2. Preenche as arestas com o menor peso
    for source, dest, weight in edges_data:
        existing_weight = graph[source].get(dest, float('inf'))
        if weight < existing_weight:
            graph[source][dest] = weight
    
    return graph