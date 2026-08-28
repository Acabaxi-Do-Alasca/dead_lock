"""Algoritmo do Banqueiro: Safety Algorithm e Resource-Request Algorithm.

Referência clássica: Silberschatz, Galvin & Gagne, "Operating System
Concepts", capítulo de Deadlocks.
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

    safety = safety_algorithm(state.available, state.allocation, state.need, n_proc, n_res)
    log.extend(safety.log)

    if safety.is_safe:
        log.append(
            LogEntry(
                99,
                "GRANT",
                f"Requisição de P{i} CONCEDIDA -- o novo estado permanece seguro.",
            )
        )
        return RequestResult(True, None, log, safety)

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
