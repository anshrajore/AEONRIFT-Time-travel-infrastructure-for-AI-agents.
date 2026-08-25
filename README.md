# AEONRIFT (⚡️🌌)

> **Autonomous Execution Orchestration, Recovery, Replay & Incident Fault-Tolerance**
> 
> *When an AI agent fails, don't restart it. Understand what happened, recover what is still valid, and continue from the safest possible state.*
>
> **AEONRIFT — Time-travel infrastructure for AI agents.**

---

[![License](https://img.shields.io/badge/License-Apache_2.0-000000.svg?style=for-the-badge)](LICENSE)
[![NPM Version](https://img.shields.io/badge/NPM-v0.1.0-black.svg?style=for-the-badge&logo=npm)](packages/sdk/ts)
[![Python](https://img.shields.io/badge/Python-3.11+-black.svg?style=for-the-badge&logo=python)](packages/core)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-black.svg?style=for-the-badge&logo=typescript)](packages/sdk/ts)
[![Tests](https://img.shields.io/badge/Tests-17%20passed-black.svg?style=for-the-badge)](tests/unit)

---

## 🏛️ System Architecture

<div align="center">
  <svg width="850" height="420" viewBox="0 0 850 420" fill="none" xmlns="http://www.w3.org/2000/svg">
    <!-- Background -->
    <rect width="850" height="420" rx="12" fill="#0A0A0A" stroke="#262626" stroke-width="2"/>
    
    <!-- Title Header -->
    <text x="425" y="40" fill="#FFFFFF" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="18" font-weight="700" text-anchor="middle" letter-spacing="1.5">AEONRIFT CAUSAL RECOVERY ARCHITECTURE</text>
    
    <!-- Outer Box: Agent -->
    <rect x="50" y="70" width="750" height="50" rx="6" fill="#141414" stroke="#404040" stroke-width="1.5"/>
    <text x="425" y="100" fill="#E5E5E5" font-family="monospace" font-size="14" font-weight="600" text-anchor="middle">AGENT EXECUTION LAYER (Python / TypeScript SDK)</text>
    
    <!-- Arrow Down -->
    <path d="M 425 120 L 425 145" stroke="#E5E5E5" stroke-width="2" stroke-dasharray="4 4"/>
    <polygon points="421,145 425,152 429,145" fill="#E5E5E5"/>
    
    <!-- Core Runtime Container -->
    <rect x="50" y="155" width="750" height="150" rx="8" fill="#171717" stroke="#525252" stroke-width="1.5"/>
    <text x="70" y="180" fill="#A3A3A3" font-family="sans-serif" font-size="11" font-weight="700" letter-spacing="1">AEONRIFT FAULT-TOLERANT RUNTIME</text>

    <!-- Subcomponents -->
    <!-- Event Interceptor -->
    <rect x="80" y="195" width="200" height="85" rx="6" fill="#0A0A0A" stroke="#404040" stroke-width="1.2"/>
    <text x="180" y="225" fill="#FFFFFF" font-family="sans-serif" font-size="13" font-weight="600" text-anchor="middle">Event Interceptor</text>
    <text x="180" y="250" fill="#737373" font-family="monospace" font-size="11" text-anchor="middle">Causal Hashing & Log</text>

    <!-- Side Effect Ledger -->
    <rect x="325" y="195" width="200" height="85" rx="6" fill="#0A0A0A" stroke="#FFFFFF" stroke-width="1.5"/>
    <text x="425" y="225" fill="#FFFFFF" font-family="sans-serif" font-size="13" font-weight="700" text-anchor="middle">Side-Effect Ledger</text>
    <text x="425" y="250" fill="#A3A3A3" font-family="monospace" font-size="11" text-anchor="middle">Rollback Protection</text>

    <!-- Checkpoint Engine -->
    <rect x="570" y="195" width="200" height="85" rx="6" fill="#0A0A0A" stroke="#404040" stroke-width="1.2"/>
    <text x="670" y="225" fill="#FFFFFF" font-family="sans-serif" font-size="13" font-weight="600" text-anchor="middle">Layered Checkpoints</text>
    <text x="670" y="250" fill="#737373" font-family="monospace" font-size="11" text-anchor="middle">Levels L0 — L5</text>

    <!-- Arrow Down to Planner -->
    <path d="M 425 305 L 425 330" stroke="#E5E5E5" stroke-width="2"/>
    <polygon points="421,330 425,337 429,330" fill="#E5E5E5"/>

    <!-- Bottom Recovery Planner -->
    <rect x="50" y="340" width="750" height="55" rx="6" fill="#262626" stroke="#737373" stroke-width="1.5"/>
    <text x="425" y="365" fill="#FFFFFF" font-family="sans-serif" font-size="14" font-weight="700" text-anchor="middle">RIFT RECOVERY PLANNER ENGINE</text>
    <text x="425" y="383" fill="#D4D4D4" font-family="monospace" font-size="11" text-anchor="middle">[ REPLAY | REPAIR | REPLAN | COMPENSATE ]</text>
  </svg>
</div>

---

## ⚡️ Key Features

1. **Causal State Graph**: Maps causal linkages across LLM decisions, OS file system mutations, subprocess invocations, and external API calls.
2. **Side-Effect Ledger & Rollback Protection (ACRFence 2026)**: Defends against duplicate execution of non-idempotent operations (Stripe payments, emails, cloud deployments).
3. **Semantic & Multi-Level Checkpointing L0–L5 (Crab 2026)**:
   - `L0`: Logical agent state & conversation history
   - `L1`: Memory variables & state
   - `L2`: Filesystem deltas
   - `L3`: Process state
   - `L4`: Container / microVM snapshot
   - `L5`: External state & resource IDs
4. **Adaptive Recovery Modes**:
   - `REPLAY`: Deterministically re-execute safe, idempotent steps.
   - `REPAIR`: Splice trajectory, skip/modify invalid steps, and reuse verified prefixes.
   - `REPLAN`: Inject updated context into agent when environment diverges significantly.
   - `COMPENSATE`: Execute inverse actions for unrollbackable side effects.
5. **State Reconciliation Engine**: Validates environment drift (Node/Python versions, active API tokens, modified files) prior to resuming execution.
6. **Time-Travel Debugger UI & CLI**: Full command-line and visual inspection of execution trees, DAGs, state diffs, and branch trajectories.
7. **RIFT CHAOS Testing & RIFT-Bench**: Fault injection benchmarking measuring Recovery Efficiency (RE) and Zero-Duplicate Side Effect guarantees.
8. **Cryptographic Integrity**: HMAC-SHA256 checkpoint signatures and automatic secret scrubbing.

---

## 📦 Installation & NPM Package

### Node.js / NPM

```bash
# Install AEONRIFT SDK in your Node project
npm install aeonrift

# Run CLI diagnostic doctor via npx
npx aeonrift doctor
```

### Python / CLI

```bash
# Install AEONRIFT Python package & CLI
pip install aeonrift-cli

# Run system health check
aeonrift doctor
```

---

## 💻 Code Examples

### TypeScript / Node.js

```typescript
import { AeonriftClient, SideEffectType, ReversibilityType } from "aeonrift";

const runtime = new AeonriftClient("coding_agent_01", "exec_8219");

// Intercept non-idempotent API payment call
const payment = await runtime.interceptTool(
  "stripe.create_payment",
  async (args) => {
    return await stripe.charges.create(args);
  },
  { orderId: "order_991", amount: 250 },
  {
    sideEffectType: SideEffectType.MUTATING_IRREVERSIBLE,
    reversibility: ReversibilityType.IRREVERSIBLE,
    idempotencyKey: "aeonrift:agent_01:order_991:payment"
  }
);
```

### Python

```python
from aeonrift.runtime.interceptor import AeonriftRuntime
from aeonrift.core.events import SideEffectType, ReversibilityType

runtime = AeonriftRuntime(agent_id="coding_agent_01", execution_id="exec_8219")

def create_payment(order_id: str, amount: int):
    return {"status": "COMMITTED", "tx_id": "tx_stripe_9941"}

payment_res = runtime.intercept_tool(
    tool_name="stripe.create_payment",
    tool_func=create_payment,
    tool_kwargs={"order_id": "order_991", "amount": 250},
    side_effect_type=SideEffectType.MUTATING_IRREVERSIBLE,
    reversibility=ReversibilityType.IRREVERSIBLE
)
```

---

## 🛠️ Advanced CLI Usage

```bash
# 1. Initialize AEONRIFT in a target workspace
aeonrift init

# 2. Inspect execution timeline
aeonrift timeline exec_8219

# 3. Recover a crashed execution safely
aeonrift recover exec_8219

# 4. Train RIFT-Predict ML Recovery Policy
aeonrift train --samples 1000 --output ml/models/weights.json

# 5. Run RIFT-CHAOS Fault Injection Suite
aeonrift chaos

# 6. Run RIFT-Bench Evaluation Suite
aeonrift benchmark

# 7. Render Terminal State Diff between Checkpoints
aeonrift diff cp_001 cp_002
```

---

## 🗺️ Roadmap & Implementation Status

- [x] **Phase 0**: Project Specification & Folder Architecture
- [x] **Phase 1**: Core Event & State Delta Model (`packages/core`)
- [x] **Phase 2**: Append-Only Event Store & Causal Log (`storage/event-log`)
- [x] **Phase 3**: Runtime Interception & Observer (`packages/runtime`)
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
