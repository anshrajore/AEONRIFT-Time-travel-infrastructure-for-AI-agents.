# AEONRIFT Technical Implementation Guide

This document details the architectural specification and implementation mechanics of **AEONRIFT**.

---

## 1. Core Principles

AEONRIFT operates on four foundational pillars:

1. **Causal State Tracking**: Agent execution is not a linear string of steps, but a directed acyclic graph (DAG) of causal events: `Event -> State Change -> Tool Effect -> External Side Effect`.
2. **Semantic Rollback Protection**: Restoring process or memory state must strictly isolate external side effects (e.g. Stripe charges, emails, AWS resource provisions).
3. **Multi-Level Checkpointing**: State is captured at varying granularities ($L0$ through $L5$) based on cost and necessity.
4. **Adaptive Recovery (Replay vs. Repair vs. Replan)**: When a failure occurs, AEONRIFT analyzes divergence and determinism to select the lowest-cost safe recovery path.

---

## 2. Event Model (`packages/core/aeonrift/core/events.py`)

Every action within AEONRIFT is encapsulated in an `ExecutionEvent`:

$$\text{Event}(id, \tau, \text{agent\_id}, \text{exec\_id}, \text{parent\_id}, \text{type}, \text{source}, \Delta_{\text{state}}, \text{side\_effect}, \text{reversibility})$$

### Event Types
- `LLM_CALL`, `LLM_RESULT`
- `TOOL_CALL`, `TOOL_RESULT`
- `FILE_WRITE`, `FILE_DELETE`
- `PROCESS_START`, `PROCESS_EXIT`
- `NETWORK_REQUEST`
- `DATABASE_WRITE`
- `EXTERNAL_SIDE_EFFECT`
- `CHECKPOINT`
- `FAILURE`
- `RECOVERY`, `REPLAY`, `ROLLBACK`, `COMPENSATION`

---

## 3. Causal State Graph (`packages/core/aeonrift/core/graph.py`)

The `CausalStateGraph` tracks parent-child causal linkages between events, state deltas, and side effects.
When a crash occurs, AEONRIFT traverses backward from the failure node to find the **last consistent frontier**, pruning invalid branches while preserving immutable side-effect nodes.

---

## 4. Multi-Level Checkpoints ($L0 - L5$)

| Level | Scope | Description | Storage Overhead |
|---|---|---|---|
| **L0** | Logical | Messages, conversation history, task state | Minimal (<10KB) |
| **L1** | Application | In-memory variables, state dicts, workflow context | Low (<1MB) |
| **L2** | Filesystem | Workdir diffs, modified files, environment vars | Moderate (1–50MB) |
| **L3** | Process | Subprocess trees, open descriptors, memory mappings | High (50–200MB) |
| **L4** | Sandbox | Docker container layer diffs, MicroVM state | Heavy (200MB–2GB) |
| **L5** | External State| Database snapshot IDs, API resource identifiers | Varies |

---

## 5. Side-Effect Ledger & Rollback Protection (`packages/core/aeonrift/core/ledger.py`)

For any event tagged with `EXTERNAL_SIDE_EFFECT`:
- An **Idempotency Key** is generated: `hash(agent_id + task_id + logical_action_signature)`.
- If a restored execution attempts to re-issue an action matching an already-committed idempotency key:
  - If idempotent: AEONRIFT intercepts the network call and returns the cached result.
  - If non-idempotent: AEONRIFT **BLOCKS** execution, flags a rollback hazard, and invokes the Recovery Planner (`REPAIR` or `COMPENSATE`).

---

## 6. Recovery Engine (`services/recovery`)

Given a failure $F$, AEONRIFT computes the **Recovery Score**:

$$S_{\text{rec}} = w_1 (1 - \text{age}) + w_2 (1 - \Delta_{\text{env}}) + w_3 (\text{det}_{\text{tool}}) + w_4 (1 - \text{risk}_{\text{fx}})$$

Based on $S_{\text{rec}}$ and side-effect ledger hazards, AEONRIFT selects:
- **REPLAY**: Full deterministic replay up to step $N$.
- **REPAIR**: Selective prefix replay, bypassing or substituting blocked/failing steps.
- **REPLAN**: Feed environment diff and failure diagnosis back to the agent LLM to synthesize a new branch.
- **COMPENSATE**: Execute explicit inverse actions for committed side effects before resuming.
