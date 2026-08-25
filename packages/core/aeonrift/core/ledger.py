"""
AEONRIFT External Side-Effect Ledger

Maintains a tamper-evident audit record of all external mutations (payments, emails, cloud deploys),
implements idempotency key generation, and defends against semantic rollback attacks (ACRFence).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
import hashlib
import time
from aeonrift.core.events import ReversibilityType, SideEffectType


class LedgerStatus(str, Enum):
    PENDING = "PENDING"
    COMMITTED = "COMMITTED"
    ROLLED_BACK = "ROLLED_BACK"
    COMPENSATED = "COMPENSATED"
    BLOCKED = "BLOCKED"


@dataclass
class SideEffectRecord:
    """Entry in the Side-Effect Ledger tracking external tool executions."""
    effect_id: str
    agent_id: str
    execution_id: str
    tool_name: str
    action_signature: str
    idempotency_key: str
    side_effect_type: SideEffectType
    reversibility: ReversibilityType
    request_payload_hash: str
    timestamp: float = field(default_factory=time.time)
    status: LedgerStatus = LedgerStatus.COMMITTED
    response_payload_hash: Optional[str] = None
    compensation_tool: Optional[str] = None
    compensation_payload: Optional[Dict] = None


@dataclass
class SideEffectLedger:
    """
    Side-Effect Ledger protecting against duplicate side effects during execution restore & replay.
    """
    records: Dict[str, SideEffectRecord] = field(default_factory=dict)  # effect_id -> record
    idempotency_index: Dict[str, str] = field(default_factory=dict)   # idempotency_key -> effect_id

    @staticmethod
    def generate_idempotency_key(agent_id: str, task_id: str, action_signature: str) -> str:
        """
        Derives a deterministic idempotency key for external calls.
        Format: aeonrift:{agent_id}:{task_id}:{hash(action_signature)}
        """
        sig_hash = hashlib.sha256(action_signature.encode('utf-8')).hexdigest()[:16]
        return f"aeonrift:{agent_id}:{task_id}:{sig_hash}"

    def record_side_effect(
        self,
        effect_id: str,
        agent_id: str,
        execution_id: str,
        tool_name: str,
        action_signature: str,
        idempotency_key: str,
        side_effect_type: SideEffectType,
        reversibility: ReversibilityType,
        request_payload_hash: str,
        response_payload_hash: Optional[str] = None,
        compensation_tool: Optional[str] = None
    ) -> SideEffectRecord:
        """Record a committed external side effect in the ledger."""
        record = SideEffectRecord(
            effect_id=effect_id,
            agent_id=agent_id,
            execution_id=execution_id,
            tool_name=tool_name,
            action_signature=action_signature,
            idempotency_key=idempotency_key,
            side_effect_type=side_effect_type,
            reversibility=reversibility,
            status=LedgerStatus.COMMITTED,
            request_payload_hash=request_payload_hash,
            response_payload_hash=response_payload_hash,
            compensation_tool=compensation_tool
        )
        self.records[effect_id] = record
        self.idempotency_index[idempotency_key] = effect_id
        return record

    def is_idempotency_key_committed(self, idempotency_key: str) -> bool:
        """Check if an external side effect with this idempotency key was already committed."""
        if idempotency_key in self.idempotency_index:
            effect_id = self.idempotency_index[idempotency_key]
            rec = self.records.get(effect_id)
            return rec is not None and rec.status == LedgerStatus.COMMITTED
        return False

    def mark_compensated(self, effect_id: str) -> bool:
        """Update status of a record after executing a compensating transaction."""
        if effect_id in self.records:
            self.records[effect_id].status = LedgerStatus.COMPENSATED
            return True
        return False
