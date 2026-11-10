"""Motor de simulação: orquestra o core (Banqueiro/detecção) e mantém histórico.

Dois modos de operação, para permitir comparar prevenção vs. deadlock real:

- PROTECTED: toda requisição passa pelo Resource-Request Algorithm (com
  verificação de segurança). Requisições perigosas são negadas -- o deadlock
  é PREVENIDO antes de acontecer.
- FREE: requisições só respeitam o limite físico de Available. Se não houver
  recursos livres, a requisição fica pendente (sem checagem de segurança),
  permitindo formar uma espera circular real. Nesse modo o deadlock pode
  acontecer; ele é DETECTADO por `check_deadlock()` e TRATADO por
  `recover_from_deadlock()` (aborta um processo-vítima e libera seus recursos).
"""

from dataclasses import dataclass, field
from enum import Enum, auto

from core.banker import request_algorithm
from core.detection import DetectionResult, detect_deadlock
from core.models import ProcessState
from core.state import SystemState
from simulation.history import StateSnapshot


class Mode(Enum):
    PROTECTED = auto()
    FREE = auto()


@dataclass
class RecoveryResult:
    """Resultado do tratamento de deadlock."""

    victims: list[int] = field(default_factory=list)       # índices dos processos abortados
    final_detection: DetectionResult | None = None          # detecção feita ao final


class SimulationEngine:
    def __init__(self, state: SystemState, mode: Mode = Mode.PROTECTED):
        self.state = state
        self.mode = mode
        n_res = len(state.resources)
        # Requisição pendente de cada processo (o que ele está esperando agora).
        # É usada pela detecção de deadlock e para desenhar as setas tracejadas
        # (processo -> recurso) no grafo.
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
        """Processa uma requisição de recursos conforme o modo atual.

        Modo Protegido: delega ao Algoritmo do Banqueiro (request_algorithm),
        que só concede se o estado resultante continuar seguro.
        Modo Livre: concede se houver recurso livre; senão, bloqueia o processo.
        """
        if self.mode == Mode.PROTECTED:
            result = request_algorithm(self.state, pid, request_vector)
            self.state.log_many(result.log)
            if result.granted:
                self.outstanding_requests[pid] = [0] * len(self.state.resources)
                self.state.processes[self.state.index_of(pid)].state = ProcessState.RUNNING
            else:
                # guarda o quanto o processo queria: aparece como aresta de
                # requisição pendente no grafo e é reavaliado quando algum
                # processo liberar recursos (ver _retry_pending).
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
            self._allocate(i, request_vector)
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

    def _allocate(self, i: int, request_vector: list[int]) -> None:
        """Efetiva uma alocação (usada no modo Livre)."""
        n_res = len(self.state.resources)
        for j in range(n_res):
            self.state.available[j] -= request_vector[j]
            self.state.allocation[i][j] += request_vector[j]
            self.state.need[i][j] -= request_vector[j]
        self.outstanding_requests[self.state.processes[i].pid] = [0] * n_res
        self.state.processes[i].state = ProcessState.RUNNING

    # -- liberação / término de processo ----------------------------------------

    def finish_process(self, pid: int) -> None:
        """O processo termina normalmente e devolve tudo o que tinha."""
        i = self.state.index_of(pid)
        released = self._release_all(i)
        self.state.processes[i].state = ProcessState.FINISHED
        self.state.log(
            "RELEASE",
            f"P{i} terminou e liberou Allocation={released}. Novo Available={self.state.available}",
        )
        self._retry_pending()
        self._snapshot(f"P{i} terminou")

    def _release_all(self, i: int) -> list[int]:
        """Devolve ao Available tudo o que o processo i tem alocado."""
        n_res = len(self.state.resources)
        released = list(self.state.allocation[i])
        for j in range(n_res):
            self.state.available[j] += self.state.allocation[i][j]
            self.state.allocation[i][j] = 0
            self.state.need[i][j] = 0
        self.outstanding_requests[self.state.processes[i].pid] = [0] * n_res
        return released

    def _retry_pending(self) -> None:
        """Reavalia processos bloqueados depois que recursos foram liberados.

        Um processo bloqueado só volta a rodar quando o que ele espera cabe no
        Available. No modo Protegido a nova tentativa passa de novo pelo
        Banqueiro (que pode negar outra vez); no modo Livre é concedida direto.
        Repete até que nenhuma nova requisição possa ser atendida.
        """
        n_res = len(self.state.resources)
        progress = True
        while progress:
            progress = False
            for i, p in enumerate(self.state.processes):
                pending = self.outstanding_requests.get(p.pid, [0] * n_res)
                if p.state != ProcessState.BLOCKED or not any(pending):
                    continue
                if not all(pending[j] <= self.state.available[j] for j in range(n_res)):
                    continue
                self.state.log(
                    "INFO",
                    f"P{i} estava bloqueado esperando {pending}; agora Available="
                    f"{self.state.available} comporta o pedido -- reavaliando.",
                )
                if self.mode == Mode.PROTECTED:
                    result = request_algorithm(self.state, p.pid, pending)
                    self.state.log_many(result.log)
                    if result.granted:
                        self.outstanding_requests[p.pid] = [0] * n_res
                        p.state = ProcessState.RUNNING
                        progress = True
                else:
                    self._allocate(i, pending)
                    self.state.log(
                        "GRANT",
                        f"P{i} recebeu {pending} e voltou a executar. Available={self.state.available}",
                    )
                    progress = True

    # -- deadlock: detecção e tratamento -----------------------------------------

    def check_deadlock(self) -> DetectionResult:
        """DETECÇÃO: roda o algoritmo de detecção sobre as requisições pendentes."""
        n_proc, n_res = len(self.state.processes), len(self.state.resources)
        outstanding_matrix = [self.outstanding_requests[p.pid] for p in self.state.processes]
        result = detect_deadlock(
            self.state.available, self.state.allocation, outstanding_matrix, n_proc, n_res
        )
        self.state.log_many(result.log)
        return result

    def recover_from_deadlock(self) -> RecoveryResult:
        """TRATAMENTO: recupera o sistema de um deadlock abortando vítimas.

        Estratégia (recuperação por término de processos, uma vítima por vez):
          1. Detecta quais processos estão em deadlock.
          2. Escolhe uma vítima entre eles (o que retém MENOS recursos, ou seja,
             o de menor custo para abortar/reiniciar).
          3. Aborta a vítima: todos os recursos dela voltam para Available.
          4. Reavalia os processos bloqueados -- agora algum deles pode receber
             o recurso que esperava.
          5. Detecta de novo; se ainda houver deadlock, volta ao passo 2.
        """
        self.state.log("RECOVERY", "Iniciando TRATAMENTO de deadlock (recuperação por término de processo).")
        result = RecoveryResult()

        detection = self.check_deadlock()
        while detection.deadlocked_processes:
            victim = self._choose_victim(detection.deadlocked_processes)
            self._abort_process(victim)
            result.victims.append(victim)
            self._retry_pending()
            self.state.log("RECOVERY", "Verificando se o deadlock foi desfeito...")
            detection = self.check_deadlock()

        result.final_detection = detection
        if result.victims:
            names = ", ".join(f"P{v}" for v in result.victims)
            self.state.log(
                "RECOVERY",
                f"Deadlock TRATADO: {names} abortado(s); o ciclo de espera foi quebrado e os "
                "demais processos podem prosseguir.",
            )
            self._snapshot(f"Recuperação de deadlock: {names} abortado(s)")
        else:
            self.state.log("RECOVERY", "Não havia deadlock -- nenhuma ação necessária.")
        return result

    def _choose_victim(self, deadlocked: list[int]) -> int:
        """Critério de escolha: menor total de recursos retidos (desempate: menor índice)."""
        held = {i: sum(self.state.allocation[i]) for i in deadlocked}
        victim = min(deadlocked, key=lambda i: (held[i], i))
        candidates = ", ".join(f"P{i} retém {held[i]}" for i in deadlocked)
        self.state.log(
            "RECOVERY",
            f"Escolha da vítima -- critério: processo em deadlock que retém MENOS recursos "
            f"(menor custo para abortar). Candidatos: {candidates}. Vítima escolhida: P{victim}.",
        )
        return victim

    def _abort_process(self, i: int) -> None:
        released = self._release_all(i)
        self.state.processes[i].state = ProcessState.ABORTED
        self.state.log(
            "ABORT",
            f"P{i} foi ABORTADO e liberou Allocation={released}. Novo Available={self.state.available}",
        )

    # -- timeline -----------------------------------------------------------------

    def _snapshot(self, description: str) -> StateSnapshot:
        snap = StateSnapshot.capture(len(self.timeline), description, self.state)
        self.timeline.append(snap)
        self.state.history.append(snap)
        return snap
