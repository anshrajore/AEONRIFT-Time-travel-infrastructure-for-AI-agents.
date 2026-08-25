"""
AEONRIFT Runtime Interception & Execution Observer

Intercepts tool execution, LLM prompts/outputs, and OS file mutations,
integrating with the Side-Effect Ledger and RIFT Policy Engine.
"""

from dataclasses import dataclass, field
import time
from typing import Any, Callable, Dict, Optional
from aeonrift.core.events import (
    ExecutionEvent, EventType, EventSource, SideEffectType, ReversibilityType, StateDelta
)
from aeonrift.core.graph import CausalStateGraph
from aeonrift.core.ledger import SideEffectLedger, SideEffectRecord
from aeonrift.core.policy import RiftPolicyEngine, RollbackGuard, PolicyAction
from event_store import DurableEventStore


class RuntimeExecutionBlockedError(Exception):
    """Raised when an operation is blocked by Rollback Guard or Policy Engine."""
    pass


class AeonriftRuntime:
    """
    Active execution wrapper for autonomous AI agents.
    Observes execution flow, intercepts non-deterministic tool/LLM steps, and guarantees fault tolerance.
    """
    def __init__(
        self,
        agent_id: str,
        execution_id: str,
        storage_dir: str = ".aeonrift/event_store",
        is_recovery_replay: bool = False
    ):
        self.agent_id = agent_id
        self.execution_id = execution_id
        self.step_counter = 0
        self.is_recovery_replay = is_recovery_replay

        self.event_store = DurableEventStore(storage_dir=storage_dir)
        self.causal_graph = CausalStateGraph(execution_id=execution_id)
        self.ledger = SideEffectLedger()
        self.policy_engine = RiftPolicyEngine()
        self.rollback_guard = RollbackGuard()

        self.last_event_id: Optional[str] = None

    def intercept_tool(
        self,
        tool_name: str,
        tool_func: Callable,
        tool_kwargs: Dict[str, Any],
        side_effect_type: SideEffectType = SideEffectType.READ_ONLY,
        reversibility: ReversibilityType = ReversibilityType.REVERSIBLE,
        idempotency_key: Optional[str] = None,
        compensation_tool: Optional[str] = None
    ) -> Any:
        """
        Intercepts tool invocation:
        1. Checks RollbackGuard for duplicate side-effect hazards.
        2. Evaluates Checkpoint Policy.
        3. Executes tool function.
        4. Emits ExecutionEvent to CausalStateGraph and EventStore.
        """
        self.step_counter += 1
        event_id = f"evt_{self.execution_id}_{self.step_counter:04d}"

        # Generate idempotency key if not explicitly passed
        if side_effect_type in (SideEffectType.MUTATING_IRREVERSIBLE, SideEffectType.EXTERNAL_STATE_MUTATION) and not idempotency_key:
            sig = f"{tool_name}:{str(tool_kwargs)}"
            idempotency_key = SideEffectLedger.generate_idempotency_key(self.agent_id, self.execution_id, sig)

        event = ExecutionEvent(
            id=event_id,
            agent_id=self.agent_id,
            execution_id=self.execution_id,
            parent_event_id=self.last_event_id,
            event_type=EventType.TOOL_CALL,
            source=EventSource.TOOL,
            step_number=self.step_counter,
            payload={"tool_name": tool_name, "kwargs": tool_kwargs},
            side_effect_type=side_effect_type,
            reversibility=reversibility,
            idempotency_key=idempotency_key,
            compensation_action=compensation_tool
        )

        # 1. Rollback Guard Hazard Check
        hazard = self.rollback_guard.check_rollback_hazard(
            event, self.ledger, is_recovery_replay=self.is_recovery_replay
        )
        if hazard.hazard_detected:
            raise RuntimeExecutionBlockedError(
                f"[AEONRIFT ROLLBACK GUARD BLOCK] {hazard.description}"
            )

        # 2. Evaluate Checkpoint Policy
        cp_decision = self.policy_engine.evaluate_checkpoint_need(event)
        event.recovery_relevant = cp_decision.recovery_relevant

        # 3. Execute tool invocation
        start_time = time.time()
        tool_result = tool_func(**tool_kwargs)
        duration = time.time() - start_time

        event.result = {"output": tool_result, "duration": duration}
        event.compute_hashes()

        # 4. Record in Ledger if side effect committed
        if side_effect_type in (SideEffectType.MUTATING_IRREVERSIBLE, SideEffectType.EXTERNAL_STATE_MUTATION) and idempotency_key:
            self.ledger.record_side_effect(
                effect_id=f"fx_{event_id}",
                agent_id=self.agent_id,
                execution_id=self.execution_id,
                tool_name=tool_name,
                action_signature=f"{tool_name}:{str(tool_kwargs)}",
                idempotency_key=idempotency_key,
                side_effect_type=side_effect_type,
                reversibility=reversibility,
                request_payload_hash=event.input_hash,
                response_payload_hash=event.output_hash,
                compensation_tool=compensation_tool
            )

        # 5. Record event in graph & store
        self.causal_graph.add_event(
            event,
            is_checkpoint=(cp_decision.action != PolicyAction.SKIP),
            checkpoint_level=cp_decision.recommended_level.value
        )
        self.event_store.append_event(event)

        self.last_event_id = event_id
        return tool_result
