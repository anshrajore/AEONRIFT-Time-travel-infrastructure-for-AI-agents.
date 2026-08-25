/**
 * AEONRIFT TypeScript Core Event & Side-Effect Types
 */

export enum EventType {
  LLM_CALL = "LLM_CALL",
  LLM_RESULT = "LLM_RESULT",
  TOOL_CALL = "TOOL_CALL",
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

export enum SideEffectType {
  READ_ONLY = "READ_ONLY",
  MUTATING_REVERSIBLE = "MUTATING_REVERSIBLE",
  MUTATING_IRREVERSIBLE = "MUTATING_IRREVERSIBLE",
  EXTERNAL_STATE_MUTATION = "EXTERNAL_STATE_MUTATION"
}

export enum ReversibilityType {
  REVERSIBLE = "REVERSIBLE",
  COMPENSABLE = "COMPENSABLE",
  IRREVERSIBLE = "IRREVERSIBLE"
}

export interface ExecutionEvent {
  id: string;
  agentId: string;
  executionId: string;
  eventType: EventType;
  stepNumber: number;
  payload: Record<string, any>;
  result?: Record<string, any>;
  timestamp: number;
  inputHash?: string;
  outputHash?: string;
  causalHash?: string;
  sideEffectType: SideEffectType;
  reversibility: ReversibilityType;
  idempotencyKey?: string;
  recoveryRelevant: boolean;
}
