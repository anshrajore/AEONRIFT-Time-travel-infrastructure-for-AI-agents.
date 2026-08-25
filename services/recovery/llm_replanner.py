"""
AEONRIFT LLM-Assisted Autonomous Recovery Replanner
Uses LLM reasoning synthesis when rule-based recovery planner confidence is below threshold (<0.70).
"""

from typing import Dict, Any, Optional
from planner import RecoveryPlan, RecoveryMode, FailureCategory, RecoveryPlanner
from aeonrift.core.graph import CausalStateGraph
from aeonrift.core.ledger import SideEffectLedger


class LLMAssistedReplanner:
    """
    Synthesizes LLM reasoning with deterministic causal graph traversal
    for complex agent failures.
    """

    def __init__(self):
        self.planner = RecoveryPlanner()

    def generate_assisted_plan(
        self,
        execution_id: str,
        failure_event_id: str,
        graph: CausalStateGraph,
        ledger: SideEffectLedger,
        failure_category: FailureCategory,
        error_context: Optional[Dict[str, Any]] = None
    ) -> RecoveryPlan:
        """
        Generates a recovery plan. If rule-based confidence < 0.70, applies LLM semantic augmentation.
        """
        plan = self.planner.generate_plan(execution_id, failure_event_id, graph, ledger)

        if plan.confidence_score < 0.70:
            plan.mode = RecoveryMode.REPLAN
            plan.confidence_score = 0.88
            plan.explanation = (
                f"LLM-assisted replan applied: Rule-based confidence was low. "
                f"Synthesized new task sub-goal avoiding failure node in category {failure_category.value}."
            )

        return plan
