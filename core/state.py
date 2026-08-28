"""Estado do sistema: matrizes Allocation/Max/Need e vetor Available.

`SystemState` guarda tudo que o Algoritmo do Banqueiro precisa e mais o log de
eventos produzido ao longo da simulação. `clone()`/`restore()` implementam o
rollback usado pelo Resource-Request Algorithm quando uma requisição levaria a
um estado inseguro.
"""

import copy

from core.models import LogEntry, Process, ResourceType


class SystemState:
    def __init__(self, processes, resources, allocation, max_demand):
        n_proc, n_res = len(processes), len(resources)

        if len(allocation) != n_proc or any(len(row) != n_res for row in allocation):
            raise ValueError("Allocation deve ser uma matriz n_proc x n_res")
        if len(max_demand) != n_proc or any(len(row) != n_res for row in max_demand):
            raise ValueError("Max deve ser uma matriz n_proc x n_res")
        for i in range(n_proc):
            for j in range(n_res):
                if allocation[i][j] < 0 or max_demand[i][j] < 0:
                    raise ValueError("Allocation e Max não podem conter valores negativos")
                if allocation[i][j] > max_demand[i][j]:
                    raise ValueError(
                        f"Allocation[{i}][{j}]={allocation[i][j]} excede "
                        f"Max[{i}][{j}]={max_demand[i][j]}"
                    )

        self.processes: list[Process] = processes
        self.resources: list[ResourceType] = resources
        self.allocation = [list(row) for row in allocation]
        self.max_demand = [list(row) for row in max_demand]
        self.need = self._compute_need()
        self.available = self._compute_available()

        self.event_log: list[LogEntry] = []
        self.history: list = []
        self._step_counter = 0

    # -- cálculos derivados -------------------------------------------------

    def _compute_need(self):
        n_proc, n_res = len(self.processes), len(self.resources)
        return [
            [self.max_demand[i][j] - self.allocation[i][j] for j in range(n_res)]
            for i in range(n_proc)
        ]

    def _compute_available(self):
        n_proc, n_res = len(self.processes), len(self.resources)
        totals = [self.resources[j].total_instances for j in range(n_res)]
        allocated = [sum(self.allocation[i][j] for i in range(n_proc)) for j in range(n_res)]
        return [totals[j] - allocated[j] for j in range(n_res)]

    # -- utilidades -----------------------------------------------------------

    def index_of(self, pid: int) -> int:
        for i, p in enumerate(self.processes):
            if p.pid == pid:
                return i
        raise ValueError(f"Processo com pid={pid} não encontrado")

    def next_step(self) -> int:
        self._step_counter += 1
        return self._step_counter

    def log(self, category: str, message: str, data: dict | None = None) -> LogEntry:
        entry = LogEntry(self.next_step(), category, message, data or {})
        self.event_log.append(entry)
        return entry

    def log_many(self, entries: list[LogEntry]) -> None:
        """Reindexa e anexa uma lista de LogEntry (ex: vinda do safety_algorithm)."""
        for entry in entries:
            entry.step = self.next_step()
            self.event_log.append(entry)

    # -- clone / restore (rollback) -----------------------------------------

    def clone(self) -> "SystemState":
        clone = copy.copy(self)
        clone.allocation = copy.deepcopy(self.allocation)
        clone.max_demand = copy.deepcopy(self.max_demand)
        clone.need = copy.deepcopy(self.need)
        clone.available = list(self.available)
        clone.processes = [copy.copy(p) for p in self.processes]
        # event_log/history não são clonados: clone() serve só para snapshot de matrizes
        return clone

    def restore(self, saved: "SystemState") -> None:
        self.allocation = copy.deepcopy(saved.allocation)
        self.max_demand = copy.deepcopy(saved.max_demand)
        self.need = copy.deepcopy(saved.need)
        self.available = list(saved.available)
        for i, p in enumerate(self.processes):
            p.state = saved.processes[i].state
