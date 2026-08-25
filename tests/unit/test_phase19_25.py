"""
Unit and Integration Tests for AEONRIFT Enterprise Components (Adapters, Gateway, LLM Replanner)
"""

import unittest
import time
import shutil
import tempfile
import os

from langchain import AeonriftLangChainAdapter
from crewai import AeonriftCrewAIToolWrapper
from api_server import AeonriftGatewayServer
from llm_replanner import LLMAssistedReplanner
from planner import FailureCategory, RecoveryMode
from aeonrift.core.graph import CausalStateGraph
from aeonrift.core.ledger import SideEffectLedger
from layered_engine import LayeredCheckpointEngine


class TestEnterprisePhaseComponents(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.execution_id = "test-phase19-25"

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_langchain_adapter(self):
        adapter = AeonriftLangChainAdapter(execution_id=self.execution_id)
        result = adapter.intercept_tool_call(
            tool_name="web_search",
            tool_input={"query": "AEONRIFT time travel"},
            is_side_effect=False
        )
        self.assertEqual(result["status"], "success")
        self.assertIn("web_search", result["result"])

    def test_crewai_tool_wrapper(self):
        wrapper = AeonriftCrewAIToolWrapper(execution_id=self.execution_id)
        
        def sample_tool(val: int):
            return val * 2

        wrapped = wrapper.wrap_tool("double_val", sample_tool, is_side_effect=False)
        res = wrapped(21)
        self.assertEqual(res, 42)

    def test_gateway_server_endpoints(self):
        gateway = AeonriftGatewayServer(base_storage_dir=self.test_dir)
        
        # Test Ingest Event
        ingest_res = gateway.handle_ingest_event(
            execution_id=self.execution_id,
            event_data={"tool_name": "db_query", "payload": {"query": "SELECT 1"}}
        )
        self.assertEqual(ingest_res["status"], "accepted")
        self.assertEqual(ingest_res["execution_id"], self.execution_id)

        # Test Get Timeline
        timeline_res = gateway.handle_get_timeline(execution_id=self.execution_id)
        self.assertEqual(timeline_res["execution_id"], self.execution_id)
        self.assertGreaterEqual(timeline_res["count"], 1)

        # Test Trigger Recovery
        rec_res = gateway.handle_trigger_recovery(
            execution_id=self.execution_id,
            failure_description="Connection timed out to LLM backend"
        )
        self.assertEqual(rec_res["execution_id"], self.execution_id)
        self.assertEqual(rec_res["failure_category"], FailureCategory.NETWORK_FAILURE.value)

    def test_llm_assisted_replanner(self):
        graph = CausalStateGraph(execution_id=self.execution_id)
        ledger = SideEffectLedger()

        replanner = LLMAssistedReplanner()
        plan = replanner.generate_assisted_plan(
            execution_id=self.execution_id,
            failure_event_id="evt_001",
            graph=graph,
            ledger=ledger,
            failure_category=FailureCategory.STATE_CORRUPTION
        )
        self.assertIsNotNone(plan)
        self.assertGreaterEqual(plan.confidence_score, 0.70)


if __name__ == "__main__":
    unittest.main()
