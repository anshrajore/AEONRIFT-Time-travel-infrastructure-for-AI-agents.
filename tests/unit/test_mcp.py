"""
Unit tests for AEONRIFT Model Context Protocol (MCP) Server and Throughput Engine.
"""

import unittest
import json
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT_DIR, "packages", "core"))
sys.path.insert(0, os.path.join(ROOT_DIR, "packages", "runtime"))
sys.path.insert(0, os.path.join(ROOT_DIR, "services", "checkpoint"))
sys.path.insert(0, os.path.join(ROOT_DIR, "services", "recovery"))
sys.path.insert(0, os.path.join(ROOT_DIR, "services", "state"))
sys.path.insert(0, os.path.join(ROOT_DIR, "services", "coordinator"))
sys.path.insert(0, os.path.join(ROOT_DIR, "storage", "event-log"))
sys.path.insert(0, os.path.join(ROOT_DIR, "services", "throughput"))
sys.path.insert(0, os.path.join(ROOT_DIR, "services", "mcp"))

from services.mcp.server import AeonriftMCPServer
from services.throughput.compressor import AdaptiveCompressor
from services.throughput.ring_buffer import EventRingBuffer


class TestMCPServer(unittest.TestCase):
    def setUp(self):
        self.server = AeonriftMCPServer(storage_dir=".aeonrift/test_mcp_store")

    def test_mcp_handshake_initialize(self):
        init_req = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "2024-11-05"}
        })
        res_str = self.server.process_rpc_message(init_req)
        res = json.loads(res_str)
        self.assertEqual(res["id"], 1)
        self.assertEqual(res["result"]["serverInfo"]["name"], "aeonrift-time-travel")

    def test_mcp_tools_list(self):
        req = json.dumps({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        })
        res = json.loads(self.server.process_rpc_message(req))
        tools = res["result"]["tools"]
        tool_names = [t["name"] for t in tools]
        self.assertIn("aeonrift_record_event", tool_names)
        self.assertIn("aeonrift_check_rollback_hazard", tool_names)
        self.assertIn("aeonrift_create_checkpoint", tool_names)
        self.assertIn("aeonrift_autonomous_recover", tool_names)
        self.assertIn("aeonrift_health_doctor", tool_names)

    def test_mcp_record_event_and_checkpoint(self):
        # 1. Record event
        req = json.dumps({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "aeonrift_record_event",
                "arguments": {
                    "execution_id": "test_exec_mcp",
                    "agent_id": "claude_agent",
                    "tool_name": "fetch_user_data",
                    "arguments": {"user_id": 42}
                }
            }
        })
        res = json.loads(self.server.process_rpc_message(req))
        content = json.loads(res["result"]["content"][0]["text"])
        self.assertEqual(content["status"], "RECORDED")
        self.assertEqual(content["step_number"], 1)

        # 2. Create checkpoint
        cp_req = json.dumps({
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "aeonrift_create_checkpoint",
                "arguments": {
                    "execution_id": "test_exec_mcp",
                    "state_payload": {"memory": {"last_user": 42}}
                }
            }
        })
        cp_res = json.loads(self.server.process_rpc_message(cp_req))
        cp_content = json.loads(cp_res["result"]["content"][0]["text"])
        self.assertEqual(cp_content["status"], "CHECKPOINT_SAVED")


class TestThroughputEngine(unittest.TestCase):
    def test_compressor(self):
        compressor = AdaptiveCompressor(min_compress_size_bytes=50)
        large_dict = {"data": "A" * 500, "meta": {"nested": "value", "id": 100}}
        compressed, is_comp, codec = compressor.compress_payload(large_dict)
        self.assertTrue(is_comp)
        self.assertEqual(codec, "zlib")
        restored = compressor.decompress_payload(compressed, codec)
        self.assertEqual(restored, large_dict)

    def test_ring_buffer(self):
        flushed_batches = []
        def on_flush(batch):
            flushed_batches.append(batch)

        buffer = EventRingBuffer(capacity=100, batch_size=5, flush_interval_ms=50, flush_callback=on_flush)
        for i in range(12):
            buffer.push({"event_id": f"evt_{i}"})

        # Manual flush remaining
        buffer.flush()
        buffer.close()

        total_items = sum(len(b) for b in flushed_batches)
        self.assertEqual(total_items, 12)


if __name__ == "__main__":
    unittest.main()
