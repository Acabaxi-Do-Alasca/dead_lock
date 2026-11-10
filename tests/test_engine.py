import unittest

from core.models import Process, ProcessState, ResourceType
from core.state import SystemState
from scenarios.loader import build_engine_from_scenario
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

    def test_finish_process_wakes_up_blocked_process_in_free_mode(self):
        engine = build_engine()
        engine.set_mode(Mode.FREE)
        engine.request(pid=0, request_vector=[1, 2])  # Available=(1,1): P0 bloqueia
        self.assertEqual(engine.state.processes[0].state, ProcessState.BLOCKED)

        engine.finish_process(pid=2)  # libera (1,1) -> Available=(2,2)

        self.assertEqual(engine.state.processes[0].state, ProcessState.RUNNING)
        self.assertEqual(engine.state.allocation[0], [2, 2])
        self.assertEqual(engine.outstanding_requests[0], [0, 0])

    def test_finish_process_retries_blocked_process_through_banker(self):
        engine = build_engine()  # modo Protegido
        engine.request(pid=1, request_vector=[1, 0])  # Cenário B: negado (inseguro)
        self.assertEqual(engine.state.processes[1].state, ProcessState.BLOCKED)

        engine.finish_process(pid=2)  # libera recursos; Banqueiro reavalia P1

        self.assertEqual(engine.state.processes[1].state, ProcessState.RUNNING)
        self.assertEqual(engine.state.allocation[1], [1, 1])

    def test_state_log_is_mirrored_to_terminal_logger(self):
        engine = build_engine()
        with self.assertLogs("banqueiro", level="INFO") as captured:
            engine.request(pid=1, request_vector=[1, 0])
        output = "\n".join(captured.output)
        self.assertIn("Testando P0", output)
        self.assertIn("NEGADA", output)


class TestDeadlockRecovery(unittest.TestCase):
    def build_deadlocked_engine(self):
        engine = build_engine_from_scenario("C")
        engine.request(pid=0, request_vector=[0, 1, 0])
        engine.request(pid=1, request_vector=[0, 0, 1])
        engine.request(pid=2, request_vector=[1, 0, 0])
        return engine

    def test_recovery_aborts_a_victim_and_breaks_the_cycle(self):
        engine = self.build_deadlocked_engine()
        self.assertEqual(sorted(engine.check_deadlock().deadlocked_processes), [0, 1, 2])

        result = engine.recover_from_deadlock()

        self.assertEqual(result.victims, [0])  # todos retêm 1 recurso: desempate pelo menor índice
        self.assertEqual(result.final_detection.deadlocked_processes, [])
        self.assertEqual(engine.state.processes[0].state, ProcessState.ABORTED)
        self.assertEqual(engine.state.allocation[0], [0, 0, 0])
        # R0 liberado pela vítima foi repassado a P2, que esperava por ele
        self.assertEqual(engine.state.processes[2].state, ProcessState.RUNNING)
        self.assertEqual(engine.state.allocation[2], [1, 0, 1])
        self.assertEqual(engine.check_deadlock().deadlocked_processes, [])

    def test_recovery_logs_detection_choice_and_abort(self):
        engine = self.build_deadlocked_engine()
        engine.recover_from_deadlock()
        categories = [e.category for e in engine.state.event_log]
        self.assertIn("RECOVERY", categories)
        self.assertIn("ABORT", categories)
        self.assertIn("DEADLOCK_CHECK", categories)

    def test_recovery_without_deadlock_does_nothing(self):
        engine = build_engine()
        allocation_before = [row[:] for row in engine.state.allocation]

        result = engine.recover_from_deadlock()

        self.assertEqual(result.victims, [])
        self.assertEqual(engine.state.allocation, allocation_before)

    def test_remaining_processes_can_finish_after_recovery(self):
        engine = self.build_deadlocked_engine()
        engine.recover_from_deadlock()

        engine.finish_process(pid=2)  # P2 termina e libera R0 e R2; P1 recebe R2

        self.assertEqual(engine.state.processes[1].state, ProcessState.RUNNING)
        self.assertEqual(engine.state.allocation[1], [0, 1, 1])


if __name__ == "__main__":
    unittest.main()
