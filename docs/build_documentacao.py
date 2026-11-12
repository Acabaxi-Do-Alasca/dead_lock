"""Gera a Documentação do Projeto (entrega formal) em .docx/.pdf.

Cobre os itens pedidos: objetivo do projeto, linguagem de programação,
ferramentas utilizadas e evidência dos testes. A evidência é produzida no
momento da geração: a suíte de testes e os cenários são executados de verdade
e os resultados (com data, hora e ambiente) entram no documento.

Uso: python docs/build_documentacao.py
Gera: entrega/Documentacao_do_Projeto.docx e .pdf
"""

import os
import platform
import re
import subprocess
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from docx_helpers import (  # noqa: E402
    CAPA_CAMPOS, ENTREGA_DIR, PROJECT_DIR, add_bullets, add_code_block, add_command, add_heading,
    add_image, add_para, add_steps, add_summary, add_table, add_title_page,
    capture_terminal_log_of_scenario_b, capture_terminal_log_of_scenario_c, new_doc,
    save_with_pdf,
)

OUT_PATH = os.path.join(ENTREGA_DIR, "Documentacao_do_Projeto.docx")
REPO_URL = "https://github.com/Acabaxi-Do-Alasca/dead_lock"
PASS_COLOR, FAIL_COLOR = "C8E6C9", "FFCDD2"

# Descrição de cada teste automatizado, agrupada por arquivo. O gerador confere
# que esta lista bate exatamente com os testes encontrados pelo unittest.
TEST_GROUPS = [
    ("Estado e matrizes", "test_state.py", {
        "test_need_equals_max_minus_allocation": "Need é calculado como Max − Allocation.",
        "test_available_equals_total_minus_sum_allocation": "Available é o total de cada recurso menos a soma do que está alocado.",
        "test_clone_is_a_real_deep_copy": "clone() gera uma cópia independente: alterar a cópia não altera o original.",
        "test_restore_brings_matrices_back_exactly": "restore() devolve Allocation, Need e Available exatamente ao estado salvo (base do rollback).",
        "test_index_of_finds_process_by_pid": "Localiza um processo pelo identificador e rejeita identificadores inexistentes.",
        "test_rejects_allocation_exceeding_max": "Rejeita configuração em que um processo tem alocado mais do que o seu Max.",
        "test_rejects_mismatched_matrix_shape": "Rejeita matrizes com dimensões incompatíveis com o número de processos e recursos.",
    }),
    ("Safety Algorithm", "test_banker_safety.py", {
        "test_classic_safe_state": "Exemplo clássico do livro-texto: estado seguro com sequência <P1, P3, P4, P0, P2>.",
        "test_unsafe_state": "Estado em que nenhum processo cabe em Work é reconhecido como inseguro.",
        "test_trivial_all_needs_zero": "Com todos os Need zerados, todos os processos terminam (estado seguro).",
        "test_log_entries_have_readable_messages": "Cada comparação do algoritmo gera uma linha de log legível com Need e Work.",
    }),
    ("Resource-Request Algorithm", "test_banker_request.py", {
        "test_initial_scenario_b_available_is_correct": "O Cenário B começa com Available = (1, 1).",
        "test_request_exceeding_need_is_denied": "Pedido maior que o Need declarado é negado (EXCEEDS_MAX).",
        "test_request_exceeding_available_blocks_process": "Pedido maior que o Available bloqueia o processo (INSUFFICIENT_RESOURCES).",
        "test_valid_safe_request_is_granted_and_matrices_update": "Pedido que mantém o estado seguro é concedido.",
        "test_scenario_b_unsafe_request_is_denied_with_exact_rollback": "Pedido que levaria a estado inseguro é negado e as matrizes voltam exatamente ao estado anterior (rollback).",
        "test_malformed_request_length_raises": "Pedido com quantidade errada de posições é rejeitado com erro.",
        "test_negative_request_raises": "Pedido com valor negativo é rejeitado com erro.",
        "test_unknown_pid_raises": "Pedido de processo inexistente é rejeitado com erro.",
    }),
    ("Detecção de deadlock", "test_detection.py", {
        "test_circular_wait_is_detected": "Espera circular entre P0, P1 e P2 é detectada como deadlock.",
        "test_no_deadlock_when_resources_available": "Sem espera circular, a detecção não acusa deadlock.",
        "test_process_with_no_allocation_never_blocks_others": "Processo sem recursos alocados nunca é apontado como parte de um deadlock.",
    }),
    ("Motor de simulação", "test_engine.py", {
        "test_starts_in_protected_mode_with_initial_snapshot": "A simulação começa no modo Protegido e registra o estado inicial na linha do tempo.",
        "test_request_appends_to_event_log_and_timeline": "Cada requisição gera entradas de log e um novo ponto na linha do tempo.",
        "test_set_mode_toggles_and_logs_change": "Alternar entre os modos Protegido e Livre funciona e fica registrado no log.",
        "test_set_mode_to_same_mode_is_noop": "Selecionar o modo que já está ativo não altera nada.",
        "test_finish_process_releases_all_resources": "Finalizar um processo devolve todos os seus recursos ao Available.",
        "test_free_mode_grants_immediately_when_resources_available": "No modo Livre, pedido que cabe no Available é concedido na hora.",
        "test_free_mode_blocks_without_safety_check": "No modo Livre, pedido maior que o Available bloqueia o processo, sem verificação de segurança.",
        "test_finish_process_wakes_up_blocked_process_in_free_mode": "Quando recursos são liberados, um processo bloqueado no modo Livre recebe o que esperava.",
        "test_finish_process_retries_blocked_process_through_banker": "No modo Protegido, o pedido de um processo bloqueado é reavaliado pelo Banqueiro após uma liberação.",
        "test_state_log_is_mirrored_to_terminal_logger": "Cada passo do algoritmo é enviado ao terminal de log.",
    }),
    ("Tratamento de deadlock", "test_engine.py", {
        "test_recovery_aborts_a_victim_and_breaks_the_cycle": "O tratamento aborta a vítima P0, repassa R0 a P2 e elimina o deadlock.",
        "test_recovery_logs_detection_choice_and_abort": "O tratamento registra no log a detecção, a escolha da vítima e o aborto.",
        "test_recovery_without_deadlock_does_nothing": "Sem deadlock, o tratamento não aborta nenhum processo.",
        "test_remaining_processes_can_finish_after_recovery": "Depois do tratamento, os processos restantes conseguem concluir normalmente.",
    }),
    ("Cenários prontos", "test_scenarios.py", {
        "test_all_scenarios_are_internally_consistent": "Os três cenários prontos têm Need e Available coerentes com seus dados.",
        "test_scenario_a_is_safe": "O Cenário A é seguro, com a sequência <P1, P3, P4, P0, P2>.",
        "test_scenario_b_suggested_request_is_denied": "No Cenário B, o pedido sugerido de P1 é negado por levar a estado inseguro.",
        "test_scenario_c_reproduces_deadlock_in_free_mode": "No Cenário C (modo Livre), os três pedidos sugeridos levam a deadlock.",
        "test_scenario_c_cycle_is_prevented_in_protected_mode": "Com o Banqueiro ligado, a alocação que fecharia o ciclo do Cenário C é negada.",
    }),
]


# -- coleta de evidências ---------------------------------------------------------

def run_test_suite():
    """Executa a suíte de verdade e devolve (saída, {nome_teste: status}, horário)."""
    started = datetime.now()
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=PROJECT_DIR, capture_output=True, text=True, encoding="utf-8",
    )
    output = (proc.stdout + proc.stderr).strip().splitlines()
    statuses = {}
    for line in output:
        match = re.match(r"^(test_\w+) \(.*\) \.\.\. (\w+)", line)
        if match:
            statuses[match.group(1)] = match.group(2)
    return output, statuses, started


def tool_versions():
    import matplotlib
    import networkx
    import tkinter
    import docx

    try:
        git = subprocess.run(["git", "--version"], capture_output=True, text=True).stdout.split()[-1]
        git = git.replace(".windows.1", "")
    except (OSError, IndexError):
        git = "—"
    return {
        "python": platform.python_version(),
        "tk": str(tkinter.TkVersion),
        "matplotlib": matplotlib.__version__,
        "networkx": networkx.__version__,
        "python-docx": getattr(docx, "__version__", "—"),
        "git": git,
    }


def run_functional_checks():
    """Executa os cenários pela mesma API usada pela interface e compara com o esperado."""
    from core.banker import safety_algorithm
    from core.models import Process, ProcessState, ResourceType
    from core.state import SystemState
    from scenarios.loader import build_engine_from_scenario
    from scenarios.scenario_definitions import SCENARIOS_BY_KEY
    from simulation.engine import SimulationEngine

    rows = []

    # 1. Cenário A: estado seguro
    s = build_engine_from_scenario("A").state
    r = safety_algorithm(s.available, s.allocation, s.need, len(s.processes), len(s.resources))
    seq = "<" + ", ".join(f"P{i}" for i in r.safe_sequence) + ">"
    rows.append(("Carregar o Cenário A (5 processos, recursos A=10, B=5, C=7)",
                 "Estado seguro, sequência <P1, P3, P4, P0, P2>",
                 f"{'Seguro' if r.is_safe else 'Inseguro'}, sequência {seq}",
                 r.is_safe and r.safe_sequence == [1, 3, 4, 0, 2]))

    # 2. Cenário B: pedido perigoso negado com rollback
    e = build_engine_from_scenario("B")
    before = ([row[:] for row in e.state.allocation], e.state.available[:])
    res = e.request(1, [1, 0])
    restored = (e.state.allocation, e.state.available) == before
    rows.append(("Cenário B, modo Protegido: P1 pede (1, 0)",
                 "Pedido negado por estado inseguro; matrizes restauradas",
                 f"{'Concedido' if res.granted else 'Negado'} ({res.reason}); "
                 f"matrizes {'restauradas' if restored else 'alteradas'}",
                 (not res.granted) and res.reason == "UNSAFE_STATE" and restored))

    # 3. Cenário C: deadlock forçado e detectado
    e = build_engine_from_scenario("C")
    e.request(0, [0, 1, 0]); e.request(1, [0, 0, 1]); e.request(2, [1, 0, 0])
    det = e.check_deadlock().deadlocked_processes
    rows.append(("Cenário C, modo Livre: P0→(0,1,0), P1→(0,0,1), P2→(1,0,0) e Verificar Deadlock",
                 "Deadlock detectado em P0, P1 e P2",
                 "Deadlock em " + ", ".join(f"P{i}" for i in det) if det else "Nenhum deadlock",
                 sorted(det) == [0, 1, 2]))

    # 4. Cenário C: tratamento
    rec = e.recover_from_deadlock()
    remaining = rec.final_detection.deadlocked_processes
    aborted = [f"P{i}" for i in rec.victims]
    rows.append(("Cenário C, após a detecção: Recuperar do Deadlock",
                 "Vítima P0 abortada, R0 repassado a P2, nenhum deadlock restante",
                 f"Vítima(s): {', '.join(aborted) or 'nenhuma'}; P2 "
                 f"{'executando' if e.state.processes[2].state == ProcessState.RUNNING else 'parado'}; "
                 f"{'nenhum deadlock restante' if not remaining else 'deadlock persiste'}",
                 rec.victims == [0] and not remaining
                 and e.state.processes[2].state == ProcessState.RUNNING))

    # 5. Mesmo ciclo do Cenário C com o Banqueiro ligado
    sc = SCENARIOS_BY_KEY["C"]
    procs = [Process(i, n) for i, n in enumerate(sc["processes"])]
    ress = [ResourceType(j, n, t) for j, (n, t) in enumerate(sc["resources"])]
    e = SimulationEngine(SystemState(procs, ress, [[0, 0, 0] for _ in procs], sc["max_demand"]))
    g = [e.request(0, [1, 0, 0]), e.request(1, [0, 1, 0]), e.request(2, [0, 0, 1])]
    rows.append(("Modo Protegido, partindo do zero: P0→R0, P1→R1, P2→R2 (as alocações que montam o Cenário C)",
                 "As duas primeiras concedidas; a terceira negada, impedindo o ciclo",
                 ", ".join("concedida" if x.granted else f"negada ({x.reason})" for x in g),
                 g[0].granted and g[1].granted and not g[2].granted))

    # 6. Configuração manual
    procs = [Process(0, "P0"), Process(1, "P1")]
    ress = [ResourceType(0, "A", 5), ResourceType(1, "B", 3)]
    e = SimulationEngine(SystemState(procs, ress, [[0, 0], [0, 0]], [[3, 2], [2, 3]]))
    res = e.request(0, [2, 1])
    rows.append(("Configuração manual (A=5, B=3; P0 Max (3,2), P1 Max (2,3)): P0 pede (2, 1)",
                 "Pedido concedido; Available passa a (3, 2)",
                 f"{'Concedido' if res.granted else 'Negado'}; Available = {tuple(e.state.available)}",
                 res.granted and e.state.available == [3, 2]))
    return rows


def run_safety_trace_scenario_a():
    """Executa o Safety Algorithm no Cenário A e devolve (estado, linhas do
    passo a passo, sequência segura), lidos do log real do algoritmo."""
    from core.banker import safety_algorithm
    from scenarios.loader import build_engine_from_scenario

    state = build_engine_from_scenario("A").state
    result = safety_algorithm(
        state.available, state.allocation, state.need, len(state.processes), len(state.resources)
    )
    rows = []
    for entry in result.log:
        if entry.category == "SAFETY_CHECK":
            d = entry.data
            rows.append([d["process"], d["need"], d["work"], d["result"], None])
        elif entry.category == "RELEASE" and rows:
            rows[-1][4] = entry.data["new_work"]
    sequence = "<" + ", ".join(f"P{i}" for i in result.safe_sequence) + ">"
    return state, rows, sequence


# -- documento --------------------------------------------------------------------------

scenario_a, safety_trace, safety_sequence = run_safety_trace_scenario_a()
test_output, test_status, test_time = run_test_suite()
versions = tool_versions()
functional = run_functional_checks()

described = {name for _, _, tests in TEST_GROUPS for name in tests}
missing_desc = set(test_status) - described
missing_run = described - set(test_status)
if missing_desc or missing_run:
    raise SystemExit(
        f"Lista de testes desatualizada. Sem descrição: {sorted(missing_desc)}; "
        f"descritos mas não executados: {sorted(missing_run)}"
    )
total = len(test_status)
passed = sum(1 for s in test_status.values() if s == "ok")
summary_line = next((l for l in test_output if l.startswith("Ran ")), "")
duration = summary_line.split(" in ")[-1] if " in " in summary_line else "—"
func_passed = sum(1 for row in functional if row[3])

doc = new_doc()
add_title_page(
    doc,
    "Simulador de Gerenciador de Deadlocks",
    "Algoritmo do Banqueiro — Documentação do Projeto",
    "Simulação de processos competindo por recursos, com prevenção, detecção e "
    "tratamento de deadlock, visualização gráfica e log passo a passo.",
    CAPA_CAMPOS,
)

add_summary(doc, [
    "1. Objetivo do projeto",
    "2. Linguagem de programação",
    "3. Ferramentas utilizadas",
    "4. Arquitetura do sistema",
    "5. Funcionamento",
    "6. Evidência dos testes",
    "7. Instalação e execução",
    "8. Referências",
    "Anexo A — Saída completa da suíte de testes",
])

# 1. Objetivo --------------------------------------------------------------------
add_heading(doc, "1. Objetivo do Projeto")
add_heading(doc, "1.1 Objetivo geral", level=2)
add_para(
    doc,
    "Desenvolver um simulador que implemente o Algoritmo do Banqueiro -- algoritmo "
    "de alocação de recursos e prevenção de deadlock -- demonstrando visualmente "
    "como processos solicitam recursos e como o sistema decide se uma alocação é "
    "segura. Deadlock é a situação em que processos ficam presos indefinidamente, "
    "cada um aguardando recursos retidos por outro, como dois grupos de amigos "
    "que se encontram de frente num corredor estreito da escola e nenhum cede "
    "passagem."
)
add_heading(doc, "1.2 Objetivos específicos", level=2)
add_bullets(doc, [
    "Simular múltiplos processos competindo por diferentes tipos de recursos, cada um com várias instâncias.",
    "Implementar o Algoritmo do Banqueiro completo: Safety Algorithm (verificação de estado seguro) e Resource-Request Algorithm (decisão de conceder ou negar, com rollback).",
    "Visualizar graficamente o grafo de alocação de recursos, destacando ciclos de espera.",
    "Representar o estado do sistema em matrizes (Allocation, Max, Need) e no vetor Available.",
    "Demonstrar um cenário que leva a deadlock e como ele é prevenido, detectado e tratado.",
    "Mostrar a evolução dos estados dos processos e recursos ao longo do tempo.",
    "Registrar em um terminal de log o raciocínio do algoritmo, passo a passo.",
])
add_heading(doc, "1.3 Escopo", level=2)
add_para(
    doc,
    "O simulador é um aplicativo de desktop com interface gráfica. O usuário pode "
    "montar uma simulação do zero (cadastrando processos, recursos e demandas "
    "máximas) ou carregar três cenários prontos: A (estado seguro), B (requisição "
    "negada por levar a estado inseguro) e C (deadlock real por espera circular). "
    "Há dois modos de operação: Protegido, em que o Banqueiro previne o deadlock, "
    "e Livre, em que a proteção é desligada para que o deadlock aconteça e possa "
    "ser detectado e tratado."
)

# 2. Linguagem --------------------------------------------------------------------
doc.add_page_break()
add_heading(doc, "2. Linguagem de Programação")
add_para(
    doc,
    f"O projeto foi desenvolvido em Python 3 (versão {versions['python']} no "
    "desenvolvimento e nos testes; compatível com Python 3.10 ou superior). "
    "Motivos da escolha:"
)
add_bullets(doc, [
    "A biblioteca padrão já oferece tudo o que a base do projeto precisa: interface gráfica (Tkinter), testes automatizados (unittest) e registro de log (logging).",
    "A sintaxe é próxima do pseudocódigo dos livros de Sistemas Operacionais, o que deixa o algoritmo fácil de ler e de apresentar.",
    "Matrizes como Allocation e Need são representadas diretamente como listas de listas, sem estruturas auxiliares.",
    "O ecossistema tem bibliotecas maduras para gráficos (matplotlib) e grafos (networkx).",
])
add_para(
    doc,
    "Recursos da linguagem usados: classes e dataclasses para os modelos "
    "(Process, ResourceType, LogEntry), Enum para estados e modos, anotações de "
    "tipo e funções puras para os algoritmos, que recebem matrizes e devolvem "
    "resultados sem depender da interface."
)

# 3. Ferramentas ---------------------------------------------------------------------
add_heading(doc, "3. Ferramentas Utilizadas")
add_table(doc, ["Ferramenta", "Versão", "Uso no projeto"], [
    ["Python", versions["python"], "Linguagem de programação do projeto."],
    ["Tkinter (biblioteca padrão)", f"Tk {versions['tk']}", "Interface gráfica: janela, abas, tabelas das matrizes e formulários."],
    ["matplotlib", versions["matplotlib"], "Desenho do grafo de alocação de recursos dentro da janela."],
    ["networkx", versions["networkx"], "Modelagem do grafo e busca de ciclos, para destacar a espera circular."],
    ["unittest (biblioteca padrão)", versions["python"], f"Testes automatizados ({total} testes)."],
    ["logging (biblioteca padrão)", versions["python"], "Terminal de log e arquivo logs/simulacao.log."],
    ["Git", versions["git"], "Controle de versão."],
    ["GitHub", "—", f"Hospedagem do código: {REPO_URL}"],
    ["PyCharm", "—", "Ambiente de desenvolvimento (IDE)."],
    ["python-docx e Microsoft Word", versions["python-docx"], "Geração desta documentação em .docx e exportação para PDF."],
], col_widths_cm=[4.5, 2.5, 9])
add_para(
    doc,
    "Dependências que precisam ser instaladas: apenas matplotlib e networkx "
    "(arquivo requirements.txt). As demais já fazem parte do Python."
)

# 4. Arquitetura ---------------------------------------------------------------------
doc.add_page_break()
add_heading(doc, "4. Arquitetura do Sistema")
add_para(
    doc,
    "O código é dividido em camadas. Os algoritmos (core) não conhecem a "
    "interface gráfica, o que permite testá-los isoladamente:"
)
add_table(doc, ["Pasta / arquivo", "Responsabilidade"], [
    ["core/models.py", "Modelos: processo, tipo de recurso, estado do processo e entrada de log."],
    ["core/state.py", "Estado do sistema: matrizes Allocation, Max, Need e vetor Available; cópia e restauração (rollback); envio de cada passo ao log."],
    ["core/banker.py", "Algoritmo do Banqueiro: safety_algorithm() e request_algorithm()."],
    ["core/detection.py", "Algoritmo de detecção de deadlock: detect_deadlock()."],
    ["simulation/engine.py", "Motor da simulação: modos Protegido e Livre, tratamento de deadlock (recover_from_deadlock) e linha do tempo."],
    ["simulation/terminal_log.py", "Terminal de log: formato, cores e arquivo de log."],
    ["simulation/history.py", "Snapshots do estado ao longo do tempo."],
    ["scenarios/", "Definição e carregamento dos cenários prontos A, B e C."],
    ["gui/", "Interface Tkinter: abas Configuração, Simulação, Log/Histórico, Cenários prontos e Ajuda; desenho do grafo."],
    ["tests/", f"Suíte de testes automatizados ({total} testes)."],
    ["main.py", "Ponto de entrada: liga o terminal de log e abre a janela."],
], col_widths_cm=[4.5, 11.5])
add_para(
    doc,
    "Fluxo de uma requisição: a interface (gui/tab_simulation.py) chama o motor "
    "(SimulationEngine.request). No modo Protegido, o motor delega ao "
    "Banqueiro (core/banker.py), que devolve a decisão e o log do raciocínio. O "
    "motor registra o log (terminal e aba Log), grava um snapshot na linha do "
    "tempo e a interface redesenha o grafo e as matrizes."
)

# 5. Funcionamento -------------------------------------------------------------------
add_heading(doc, "5. Funcionamento")
add_heading(doc, "5.1 Conceitos: deadlock e estado seguro", level=2)
add_para(
    doc,
    "Deadlock é a situação em que um conjunto de processos fica bloqueado para "
    "sempre: cada um retém um recurso e espera outro, que está retido por outro "
    "processo do conjunto. A analogia usada no projeto é a do corredor estreito "
    "da escola: dois grupos se encontram de frente, cada um ocupa seu espaço e "
    "espera o outro recuar. Ninguém recua, e ninguém passa."
)
add_para(doc, "Um deadlock só ocorre se as quatro condições abaixo estiverem presentes ao mesmo tempo:")
add_table(doc, ["Condição", "Significado"], [
    ["1. Exclusão mútua", "Um recurso só pode ser usado por um processo de cada vez."],
    ["2. Posse e espera", "O processo segura o que já tem enquanto espera pelo resto."],
    ["3. Não preempção", "Nenhum recurso é tomado à força de um processo; só ele mesmo o libera."],
    ["4. Espera circular", "Existe um ciclo de processos, cada um esperando um recurso retido pelo próximo."],
], col_widths_cm=[4.5, 11.5])
add_para(
    doc,
    "Basta impedir uma delas para evitar o deadlock. O Algoritmo do Banqueiro "
    "impede a quarta: nunca concede um pedido que possa levar a um ciclo de espera. "
    "Para isso ele classifica o estado do sistema:"
)
add_bullets(doc, [
    "Estado seguro: existe pelo menos uma ordem em que todos os processos conseguem obter o que falta, terminar e devolver seus recursos.",
    "Estado inseguro: não há garantia dessa ordem. Ainda não é um deadlock, mas ele se tornou possível, por isso o Banqueiro não deixa o sistema entrar nesse estado.",
    "Deadlock: a espera circular já aconteceu; os processos envolvidos não progridem mais sozinhos.",
])

add_heading(doc, "5.2 Estruturas do algoritmo", level=2)
add_para(doc, "Com n processos e m tipos de recurso, o Banqueiro mantém quatro estruturas (exemplos reais do Cenário A, processo P1):")
add_table(doc, ["Estrutura", "Significado", "Exemplo"], [
    ["Available[m]", "Instâncias livres de cada recurso.", str(scenario_a.available)],
    ["Max[n][m]", "O máximo que cada processo declarou que pode pedir.", f"P1: {scenario_a.max_demand[1]}"],
    ["Allocation[n][m]", "O que cada processo já segura.", f"P1: {scenario_a.allocation[1]}"],
    ["Need[n][m]", "O que cada processo ainda pode pedir: Need = Max − Allocation.", f"P1: {scenario_a.need[1]}"],
], col_widths_cm=[3.6, 8.4, 4])

add_heading(doc, "5.3 Prevenção: Algoritmo do Banqueiro", level=2)
add_para(doc, "Resource-Request Algorithm, executado a cada pedido no modo Protegido:")
add_steps(doc, [
    "Se Request > Need, o pedido é inválido (o processo pediu mais do que declarou).",
    "Se Request > Available, não há recurso livre: o processo espera (fica bloqueado).",
    "Simula a concessão: Available -= Request; Allocation += Request; Need -= Request.",
    "Executa o Safety Algorithm sobre esse estado hipotético.",
    "Se o estado for seguro, a concessão vira definitiva. Se for inseguro, tudo é desfeito (rollback) e o processo espera.",
])
add_para(doc, "Safety Algorithm:")
add_steps(doc, [
    "Work = Available; Finish[i] = falso para todo processo.",
    "Procura um processo i com Finish[i] = falso e Need[i] <= Work.",
    "Se encontrar, ele pode terminar: Work += Allocation[i]; Finish[i] = verdadeiro; volta ao passo 2.",
    "Se todos ficarem com Finish = verdadeiro, o estado é seguro (a ordem encontrada é a sequência segura).",
])
add_para(
    doc,
    "Exemplo: o Safety Algorithm executado sobre o estado inicial do Cenário A "
    "(execução real; cada linha é uma comparação, na ordem em que o algoritmo a fez):"
)
trace_rows, trace_colors = [], {}
for i, (proc, need, work, fits, work_after) in enumerate(safety_trace):
    trace_rows.append([f"P{proc}", str(need), str(work), "Sim" if fits else "Não", str(work_after) if fits else "—"])
    trace_colors[(i, 3)] = PASS_COLOR if fits else FAIL_COLOR
add_table(doc, ["Processo", "Need", "Work", "Need ≤ Work?", "Work depois"], trace_rows,
          col_widths_cm=[2.6, 3.4, 3.4, 3.2, 3.4], font_size=10, cell_colors=trace_colors)
add_para(
    doc,
    f"Todos terminaram: estado seguro, com a sequência {safety_sequence}. Repare "
    "que P0 e P2 não cabem na primeira passada, mas cabem depois que P1, P3 e P4 "
    "devolvem seus recursos."
)
add_heading(doc, "5.4 Detecção de deadlock", level=2)
add_para(
    doc,
    "No modo Livre não há verificação de segurança, e o deadlock pode acontecer. "
    "O algoritmo de detecção é parecido com o Safety Algorithm, mas usa o pedido "
    "pendente de cada processo (o que ele espera agora) em vez do Need. Processos "
    "cujo pedido nunca cabe em Work estão em deadlock."
)
add_heading(doc, "5.5 Tratamento de deadlock", level=2)
add_para(doc, "Recuperação por término de processo (recover_from_deadlock):")
add_steps(doc, [
    "Detecta os processos em deadlock.",
    "Escolhe uma vítima: a que retém menos recursos (menor custo); em empate, a de menor índice.",
    "Aborta a vítima e devolve seus recursos ao Available.",
    "Reavalia os processos bloqueados, que podem receber o que esperavam.",
    "Detecta de novo e repete até não haver mais deadlock.",
])
add_heading(doc, "5.6 Visualização e log", level=2)
add_para(
    doc,
    "O grafo de alocação mostra processos (círculos, coloridos pelo estado) e "
    "recursos (quadrados com instâncias livres/total), com setas de alocação "
    "(recurso → processo) e de pedido pendente (processo → recurso, tracejadas). "
    "Ciclos são destacados em vermelho. Cada decisão gera linhas de log no "
    "formato [passo] CATEGORIA | mensagem, exibidas no terminal e na aba Log."
)

# 6. Evidência dos testes ----------------------------------------------------------
doc.add_page_break()
add_heading(doc, "6. Evidência dos Testes")
add_heading(doc, "6.1 Estratégia de testes", level=2)
add_bullets(doc, [
    f"Testes automatizados ({total} casos, com unittest): verificam os algoritmos e o motor da simulação diretamente pelo código, sem interface gráfica.",
    f"Testes funcionais ({len(functional)} casos): reproduzem os cenários de uso da apresentação pela mesma API usada pela interface e comparam o resultado obtido com o esperado.",
    "Verificação visual: execução da interface com captura das telas (seção 6.5).",
])

add_heading(doc, "6.2 Ambiente de execução", level=2)
add_table(doc, ["Item", "Valor"], [
    ["Data e hora da execução", test_time.strftime("%d/%m/%Y às %H:%M:%S")],
    ["Sistema operacional", f"{platform.system()} {platform.release()} ({platform.version()})"],
    ["Python", versions["python"]],
    ["Comando", "python -m unittest discover -s tests -v"],
], col_widths_cm=[5, 11])

add_heading(doc, "6.3 Testes automatizados — resultado", level=2)
summary_rows, summary_colors = [], {}
for index, (group, filename, tests) in enumerate(TEST_GROUPS):
    ok = sum(1 for name in tests if test_status.get(name) == "ok")
    summary_rows.append([group, filename, str(len(tests)), f"{ok} de {len(tests)}"])
    summary_colors[(index, 3)] = PASS_COLOR if ok == len(tests) else FAIL_COLOR
summary_rows.append(["Total", "", str(total), f"{passed} de {total}"])
summary_colors[(len(TEST_GROUPS), 3)] = PASS_COLOR if passed == total else FAIL_COLOR
add_table(doc, ["Grupo", "Arquivo", "Testes", "Passaram"], summary_rows,
          col_widths_cm=[5.5, 5, 2.5, 3], cell_colors=summary_colors)
add_para(
    doc,
    f"Resultado: {passed} de {total} testes passaram, executados em {duration}. "
    "Final da saída do terminal (a saída completa está no Anexo A):",
    bold=True,
)
tail = [l for l in test_output if l.startswith("Ran ") or l in ("OK",) or l.startswith("FAILED")]
add_code_block(doc, ["-" * 70] + tail, font_size=9,
               color_for_line=lambda l: "8CD17D" if l == "OK" else ("F2726F" if l.startswith("FAILED") else "D4D4D4"))

add_heading(doc, "6.4 Casos de teste automatizados", level=2)
case_rows, case_colors, n = [], {}, 0
for group, filename, tests in TEST_GROUPS:
    for name, description in tests.items():
        status = test_status.get(name)
        case_rows.append([str(n + 1), group, f"{description}\n{name}",
                          "Passou" if status == "ok" else f"Falhou ({status})"])
        case_colors[(n, 3)] = PASS_COLOR if status == "ok" else FAIL_COLOR
        n += 1
add_table(doc, ["#", "Grupo", "O que o teste verifica", "Resultado"], case_rows,
          col_widths_cm=[0.9, 3.4, 9.6, 2.1], font_size=9, cell_colors=case_colors)
add_para(doc, "Abaixo de cada descrição está o nome técnico do teste, que pode ser localizado na saída completa da execução (Anexo A).", italic=True, size=9)

add_heading(doc, "6.5 Testes funcionais (cenários de uso)", level=2)
func_rows, func_colors = [], {}
for i, (action, expected, obtained, ok) in enumerate(functional):
    func_rows.append([str(i + 1), action, expected, obtained, "Passou" if ok else "Falhou"])
    func_colors[(i, 4)] = PASS_COLOR if ok else FAIL_COLOR
add_table(doc, ["#", "Ação", "Resultado esperado", "Resultado obtido", "Status"], func_rows,
          col_widths_cm=[0.8, 5, 4.2, 4.2, 1.8], font_size=9, cell_colors=func_colors)
add_para(doc, f"Resultado: {func_passed} de {len(functional)} testes funcionais passaram.", bold=True)

add_para(doc, "Telas capturadas executando a interface nos mesmos cenários:")
add_image(doc, "06_cenario_a.png", "Teste funcional 1 — Cenário A carregado: estado seguro, todos os processos prontos.")
add_image(doc, "08_cenario_b_negado.png", "Teste funcional 2 — Cenário B: pedido de P1 negado; P1 bloqueado (amarelo) e matrizes restauradas.")
add_image(doc, "11_cenario_c_ciclo.png", "Teste funcional 3 — Cenário C: ciclo de espera destacado em vermelho (deadlock).")
add_image(doc, "14_cenario_c_recuperado.png", "Teste funcional 4 — Cenário C após o tratamento: P0 abortado, P2 executando, ciclo desfeito.")
add_para(doc, "Terminal de log gerado durante o teste funcional 2 (Cenário B: o Banqueiro nega o pedido e desfaz a alocação):")
add_code_block(doc, capture_terminal_log_of_scenario_b())
add_para(doc, "Terminal de log gerado durante os testes funcionais 3 e 4 (forçar o deadlock, detectar e tratar):")
add_code_block(doc, capture_terminal_log_of_scenario_c())

add_heading(doc, "6.6 Conclusão dos testes", level=2)
add_para(
    doc,
    f"Todos os {total} testes automatizados e os {len(functional)} testes funcionais "
    "passaram. Eles cobrem o cálculo das matrizes, o Safety Algorithm (incluindo o "
    "exemplo clássico do livro-texto), o Resource-Request Algorithm (com o rollback "
    "exato), a detecção e o tratamento de deadlock, os modos de operação, o "
    "terminal de log e os três cenários usados na apresentação."
    if passed == total and func_passed == len(functional) else
    f"Atenção: {total - passed} teste(s) automatizado(s) e "
    f"{len(functional) - func_passed} teste(s) funcional(is) falharam nesta execução."
)

# 7. Instalação --------------------------------------------------------------------------
doc.add_page_break()
add_heading(doc, "7. Instalação e Execução")
add_para(doc, "Resumo (o passo a passo completo, com solução de problemas, está no Roteiro de Instalação):")
for number, (text, command) in enumerate([
    ("Instalar o Python 3.10 ou superior (python.org), marcando \"Add python.exe to PATH\".", None),
    ("Baixar o projeto (ou usar Code → Download ZIP no GitHub):", f"git clone {REPO_URL}.git"),
    ("No terminal, dentro da pasta do projeto, instalar as dependências:", "python -m pip install -r requirements.txt"),
    ("Conferir a instalação rodando os testes:", "python -m unittest discover -s tests -v"),
    ("Executar o simulador:", "python main.py"),
], start=1):
    add_para(doc, f"{number}. {text}")
    if command:
        add_command(doc, command)

# 8. Referências ---------------------------------------------------------------------
add_heading(doc, "8. Referências")
add_bullets(doc, [
    "SILBERSCHATZ, A.; GALVIN, P. B.; GAGNE, G. Operating System Concepts. 10. ed. Hoboken: Wiley, 2018. Capítulo \"Deadlocks\".",
    "TANENBAUM, A. S.; BOS, H. Sistemas Operacionais Modernos. 4. ed. São Paulo: Pearson, 2016.",
    "PYTHON SOFTWARE FOUNDATION. Documentação do Python 3 (tkinter, unittest, logging). Disponível em: https://docs.python.org/3/",
    "MATPLOTLIB. Documentação. Disponível em: https://matplotlib.org/",
    "NETWORKX. Documentação. Disponível em: https://networkx.org/",
    f"Repositório do projeto: {REPO_URL}",
])

# Anexo A ----------------------------------------------------------------------------------
doc.add_page_break()
add_heading(doc, "Anexo A — Saída Completa da Suíte de Testes")
add_para(doc, f"Saída do comando python -m unittest discover -s tests -v, executado em {test_time.strftime('%d/%m/%Y às %H:%M:%S')}:")
add_code_block(
    doc, test_output, font_size=6.5,
    color_for_line=lambda l: "8CD17D" if l.endswith("... ok") or l == "OK" else (
        "F2726F" if ("FAIL" in l or "ERROR" in l) else "D4D4D4"),
)

save_with_pdf(doc, OUT_PATH)
