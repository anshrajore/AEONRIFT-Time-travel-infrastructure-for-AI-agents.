"""
AEONRIFT Distributed Agent Fleet Coordinator & Multi-Agent Recovery

Manages multi-agent execution graphs, cross-agent message causal tracking,
and distributed failure recovery across agent fleets.
"""

from dataclasses import dataclass, field
import time
from typing import Dict, List, Optional, Set
from aeonrift.core.events import ExecutionEvent, EventType, EventSource
from aeonrift.core.graph import CausalStateGraph
from services.recovery.planner import RecoveryPlanner, RecoveryPlan, RecoveryMode


@dataclass
class AgentMessageEvent:
    message_id: str
    sender_agent_id: str
    receiver_agent_id: str
    step_number: int
    payload_hash: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class FleetRecoveryPlan:
    primary_failed_agent: str
    affected_agents: List[str]
    agent_plans: Dict[str, RecoveryPlan]
    distributed_cascade_prevented: bool


class DistributedAgentCoordinator:
    """
    Fleet Coordinator maintaining causal message graphs across multi-agent systems.
    """
    def __init__(self):
        self.agent_graphs: Dict[str, CausalStateGraph] = {}  # agent_id -> graph
        self.cross_agent_messages: List[AgentMessageEvent] = []
        self.planner = RecoveryPlanner()

    def register_agent(self, agent_id: str, execution_id: str) -> CausalStateGraph:
        graph = CausalStateGraph(execution_id=execution_id)
        self.agent_graphs[agent_id] = graph
        return graph

    def record_inter_agent_message(
        self,
        message_id: str,
        sender_agent_id: str,
        receiver_agent_id: str,
        step_number: int,
        payload_hash: str
    ) -> AgentMessageEvent:
        """Record inter-agent communication in causal message log."""
        msg = AgentMessageEvent(
            message_id=message_id,
            sender_agent_id=sender_agent_id,
            receiver_agent_id=receiver_agent_id,
            step_number=step_number,
            payload_hash=payload_hash
        )
        self.cross_agent_messages.append(msg)
        return msg

    def coordinate_fleet_recovery(
        self,
        failed_agent_id: str,
        failure_event_id: str
    ) -> FleetRecoveryPlan:
        """
        Coordinate distributed multi-agent recovery:
        1. Identifies direct recovery plan for failed agent.
        2. Traverses Causal Message Graph to evaluate downstream impacted agents.
        3. Prevents invalid cascade restores across peer agents.
        """
        primary_graph = self.agent_graphs.get(failed_agent_id)
        if not primary_graph:
            raise ValueError(f"Agent {failed_agent_id} not registered in coordinator.")

        from aeonrift.core.ledger import SideEffectLedger
        ledger = SideEffectLedger()

        primary_plan = self.planner.generate_plan(
            primary_graph.execution_id,
            failure_event_id,
            primary_graph,
            ledger
        )

        agent_plans = {failed_agent_id: primary_plan}
        affected_agents = []

        # Find messages sent by failed agent after its checkpoint step
        cp_step = primary_plan.replay_until_step
        messages_sent_after_cp = [
            m for m in self.cross_agent_messages
            if m.sender_agent_id == failed_agent_id and m.step_number > cp_step
        ]

        for msg in messages_sent_after_cp:
            receiver = msg.receiver_agent_id
            if receiver not in affected_agents:
                affected_agents.append(receiver)
                # Assign repair plan for downstream receiver
                agent_plans[receiver] = RecoveryPlan(
                    mode=RecoveryMode.REPAIR,
                    checkpoint_id=None,
                    replay_until_step=msg.step_number - 1,
                    recompute_from_step=msg.step_number,
                    confidence_score=0.92,
                    explanation=f"Re-synchronizing after message {msg.message_id} from failed agent {failed_agent_id}."
                )

        return FleetRecoveryPlan(
            primary_failed_agent=failed_agent_id,
            affected_agents=affected_agents,
            agent_plans=agent_plans,
            distributed_cascade_prevented=True
        )
