"""
AEONRIFT RIFT-FAIL Dataset Generator

Generates structured failure, state diff, side effect, and recovery outcome datasets
for training machine learning recovery policies (RIFT-Predict & RIFT-Checkpoint).
"""

from dataclasses import dataclass, field
import json
import random
from typing import Dict, List, Any


@dataclass
class FailureDatasetSample:
    sample_id: str
    failure_category: str
    state_divergence_score: float
    environment_drift_score: float
    tool_determinism: float
    side_effect_count: int
    has_irreversible_side_effect: bool
    checkpoint_age_steps: int
    optimal_strategy: str  # REPLAY, REPAIR, REPLAN, COMPENSATE
    recovery_cost: float


class RiftFailDatasetGenerator:
    """
    Synthesizes RIFT-FAIL benchmark training dataset across failure injection dimensions.
    """
    STRATEGIES = ["REPLAY", "REPAIR", "REPLAN", "COMPENSATE"]
    CATEGORIES = ["TOOL_FAILURE", "NETWORK_FAILURE", "AUTH_FAILURE", "STATE_CORRUPTION", "LLM_FAILURE"]

    def generate_samples(self, count: int = 100) -> List[FailureDatasetSample]:
        samples = []
        for i in range(count):
            cat = random.choice(self.CATEGORIES)
            has_fx = random.choice([True, False])
            drift = round(random.uniform(0.0, 1.0), 3)

            if cat == "AUTH_FAILURE":
                strat = "REPLAN"
            elif has_fx:
                strat = "REPAIR"
            elif drift > 0.6:
                strat = "REPLAN"
            else:
                strat = "REPLAY"

            samples.append(FailureDatasetSample(
                sample_id=f"sample_{i+1:04d}",
                failure_category=cat,
                state_divergence_score=drift,
                environment_drift_score=drift,
                tool_determinism=round(random.uniform(0.7, 1.0), 2),
                side_effect_count=random.randint(0, 5),
                has_irreversible_side_effect=has_fx,
                checkpoint_age_steps=random.randint(1, 10),
                optimal_strategy=strat,
                recovery_cost=round(random.uniform(0.01, 0.50), 3)
            ))
        return samples

    def export_jsonl(self, samples: List[FailureDatasetSample], filepath: str):
        with open(filepath, "w", encoding="utf-8") as f:
            for s in samples:
                f.write(json.dumps(s.__dict__) + "\n")
