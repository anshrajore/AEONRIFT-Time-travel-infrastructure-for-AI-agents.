"""
AEONRIFT Enterprise Gateway Server
Provides HTTP REST endpoints and real-time event streaming for AEONRIFT executions.
"""

from typing import Dict, Any, List, Optional
import json
import time

from aeonrift.core.events import ExecutionEvent, EventType, EventSource
from aeonrift.runtime.interceptor import AeonriftRuntime
from event_store import DurableEventStore
from planner import RecoveryPlanner, FailureClassifier, FailureCategory


class AeonriftGatewayServer:
    """
    Lightweight REST & WebSockets gateway handler for AEONRIFT orchestration.
    """

    def __init__(self, base_storage_dir: str = "./storage_data"):
        self.base_storage_dir = base_storage_dir
        self.runtimes: Dict[str, AeonriftRuntime] = {}

    def get_or_create_runtime(self, execution_id: str) -> AeonriftRuntime:
        if execution_id not in self.runtimes:
            self.runtimes[execution_id] = AeonriftRuntime(
                agent_id="gateway_agent",
                execution_id=execution_id,
                storage_dir=self.base_storage_dir
            )
        return self.runtimes[execution_id]

    def handle_ingest_event(self, execution_id: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST /api/v1/events
        Ingests an external event into the causal DAG and durable store.
        """
        runtime = self.get_or_create_runtime(execution_id)
        event_type_str = event_data.get("event_type", EventType.TOOL_CALL.value)
        event_id = event_data.get("id", f"evt-{execution_id}-{int(time.time()*1000)}")
        
        event = ExecutionEvent(
            id=event_id,
            agent_id="gateway_agent",
            execution_id=execution_id,
            event_type=EventType(event_type_str),
            source=EventSource(event_data.get("source", EventSource.RUNTIME.value)),
            step_number=len(runtime.causal_graph.nodes) + 1,
            timestamp=event_data.get("timestamp", time.time()),
            payload=event_data.get("payload", {})
        )
        runtime.causal_graph.add_event(event)
        runtime.event_store.append_event(event)
        return {
            "status": "accepted",
            "event_id": event.id,
            "hash": event.causal_hash,
            "execution_id": execution_id
        }

    def handle_get_timeline(self, execution_id: str) -> Dict[str, Any]:
        """
        GET /api/v1/timeline/{execution_id}
        Returns trajectory events and graph topological ordering.
        """
        event_store = DurableEventStore(storage_dir=self.base_storage_dir)
        events = event_store.read_trajectory(execution_id)
        return {
            "execution_id": execution_id,
            "count": len(events),
            "events": [
                {
                    "event_id": e.id,
                    "event_type": e.event_type.value,
                    "timestamp": e.timestamp,
                    "hash": e.causal_hash,
                    "payload": e.payload
                }
                for e in events
            ]
        }

    def handle_trigger_recovery(self, execution_id: str, failure_description: str) -> Dict[str, Any]:
        """
        POST /api/v1/recover/{execution_id}
        Triggers failure classification and recovery planning.
        """
        runtime = self.get_or_create_runtime(execution_id)
        category = FailureClassifier.classify_error_message(failure_description)
        planner = RecoveryPlanner()
        last_event_id = runtime.last_event_id or f"evt_{execution_id}_0001"
        plan = planner.generate_plan(
            execution_id=execution_id,
            failure_event_id=last_event_id,
            graph=runtime.causal_graph,
            ledger=runtime.ledger
        )

        return {
            "execution_id": execution_id,
            "failure_category": category.value,
            "recommended_strategy": plan.mode.value,
            "target_checkpoint_id": plan.checkpoint_id,
            "confidence_score": plan.confidence_score,
            "idempotent_skip_events": plan.blocked_actions
        }
