/**
 * AEONRIFT TypeScript Runtime Client & Tool Interceptor
 */

import { ExecutionEvent, EventType, EventSource, SideEffectType, ReversibilityType, SideEffectRecord, LayeredCheckpoint } from "./events";

declare var require: any;
const crypto = require("crypto");

export class AeonriftClient {
  public agentId: string;
  public executionId: string;
  private stepCounter: number = 0;
  private committedKeys: Set<string> = new Set();

  constructor(executionId: string, agentId: string = "default-agent") {
    this.executionId = executionId;
    this.agentId = agentId;
  }

  public createEvent(
    eventType: EventType,
    source: EventSource,
    payload: Record<string, any>
  ): ExecutionEvent {
    this.stepCounter++;
    const timestamp = Date.now() / 1000;
    const eventId = `evt-${this.executionId}-${this.stepCounter}`;
    const hash = crypto.createHash("sha256").update(`${eventId}:${this.executionId}:${timestamp}:${JSON.stringify(payload)}`).digest("hex");

    return {
      event_id: eventId,
      execution_id: this.executionId,
      timestamp,
      event_type: eventType,
      source,
      payload,
      hash
    };
  }

  public registerSideEffect(
    actionName: string,
    target: Record<string, any>,
    type: SideEffectType = SideEffectType.API_WRITE,
    reversibility: ReversibilityType = ReversibilityType.IRREVERSIBLE
  ): SideEffectRecord {
    const key = `aeonrift:${this.executionId}:${actionName}:${JSON.stringify(target)}`;
    this.committedKeys.add(key);
    return {
      record_id: `rec-${Date.now()}`,
      action_name: actionName,
      idempotency_key: key,
      status: "COMMITTED",
      reversibility
    };
  }

  public checkIdempotency(key: string): boolean {
    return this.committedKeys.has(key);
  }

  public createCheckpoint(level: string, state: Record<string, any>): LayeredCheckpoint {
    const stateHash = crypto.createHash("sha256").update(JSON.stringify(state)).digest("hex");
    return {
      checkpoint_id: `ckpt-${this.executionId}-${level}-${Date.now()}`,
      execution_id: this.executionId,
      level,
      timestamp: Date.now() / 1000,
      state_hash: stateHash,
      metadata: state
    };
  }

  public async interceptTool<T>(
    toolName: string,
    toolFn: (...args: any[]) => Promise<T> | T,
    args: Record<string, any>,
    options?: {
      sideEffectType?: SideEffectType;
      reversibility?: ReversibilityType;
      idempotencyKey?: string;
    }
  ): Promise<T> {
    this.stepCounter++;
    const key = options?.idempotencyKey || `aeonrift:${this.agentId}:${this.executionId}:${toolName}`;

    if (options?.sideEffectType === SideEffectType.MUTATING_IRREVERSIBLE && this.committedKeys.has(key)) {
      throw new Error(`[AEONRIFT ROLLBACK GUARD BLOCK] Action '${key}' already committed in ledger. Duplicate replay blocked.`);
    }

    const result = await toolFn(args);

    if (options?.sideEffectType === SideEffectType.MUTATING_IRREVERSIBLE) {
      this.committedKeys.add(key);
    }

    return result;
  }
}
