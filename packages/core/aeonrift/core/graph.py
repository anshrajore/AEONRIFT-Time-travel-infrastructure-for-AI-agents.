"""
AEONRIFT Causal State Graph

Implements a Directed Acyclic Graph (DAG) of execution events, state deltas,
tool side effects, and causal linkages to enable state-aware time travel and recovery.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from aeonrift.core.events import ExecutionEvent, EventType, ReversibilityType, SideEffectType


@dataclass
class CausalNode:
    """A node in the Causal State Graph representing an event and its causal state."""
    event: ExecutionEvent
    parent_ids: List[str] = field(default_factory=list)
    child_ids: List[str] = field(default_factory=list)
    is_checkpoint: bool = False
    checkpoint_level: Optional[int] = None
    state_valid: bool = True


@dataclass
class CausalStateGraph:
    """
    DAG tracking causal dependencies across agent actions, OS state changes,
    tool executions, and external side effects.
    """
    execution_id: str
    nodes: Dict[str, CausalNode] = field(default_factory=dict)
    branches: Dict[str, List[str]] = field(default_factory=dict)  # branch_id -> list of event_ids
    active_branch: str = "branch_main"

    def add_event(self, event: ExecutionEvent, is_checkpoint: bool = False, checkpoint_level: Optional[int] = None) -> CausalNode:
        """Add an execution event to the causal state graph and wire causal edges."""
        event.compute_hashes()

        parents = []
        if event.parent_event_id and event.parent_event_id in self.nodes:
            parents.append(event.parent_event_id)

        node = CausalNode(
            event=event,
            parent_ids=parents,
            child_ids=[],
            is_checkpoint=is_checkpoint,
            checkpoint_level=checkpoint_level
        )

        self.nodes[event.id] = node

        # Wire parent child edges
        for pid in parents:
            if pid in self.nodes:
                self.nodes[pid].child_ids.append(event.id)

        # Track in active branch
        branch_list = self.branches.setdefault(event.branch_id, [])
        branch_list.append(event.id)

        return node

    def get_trajectory(self, branch_id: Optional[str] = None) -> List[ExecutionEvent]:
        """Return chronological list of events for a given execution branch."""
        target_branch = branch_id or self.active_branch
        event_ids = self.branches.get(target_branch, [])
        return [self.nodes[eid].event for eid in event_ids if eid in self.nodes]

    def find_last_safe_checkpoint(self, failure_event_id: str) -> Optional[Tuple[CausalNode, int]]:
        """
        Traverse backward from failure event to identify the latest safe checkpoint.
        Returns (checkpoint_node, step_number).
        """
        if failure_event_id not in self.nodes:
            return None

        current_id: Optional[str] = failure_event_id
        visited: Set[str] = set()

        while current_id and current_id not in visited:
            visited.add(current_id)
            node = self.nodes[current_id]

            if node.is_checkpoint and node.state_valid:
                return node, node.event.step_number

            # Move to parent
            if node.parent_ids:
                current_id = node.parent_ids[0]
            else:
                # Fall back to step ordering in branch if parent link missing
                branch_events = self.get_trajectory(node.event.branch_id)
                current_idx = next((i for i, e in enumerate(branch_events) if e.id == current_id), 0)
                if current_idx > 0:
                    current_id = branch_events[current_idx - 1].id
                else:
                    break

        return None

    def get_committed_side_effects_after(self, step_number: int, branch_id: Optional[str] = None) -> List[ExecutionEvent]:
        """
        Find all external side effects executed after a specified step number.
        Crucial for detecting Semantic Rollback Hazards (ACRFence).
        """
        trajectory = self.get_trajectory(branch_id)
        side_effects = []
        for evt in trajectory:
            if evt.step_number > step_number:
                if evt.side_effect_type in (SideEffectType.MUTATING_IRREVERSIBLE, SideEffectType.EXTERNAL_STATE_MUTATION) \
                   or evt.event_type == EventType.EXTERNAL_SIDE_EFFECT:
                    side_effects.append(evt)
        return side_effects

    def create_branch(self, from_event_id: str, new_branch_id: str) -> str:
        """Fork execution trajectory at a specific event node to create an execution tree branch."""
        if from_event_id not in self.nodes:
            raise ValueError(f"Event ID {from_event_id} not found in graph.")

        parent_node = self.nodes[from_event_id]
        orig_branch = parent_node.event.branch_id
        orig_trajectory = self.branches.get(orig_branch, [])

        # Copy prefix event IDs up to from_event_id
        prefix = []
        for eid in orig_trajectory:
            prefix.append(eid)
            if eid == from_event_id:
                break

        self.branches[new_branch_id] = prefix
        return new_branch_id
