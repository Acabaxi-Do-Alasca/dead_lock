import unittest

from core.banker import safety_algorithm


class TestSafetyAlgorithm(unittest.TestCase):
    def test_classic_safe_state(self):
        # Cenário A (Silberschatz): 5 processos, recursos A=10,B=5,C=7
        available = [3, 3, 2]
        allocation = [
            [0, 1, 0],
            [2, 0, 0],
            [3, 0, 2],
            [2, 1, 1],
            [0, 0, 2],
        ]
        max_demand = [
            [7, 5, 3],
            [3, 2, 2],
            [9, 0, 2],
            [2, 2, 2],
            [4, 3, 3],
        ]
        need = [
            [max_demand[i][j] - allocation[i][j] for j in range(3)]
            for i in range(5)
        ]

        result = safety_algorithm(available, allocation, need, 5, 3)

        self.assertTrue(result.is_safe)
        self.assertEqual(result.safe_sequence, [1, 3, 4, 0, 2])
        self.assertTrue(len(result.log) > 0)
        self.assertTrue(any(e.category == "RESULT" for e in result.log))
        self.assertTrue(all(e.message for e in result.log))

    def test_unsafe_state(self):
        # Nenhum processo consegue progredir com o Work disponível
        available = [0, 0]
        allocation = [[1, 0], [0, 1]]
        need = [[2, 2], [2, 2]]  # nada cabe em work=[0,0]

        result = safety_algorithm(available, allocation, need, 2, 2)

        self.assertFalse(result.is_safe)
        self.assertEqual(result.safe_sequence, [])
        self.assertTrue(any(e.category == "RESULT" and not e.data.get("safe", True) for e in result.log))

    def test_trivial_all_needs_zero(self):
        available = [0, 0]
        allocation = [[1, 1], [2, 2]]
        need = [[0, 0], [0, 0]]

        result = safety_algorithm(available, allocation, need, 2, 2)

        self.assertTrue(result.is_safe)
        self.assertEqual(set(result.safe_sequence), {0, 1})

    def test_log_entries_have_readable_messages(self):
        available = [3, 3, 2]
        allocation = [[0, 1, 0], [2, 0, 0]]
        need = [[7, 4, 3], [1, 2, 2]]

        result = safety_algorithm(available, allocation, need, 2, 3)

        safety_checks = [e for e in result.log if e.category == "SAFETY_CHECK"]
        self.assertTrue(len(safety_checks) > 0)
        for entry in safety_checks:
            self.assertIn("Need", entry.message)
            self.assertIn("Work", entry.message)


if __name__ == "__main__":
    unittest.main()
