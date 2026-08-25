"""
AEONRIFT Durable Event Store

Implements append-only persistent event storage for execution trajectories,
time-travel query interfaces, and causal history replay.
"""

from dataclasses import dataclass, field
import json
import os
from typing import Dict, List, Optional
from aeonrift.core.events import ExecutionEvent, EventType, EventSource, SideEffectType, ReversibilityType


class DurableEventStore:
    """
    Append-only durable storage engine for AEONRIFT execution events.
    Supports file-backed storage (JSONL) and in-memory indexing for high throughput.
    """
    def __init__(self, storage_dir: str = ".aeonrift/event_store"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        self._indexes: Dict[str, List[ExecutionEvent]] = {}  # execution_id -> event list

    def _get_log_filepath(self, execution_id: str) -> str:
        return os.path.join(self.storage_dir, f"{execution_id}.jsonl")

    def append_event(self, event: ExecutionEvent) -> bool:
        """Append an event to the persistent event log and update in-memory trajectory index."""
        event.compute_hashes()

        # Update in-memory index
        trajectory = self._indexes.setdefault(event.execution_id, [])
        trajectory.append(event)

        # Write to JSONL file
        log_path = self._get_log_filepath(event.execution_id)
        event_dict = {
            "id": event.id,
            "agent_id": event.agent_id,
            "execution_id": event.execution_id,
            "branch_id": event.branch_id,
            "parent_event_id": event.parent_event_id,
            "timestamp": event.timestamp,
            "event_type": event.event_type.value,
            "source": event.source.value,
            "step_number": event.step_number,
            "payload": event.payload,
            "result": event.result,
            "input_hash": event.input_hash,
            "output_hash": event.output_hash,
            "causal_hash": event.causal_hash,
            "side_effect_type": event.side_effect_type.value,
            "reversibility": event.reversibility.value,
            "idempotency_key": event.idempotency_key,
            "recovery_relevant": event.recovery_relevant
        }

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event_dict) + "\n")

        return True

    def read_trajectory(self, execution_id: str, branch_id: str = "branch_main") -> List[ExecutionEvent]:
        """Load and return all events for a given execution ID and branch."""
        if execution_id in self._indexes and self._indexes[execution_id]:
            return [e for e in self._indexes[execution_id] if e.branch_id == branch_id]

        log_path = self._get_log_filepath(execution_id)
        if not os.path.exists(log_path):
            return []

        events = []
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                data = json.loads(line.strip())
                evt = ExecutionEvent(
                    id=data["id"],
                    agent_id=data["agent_id"],
                    execution_id=data["execution_id"],
                    branch_id=data.get("branch_id", "branch_main"),
                    parent_event_id=data.get("parent_event_id"),
                    timestamp=data["timestamp"],
                    event_type=EventType(data["event_type"]),
                    source=EventSource(data["source"]),
                    step_number=data["step_number"],
                    payload=data.get("payload", {}),
                    result=data.get("result"),
                    input_hash=data.get("input_hash", ""),
                    output_hash=data.get("output_hash", ""),
                    causal_hash=data.get("causal_hash", ""),
                    side_effect_type=SideEffectType(data.get("side_effect_type", "READ_ONLY")),
                    reversibility=ReversibilityType(data.get("reversibility", "REVERSIBLE")),
                    idempotency_key=data.get("idempotency_key"),
                    recovery_relevant=data.get("recovery_relevant", False)
                )
                if evt.branch_id == branch_id:
                    events.append(evt)

        self._indexes[execution_id] = events
        return events
