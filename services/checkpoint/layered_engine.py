"""
AEONRIFT Layered Checkpoint Engine

Implements creation, persistence, restoration, and cryptographic validation
of multi-level checkpoints (L0–L5).
"""

from dataclasses import dataclass, field
import json
import os
import time
from typing import Dict, List, Optional
from aeonrift.core.checkpoint import CheckpointLevel, CheckpointMetadata, LayeredCheckpoint


class LayeredCheckpointEngine:
    """
    Manages creation, restoration, and cryptographic integrity of multi-level checkpoints.
    """
    def __init__(self, checkpoint_dir: str = ".aeonrift/checkpoints"):
        self.checkpoint_dir = checkpoint_dir
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        self.checkpoints: Dict[str, LayeredCheckpoint] = {}

    def create_checkpoint(
        self,
        checkpoint_id: str,
        execution_id: str,
        step_number: int,
        level: CheckpointLevel,
        messages: List[Dict] = None,
        memory_variables: Dict = None,
        filesystem_manifest: Dict[str, str] = None,
        environment_variables: Dict[str, str] = None,
        parent_checkpoint_id: Optional[str] = None
    ) -> LayeredCheckpoint:
        """Create and persist a multi-level checkpoint."""
        metadata = CheckpointMetadata(
            checkpoint_id=checkpoint_id,
            execution_id=execution_id,
            step_number=step_number,
            level=level,
            parent_checkpoint_id=parent_checkpoint_id
        )

        cp = LayeredCheckpoint(
            metadata=metadata,
            messages=messages or [],
            memory_variables=memory_variables or {},
            filesystem_manifest=filesystem_manifest or {},
            environment_variables=environment_variables or {}
        )
        cp.compute_state_hash()

        self.checkpoints[checkpoint_id] = cp

        # Persist checkpoint to disk
        filepath = os.path.join(self.checkpoint_dir, f"{checkpoint_id}.json")
        cp_dict = {
            "checkpoint_id": metadata.checkpoint_id,
            "execution_id": metadata.execution_id,
            "step_number": metadata.step_number,
            "level": metadata.level.value,
            "timestamp": metadata.timestamp,
            "parent_checkpoint_id": metadata.parent_checkpoint_id,
            "state_hash": metadata.state_hash,
            "messages": cp.messages,
            "memory_variables": cp.memory_variables,
            "filesystem_manifest": cp.filesystem_manifest,
            "environment_variables": cp.environment_variables
        }

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(json.dumps(cp_dict, indent=2))

        return cp

    def restore_checkpoint(self, checkpoint_id: str) -> Optional[LayeredCheckpoint]:
        """Restore a checkpoint from memory index or file storage."""
        if checkpoint_id in self.checkpoints:
            return self.checkpoints[checkpoint_id]

        filepath = os.path.join(self.checkpoint_dir, f"{checkpoint_id}.json")
        if not os.path.exists(filepath):
            return None

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        metadata = CheckpointMetadata(
            checkpoint_id=data["checkpoint_id"],
            execution_id=data["execution_id"],
            step_number=data["step_number"],
            level=CheckpointLevel(data["level"]),
            timestamp=data["timestamp"],
            parent_checkpoint_id=data.get("parent_checkpoint_id"),
            state_hash=data["state_hash"]
        )

        cp = LayeredCheckpoint(
            metadata=metadata,
            messages=data.get("messages", []),
            memory_variables=data.get("memory_variables", {}),
            filesystem_manifest=data.get("filesystem_manifest", {}),
            environment_variables=data.get("environment_variables", {})
        )

        self.checkpoints[checkpoint_id] = cp
        return cp
