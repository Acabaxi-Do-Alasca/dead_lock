import unittest

from core.models import Process, ResourceType
from core.state import SystemState
from simulation.engine import Mode, SimulationEngine


def build_engine():
    processes = [Process(0, "P0"), Process(1, "P1"), Process(2, "P2")]
    resources = [ResourceType(0, "A", 3), ResourceType(1, "B", 3)]
    allocation = [[1, 0], [0, 1], [1, 1]]
    max_demand = [[2, 2], [2, 2], [2, 2]]
    state = SystemState(processes, resources, allocation, max_demand)
    return SimulationEngine(state)


class TestSimulationEngine(unittest.TestCase):
    def test_starts_in_protected_mode_with_initial_snapshot(self):
        engine = build_engine()
        self.assertEqual(engine.mode, Mode.PROTECTED)
        self.assertEqual(len(engine.timeline), 1)

    def test_request_appends_to_event_log_and_timeline(self):
        engine = build_engine()
        log_before = len(engine.state.event_log)
        timeline_before = len(engine.timeline)

        engine.request(pid=2, request_vector=[0, 0])

        self.assertGreater(len(engine.state.event_log), log_before)
        self.assertEqual(len(engine.timeline), timeline_before + 1)

    def test_set_mode_toggles_and_logs_change(self):
        engine = build_engine()
        log_before = len(engine.state.event_log)

        engine.set_mode(Mode.FREE)

        self.assertEqual(engine.mode, Mode.FREE)
        self.assertGreater(len(engine.state.event_log), log_before)

    def test_set_mode_to_same_mode_is_noop(self):
        engine = build_engine()
        log_before = len(engine.state.event_log)

        engine.set_mode(Mode.PROTECTED)

        self.assertEqual(len(engine.state.event_log), log_before)

    def test_finish_process_releases_all_resources(self):
        engine = build_engine()
        engine.finish_process(pid=2)

        self.assertEqual(engine.state.allocation[2], [0, 0])
        self.assertEqual(engine.state.available, [2, 2])

    def test_free_mode_grants_immediately_when_resources_available(self):
        engine = build_engine()
        engine.set_mode(Mode.FREE)

        granted = engine.request(pid=2, request_vector=[0, 0])

        self.assertTrue(granted)

    def test_free_mode_blocks_without_safety_check(self):
        engine = build_engine()
        engine.set_mode(Mode.FREE)

        # Available=(1,1); pedir mais do que existe fica pendente sem checagem de segurança
        granted = engine.request(pid=0, request_vector=[2, 1])

        self.assertFalse(granted)
        self.assertEqual(engine.outstanding_requests[0], [2, 1])


if __name__ == "__main__":
    unittest.main()
