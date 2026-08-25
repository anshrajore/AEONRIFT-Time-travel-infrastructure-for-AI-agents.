"""
AEONRIFT CrewAI Integration Adapter
Provides tool wrappers and multi-agent coordination hooks for CrewAI agents.
"""

from typing import Dict, Any, Callable, Optional
from aeonrift.core.events import ReversibilityType, SideEffectType
from aeonrift.runtime.interceptor import AeonriftRuntime
from fleet_coordinator import DistributedAgentCoordinator


class AeonriftCrewAIToolWrapper:
    """
    Decorator / wrapper class for CrewAI tools to enforce idempotent execution,
    automatic layered checkpointing, and side-effect safety.
    """

    def __init__(
        self,
        execution_id: str,
        agent_id: str = "crew_agent",
        coordinator: Optional[DistributedAgentCoordinator] = None
    ):
        self.execution_id = execution_id
        self.agent_id = agent_id
        self.runtime = AeonriftRuntime(agent_id=agent_id, execution_id=execution_id)
        self.coordinator = coordinator or DistributedAgentCoordinator()
        self.coordinator.register_agent(agent_id=agent_id, execution_id=execution_id)

    def wrap_tool(
        self,
        tool_name: str,
        func: Callable,
        is_side_effect: bool = False,
        reversibility: ReversibilityType = ReversibilityType.REVERSIBLE
    ) -> Callable:
        """
        Wraps a CrewAI tool function with AEONRIFT interception.
        """
        side_effect_type = SideEffectType.EXTERNAL_STATE_MUTATION if is_side_effect else SideEffectType.READ_ONLY

        def wrapped(*args, **kwargs):
            tool_input = kwargs if kwargs else {"val": args[0]} if args else {}
            return self.runtime.intercept_tool(
                tool_name=tool_name,
                tool_func=lambda **k: func(*args, **kwargs),
                tool_kwargs=tool_input,
                side_effect_type=side_effect_type,
                reversibility=reversibility
            )

        return wrapped
