"""
Unit tests for AEONRIFT Recovery Planner & Failure Classifier
"""

import os
import shutil
import tempfile
import unittest
import sys

sys.path.insert(0, os.path.abspath("packages/core"))
sys.path.insert(0, os.path.abspath("packages/runtime"))
sys.path.insert(0, os.path.abspath("services/recovery"))
sys.path.insert(0, os.path.abspath("storage/event-log"))

from aeonrift.core.events import (
    ExecutionEvent, EventType, EventSource, SideEffectType, ReversibilityType
)
from aeonrift.core.graph import CausalStateGraph
from aeonrift.core.ledger import SideEffectLedger
from planner import RecoveryPlanner, RecoveryMode, FailureCategory


class TestRecoveryPlanner(unittest.TestCase):

    def setUp(self):
        self.planner = RecoveryPlanner()

    def test_clean_trajectory_selects_replay(self):
        graph = CausalStateGraph(execution_id="exec_500")

        evt1 = ExecutionEvent(
            id="evt_1", agent_id="a1", execution_id="exec_500",
            event_type=EventType.LLM_CALL, source=EventSource.AGENT, step_number=1
        )
        evt2 = ExecutionEvent(
            id="evt_2", agent_id="a1", execution_id="exec_500",
            event_type=EventType.FILE_WRITE, source=EventSource.TOOL, step_number=2,
            parent_event_id="evt_1"
        )
        evt3 = ExecutionEvent(
            id="evt_3", agent_id="a1", execution_id="exec_500",
            event_type=EventType.TOOL_CALL, source=EventSource.TOOL, step_number=3,
            parent_event_id="evt_2", payload={"error": "connection timeout"}
        )

        graph.add_event(evt1)
        graph.add_event(evt2, is_checkpoint=True, checkpoint_level=2)
        graph.add_event(evt3)

        ledger = SideEffectLedger()
        plan = self.planner.generate_plan("exec_500", "evt_3", graph, ledger)

        self.assertEqual(plan.mode, RecoveryMode.REPLAY)
        self.assertEqual(plan.checkpoint_id, "evt_2")
        self.assertEqual(plan.replay_until_step, 2)
        self.assertGreaterEqual(plan.confidence_score, 0.90)

    def test_trajectory_with_side_effects_selects_repair(self):
        graph = CausalStateGraph(execution_id="exec_600")
        ledger = SideEffectLedger()

        evt1 = ExecutionEvent(
            id="evt_10", agent_id="a1", execution_id="exec_600",
            event_type=EventType.LLM_CALL, source=EventSource.AGENT, step_number=1
        )
        evt2 = ExecutionEvent(
            id="evt_20", agent_id="a1", execution_id="exec_600",
            event_type=EventType.FILE_WRITE, source=EventSource.TOOL, step_number=2,
            parent_event_id="evt_10"
        )

        key = SideEffectLedger.generate_idempotency_key("a1", "exec_600", "stripe_charge")

        evt3 = ExecutionEvent(
            id="evt_30", agent_id="a1", execution_id="exec_600",
            event_type=EventType.TOOL_CALL, source=EventSource.TOOL, step_number=3,
            parent_event_id="evt_20", side_effect_type=SideEffectType.MUTATING_IRREVERSIBLE,
            reversibility=ReversibilityType.IRREVERSIBLE, idempotency_key=key,
            payload={"tool_name": "stripe_charge"}
        )

        evt4 = ExecutionEvent(
            id="evt_40", agent_id="a1", execution_id="exec_600",
            event_type=EventType.TOOL_CALL, source=EventSource.TOOL, step_number=4,
            parent_event_id="evt_30", payload={"error": "process crash"}
        )

        graph.add_event(evt1)
        graph.add_event(evt2, is_checkpoint=True, checkpoint_level=2)
        graph.add_event(evt3)
        graph.add_event(evt4)

        ledger.record_side_effect(
            effect_id="fx_30", agent_id="a1", execution_id="exec_600",
            tool_name="stripe_charge", action_signature="stripe_charge",
            idempotency_key=key, side_effect_type=SideEffectType.MUTATING_IRREVERSIBLE,
            reversibility=ReversibilityType.IRREVERSIBLE, request_payload_hash="hash1"
        )

        plan = self.planner.generate_plan("exec_600", "evt_40", graph, ledger)

        self.assertEqual(plan.mode, RecoveryMode.REPAIR)
        self.assertEqual(plan.checkpoint_id, "evt_20")
        self.assertIn("stripe_charge", plan.blocked_actions)


if __name__ == '__main__':
    unittest.main()
