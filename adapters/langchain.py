"""
AEONRIFT LangChain Integration Adapter
Provides automatic tool interception, causal state graph tracking,
and side-effect idempotency protection for LangChain agents.
"""

from typing import Dict, Any, Optional
import time

from aeonrift.core.events import SideEffectType, ReversibilityType
from aeonrift.runtime.interceptor import AeonriftRuntime


class AeonriftLangChainAdapter:
    """
    Adapter that integrates AEONRIFT time-travel runtime into LangChain execution flows.
    """

    def __init__(
        self,
        execution_id: str,
        agent_name: str = "langchain_agent",
        runtime: Optional[AeonriftRuntime] = None
    ):
        self.execution_id = execution_id
        self.agent_name = agent_name
        self.runtime = runtime or AeonriftRuntime(agent_id=agent_name, execution_id=execution_id)
        self.last_event_id: Optional[str] = None

    def intercept_tool_call(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        is_side_effect: bool = False,
        reversibility: ReversibilityType = ReversibilityType.REVERSIBLE,
        tool_func: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Intercepts a LangChain tool execution through the AEONRIFT runtime guard pipeline.
        """
        side_effect_type = SideEffectType.MUTATING_IRREVERSIBLE if is_side_effect else SideEffectType.READ_ONLY

        if tool_func is None:
            def dummy_func(**kwargs):
                return {"status": "success", "result": f"Executed {tool_name}", "input": kwargs}
            target_func = dummy_func
        else:
            target_func = tool_func

        result = self.runtime.intercept_tool(
            tool_name=tool_name,
            tool_func=target_func,
            tool_kwargs=tool_input,
            side_effect_type=side_effect_type,
            reversibility=reversibility
        )

        return result
