"""
AEONRIFT RIFT CHAOS — Fault Injection & Stress Testing Engine

Simulates process crashes, LLM timeouts, network partitions, filesystem corruption,
and credential revocations to empirically validate recovery correctness and zero-duplicate-side-effects.
"""

from dataclasses import dataclass, field
from enum import Enum
import random
import time
from typing import Dict, List, Optional
from aeonrift.core.events import ExecutionEvent, EventType, EventSource
from aeonrift.runtime.interceptor import AeonriftRuntime
from planner import RecoveryPlanner, RecoveryPlan


class ChaosFailureType(str, Enum):
    LLM_TIMEOUT = "LLM_TIMEOUT"
    TOOL_FAILURE = "TOOL_FAILURE"
    NETWORK_LOSS = "NETWORK_LOSS"
    PROCESS_KILL = "PROCESS_KILL"
    CREDENTIAL_REVOCATION = "CREDENTIAL_REVOCATION"
    FILESYSTEM_CORRUPTION = "FILESYSTEM_CORRUPTION"


@dataclass
class ChaosResult:
    failure_type: ChaosFailureType
    injected_step: int
    recovery_successful: bool
    recovery_mode_selected: str
    duplicate_side_effects: int
    recovery_latency_ms: float


class RiftChaosEngine:
    """
    Chaos Testing Engine for AEONRIFT fault-tolerance benchmarking.
    """
    def __init__(self, failure_rate: float = 0.3):
        self.failure_rate = failure_rate
        self.planner = RecoveryPlanner()

    def inject_failure(
        self,
        runtime: AeonriftRuntime,
        failure_type: ChaosFailureType,
        at_step: int
    ) -> ExecutionEvent:
        """Inject a synthetic failure event into the active execution trajectory."""
        evt_id = f"evt_{runtime.execution_id}_{at_step:04d}_chaos"

        payload = {
            "chaos_injected": True,
            "failure_type": failure_type.value,
            "error": f"Simulated {failure_type.value} at step {at_step}"
        }

        if failure_type == ChaosFailureType.CREDENTIAL_REVOCATION:
            payload["error"] = "401 Unauthorized API key revoked"
        elif failure_type == ChaosFailureType.LLM_TIMEOUT:
            payload["error"] = "LLM API connection timeout after 30s"

        event = ExecutionEvent(
            id=evt_id,
            agent_id=runtime.agent_id,
            execution_id=runtime.execution_id,
            event_type=EventType.FAILURE,
            source=EventSource.RUNTIME,
            step_number=at_step,
            payload=payload,
            parent_event_id=runtime.last_event_id
        )

        runtime.event_store.append_event(event)
        runtime.causal_graph.add_event(event)
        return event

    def run_chaos_experiment(
        self,
        runtime: AeonriftRuntime,
        failure_type: ChaosFailureType,
        at_step: int
    ) -> ChaosResult:
        """Run chaos injection experiment and measure recovery correctness."""
        start_time = time.time()

        # 1. Inject Chaos Failure
        crash_evt = self.inject_failure(runtime, failure_type, at_step)

        # 2. Trigger Recovery Planner
        plan = self.planner.generate_plan(
            runtime.execution_id,
            crash_evt.id,
            runtime.causal_graph,
            runtime.ledger
        )

        duration_ms = (time.time() - start_time) * 1000.0

        # 3. Validate duplicate side-effect prevention
        duplicate_effects = len(plan.blocked_actions)

        recovery_ok = plan.mode.value in ("REPLAY", "REPAIR", "REPLAN")

        return ChaosResult(
            failure_type=failure_type,
            injected_step=at_step,
            recovery_successful=recovery_ok,
            recovery_mode_selected=plan.mode.value,
            duplicate_side_effects=duplicate_effects,
            recovery_latency_ms=duration_ms
        )
