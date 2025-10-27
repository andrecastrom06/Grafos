# Conteúdo para: tests/test_bellman_ford.py
import sys
import os
import pytest

# Adiciona a pasta raiz (GRAFOS) ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Imports do seu código fonte
from src.graphs.bellman_ford import bellman_ford
# IMPORTANTE: Importa do NOVO arquivo loader.py
from src.graphs.loader import carregar_grafo_do_csv 

# --- Caminhos do Projeto ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CSV_PATH = os.path.join(PROJECT_ROOT, "data", "flight_filtrado.csv")

# --- Fixture para carregar o grafo real (do CSV) ---
@pytest.fixture(scope="module")
def grafo_real():
    graph = carregar_grafo_do_csv(CSV_PATH)
    if not graph:
        pytest.skip("Grafo real (CSV) não foi carregado, pulando testes de integração.")
    return graph

# ===== TESTES UNITÁRIOS (CUMPRINDO OS REQUISITOS DA TAREFA) =====

def test_bellman_ford_com_peso_negativo_SEM_ciclo():
    """ 
    Cenário 1: Testa um grafo com pesos negativos, mas sem ciclos negativos.
    (Grafo corrigido: C -> B agora tem peso 5 para evitar o ciclo negativo)
    """
    graph = {
        'S': {'A': 6, 'B': 5},
        'A': {'C': -2},
        'B': {'A': -2, 'D': 4},
        'C': {'B': 5, 'E': 3},  # <-- CORRIGIDO AQUI (era 1)
        'D': {'C': 3, 'E': -1},
        'E': {}
    }
    
    dist, pred, has_neg, _ = bellman_ford(graph, 'S')
    
    # 1. Valida a detecção de ciclo
    assert has_neg is False
    
    # 2. Valida as novas distâncias corretas
    assert dist['A'] == 3  # Caminho: S -> B -> A (5 + -2 = 3)
    assert dist['C'] == 1  # Caminho: S -> B -> A -> C (3 + -2 = 1)
    assert dist['D'] == 9  # Caminho: S -> B -> D (5 + 4 = 9)
    assert dist['E'] == 4  # Caminho: S -> B -> A -> C -> E (1 + 3 = 4)
    assert pred['E'] == 'C' # Predecessor de E é C

def test_bellman_ford_COM_ciclo_negativo():
    """ Cenário 2: Testa um grafo com um ciclo negativo e valida sua detecção. """
    graph = { 'A': {'B': 1}, 'B': {'C': -1}, 'C': {'A': -1} }
    dist, pred, has_neg, _ = bellman_ford(graph, 'A')
    assert has_neg is True

# ===== TESTE DE INTEGRAÇÃO (USANDO DADOS REAIS DO CSV) =====

def test_integracao_bellman_ford_dados_reais(grafo_real):
    """ Testa o algoritmo com os dados reais do CSV. """
    origem = 'Brazil'
    dist, pred, has_neg, exec_time = bellman_ford(grafo_real, origem)

    assert has_neg is False # Não deve detectar ciclos negativos
    assert exec_time > 0
    assert dist['Taiwan'] == 2080 # Valida um caminho conhecido
    assert pred['Taiwan'] == 'China'