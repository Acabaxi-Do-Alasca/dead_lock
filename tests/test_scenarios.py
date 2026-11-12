import unittest

from core.banker import safety_algorithm
from core.models import Process, ResourceType
from core.state import SystemState
from scenarios.loader import build_engine_from_scenario
from scenarios.scenario_definitions import ALL_SCENARIOS, SCENARIOS_BY_KEY
from simulation.engine import Mode, SimulationEngine


class TestScenarios(unittest.TestCase):
    def test_all_scenarios_are_internally_consistent(self):
        for scenario in ALL_SCENARIOS:
            engine = build_engine_from_scenario(scenario["key"])
            state = engine.state
            n_proc, n_res = len(state.processes), len(state.resources)

            for i in range(n_proc):
                for j in range(n_res):
                    self.assertEqual(
                        state.need[i][j],
                        scenario["max_demand"][i][j] - scenario["allocation"][i][j],
                    )
            totals = [r[1] for r in scenario["resources"]]
            allocated = [sum(state.allocation[i][j] for i in range(n_proc)) for j in range(n_res)]
            expected_available = [totals[j] - allocated[j] for j in range(n_res)]
            self.assertEqual(state.available, expected_available)

    def test_scenario_a_is_safe(self):
        engine = build_engine_from_scenario("A")
        state = engine.state
        result = safety_algorithm(
            state.available, state.allocation, state.need, len(state.processes), len(state.resources)
        )
        self.assertTrue(result.is_safe)
        self.assertEqual(result.safe_sequence, [1, 3, 4, 0, 2])

    def test_scenario_b_suggested_request_is_denied(self):
        engine = build_engine_from_scenario("B")
        process_name, request = engine.state.processes[1].name, [1, 0]
        self.assertEqual(process_name, "P1")

        result = engine.request(pid=1, request_vector=request)
        self.assertFalse(result.granted)
        self.assertEqual(result.reason, "UNSAFE_STATE")

    def test_scenario_c_reproduces_deadlock_in_free_mode(self):
        engine = build_engine_from_scenario("C")
        self.assertEqual(engine.mode, Mode.FREE)

        engine.request(pid=0, request_vector=[0, 1, 0])
        engine.request(pid=1, request_vector=[0, 0, 1])
        engine.request(pid=2, request_vector=[1, 0, 0])

        result = engine.check_deadlock()
        self.assertEqual(sorted(result.deadlocked_processes), [0, 1, 2])

    def test_scenario_c_cycle_is_prevented_in_protected_mode(self):
        # Mesmos processos/recursos/Max do Cenário C, mas partindo do zero e com
        # o Banqueiro ligado: cada Pi tenta pegar seu Ri, como no cenário.
        scenario = SCENARIOS_BY_KEY["C"]
        processes = [Process(i, name) for i, name in enumerate(scenario["processes"])]
        resources = [ResourceType(j, n, t) for j, (n, t) in enumerate(scenario["resources"])]
        zero = [[0, 0, 0] for _ in processes]
        engine = SimulationEngine(SystemState(processes, resources, zero, scenario["max_demand"]))

        self.assertTrue(engine.request(pid=0, request_vector=[1, 0, 0]).granted)
        self.assertTrue(engine.request(pid=1, request_vector=[0, 1, 0]).granted)
        third = engine.request(pid=2, request_vector=[0, 0, 1])

        # A terceira alocação fecharia o ciclo: o Banqueiro nega e desfaz
        self.assertFalse(third.granted)
        self.assertEqual(third.reason, "UNSAFE_STATE")
        self.assertEqual(engine.state.allocation[2], [0, 0, 0])


if __name__ == "__main__":
    unittest.main()
