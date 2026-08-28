"""Constrói um SimulationEngine pronto a partir de uma definição de cenário."""

from core.models import Process, ResourceType
from core.state import SystemState
from scenarios.scenario_definitions import SCENARIOS_BY_KEY
from simulation.engine import Mode, SimulationEngine


def build_engine_from_scenario(key: str) -> SimulationEngine:
    if key not in SCENARIOS_BY_KEY:
        raise ValueError(f"Cenário desconhecido: {key}")
    scenario = SCENARIOS_BY_KEY[key]

    processes = [Process(i, name) for i, name in enumerate(scenario["processes"])]
    resources = [
        ResourceType(j, name, total) for j, (name, total) in enumerate(scenario["resources"])
    ]
    state = SystemState(processes, resources, scenario["allocation"], scenario["max_demand"])

    mode = Mode.PROTECTED if scenario["mode"] == "PROTECTED" else Mode.FREE
    engine = SimulationEngine(state, mode=mode)
    engine.state.log("INFO", f"Cenário '{scenario['title']}' carregado.")
    return engine
