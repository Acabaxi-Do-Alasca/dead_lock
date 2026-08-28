"""Definições dos cenários prontos, com dados fixos e uma descrição didática.

Cada cenário é um dicionário simples (fácil de inspecionar/testar) contendo:
- processos: lista de nomes
- recursos: lista de (nome, total_instances)
- allocation / max_demand: matrizes n_proc x n_res
- mode: "PROTECTED" ou "FREE" -- modo inicial sugerido para o cenário
- suggested_requests: lista de (nome_processo, request) para o usuário
  reproduzir com um clique e observar o log do algoritmo
"""

SCENARIO_A_SAFE = {
    "key": "A",
    "title": "A - Estado seguro (exemplo clássico)",
    "description": (
        "5 processos disputando 3 tipos de recursos (A=10, B=5, C=7). O estado "
        "inicial é seguro: existe uma sequência de execução, <P1, P3, P4, P0, P2>, "
        "em que todos os processos conseguem terminar sem travar."
    ),
    "processes": ["P0", "P1", "P2", "P3", "P4"],
    "resources": [("A", 10), ("B", 5), ("C", 7)],
    "allocation": [
        [0, 1, 0],
        [2, 0, 0],
        [3, 0, 2],
        [2, 1, 1],
        [0, 0, 2],
    ],
    "max_demand": [
        [7, 5, 3],
        [3, 2, 2],
        [9, 0, 2],
        [2, 2, 2],
        [4, 3, 3],
    ],
    "mode": "PROTECTED",
    "suggested_requests": [],
}

SCENARIO_B_DENIED = {
    "key": "B",
    "title": "B - Requisição negada (estado inseguro)",
    "description": (
        "3 processos disputando 2 tipos de recursos (A=3, B=3). O estado inicial "
        "é seguro, mas se P1 pedir (1, 0), o Available cai para (0, 1) e nenhum "
        "processo consegue mais progredir -- o Banqueiro nega a requisição e "
        "reverte a alocação para evitar o risco de deadlock. Use o formulário de "
        "requisição na aba Simulação: processo P1, request (1, 0)."
    ),
    "processes": ["P0", "P1", "P2"],
    "resources": [("A", 3), ("B", 3)],
    "allocation": [
        [1, 0],
        [0, 1],
        [1, 1],
    ],
    "max_demand": [
        [2, 2],
        [2, 2],
        [2, 2],
    ],
    "mode": "PROTECTED",
    "suggested_requests": [("P1", [1, 0])],
}

SCENARIO_C_DEADLOCK = {
    "key": "C",
    "title": "C - Deadlock por espera circular (modo Livre)",
    "description": (
        "3 processos e 3 recursos de instância única (R0, R1, R2), cada um já "
        "alocado por um processo diferente (Available = 0,0,0). Este cenário "
        "carrega em modo LIVRE (sem verificação de segurança): peça, na aba "
        "Simulação, P0->(0,1,0), P1->(0,0,1) e P2->(1,0,0), nessa ordem. As três "
        "requisições ficam pendentes e fecham um ciclo P0->R1->P1->R2->P2->R0->P0. "
        "A detecção de deadlock confirma que os 3 processos ficam travados. "
        "Compare com o modo Protegido: lá, a segunda ou terceira requisição já "
        "seria negada antes de o ciclo se fechar."
    ),
    "processes": ["P0", "P1", "P2"],
    "resources": [("R0", 1), ("R1", 1), ("R2", 1)],
    "allocation": [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
    ],
    "max_demand": [
        [1, 1, 0],
        [0, 1, 1],
        [1, 0, 1],
    ],
    "mode": "FREE",
    "suggested_requests": [("P0", [0, 1, 0]), ("P1", [0, 0, 1]), ("P2", [1, 0, 0])],
}

ALL_SCENARIOS = [SCENARIO_A_SAFE, SCENARIO_B_DENIED, SCENARIO_C_DEADLOCK]

SCENARIOS_BY_KEY = {s["key"]: s for s in ALL_SCENARIOS}
