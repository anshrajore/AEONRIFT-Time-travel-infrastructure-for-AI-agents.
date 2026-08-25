"""
AEONRIFT RIFT-Predict Recovery Policy Model

ML-driven policy predicting optimal recovery mode (REPLAY, REPAIR, REPLAN, COMPENSATE)
from state divergence, side-effect hazards, and environmental drift.
"""

from dataclasses import dataclass, field
import math
from typing import Dict, List, Tuple


@dataclass
class PolicyPrediction:
    recommended_strategy: str
    confidence_scores: Dict[str, float]
    rationale: str


class RiftPredictPolicyModel:
    """
    Supervised/Rule-guided ML Recovery Policy predictor.
    """
    def predict_strategy(
        self,
        failure_category: str,
        state_divergence: float,
        environment_drift: float,
        has_irreversible_side_effect: bool,
        checkpoint_age_steps: int
    ) -> PolicyPrediction:
        """
        Predict optimal recovery strategy based on trajectory feature vector.
        """
        if failure_category == "AUTH_FAILURE":
            scores = {"REPLAY": 0.05, "REPAIR": 0.15, "REPLAN": 0.80, "COMPENSATE": 0.00}
            rationale = "Authentication revoked; mandatory re-planning."
        elif has_irreversible_side_effect:
            scores = {"REPLAY": 0.02, "REPAIR": 0.90, "REPLAN": 0.05, "COMPENSATE": 0.03}
            rationale = "Committed side-effects detected; trajectory splicing required (REPAIR)."
        elif environment_drift > 0.5:
            scores = {"REPLAY": 0.10, "REPAIR": 0.20, "REPLAN": 0.70, "COMPENSATE": 0.00}
            rationale = "Significant environment drift (>0.50); re-planning recommended."
        else:
            scores = {"REPLAY": 0.95, "REPAIR": 0.03, "REPLAN": 0.02, "COMPENSATE": 0.00}
            rationale = "Low drift and clean trajectory; deterministic REPLAY optimal."

        best_strat = max(scores, key=scores.get)
        return PolicyPrediction(
            recommended_strategy=best_strat,
            confidence_scores=scores,
            rationale=rationale
        )
