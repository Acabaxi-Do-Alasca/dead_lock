import unittest

from core.detection import detect_deadlock


class TestDetectDeadlock(unittest.TestCase):
    def test_circular_wait_is_detected(self):
        # Cenário C: 3 processos, 3 recursos de instância única, cada Pi aloca Ri
        # e pede o recurso do próximo -> ciclo fechado, ninguém progride.
        available = [0, 0, 0]
        allocation = [
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
        ]
        outstanding_request = [
            [0, 1, 0],  # P0 pede R1
            [0, 0, 1],  # P1 pede R2
            [1, 0, 0],  # P2 pede R0
        ]

        result = detect_deadlock(available, allocation, outstanding_request, 3, 3)

        self.assertEqual(sorted(result.deadlocked_processes), [0, 1, 2])
        self.assertTrue(any(e.category == "RESULT" and e.data.get("deadlocked") for e in result.log))

    def test_no_deadlock_when_resources_available(self):
        available = [1, 0, 0]
        allocation = [
            [0, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
        ]
        outstanding_request = [
            [0, 0, 0],
            [0, 0, 1],
            [0, 0, 0],
        ]

        result = detect_deadlock(available, allocation, outstanding_request, 3, 3)

        self.assertEqual(result.deadlocked_processes, [])

    def test_process_with_no_allocation_never_blocks_others(self):
        available = [0]
        allocation = [[0], [1]]
        outstanding_request = [[0], [0]]

        result = detect_deadlock(available, allocation, outstanding_request, 2, 1)

        self.assertEqual(result.deadlocked_processes, [])


if __name__ == "__main__":
    unittest.main()
