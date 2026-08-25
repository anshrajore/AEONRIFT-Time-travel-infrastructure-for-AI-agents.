"""
Unit tests for ML Policies, Distributed Fleet Coordinator, and Dashboard
"""

import os
import shutil
import tempfile
import unittest
import sys

sys.path.insert(0, os.path.abspath("packages/core"))
sys.path.insert(0, os.path.abspath("packages/runtime"))
sys.path.insert(0, os.path.abspath("services/coordinator"))
sys.path.insert(0, os.path.abspath("services/recovery"))
sys.path.insert(0, os.path.abspath("storage/event-log"))
sys.path.insert(0, os.path.abspath("ml/datasets"))
sys.path.insert(0, os.path.abspath("ml/models"))
sys.path.insert(0, os.path.abspath("apps/dashboard"))

from dataset_generator import RiftFailDatasetGenerator
from recovery_policy import RiftPredictPolicyModel
from checkpoint_policy import RiftCheckpointPredictor
from fleet_coordinator import DistributedAgentCoordinator
from app import AeonriftDashboardServer


class TestPhase13_16_17(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_ml_dataset_generator(self):
        gen = RiftFailDatasetGenerator()
        samples = gen.generate_samples(count=10)
        self.assertEqual(len(samples), 10)
        self.assertTrue(samples[0].sample_id.startswith("sample_"))

    def test_ml_predict_models(self):
        rec_model = RiftPredictPolicyModel()
        pred = rec_model.predict_strategy(
            failure_category="TOOL_FAILURE",
            state_divergence=0.1,
            environment_drift=0.1,
            has_irreversible_side_effect=True,
            checkpoint_age_steps=2
        )
        self.assertEqual(pred.recommended_strategy, "REPAIR")

        cp_model = RiftCheckpointPredictor()
        cp_pred = cp_model.predict_importance("TOOL_CALL", "MUTATING_IRREVERSIBLE", 0, 0)
        self.assertTrue(cp_pred.should_checkpoint)
        self.assertEqual(cp_pred.recommended_level, 5)

    def test_fleet_coordinator_multi_agent_recovery(self):
        coord = DistributedAgentCoordinator()
        g_a = coord.register_agent("agent_A", "exec_A")
        g_b = coord.register_agent("agent_B", "exec_B")

        from aeonrift.core.events import ExecutionEvent, EventType, EventSource
        evt1 = ExecutionEvent(id="e_a1", agent_id="agent_A", execution_id="exec_A", event_type=EventType.LLM_CALL, source=EventSource.AGENT, step_number=1)
        g_a.add_event(evt1, is_checkpoint=True)

        coord.record_inter_agent_message("msg_1", "agent_A", "agent_B", step_number=2, payload_hash="hash_msg")

        evt2 = ExecutionEvent(id="e_a2", agent_id="agent_A", execution_id="exec_A", event_type=EventType.FAILURE, source=EventSource.RUNTIME, step_number=3)
        g_a.add_event(evt2)

        fleet_plan = coord.coordinate_fleet_recovery("agent_A", "e_a2")
        self.assertTrue(fleet_plan.distributed_cascade_prevented)
        self.assertIn("agent_B", fleet_plan.affected_agents)

    def test_dashboard_server_dag_rendering(self):
        dash = AeonriftDashboardServer(storage_dir=self.test_dir)
        dag_data = dash.get_execution_dag_data("non_existent_exec")
        self.assertEqual(dag_data["total_nodes"], 0)

        diff = dash.compute_state_diff({"memory_variables": {"v1": 1}}, {"memory_variables": {"v1": 2, "v2": 3}})
        self.assertEqual(diff["memory_diff"]["added"], {"v2": 3})
        self.assertEqual(diff["memory_diff"]["modified"]["v1"], {"old": 1, "new": 2})


if __name__ == '__main__':
    unittest.main()
