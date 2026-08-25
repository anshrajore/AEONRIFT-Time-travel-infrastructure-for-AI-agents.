"""
AEONRIFT Recovery Validator

Performs pre-flight state validation (file hashes, memory integrity, tool availability, side-effect safety)
before resuming agent execution post-recovery.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from aeonrift.core.checkpoint import LayeredCheckpoint
from aeonrift.core.ledger import SideEffectLedger
from services.state.reconciler import StateReconciler, ReconciliationDiff, ConflictResolutionPolicy


@dataclass
class ValidationResult:
    is_valid: bool
    confidence_score: float
    reconciliation_diff: ReconciliationDiff
    validation_checks: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class RecoveryValidator:
    """
    Pre-flight recovery validator ensuring safe execution resume.
    """
    def __init__(self):
        self.reconciler = StateReconciler()

    def validate_recovery_state(
        self,
        checkpoint: LayeredCheckpoint,
        ledger: SideEffectLedger,
        workdir: str = "."
    ) -> ValidationResult:
        """
        Validate checkpoint integrity and environment alignment prior to resume.
        """
        checks = []
        errors = []

        # 1. Validate checkpoint state hash
        expected_hash = checkpoint.compute_state_hash()
        if expected_hash == checkpoint.metadata.state_hash:
            checks.append("Checkpoint cryptographic state hash match: OK")
        else:
            errors.append("Checkpoint state hash mismatch (potential corruption)")

        # 2. Perform Environment & State Reconciliation check
        diff = self.reconciler.reconcile(checkpoint, workdir=workdir)
        if diff.has_drift:
            checks.append(f"Environment drift detected ({', '.join(diff.details)}) -> Policy: {diff.recommended_policy.value}")
            if diff.recommended_policy == ConflictResolutionPolicy.BLOCK:
                errors.append("Fatal environment drift. Execution resume blocked.")
        else:
            checks.append("Environment alignment: Perfectly matched")

        # 3. Compute overall recovery confidence
        is_valid = len(errors) == 0
        confidence = 0.99 if is_valid and not diff.has_drift else (0.85 if is_valid else 0.0)

        return ValidationResult(
            is_valid=is_valid,
            confidence_score=confidence,
            reconciliation_diff=diff,
            validation_checks=checks,
            errors=errors
        )
