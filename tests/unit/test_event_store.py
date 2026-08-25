"""
Unit tests for AEONRIFT Durable Event Store
"""

import os
import shutil
import tempfile
import unittest
import sys

# Ensure storage path is in sys.path
sys.path.insert(0, os.path.abspath("packages/core"))
sys.path.insert(0, os.path.abspath("storage/event-log"))

from aeonrift.core.events import ExecutionEvent, EventType, EventSource
from event_store import DurableEventStore


class TestEventStore(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.store = DurableEventStore(storage_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_append_and_read_events(self):
        evt1 = ExecutionEvent(
            id="evt_01", agent_id="agent_alpha", execution_id="exec_100",
            event_type=EventType.LLM_CALL, source=EventSource.AGENT, step_number=1,
            payload={"prompt": "Hello"}
        )
        evt2 = ExecutionEvent(
            id="evt_02", agent_id="agent_alpha", execution_id="exec_100",
            event_type=EventType.TOOL_CALL, source=EventSource.TOOL, step_number=2,
            parent_event_id="evt_01", payload={"tool": "search"}
        )

        self.store.append_event(evt1)
        self.store.append_event(evt2)

        # Clear in-memory cache to force disk reload
        self.store._indexes.clear()

        events = self.store.read_trajectory("exec_100")
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].id, "evt_01")
        self.assertEqual(events[1].id, "evt_02")
        self.assertEqual(events[1].parent_event_id, "evt_01")


if __name__ == '__main__':
    unittest.main()
