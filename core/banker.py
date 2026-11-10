"""Algoritmo do Banqueiro: Safety Algorithm e Resource-Request Algorithm.

Referência clássica: Silberschatz, Galvin & Gagne, "Operating System
Concepts", capítulo de Deadlocks.

Estruturas usadas (n processos, m tipos de recurso):
  Available[m]     -- instâncias livres de cada recurso
  Max[n][m]        -- demanda máxima declarada por cada processo
  Allocation[n][m] -- o que cada processo já tem
  Need[n][m]       -- o que ainda pode pedir (Need = Max - Allocation)

Ideia central: o sistema só concede uma requisição se, depois dela, ainda
existir uma ordem (sequência segura) em que TODOS os processos conseguem
obter o que falta, terminar e devolver seus recursos. Assim a espera
circular nunca chega a se formar -- o deadlock é PREVENIDO.
"""

from dataclasses import dataclass, field

from core.models import LogEntry, ProcessState
from core.state import SystemState


@dataclass
class SafetyResult:
    is_safe: bool
    safe_sequence: list[int]
    log: list[LogEntry] = field(default_factory=list)


@dataclass
class RequestResult:
    granted: bool
    reason: str | None  # None | "EXCEEDS_MAX" | "INSUFFICIENT_RESOURCES" | "UNSAFE_STATE"
    log: list[LogEntry] = field(default_factory=list)
    safety: SafetyResult | None = None


def safety_algorithm(available, allocation, need, n_proc, n_res) -> SafetyResult:
    """Executa o Safety Algorithm sobre matrizes soltas (sem depender de SystemState).

    Retorna se o estado é seguro, a sequência segura encontrada (se houver) e
    um log passo a passo explicando cada comparação Need[i] <= Work.
    """
    # Passo 1: Work = Available (cópia, para simular sem alterar o estado real)
    #          e Finish[i] = False para todo processo.
    work = list(available)
    finish = [False] * n_proc
    safe_sequence: list[int] = []
    log: list[LogEntry] = [
        LogEntry(0, "INFO", f"Iniciando Safety Algorithm. Work inicial = {work}")
    ]

    progress = True
    step = 0
    while progress and len(safe_sequence) < n_proc:
        progress = False
        for i in range(n_proc):
            if finish[i]:
                continue
            step += 1
            # Passo 2: procurar um processo i ainda não finalizado cujo Need[i]
            #          caiba no que está livre (Need[i] <= Work, recurso a recurso).
            can_proceed = all(need[i][j] <= work[j] for j in range(n_res))
            log.append(
                LogEntry(
                    step,
                    "SAFETY_CHECK",
                    f"Testando P{i}: Need[{i}]={need[i]} <= Work={work}? "
                    + ("Sim" if can_proceed else "Não"),
                    {"process": i, "need": list(need[i]), "work": list(work), "result": can_proceed},
                )
            )
            if can_proceed:
                # Passo 3: se couber, o processo i consegue terminar e devolve
                #          tudo o que tem: Work = Work + Allocation[i];
                #          Finish[i] = True. Volta ao passo 2 com mais recurso livre.
                work = [work[j] + allocation[i][j] for j in range(n_res)]
                finish[i] = True
                safe_sequence.append(i)
                progress = True
                step += 1
                log.append(
                    LogEntry(
                        step,
                        "RELEASE",
                        f"P{i} pode terminar, libera Allocation[{i}]={allocation[i]}. "
                        f"Novo Work={work}",
                        {"process": i, "new_work": list(work)},
                    )
                )

    # Passo 4: se Finish[i] == True para todo i, o estado é SEGURO (a ordem em
    #          que os processos foram encaixados é a sequência segura). Se
    #          sobrou alguém, ninguém garante que ele termine: estado INSEGURO.
    is_safe = all(finish)
    step += 1
    if is_safe:
        log.append(
            LogEntry(
                step,
                "RESULT",
                f"Estado SEGURO. Sequência segura encontrada: {safe_sequence}",
                {"safe": True, "sequence": list(safe_sequence)},
            )
        )
    else:
        stuck = [i for i in range(n_proc) if not finish[i]]
        log.append(
            LogEntry(
                step,
                "RESULT",
                f"Estado INSEGURO. Nenhum processo pôde progredir a partir daqui: {stuck}",
                {"safe": False, "sequence": list(safe_sequence)},
            )
        )
    return SafetyResult(is_safe, safe_sequence, log)


def request_algorithm(state: SystemState, pid: int, request: list[int]) -> RequestResult:
    """Resource-Request Algorithm: valida, tenta alocar e verifica segurança.

    Se a alocação tentativa deixar o sistema em estado inseguro, desfaz a
    alocação (rollback) e nega a requisição.
    """
    i = state.index_of(pid)
    n_proc, n_res = len(state.processes), len(state.resources)

    if len(request) != n_res:
        raise ValueError(f"Request deve ter {n_res} posições, recebeu {len(request)}")
    if any(r < 0 for r in request):
        raise ValueError("Request não pode conter valores negativos")

    log: list[LogEntry] = [LogEntry(0, "REQUEST", f"P{i} solicita Request={request}")]

    # Passo 1: o pedido não pode passar do que o processo declarou precisar
    #          (Request <= Need). Se passar, é erro do próprio processo.
    if not all(request[j] <= state.need[i][j] for j in range(n_res)):
        log.append(
            LogEntry(
                1,
                "DENY",
                f"Erro: Request{request} > Need[{i}]={state.need[i]}. "
                "O processo excedeu o máximo que declarou precisar.",
            )
        )
        return RequestResult(False, "EXCEEDS_MAX", log)

    # Passo 2: precisa haver recurso livre agora (Request <= Available).
    #          Se não houver, o processo simplesmente espera (fica bloqueado).
    if not all(request[j] <= state.available[j] for j in range(n_res)):
        log.append(
            LogEntry(
                1,
                "DENY",
                f"P{i} deve esperar: Request{request} > Available={state.available}. "
                "Não há recursos suficientes disponíveis agora.",
            )
        )
        state.processes[i].state = ProcessState.BLOCKED
        return RequestResult(False, "INSUFFICIENT_RESOURCES", log)

    # Passo 3: "finge" que concede -- guarda uma cópia do estado (para poder
    #          desfazer) e aplica a alocação tentativa:
    #          Available -= Request; Allocation[i] += Request; Need[i] -= Request.
    saved = state.clone()
    for j in range(n_res):
        state.available[j] -= request[j]
        state.allocation[i][j] += request[j]
        state.need[i][j] -= request[j]
    log.append(
        LogEntry(
            2,
            "INFO",
            f"Alocação tentativa aplicada: Available={state.available}, "
            f"Allocation[{i}]={state.allocation[i]}, Need[{i}]={state.need[i]}. "
            "Verificando se o novo estado é seguro...",
        )
    )

    # Passo 4: roda o Safety Algorithm sobre esse estado hipotético.
    safety = safety_algorithm(state.available, state.allocation, state.need, n_proc, n_res)
    log.extend(safety.log)

    # Passo 5a: estado seguro -> a alocação tentativa vira definitiva.
    if safety.is_safe:
        log.append(
            LogEntry(
                99,
                "GRANT",
                f"Requisição de P{i} CONCEDIDA -- o novo estado permanece seguro.",
            )
        )
        return RequestResult(True, None, log, safety)

    # Passo 5b: estado inseguro -> desfaz tudo (rollback para a cópia salva) e
    #           o processo espera. É aqui que o deadlock é PREVENIDO.
    state.restore(saved)
    state.processes[i].state = ProcessState.BLOCKED
    log.append(
        LogEntry(
            99,
            "ROLLBACK",
            f"Requisição de P{i} NEGADA e revertida -- concedê-la levaria a um "
            "estado inseguro (risco de deadlock).",
        )
    )
    return RequestResult(False, "UNSAFE_STATE", log, safety)
