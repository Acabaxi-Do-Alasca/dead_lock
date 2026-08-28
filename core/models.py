"""Estruturas de dados fundamentais: processos, recursos e entradas de log.

Este módulo não depende de nenhuma biblioteca de interface gráfica -- é lógica
pura, para poder ser testada e explicada isoladamente do restante do projeto.
"""

from dataclasses import dataclass, field
from enum import Enum, auto


class ProcessState(Enum):
    """Estado de um processo ao longo da simulação."""

    READY = auto()      # sem requisição pendente, pronto para pedir recursos
    RUNNING = auto()     # marcado como em execução (uso decorativo/didático)
    BLOCKED = auto()      # esperando um recurso (requisição negada ou insuficiente)
    FINISHED = auto()     # terminou e liberou todos os recursos


@dataclass
class Process:
    pid: int
    name: str
    state: ProcessState = ProcessState.READY


@dataclass
class ResourceType:
    rid: int
    name: str
    total_instances: int


@dataclass
class LogEntry:
    """Uma linha do log de raciocínio do algoritmo, pronta para exibição."""

    step: int
    category: str
    # SAFETY_CHECK | RELEASE | RESULT | REQUEST | GRANT | DENY | ROLLBACK | INFO
    message: str
    data: dict = field(default_factory=dict)
