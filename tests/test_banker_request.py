import copy
import unittest

from core.banker import request_algorithm
from core.models import Process, ProcessState, ResourceType
from core.state import SystemState


def build_scenario_b():
    # Cenário B: 3 processos, recursos A=3,B=3, Available=(1,1)
    processes = [Process(0, "P0"), Process(1, "P1"), Process(2, "P2")]
    resources = [ResourceType(0, "A", 3), ResourceType(1, "B", 3)]
    allocation = [[1, 0], [0, 1], [1, 1]]
    max_demand = [[2, 2], [2, 2], [2, 2]]
    return SystemState(processes, resources, allocation, max_demand)


class TestRequestAlgorithm(unittest.TestCase):
    def test_initial_scenario_b_available_is_correct(self):
        state = build_scenario_b()
        self.assertEqual(state.available, [1, 1])

    def test_request_exceeding_need_is_denied(self):
        state = build_scenario_b()
        result = request_algorithm(state, pid=0, request=[2, 2])  # Need[0] = [1,2]
        self.assertFalse(result.granted)
        self.assertEqual(result.reason, "EXCEEDS_MAX")

    def test_request_exceeding_available_blocks_process(self):
        state = build_scenario_b()
        result = request_algorithm(state, pid=0, request=[1, 2])  # <= Need mas > Available
        self.assertFalse(result.granted)
        self.assertEqual(result.reason, "INSUFFICIENT_RESOURCES")
        self.assertEqual(state.processes[0].state, ProcessState.BLOCKED)

    def test_valid_safe_request_is_granted_and_matrices_update(self):
        state = build_scenario_b()
        result = request_algorithm(state, pid=2, request=[0, 0])
        self.assertTrue(result.granted)
        self.assertIsNone(result.reason)

    def test_scenario_b_unsafe_request_is_denied_with_exact_rollback(self):
        state = build_scenario_b()
        allocation_before = copy.deepcopy(state.allocation)
        need_before = copy.deepcopy(state.need)
        available_before = list(state.available)

        # P1 pede (1,0): Request<=Need e Request<=Available, mas leva a Work=(0,1)
        # sem nenhum processo conseguir progredir -> estado inseguro
        result = request_algorithm(state, pid=1, request=[1, 0])

        self.assertFalse(result.granted)
        self.assertEqual(result.reason, "UNSAFE_STATE")
        self.assertIsNotNone(result.safety)
        self.assertFalse(result.safety.is_safe)

        # rollback deve ser byte-a-byte igual ao estado anterior à tentativa
        self.assertEqual(state.allocation, allocation_before)
        self.assertEqual(state.need, need_before)
        self.assertEqual(state.available, available_before)
        self.assertEqual(state.processes[1].state, ProcessState.BLOCKED)

    def test_malformed_request_length_raises(self):
        state = build_scenario_b()
        with self.assertRaises(ValueError):
            request_algorithm(state, pid=0, request=[1])

    def test_negative_request_raises(self):
        state = build_scenario_b()
        with self.assertRaises(ValueError):
            request_algorithm(state, pid=0, request=[-1, 0])

    def test_unknown_pid_raises(self):
        state = build_scenario_b()
        with self.assertRaises(ValueError):
            request_algorithm(state, pid=99, request=[0, 0])


if __name__ == "__main__":
    unittest.main()
