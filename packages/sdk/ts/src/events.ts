/**
 * AEONRIFT TypeScript Core Event & Side-Effect Types
 */

export enum EventType {
  LLM_CALL = "LLM_CALL",
  LLM_RESULT = "LLM_RESULT",
  TOOL_CALL = "TOOL_CALL",
  TOOL_CALL_INITIATED = "TOOL_CALL_INITIATED",
  TOOL_RESULT = "TOOL_RESULT",
  FILE_WRITE = "FILE_WRITE",
  FILE_DELETE = "FILE_DELETE",
  PROCESS_START = "PROCESS_START",
  EXTERNAL_SIDE_EFFECT = "EXTERNAL_SIDE_EFFECT",
  CHECKPOINT = "CHECKPOINT",
  FAILURE = "FAILURE",
  RECOVERY = "RECOVERY",
  REPLAY = "REPLAY",
  ROLLBACK = "ROLLBACK"
}

export enum EventSource {
  RUNTIME_INTERCEPTOR = "RUNTIME_INTERCEPTOR",
  AGENT = "AGENT",
  SYSTEM = "SYSTEM"
}

export enum SideEffectType {
  READ_ONLY = "READ_ONLY",
  MUTATING_REVERSIBLE = "MUTATING_REVERSIBLE",
  MUTATING_IRREVERSIBLE = "MUTATING_IRREVERSIBLE",
  EXTERNAL_STATE_MUTATION = "EXTERNAL_STATE_MUTATION",
  API_WRITE = "API_WRITE",
  NONE = "NONE"
}

export enum ReversibilityType {
  REVERSIBLE = "REVERSIBLE",
  COMPENSABLE = "COMPENSABLE",
  IRREVERSIBLE = "IRREVERSIBLE"
}

export interface ExecutionEvent {
  event_id: string;
  execution_id: string;
  timestamp: number;
  event_type: EventType;
  source: EventSource;
  payload: Record<string, any>;
  hash?: string;
}

export interface SideEffectRecord {
  record_id: string;
  action_name: string;
  idempotency_key: string;
  status: string;
  reversibility: ReversibilityType;
}

export interface LayeredCheckpoint {
  checkpoint_id: string;
  execution_id: string;
  level: string;
  timestamp: number;
  state_hash: string;
  metadata: Record<string, any>;
}
