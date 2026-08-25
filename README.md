# AEONRIFT (⚡️🌌)

> **Autonomous Execution Orchestration, Recovery, Replay & Incident Fault-Tolerance**
> 
> *When an AI agent fails, don't restart it. Understand what happened, recover what is still valid, and continue from the safest possible state.*
>
> **AEONRIFT — Time-travel infrastructure for AI agents.**

---

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](packages/core)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](packages/sdk/ts)
[![Architecture](https://img.shields.io/badge/Architecture-Causal%20Recovery%20Graph-purple.svg)](docs/architecture/overview.md)
[![Build Status](https://img.shields.io/badge/Tests-17%20passed-brightgreen.svg)](tests/unit)

---

## 💡 Why AEONRIFT?

Current AI agent recovery paradigms rely on naive strategies:
- **Blind Retry**: Restart execution from scratch upon tool or LLM errors.
- **Unaware Checkpoint/Restore**: Restore process state without considering external side effects or environment drift.

These approaches fail dangerously in real-world environments. For instance:
If an agent executes steps 1–5 successfully, performs an API payment at step 6, and crashes at step 7, naive checkpoint restoration will re-execute step 6—charging the user twice. This vulnerability class is known as **Semantic Rollback Attacks** (ACRFence, 2026). Moreover, up to 75% of agent turns produce no recovery-relevant state updates (Crab, 2026).

**AEONRIFT** introduces **Causal State Recovery**: an execution runtime that models agent intent, OS states, tool side effects, and external environment changes in a unified **Causal State Graph**.

---

## 🏛️ System Architecture

```text
                  AGENT / WORKFLOW
                        │
                        ▼
       ┌─────────────────────────────────┐
       │         AEONRIFT RUNTIME        │
       └────────────────┬────────────────┘
                        │
    ┌───────────────────┼───────────────────┐
    ▼                   ▼                   ▼
EVENT CAPTURE     STATE OBSERVER     SIDE EFFECT LEDGER
    │                   │                   │
    └───────────────────┼───────────────────┘
                        ▼
               CAUSAL STATE GRAPH
                        │
       ┌────────────────┴────────────────┐
       ▼                                 ▼
CHECKPOINT POLICY                 FAILURE DIAGNOSTICS
       │                                 │
       ▼                                 ▼
LAYERED CHECKPOINT (L0-L5)        RECOVERY PLANNER
                                         │
                   ┌─────────────────────┼─────────────────────┐
                   ▼                     ▼                     ▼
                REPLAY                REPAIR                REPLAN
                   │                     │                     │
                   └─────────────────────┼─────────────────────┘
                                         ▼
                               STATE RECONCILIATION
                                         │
                                         ▼
                             RESUME EXECUTION / HUMAN GATE
```

---

## 🚀 Key Features

1. **Causal State Graph**: Maps causal linkages across LLM decisions, OS file system mutations, subprocess invocations, and external API mutations.
2. **Side-Effect Ledger & Rollback Protection**: Prevents duplicate execution of non-idempotent operations (payments, emails, production deploys).
3. **Semantic & Multi-Level Checkpointing (L0–L5)**:
   - `L0`: Logical agent state & conversation history
   - `L1`: Memory variables & state
   - `L2`: Filesystem deltas
   - `L3`: Process state
   - `L4`: Container / microVM snapshot
   - `L5`: External state & resource IDs
4. **Three Recovery Modes**:
   - `REPLAY`: Deterministically re-execute safe, idempotent steps.
   - `REPAIR`: Splice trajectory, skip/modify invalid steps, and reuse verified prefixes.
   - `REPLAN`: Inject updated context into agent when environment diverges significantly.
   - `COMPENSATE`: Execute inverse actions for unrollbackable side effects.
5. **State Reconciliation Engine**: Validates environment drift (Node/Python versions, active API tokens, modified files) prior to resuming execution.
6. **Time-Travel Debugger UI & CLI**: Full command-line and visual inspection of execution trees, DAGs, state diffs, and branch trajectories.
7. **RIFT CHAOS Testing & RIFT-Bench**: Fault injection benchmarking measuring Recovery Efficiency (RE) and Zero-Duplicate Side Effect guarantees.
8. **Cryptographic Checkpoint Integrity**: HMAC-SHA256 checkpoint signatures and automatic secret scrubbing.
9. **ML Predictive Recovery Policies**: RIFT-Predict and RIFT-Checkpoint models trained on RIFT-FAIL benchmark dataset.
10. **Distributed Fleet & Multi-Agent Recovery**: Distributed coordinator managing multi-agent causal message graphs ($N=1000$ fleet scaling).

---

## 📦 Quick Start (CLI)

```bash
# Initialize AEONRIFT in your project
aeonrift init

# Run health diagnostics
aeonrift doctor

# Inspect execution history
aeonrift timeline exec_8219

# Recover a crashed execution safely
aeonrift recover exec_8219
```

---

## 🗺️ Roadmap & Implementation Status

- [x] **Phase 0**: Project Specification & Folder Architecture
- [x] **Phase 1**: Core Event & State Delta Model (`packages/core`)
- [x] **Phase 2**: Append-Only Event Store & Causal Log (`storage/event-log`)
- [x] **Phase 3**: Runtime Interception & Proxies (`packages/runtime`)
- [x] **Phase 4**: Layered Checkpoint Engine L0–L5 (`services/checkpoint`)
- [x] **Phase 5**: Deterministic Execution Replay Engine (`services/replay`)
- [x] **Phase 6**: External Side-Effect Ledger & Idempotency Key Manager (`packages/core/ledger.py`)
- [x] **Phase 7**: Semantic Rollback Protection (`packages/core/policy.py`)
- [x] **Phase 8**: Failure Diagnostic & Classifier (`services/recovery/planner.py`)
- [x] **Phase 9**: Replay / Repair / Replan Recovery Planner (`services/recovery/planner.py`)
- [x] **Phase 10**: State & Environment Reconciliation (`services/state`)
- [x] **Phase 11**: Recovery Validator (`services/recovery/validator.py`)
- [x] **Phase 12**: AEONRIFT Developer CLI (`packages/cli`)
- [x] **Phase 13**: Time-Travel Debugger UI & Visual DAG (`apps/dashboard`)
- [x] **Phase 14**: Chaos Testing & Failure Injector (`tests/chaos`)
- [x] **Phase 15**: RIFT-Bench Evaluation Suite (`benchmarks`)
- [x] **Phase 16**: ML Policy & Learning-to-Recover (`ml`)
- [x] **Phase 17**: Distributed Fleet & Multi-Agent Recovery (`services/coordinator`)
- [x] **Phase 18**: Security Hardening & Tamper-Evident Signatures (`services/checkpoint/security.py`)

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) and our [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before submitting Pull Requests.

---

## 🛡️ License

AEONRIFT is licensed under the [Apache 2.0 License](LICENSE).
