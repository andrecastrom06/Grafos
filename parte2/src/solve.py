# Conteúdo para: src/solve.py

import os
import sys
import json
import time

# --- Configuração de Caminho ---
# Isso é crucial para resolver os erros de importação.
# Adiciona a pasta raiz (parte2) ao sys.path para que 'from src.graphs...' funcione.
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.append(PROJECT_ROOT)

# --- Imports dos Módulos do Projeto ---
# (Agora o Python deve encontrar 'src.graphs')
try:
    from src.graphs.loader import carregar_grafo_do_csv
    from src.graphs.bellman_ford import bellman_ford
except ImportError as e:
    print(f"Erro de Importação: {e}", file=sys.stderr)
    print("Verifique se os arquivos 'loader.py' e 'bellman_ford.py' existem em 'src/graphs/'", file=sys.stderr)
    sys.exit(1)

# --- Constantes ---
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "flight_filtrado.csv")
OUT_PATH = os.path.join(PROJECT_ROOT, "out")

ROTAS_PARA_CALCULAR = [
    ("Brazil", "Philippines"),
    ("Brazil", "Taiwan"),
    ("Brazil", "Indonesia"),
    ("Chile", "Malaysia"),
    ("Chile", "Philippines")
]

# --- Funções Auxiliares ---

def reconstruir_caminho(pred, origem, destino):
    """ Reconstrói um caminho a partir de um dicionário de predecessores. """
    caminho = []
    temp_node = destino
    
    if temp_node not in pred:
        return []

    while temp_node is not None and temp_node != origem:
        caminho.insert(0, temp_node)
        temp_node = pred.get(temp_node)
    
    if temp_node == origem:
        caminho.insert(0, origem)
        return caminho
    
    return []

def salvar_json(data, filename):
    """ Salva uma lista de resultados em um arquivo JSON. """
    output_file = os.path.join(OUT_PATH, filename)
    try:
        # Garante que a pasta /out exista
        os.makedirs(OUT_PATH, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"  Resultados salvos com sucesso em: {output_file}")
    except Exception as e:
        print(f"    ERRO ao salvar {output_file}: {e}", file=sys.stderr)

# --- Função Principal ---

def main():
    print("="*60)
    print("Executando Algoritmo Bellman-Ford")
    print("="*60)
    
    # --- 1. Carregar o Grafo ---
    print(f"Carregando grafo de: {DATA_PATH}")
    graph = carregar_grafo_do_csv(DATA_PATH)
    if not graph:
        print("Falha ao carregar o grafo. Saindo.", file=sys.stderr)
        return
    print(f"Grafo carregado com {len(graph)} nós (países).")

    # --- 2. Executar Bellman-Ford ---
    print("\nCalculando rotas...")
    resultados_bf_json = []
    
    # Agrupa por origem para não recalcular
    origens_unicas = set(o for o, d in ROTAS_PARA_CALCULAR)

    for origem in origens_unicas:
        print(f"  Calculando caminhos a partir de: {origem}")
        
        # Chama o algoritmo
        dist, pred, has_neg, exec_time = bellman_ford(graph, origem)
        
        if has_neg:
            print(f"    ALERTA: Ciclo negativo detectado a partir de {origem}")

        # Salva os resultados para os destinos que nos interessam
        for o, destino_final in ROTAS_PARA_CALCULAR:
            if o != origem:
                continue

            custo_total = dist.get(destino_final, float('inf'))
            caminho = reconstruir_caminho(pred, origem, destino_final)
            
            resultado = {
                "algoritmo": "Bellman-Ford",
                "origem": origem,
                "destino": destino_final,
                "custo_total_minutos": custo_total if custo_total != float('inf') else "Inalcançável",
                "tempo_execucao_segundos": exec_time,
                "caminho": caminho,
                "detectou_ciclo_negativo": has_neg
            }
            resultados_bf_json.append(resultado)

    # --- 3. Salvar o resultado ---
    print("\nSalvando arquivo de resultado...")
    salvar_json(resultados_bf_json, "percurso_voo_bellman_ford.json")

    print("\nExecução concluída.")
    print("="*60)


# --- Ponto de Entrada do Script ---
if __name__ == "__main__":
    main()