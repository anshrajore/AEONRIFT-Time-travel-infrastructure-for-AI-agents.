"""
Unit tests for AEONRIFT Core Event Model & Policy Guard
"""

import unittest
from aeonrift.core.events import (
    ExecutionEvent, EventType, EventSource, SideEffectType, ReversibilityType
)
from aeonrift.core.graph import CausalStateGraph
from aeonrift.core.ledger import SideEffectLedger, LedgerStatus
from aeonrift.core.policy import RiftPolicyEngine, RollbackGuard, PolicyAction


class TestAeonriftCore(unittest.TestCase):

    def test_event_hash_computation(self):
        event = ExecutionEvent(
            id="evt_101",
            agent_id="test_agent",
            execution_id="exec_001",
            event_type=EventType.TOOL_CALL,
            source=EventSource.TOOL,
            step_number=1,
            payload={"tool": "file_write", "path": "config.yaml"}
        )
        event.compute_hashes()
        self.assertEqual(len(event.input_hash), 64)
        self.assertNotEqual(event.causal_hash, "")

    def test_causal_state_graph_trajectory_and_checkpoint(self):
        graph = CausalStateGraph(execution_id="exec_001")

        evt1 = ExecutionEvent(
            id="evt_001", agent_id="agent_1", execution_id="exec_001",
            event_type=EventType.LLM_CALL, source=EventSource.AGENT, step_number=1
        )
        evt2 = ExecutionEvent(
            id="evt_002", agent_id="agent_1", execution_id="exec_001",
            event_type=EventType.FILE_WRITE, source=EventSource.TOOL, step_number=2,
            parent_event_id="evt_001"
        )

        graph.add_event(evt1)
        graph.add_event(evt2, is_checkpoint=True, checkpoint_level=2)

        last_cp = graph.find_last_safe_checkpoint("evt_002")
        self.assertIsNotNone(last_cp)
        self.assertEqual(last_cp[0].event.id, "evt_002")
        self.assertEqual(last_cp[1], 2)

    def test_side_effect_ledger_and_rollback_guard(self):
        ledger = SideEffectLedger()
        key = SideEffectLedger.generate_idempotency_key("agent_1", "task_991", "payment.create")

        ledger.record_side_effect(
            effect_id="fx_001",
            agent_id="agent_1",
            execution_id="exec_001",
            tool_name="stripe.create_payment",
            action_signature="payment.create",
            idempotency_key=key,
            side_effect_type=SideEffectType.MUTATING_IRREVERSIBLE,
            reversibility=ReversibilityType.IRREVERSIBLE,
            request_payload_hash="abc123hash"
        )

        self.assertTrue(ledger.is_idempotency_key_committed(key))

        guard = RollbackGuard()
        event_repeat = ExecutionEvent(
            id="evt_003", agent_id="agent_1", execution_id="exec_001",
            event_type=EventType.TOOL_CALL, source=EventSource.TOOL, step_number=3,
            idempotency_key=key, payload={"tool_name": "stripe.create_payment"}
        )

        hazard = guard.check_rollback_hazard(event_repeat, ledger)
        self.assertTrue(hazard.hazard_detected)
        self.assertEqual(hazard.recommended_mode, "REPAIR")

    def test_rift_policy_engine_semantic_skipping(self):
        engine = RiftPolicyEngine()

        llm_evt = ExecutionEvent(
            id="evt_llm", agent_id="a1", execution_id="ex1",
            event_type=EventType.LLM_CALL, source=EventSource.AGENT, step_number=1
        )
        decision = engine.evaluate_checkpoint_need(llm_evt)
        self.assertEqual(decision.action, PolicyAction.SKIP)

        file_evt = ExecutionEvent(
            id="evt_file", agent_id="a1", execution_id="ex1",
            event_type=EventType.FILE_WRITE, source=EventSource.TOOL, step_number=2
        )
        decision_file = engine.evaluate_checkpoint_need(file_evt)
        self.assertEqual(decision_file.action, PolicyAction.FULL_CHECKPOINT)


if __name__ == '__main__':
    unittest.main()
