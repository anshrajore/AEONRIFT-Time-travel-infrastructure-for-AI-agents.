/**
 * AEONRIFT TypeScript Runtime Client & Tool Interceptor
 */

import { ExecutionEvent, EventType, SideEffectType, ReversibilityType } from "./events";

export class AeonriftClient {
  private agentId: string;
  private executionId: string;
  private stepCounter: number = 0;
  private committedKeys: Set<string> = new Set();

  constructor(agentId: string, executionId: string) {
    this.agentId = agentId;
    this.executionId = executionId;
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

    // Rollback Protection Guard check
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
