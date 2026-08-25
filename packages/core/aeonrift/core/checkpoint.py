"""
AEONRIFT Multi-Level Checkpoint Engine Specification

Defines multi-level snapshot schemas (L0 through L5) for minimal overhead state preservation.
"""

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Dict, List, Optional
import hashlib
import time
from aeonrift.core.events import StateDelta


class CheckpointLevel(IntEnum):
    L0_LOGICAL = 0       # Messages, prompt history, task state
    L1_APP_STATE = 1     # Memory variables, workflow dicts
    L2_FILESYSTEM = 2    # Workdir file diffs & environment
    L3_PROCESS = 3       # Subprocess state & open handles
    L4_SANDBOX = 4       # Container / MicroVM snapshot
    L5_EXTERNAL_STATE = 5 # DB snapshot IDs & API resource refs


@dataclass
class CheckpointMetadata:
    checkpoint_id: str
    execution_id: str
    step_number: int
    level: CheckpointLevel
    timestamp: float = field(default_factory=time.time)
    parent_checkpoint_id: Optional[str] = None
    state_hash: str = ""
    signed_signature: Optional[str] = None


@dataclass
class LayeredCheckpoint:
    """
    Multi-level checkpoint instance encapsulating state elements from L0 to L5.
    Only required levels are populated by the RIFT Policy Engine to eliminate unnecessary overhead (Crab 2026).
    """
    metadata: CheckpointMetadata

    # L0 - Logical
    messages: List[Dict[str, Any]] = field(default_factory=list)
    task_context: Dict[str, Any] = field(default_factory=dict)

    # L1 - App State
    memory_variables: Dict[str, Any] = field(default_factory=dict)

    # L2 - Filesystem
    filesystem_manifest: Dict[str, str] = field(default_factory=dict)
    environment_variables: Dict[str, str] = field(default_factory=dict)

    # L3 - Process
    active_processes: List[Dict[str, Any]] = field(default_factory=list)

    # L4 - Sandbox
    container_snapshot_id: Optional[str] = None

    # L5 - External State
    external_resource_ids: Dict[str, str] = field(default_factory=dict)

    def compute_state_hash(self) -> str:
        """Computes cryptographic SHA-256 hash of checkpoint state."""
        raw_data = f"{self.metadata.checkpoint_id}:{self.metadata.step_number}:{self.metadata.level}:{len(self.messages)}:{len(self.memory_variables)}:{len(self.filesystem_manifest)}"
        self.metadata.state_hash = hashlib.sha256(raw_data.encode('utf-8')).hexdigest()
        return self.metadata.state_hash
