"""
AEONRIFT RIFT Policy Engine & Semantic Rollback Guard

Implements semantic-aware checkpointing policies (Crab 2026) and rollback hazard protection (ACRFence 2026).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from aeonrift.core.events import ExecutionEvent, EventType, SideEffectType, ReversibilityType
from aeonrift.core.checkpoint import CheckpointLevel
from aeonrift.core.ledger import SideEffectLedger


class PolicyAction(str, Enum):
    SKIP = "SKIP"
    LIGHT_CHECKPOINT = "LIGHT_CHECKPOINT" # L0 - L1
    FULL_CHECKPOINT = "FULL_CHECKPOINT"   # L0 - L5


@dataclass
class CheckpointDecision:
    action: PolicyAction
    recommended_level: CheckpointLevel
    reason: str
    recovery_relevant: bool


@dataclass
class RollbackHazard:
    hazard_detected: bool
    event_id: str
    tool_name: str
    idempotency_key: Optional[str]
    description: str
    recommended_mode: str  # REPAIR, COMPENSATE, BLOCK


@dataclass
class RiftPolicyEngine:
    """
    Semantic Checkpoint Policy Engine.
    Determines whether an action modified recovery-relevant state, avoiding unnecessary checkpoint traffic.
    """

    def evaluate_checkpoint_need(self, event: ExecutionEvent) -> CheckpointDecision:
        """
        Determines whether an event warrants a checkpoint and at what level.
        Non-mutating read steps or conversational turns are skipped (SKIP).
        """
        # File writes or deletions -> L2 Filesystem checkpoint
        if event.event_type in (EventType.FILE_WRITE, EventType.FILE_DELETE):
            return CheckpointDecision(
                action=PolicyAction.FULL_CHECKPOINT,
                recommended_level=CheckpointLevel.L2_FILESYSTEM,
                reason="Filesystem mutation detected",
                recovery_relevant=True
            )

        # External side effect -> L5 External State checkpoint
        if event.side_effect_type in (SideEffectType.MUTATING_IRREVERSIBLE, SideEffectType.EXTERNAL_STATE_MUTATION):
            return CheckpointDecision(
                action=PolicyAction.FULL_CHECKPOINT,
                recommended_level=CheckpointLevel.L5_EXTERNAL_STATE,
                reason="External state mutation side-effect committed",
                recovery_relevant=True
            )

        # Subprocess spawn -> L3 Process checkpoint
        if event.event_type == EventType.PROCESS_START:
            return CheckpointDecision(
                action=PolicyAction.LIGHT_CHECKPOINT,
                recommended_level=CheckpointLevel.L3_PROCESS,
                reason="Process state change detected",
                recovery_relevant=True
            )

        # Simple read/conversational turns -> SKIP
        if event.event_type in (EventType.LLM_CALL, EventType.LLM_RESULT):
            return CheckpointDecision(
                action=PolicyAction.SKIP,
                recommended_level=CheckpointLevel.L0_LOGICAL,
                reason="Read-only LLM turn produces no immediate recovery-relevant state",
                recovery_relevant=False
            )

        # Default fallback
        return CheckpointDecision(
            action=PolicyAction.LIGHT_CHECKPOINT,
            recommended_level=CheckpointLevel.L1_APP_STATE,
            reason="Standard execution step",
            recovery_relevant=True
        )


@dataclass
class RollbackGuard:
    """
    Enforces Semantic Rollback Protection (ACRFence 2026).
    Prevents restored trajectories from re-executing non-idempotent side effects.
    """

    def check_rollback_hazard(
        self,
        event: ExecutionEvent,
        ledger: SideEffectLedger,
        is_recovery_replay: bool = False
    ) -> RollbackHazard:
        """
        Validates whether executing or re-executing an event presents a Rollback Hazard.
        """
        if event.idempotency_key and ledger.is_idempotency_key_committed(event.idempotency_key):
            return RollbackHazard(
                hazard_detected=True,
                event_id=event.id,
                tool_name=event.payload.get("tool_name", "unknown"),
                idempotency_key=event.idempotency_key,
                description=f"Action '{event.idempotency_key}' already committed in external ledger. Duplicate execution blocked.",
                recommended_mode="REPAIR"
            )

        if is_recovery_replay and event.reversibility == ReversibilityType.IRREVERSIBLE:
            return RollbackHazard(
                hazard_detected=True,
                event_id=event.id,
                tool_name=event.payload.get("tool_name", "unknown"),
                idempotency_key=event.idempotency_key,
                description="Irreversible external action cannot be safely re-executed upon restore.",
                recommended_mode="COMPENSATE"
            )

        return RollbackHazard(
            hazard_detected=False,
            event_id=event.id,
            tool_name=event.payload.get("tool_name", "unknown"),
            idempotency_key=event.idempotency_key,
            description="Safe to execute",
            recommended_mode="REPLAY"
        )
