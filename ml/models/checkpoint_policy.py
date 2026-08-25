"""
AEONRIFT RIFT-Checkpoint Predictive Policy

Learns semantic checkpoint importance to eliminate up to 75% of unneeded agent turn snapshots (Crab 2026).
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class CheckpointPrediction:
    should_checkpoint: bool
    importance_score: float  # 0.0 to 1.0
    recommended_level: int    # L0 to L5


class RiftCheckpointPredictor:
    """
    Predictive model evaluating recovery-relevance of execution steps.
    """
    def predict_importance(
        self,
        event_type: str,
        side_effect_type: str,
        files_modified_count: int,
        processes_spawned_count: int
    ) -> CheckpointPrediction:

        if side_effect_type in ("MUTATING_IRREVERSIBLE", "EXTERNAL_STATE_MUTATION"):
            return CheckpointPrediction(
                should_checkpoint=True,
                importance_score=0.98,
                recommended_level=5  # L5 External State
            )

        if files_modified_count > 0:
            return CheckpointPrediction(
                should_checkpoint=True,
                importance_score=0.85,
                recommended_level=2  # L2 Filesystem
            )

        if processes_spawned_count > 0:
            return CheckpointPrediction(
                should_checkpoint=True,
                importance_score=0.70,
                recommended_level=3  # L3 Process
            )

        # Conversational LLM turns without mutations -> Skip (Crab 2026)
        if event_type in ("LLM_CALL", "LLM_RESULT"):
            return CheckpointPrediction(
                should_checkpoint=False,
                importance_score=0.05,
                recommended_level=0  # L0 Logical
            )

        return CheckpointPrediction(
            should_checkpoint=True,
            importance_score=0.50,
            recommended_level=1  # L1 App State
        )
