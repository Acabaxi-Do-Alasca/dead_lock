import unittest

from core.models import Process, ResourceType
from core.state import SystemState


def build_simple_state():
    processes = [Process(0, "P0"), Process(1, "P1")]
    resources = [ResourceType(0, "A", 10), ResourceType(1, "B", 5)]
    allocation = [[1, 2], [3, 1]]
    max_demand = [[3, 2], [4, 3]]
    return SystemState(processes, resources, allocation, max_demand)


class TestSystemState(unittest.TestCase):
    def test_need_equals_max_minus_allocation(self):
        state = build_simple_state()
        self.assertEqual(state.need, [[2, 0], [1, 2]])

    def test_available_equals_total_minus_sum_allocation(self):
        state = build_simple_state()
        # total A=10, alocado 1+3=4 -> disponivel 6; total B=5, alocado 2+1=3 -> disponivel 2
        self.assertEqual(state.available, [6, 2])

    def test_clone_is_a_real_deep_copy(self):
        state = build_simple_state()
        clone = state.clone()
        clone.allocation[0][0] = 999
        clone.available[0] = 999
        clone.processes[0].name = "mutated"

        self.assertEqual(state.allocation[0][0], 1)
        self.assertEqual(state.available[0], 6)
        self.assertEqual(state.processes[0].name, "P0")

    def test_restore_brings_matrices_back_exactly(self):
        state = build_simple_state()
        saved = state.clone()

        state.allocation[0][0] = 2
        state.available[0] -= 1
        state.need[0][0] -= 1

        state.restore(saved)

        self.assertEqual(state.allocation, saved.allocation)
        self.assertEqual(state.available, saved.available)
        self.assertEqual(state.need, saved.need)

    def test_index_of_finds_process_by_pid(self):
        state = build_simple_state()
        self.assertEqual(state.index_of(1), 1)
        with self.assertRaises(ValueError):
            state.index_of(99)

    def test_rejects_allocation_exceeding_max(self):
        processes = [Process(0, "P0")]
        resources = [ResourceType(0, "A", 10)]
        with self.assertRaises(ValueError):
            SystemState(processes, resources, [[5]], [[3]])

    def test_rejects_mismatched_matrix_shape(self):
        processes = [Process(0, "P0")]
        resources = [ResourceType(0, "A", 10), ResourceType(1, "B", 5)]
        with self.assertRaises(ValueError):
            SystemState(processes, resources, [[1]], [[2, 2]])


if __name__ == "__main__":
    unittest.main()
