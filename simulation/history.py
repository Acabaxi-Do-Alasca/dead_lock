"""Snapshot do estado do sistema em um ponto no tempo, para a timeline da GUI."""

import copy
from dataclasses import dataclass, field

from core.models import ProcessState


@dataclass
class StateSnapshot:
    step: int
    description: str
    allocation: list
    need: list
    available: list
    process_states: dict = field(default_factory=dict)

    @staticmethod
    def capture(step: int, description: str, state) -> "StateSnapshot":
        return StateSnapshot(
            step=step,
            description=description,
            allocation=copy.deepcopy(state.allocation),
            need=copy.deepcopy(state.need),
            available=list(state.available),
            process_states={p.pid: p.state for p in state.processes},
        )
