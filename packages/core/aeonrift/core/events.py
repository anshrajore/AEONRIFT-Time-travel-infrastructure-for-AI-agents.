"""
AEONRIFT Core Event Model

Defines the append-only event schema, event types, state deltas, side-effect attributes,
and causal lineage fields for agent execution monitoring and time-travel recovery.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import hashlib
import json
import time


class EventType(str, Enum):
    LLM_CALL = "LLM_CALL"
    LLM_RESULT = "LLM_RESULT"
    TOOL_CALL = "TOOL_CALL"
    TOOL_RESULT = "TOOL_RESULT"
    FILE_WRITE = "FILE_WRITE"
    FILE_DELETE = "FILE_DELETE"
    PROCESS_START = "PROCESS_START"
    PROCESS_EXIT = "PROCESS_EXIT"
    NETWORK_REQUEST = "NETWORK_REQUEST"
    DATABASE_WRITE = "DATABASE_WRITE"
    EXTERNAL_SIDE_EFFECT = "EXTERNAL_SIDE_EFFECT"
    CHECKPOINT = "CHECKPOINT"
    FAILURE = "FAILURE"
    RECOVERY = "RECOVERY"
    REPLAY = "REPLAY"
    ROLLBACK = "ROLLBACK"
    COMPENSATION = "COMPENSATION"


class EventSource(str, Enum):
    AGENT = "AGENT"
    RUNTIME = "RUNTIME"
    OS = "OS"
    TOOL = "TOOL"
    EXTERNAL = "EXTERNAL"
    RECOVERY_ENGINE = "RECOVERY_ENGINE"


class SideEffectType(str, Enum):
    READ_ONLY = "READ_ONLY"
    MUTATING_REVERSIBLE = "MUTATING_REVERSIBLE"
    MUTATING_IRREVERSIBLE = "MUTATING_IRREVERSIBLE"
    EXTERNAL_STATE_MUTATION = "EXTERNAL_STATE_MUTATION"


class ReversibilityType(str, Enum):
    REVERSIBLE = "REVERSIBLE"
    COMPENSABLE = "COMPENSABLE"
    IRREVERSIBLE = "IRREVERSIBLE"


@dataclass
class StateDelta:
    """Represents mutations to agent memory, filesystem, or process environment."""
    memory_diff: Dict[str, Any] = field(default_factory=dict)
    files_added: List[str] = field(default_factory=list)
    files_modified: List[str] = field(default_factory=list)
    files_deleted: List[str] = field(default_factory=list)
    env_diff: Dict[str, Any] = field(default_factory=dict)
    process_delta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionEvent:
    """
    Primary execution primitive for AEONRIFT time-travel recovery and causal state tracking.
    """
    id: str
    agent_id: str
    execution_id: str
    event_type: EventType
    source: EventSource
    step_number: int

    branch_id: str = "branch_main"
    parent_event_id: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

    payload: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None

    input_hash: str = ""
    output_hash: str = ""
    causal_hash: str = ""

    state_delta: Optional[StateDelta] = None

    side_effect_type: SideEffectType = SideEffectType.READ_ONLY
    reversibility: ReversibilityType = ReversibilityType.REVERSIBLE
    idempotency_key: Optional[str] = None
    compensation_action: Optional[str] = None

    recovery_relevant: bool = False

    def compute_hashes(self) -> None:
        """Compute SHA-256 hashes for inputs, outputs, and causal chaining."""
        input_str = json.dumps(self.payload, sort_keys=True, default=str)
        self.input_hash = hashlib.sha256(input_str.encode('utf-8')).hexdigest()

        if self.result is not None:
            output_str = json.dumps(self.result, sort_keys=True, default=str)
            self.output_hash = hashlib.sha256(output_str.encode('utf-8')).hexdigest()

        causal_data = f"{self.parent_event_id}:{self.event_type}:{self.input_hash}:{self.output_hash}"
        self.causal_hash = hashlib.sha256(causal_data.encode('utf-8')).hexdigest()
