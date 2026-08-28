"""Algoritmo de detecção de deadlock (usado no modo Livre, sem prevenção).

É estruturalmente parecido com o Safety Algorithm, mas parte da matriz de
Request pendente (o que cada processo está esperando agora) em vez da matriz
Need (o que o processo ainda pode vir a pedir no futuro). Processos sem
nenhum recurso alocado já começam "terminados" para efeito da varredura,
pois não retêm nada que outros processos precisem esperar.
"""

from dataclasses import dataclass, field

from core.models import LogEntry


@dataclass
class DetectionResult:
    deadlocked_processes: list[int]
    log: list[LogEntry] = field(default_factory=list)


def detect_deadlock(available, allocation, outstanding_request, n_proc, n_res) -> DetectionResult:
    work = list(available)
    finish = [all(allocation[i][j] == 0 for j in range(n_res)) for i in range(n_proc)]
    log: list[LogEntry] = [
        LogEntry(0, "INFO", f"Iniciando detecção de deadlock. Work inicial = {work}")
    ]

    step = 0
    changed = True
    while changed:
        changed = False
        for i in range(n_proc):
            if finish[i]:
                continue
            step += 1
            can_proceed = all(outstanding_request[i][j] <= work[j] for j in range(n_res))
            log.append(
                LogEntry(
                    step,
                    "DEADLOCK_CHECK",
                    f"Testando P{i}: Request pendente[{i}]={outstanding_request[i]} "
                    f"<= Work={work}? " + ("Sim" if can_proceed else "Não"),
                    {"process": i, "result": can_proceed},
                )
            )
            if can_proceed:
                work = [work[j] + allocation[i][j] for j in range(n_res)]
                finish[i] = True
                changed = True
                step += 1
                log.append(
                    LogEntry(
                        step,
                        "RELEASE",
                        f"P{i} consegue prosseguir e libera Allocation[{i}]={allocation[i]}. "
                        f"Novo Work={work}",
                    )
                )

    deadlocked = [i for i in range(n_proc) if not finish[i]]
    step += 1
    if deadlocked:
        log.append(
            LogEntry(
                step,
                "RESULT",
                f"DEADLOCK detectado. Processos presos em espera circular: {deadlocked}",
                {"deadlocked": list(deadlocked)},
            )
        )
    else:
        log.append(
            LogEntry(step, "RESULT", "Nenhum deadlock detectado.", {"deadlocked": []})
        )
    return DetectionResult(deadlocked, log)
