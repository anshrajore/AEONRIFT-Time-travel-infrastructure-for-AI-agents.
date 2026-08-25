"""
AEONRIFT End-to-End Demonstration Agent

Demonstrates:
1. Active interception of tool calls & file system state deltas.
2. External payment side-effect registration with idempotency tracking.
3. Mid-trajectory crash recovery.
4. AEONRIFT Recovery Engine generating a REPAIR plan with Semantic Rollback Protection.
"""

import os
import shutil
import sys

# Add project roots to path
sys.path.insert(0, os.path.abspath("packages/core"))
sys.path.insert(0, os.path.abspath("packages/runtime"))
sys.path.insert(0, os.path.abspath("services/checkpoint"))
sys.path.insert(0, os.path.abspath("services/recovery"))
sys.path.insert(0, os.path.abspath("storage/event-log"))
sys.path.insert(0, os.path.abspath("packages/cli"))

from aeonrift.core.events import SideEffectType, ReversibilityType
from aeonrift.runtime.interceptor import AeonriftRuntime, RuntimeExecutionBlockedError
from aeonrift.cli.main import main as cli_main


def main():
    print("\n🚀 STAGE 1: Starting Agent Run under AEONRIFT Runtime (Execution ID: exec_8219)...\n")

    # Clean previous run state
    if os.path.exists(".aeonrift/event_store/exec_8219.jsonl"):
        os.remove(".aeonrift/event_store/exec_8219.jsonl")

    runtime = AeonriftRuntime(
        agent_id="coding_agent_01",
        execution_id="exec_8219",
        storage_dir=".aeonrift/event_store"
    )

    # Step 1: Read config file (Read-only)
    def read_config():
        return "env: production\nversion: 1.0.0"

    runtime.intercept_tool(
        tool_name="read_file",
        tool_func=read_config,
        tool_kwargs={},
        side_effect_type=SideEffectType.READ_ONLY
    )
    print("  [Step 01] Read configuration -> OK")

    # Step 2: Modify package.json (Filesystem Checkpoint L2)
    def update_package(path: str = "package.json"):
        return f"Updated {path} dependencies"

    runtime.intercept_tool(
        tool_name="write_file",
        tool_func=update_package,
        tool_kwargs={"path": "package.json"},
        side_effect_type=SideEffectType.MUTATING_REVERSIBLE,
        reversibility=ReversibilityType.REVERSIBLE
    )
    print("  [Step 02] Modified package.json -> 💾 Checkpoint L2 Created")

    # Step 3: Execute Stripe Payment API Call (External Irreversible Side Effect)
    def create_payment(order_id: str, amount: int):
        return {"status": "COMMITTED", "tx_id": "tx_stripe_9941"}

    payment_key = "aeonrift:coding_agent_01:exec_8219:stripe_payment_order_991"

    payment_res = runtime.intercept_tool(
        tool_name="stripe.create_payment",
        tool_func=create_payment,
        tool_kwargs={"order_id": "order_991", "amount": 250},
        side_effect_type=SideEffectType.MUTATING_IRREVERSIBLE,
        reversibility=ReversibilityType.IRREVERSIBLE,
        idempotency_key=payment_key
    )
    print(f"  [Step 03] Executed stripe.create_payment -> {payment_res['status']} ({payment_res['tx_id']})")

    # Step 4: Simulate Agent Process Crash / Network Failure
    print("\n⚠️ STAGE 2: Injecting Unhandled Process Failure at Step 04 (API Timeout)...")
    from aeonrift.core.events import ExecutionEvent, EventType, EventSource
    crash_evt = ExecutionEvent(
        id="evt_exec_8219_0004",
        agent_id="coding_agent_01",
        execution_id="exec_8219",
        event_type=EventType.FAILURE,
        source=EventSource.RUNTIME,
        step_number=4,
        payload={"error": "API timeout connection reset"},
        parent_event_id="evt_exec_8219_0003"
    )
    runtime.event_store.append_event(crash_evt)
    print("  [Step 04] Process Crashed!")

    print("\n🔍 STAGE 3: Executing CLI Timeline Inspection...\n")
    sys.argv = ["aeonrift", "timeline", "exec_8219"]
    cli_main()

    print("\n🛡️ STAGE 4: Executing AEONRIFT Autonomous Recovery Engine...\n")
    sys.argv = ["aeonrift", "recover", "exec_8219"]
    cli_main()


if __name__ == '__main__':
    main()
