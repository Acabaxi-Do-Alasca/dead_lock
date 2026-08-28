"""Motor de simulação: orquestra o core (Banqueiro/detecção) e mantém histórico.

Dois modos de operação, para permitir comparar prevenção vs. deadlock real:

- PROTECTED: toda requisição passa pelo Resource-Request Algorithm (com
  verificação de segurança). Requisições perigosas são negadas.
- FREE: requisições só respeitam o limite físico de Available. Se não houver
  recursos livres, a requisição fica pendente (sem checagem de segurança),
  permitindo formar uma espera circular real que pode terminar em deadlock.
"""

from enum import Enum, auto

from core.banker import request_algorithm
from core.detection import detect_deadlock
from core.models import ProcessState
from core.state import SystemState
from simulation.history import StateSnapshot


class Mode(Enum):
    PROTECTED = auto()
    FREE = auto()


class SimulationEngine:
    def __init__(self, state: SystemState, mode: Mode = Mode.PROTECTED):
        self.state = state
        self.mode = mode
        n_res = len(state.resources)
        self.outstanding_requests: dict[int, list[int]] = {
            p.pid: [0] * n_res for p in state.processes
        }
        self.timeline: list[StateSnapshot] = []
        self._snapshot("Estado inicial")

    # -- controle de modo -----------------------------------------------------

    def set_mode(self, mode: Mode) -> None:
        if mode == self.mode:
            return
        self.mode = mode
        self.state.log(
            "INFO",
            f"Modo alterado para {'PROTEGIDO (com verificação de segurança)' if mode == Mode.PROTECTED else 'LIVRE (sem prevenção)'}.",
        )

    # -- requisições ------------------------------------------------------------

    def request(self, pid: int, request_vector: list[int]):
        if self.mode == Mode.PROTECTED:
            result = request_algorithm(self.state, pid, request_vector)
            self.state.log_many(result.log)
            if result.granted:
                self.outstanding_requests[pid] = [0] * len(self.state.resources)
                self.state.processes[self.state.index_of(pid)].state = ProcessState.RUNNING
            else:
                # guarda o quanto o processo queria, só para exibir a aresta de
                # requisição pendente no grafo -- não afeta o algoritmo.
                self.outstanding_requests[pid] = list(request_vector)
            self._snapshot(
                f"Requisição de P{pid}={request_vector} "
                + ("concedida" if result.granted else f"negada ({result.reason})")
            )
            return result
        return self._request_free(pid, request_vector)

    def _request_free(self, pid: int, request_vector: list[int]):
        i = self.state.index_of(pid)
        n_res = len(self.state.resources)
        if len(request_vector) != n_res:
            raise ValueError(f"Request deve ter {n_res} posições, recebeu {len(request_vector)}")
        if any(r < 0 for r in request_vector):
            raise ValueError("Request não pode conter valores negativos")

        self.state.log(
            "REQUEST", f"[Modo Livre] P{i} solicita Request={request_vector} (sem verificação de segurança)"
        )

        if all(request_vector[j] <= self.state.available[j] for j in range(n_res)):
            for j in range(n_res):
                self.state.available[j] -= request_vector[j]
                self.state.allocation[i][j] += request_vector[j]
                self.state.need[i][j] -= request_vector[j]
            self.outstanding_requests[pid] = [0] * n_res
            self.state.processes[i].state = ProcessState.RUNNING
            self.state.log(
                "GRANT",
                f"[Modo Livre] Recursos suficientes disponíveis -- requisição de P{i} "
                f"concedida imediatamente. Available={self.state.available}",
            )
            granted = True
        else:
            self.outstanding_requests[pid] = list(request_vector)
            self.state.processes[i].state = ProcessState.BLOCKED
            self.state.log(
                "DENY",
                f"[Modo Livre] Available={self.state.available} insuficiente para "
                f"Request={request_vector}. P{i} fica bloqueado aguardando -- "
                "nenhuma verificação de segurança é feita neste modo.",
            )
            granted = False

        self._snapshot(f"[Livre] Requisição de P{i}={request_vector}")
        return granted

    # -- liberação / término de processo ----------------------------------------

    def finish_process(self, pid: int) -> None:
        i = self.state.index_of(pid)
        n_res = len(self.state.resources)
        released = list(self.state.allocation[i])
        for j in range(n_res):
            self.state.available[j] += self.state.allocation[i][j]
            self.state.allocation[i][j] = 0
            self.state.need[i][j] = 0
        self.outstanding_requests[pid] = [0] * n_res
        self.state.processes[i].state = ProcessState.FINISHED
        self.state.log(
            "RELEASE",
            f"P{i} terminou e liberou Allocation={released}. Novo Available={self.state.available}",
        )
        self._snapshot(f"P{i} terminou")

    # -- detecção de deadlock (modo Livre) ---------------------------------------

    def check_deadlock(self):
        n_proc, n_res = len(self.state.processes), len(self.state.resources)
        outstanding_matrix = [self.outstanding_requests[p.pid] for p in self.state.processes]
        result = detect_deadlock(
            self.state.available, self.state.allocation, outstanding_matrix, n_proc, n_res
        )
        self.state.log_many(result.log)
        return result

    # -- timeline -----------------------------------------------------------------

    def _snapshot(self, description: str) -> StateSnapshot:
        snap = StateSnapshot.capture(len(self.timeline), description, self.state)
        self.timeline.append(snap)
        self.state.history.append(snap)
        return snap
