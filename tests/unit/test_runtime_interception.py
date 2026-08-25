"""
Unit tests for AEONRIFT Runtime Interception & Rollback Protection
"""

import os
import shutil
import tempfile
import unittest
import sys

sys.path.insert(0, os.path.abspath("packages/core"))
sys.path.insert(0, os.path.abspath("packages/runtime"))
sys.path.insert(0, os.path.abspath("storage/event-log"))

from aeonrift.core.events import SideEffectType, ReversibilityType
from aeonrift.runtime.interceptor import AeonriftRuntime, RuntimeExecutionBlockedError


class TestRuntimeInterception(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.runtime = AeonriftRuntime(
            agent_id="test_agent",
            execution_id="exec_999",
            storage_dir=self.test_dir
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_intercept_safe_tool(self):
        def sample_tool(path: str):
            return f"content of {path}"

        result = self.runtime.intercept_tool(
            tool_name="read_file",
            tool_func=sample_tool,
            tool_kwargs={"path": "notes.txt"},
            side_effect_type=SideEffectType.READ_ONLY
        )
        self.assertEqual(result, "content of notes.txt")
        self.assertEqual(self.runtime.step_counter, 1)

    def test_intercept_side_effect_and_block_duplicate_replay(self):
        def payment_tool(amount: int):
            return {"status": "paid", "tx_id": "tx_888"}

        key = "aeonrift:test_agent:exec_999:payment_unique_01"

        res = self.runtime.intercept_tool(
            tool_name="stripe_charge",
            tool_func=payment_tool,
            tool_kwargs={"amount": 100},
            side_effect_type=SideEffectType.MUTATING_IRREVERSIBLE,
            reversibility=ReversibilityType.IRREVERSIBLE,
            idempotency_key=key
        )
        self.assertEqual(res["tx_id"], "tx_888")

        # Second invocation with same idempotency key must be BLOCKED by Rollback Guard
        with self.assertRaises(RuntimeExecutionBlockedError):
            self.runtime.intercept_tool(
                tool_name="stripe_charge",
                tool_func=payment_tool,
                tool_kwargs={"amount": 100},
                side_effect_type=SideEffectType.MUTATING_IRREVERSIBLE,
                reversibility=ReversibilityType.IRREVERSIBLE,
                idempotency_key=key
            )


if __name__ == '__main__':
    unittest.main()
