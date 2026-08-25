"""
AEONRIFT Time-Travel Debugger Dashboard API & Web Server

Provides visual execution DAG data, checkpoint state diff rendering,
and recovery explanation endpoints.
"""

from dataclasses import dataclass
import json
import os
import sys
from typing import Dict, List, Any

# Ensure imports
sys.path.insert(0, os.path.abspath("packages/core"))
sys.path.insert(0, os.path.abspath("services/recovery"))
sys.path.insert(0, os.path.abspath("storage/event-log"))

from event_store import DurableEventStore


class AeonriftDashboardServer:
    """
    Renders visual time-travel execution tree data for AI agent trajectories.
    """
    def __init__(self, storage_dir: str = ".aeonrift/event_store"):
        self.event_store = DurableEventStore(storage_dir=storage_dir)

    def get_execution_dag_data(self, execution_id: str) -> Dict[str, Any]:
        """Generate JSON structure for React Flow / Mermaid visual rendering."""
        events = self.event_store.read_trajectory(execution_id)
        nodes = []
        edges = []

        for evt in events:
            nodes.append({
                "id": evt.id,
                "type": evt.event_type.value,
                "step": evt.step_number,
                "is_checkpoint": evt.recovery_relevant,
                "side_effect": evt.side_effect_type.value,
                "label": f"Step {evt.step_number}: {evt.event_type.value}"
            })
            if evt.parent_event_id:
                edges.append({
                    "id": f"{evt.parent_event_id}->{evt.id}",
                    "source": evt.parent_event_id,
                    "target": evt.id
                })

        return {
            "execution_id": execution_id,
            "total_nodes": len(nodes),
            "nodes": nodes,
            "edges": edges
        }

    def compute_state_diff(self, checkpoint_a: Dict, checkpoint_b: Dict) -> Dict[str, Any]:
        """Compute state diff between Checkpoint A and Checkpoint B."""
        mem_a = checkpoint_a.get("memory_variables", {})
        mem_b = checkpoint_b.get("memory_variables", {})

        added = {k: v for k, v in mem_b.items() if k not in mem_a}
        modified = {k: {"old": mem_a[k], "new": mem_b[k]} for k in mem_a if k in mem_b and mem_a[k] != mem_b[k]}
        deleted = [k for k in mem_a if k not in mem_b]

        return {
            "memory_diff": {
                "added": added,
                "modified": modified,
                "deleted": deleted
            }
        }
