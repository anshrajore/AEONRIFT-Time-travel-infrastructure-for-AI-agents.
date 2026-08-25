<div align="center">

# AEONRIFT (⚡️🌌)

> **Autonomous Execution Orchestration, Recovery, Replay & Incident Fault-Tolerance**
> 
> *When an AI agent fails, don't restart it. Understand what happened, recover what is still valid, and continue from the safest possible state.*
>
> **AEONRIFT — Time-travel infrastructure for AI agents.**

---

[![Created by Ansh Rajore](https://img.shields.io/badge/Creator-Ansh%20Rajore-black.svg?style=for-the-badge&logo=github)](https://github.com/anshrajore)
[![License](https://img.shields.io/badge/License-Apache_2.0-000000.svg?style=for-the-badge)](LICENSE)
[![NPM Version](https://img.shields.io/badge/NPM-v0.1.0-black.svg?style=for-the-badge&logo=npm)](packages/sdk/ts)
[![Python](https://img.shields.io/badge/Python-3.11+-black.svg?style=for-the-badge&logo=python)](packages/core)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-black.svg?style=for-the-badge&logo=typescript)](packages/sdk/ts)
[![Build Status](https://img.shields.io/badge/Tests-17%20passed-black.svg?style=for-the-badge)](tests/unit)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-aeonrift.vercel.app-black.svg?style=for-the-badge&logo=vercel)](https://aeonrift.vercel.app)

</div>

> 🌐 **Live landing page**: [aeonrift.vercel.app](https://aeonrift.vercel.app)

---

## 👨‍💻 Creator & Author Attribution

**AEONRIFT** was designed, architected, and created by **Ansh Rajore** ([@anshrajore](https://github.com/anshrajore)) as open-source AI infrastructure to solve critical vulnerabilities in long-horizon autonomous agent execution.

> *"Naive checkpoint restore creates semantic rollback attacks; naive retries duplicate external side-effects. AEONRIFT brings causal time-travel durability to AI agent runtimes."* — **Ansh Rajore**

---

## 🏛️ System Architecture (Strict Black & White Vector Diagram)

<div align="center">
  <svg width="850" height="460" viewBox="0 0 850 460" fill="none" xmlns="http://www.w3.org/2000/svg">
    <!-- Pure Black Background -->
    <rect width="850" height="460" rx="10" fill="#000000" stroke="#FFFFFF" stroke-width="2"/>
    
    <!-- Title -->
    <text x="425" y="42" fill="#FFFFFF" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, monospace" font-size="16" font-weight="800" text-anchor="middle" letter-spacing="2">AEONRIFT CAUSAL RECOVERY ARCHITECTURE</text>
    <line x1="50" y1="58" x2="800" y2="58" stroke="#FFFFFF" stroke-width="1" stroke-dasharray="2 2"/>

    <!-- Agent Layer -->
    <rect x="70" y="75" width="710" height="45" rx="4" fill="#000000" stroke="#FFFFFF" stroke-width="1.5"/>
    <text x="425" y="103" fill="#FFFFFF" font-family="monospace" font-size="13" font-weight="700" text-anchor="middle">AGENTS & WORKFLOWS (Python SDK / TypeScript NPM Package)</text>

    <!-- Connector Arrow -->
    <path d="M 425 120 L 425 145" stroke="#FFFFFF" stroke-width="1.5" stroke-dasharray="4 4"/>
    <polygon points="421,145 425,152 429,145" fill="#FFFFFF"/>

    <!-- Runtime Container -->
    <rect x="70" y="155" width="710" height="170" rx="6" fill="#000000" stroke="#FFFFFF" stroke-width="2"/>
    <text x="90" y="180" fill="#FFFFFF" font-family="sans-serif" font-size="11" font-weight="800" letter-spacing="1.5">AEONRIFT RUNTIME OBSERVATION LAYER</text>

    <!-- Box 1: Event Interceptor -->
    <rect x="95" y="195" width="185" height="105" rx="4" fill="#000000" stroke="#FFFFFF" stroke-width="1.2"/>
    <text x="187" y="225" fill="#FFFFFF" font-family="sans-serif" font-size="13" font-weight="700" text-anchor="middle">Event Interceptor</text>
    <line x1="115" y1="235" x2="260" y2="235" stroke="#FFFFFF" stroke-width="0.8"/>
    <text x="187" y="255" fill="#FFFFFF" font-family="monospace" font-size="10" text-anchor="middle">Causal Hashing</text>
    <text x="187" y="275" fill="#FFFFFF" font-family="monospace" font-size="10" text-anchor="middle">State Delta Tracking</text>

    <!-- Box 2: Side-Effect Ledger -->
    <rect x="332" y="195" width="185" height="105" rx="4" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
    <text x="425" y="225" fill="#000000" font-family="sans-serif" font-size="13" font-weight="800" text-anchor="middle">Side-Effect Ledger</text>
    <line x1="352" y1="235" x2="498" y2="235" stroke="#000000" stroke-width="0.8"/>
    <text x="425" y="255" fill="#000000" font-family="monospace" font-size="10" font-weight="700" text-anchor="middle">Idempotency Manager</text>
    <text x="425" y="275" fill="#000000" font-family="monospace" font-size="10" font-weight="700" text-anchor="middle">Rollback Guard</text>

    <!-- Box 3: Layered Checkpoint Engine -->
    <rect x="570" y="195" width="185" height="105" rx="4" fill="#000000" stroke="#FFFFFF" stroke-width="1.2"/>
    <text x="662" y="225" fill="#FFFFFF" font-family="sans-serif" font-size="13" font-weight="700" text-anchor="middle">Layered Engine</text>
    <line x1="590" y1="235" x2="735" y2="235" stroke="#FFFFFF" stroke-width="0.8"/>
    <text x="662" y="255" fill="#FFFFFF" font-family="monospace" font-size="10" text-anchor="middle">Semantic Filter</text>
    <text x="662" y="275" fill="#FFFFFF" font-family="monospace" font-size="10" text-anchor="middle">Levels L0 — L5</text>

    <!-- Connector Arrow -->
    <path d="M 425 325 L 425 350" stroke="#FFFFFF" stroke-width="1.5"/>
    <polygon points="421,350 425,357 429,350" fill="#FFFFFF"/>

    <!-- Bottom: Recovery Engine -->
    <rect x="70" y="360" width="710" height="65" rx="4" fill="#000000" stroke="#FFFFFF" stroke-width="2"/>
    <text x="425" y="388" fill="#FFFFFF" font-family="sans-serif" font-size="14" font-weight="800" text-anchor="middle">RIFT RECOVERY PLANNER ENGINE</text>
    <text x="425" y="408" fill="#FFFFFF" font-family="monospace" font-size="11" text-anchor="middle">[ REPLAY | REPAIR | REPLAN | COMPENSATE ]</text>
  </svg>
</div>

---

## 💡 Why AEONRIFT? (The Problem & Research Rationale)

Existing agent recovery mechanisms rely on naive, broken strategies:

1. **Blind Retry**: Restarts the agent loop from scratch upon exceptions.
2. **Unaware Checkpoint/Restore**: Restores in-memory process or container state without accounting for external side effects or environment changes.

### The Vulnerability: Semantic Rollback Attacks (ACRFence, 2026)
Consider an autonomous coding or purchasing agent performing a 7-step task:

$$\text{Step 1 (Read Config)} \rightarrow \text{Step 2 (Update Code)} \rightarrow \dots \rightarrow \text{Step 6 (Stripe Payment API)} \rightarrow \text{Step 7 (Deploy)} \rightarrow \text{CRASH!}$$

If a traditional checkpoint engine blindly restores state at Step 5 and replays the trajectory, **Step 6 (Stripe Payment) will be re-executed**, resulting in duplicate charges or resurrected credentials. This flaw is defined as a **Semantic Rollback Attack** (*ACRFence, 2026*).

### Wasteful Checkpointing (Crab, 2026)
Crab (2026) demonstrates that **over 75% of agent turns produce no recovery-relevant state change** (e.g. conversational LLM turns or read-only file inspections). Checkpointing every turn wastes massive storage and I/O.

### Verified-Prefix Replay (RePoT, 2026)
RePoT (2026) proves that crashed agent trajectories can be repaired from verified prefixes rather than restarted.

### AEONRIFT Solution: Causal State Recovery
AEONRIFT models agent intent, OS state deltas, tool side effects, and external environment mutations inside a unified **Causal State Graph**. It guarantees:
- **Zero Duplicate Side Effects**: Non-idempotent side effects are blocked or compensated upon restore.
- **Minimal Checkpointing (L0–L5)**: Only recovery-relevant mutations trigger snapshots.
- **Adaptive Recovery Modes**: Automatically selects between `REPLAY`, `REPAIR`, `REPLAN`, and `COMPENSATE`.

---

## 📦 Installation & Setup

### TypeScript / Node.js Package (NPM)

```bash
# Install AEONRIFT SDK in your project
npm install aeonrift

# Verify installation with Node CLI
npx aeonrift doctor
```

### Python Package & CLI

```bash
# Install AEONRIFT core runtime and CLI
pip install aeonrift-cli

# Run system diagnostic doctor
aeonrift doctor
```

---

## 🛠️ Step-by-Step Implementation Guide

### 1. TypeScript / Node.js Implementation

```typescript
import { AeonriftClient, SideEffectType, ReversibilityType } from "aeonrift";

// Initialize runtime observer
const runtime = new AeonriftClient("coding_agent_01", "exec_8219");

// Intercept tool call with side-effect tracking and rollback protection
async function executePayment() {
  const result = await runtime.interceptTool(
    "stripe.create_payment",
    async (args) => {
      // Your actual tool or API invocation
      return { status: "PAID", txId: "tx_9941" };
    },
    { orderId: "order_991", amount: 250 },
    {
      sideEffectType: SideEffectType.MUTATING_IRREVERSIBLE,
      reversibility: ReversibilityType.IRREVERSIBLE,
      idempotencyKey: "aeonrift:coding_agent_01:exec_8219:order_991"
    }
  );

  console.log("Payment Result:", result);
}

executePayment().catch(console.error);
```

---

### 2. Python Implementation

```python
from aeonrift.runtime.interceptor import AeonriftRuntime
from aeonrift.core.events import SideEffectType, ReversibilityType

# Initialize AEONRIFT execution runtime
runtime = AeonriftRuntime(
    agent_id="coding_agent_01",
    execution_id="exec_8219",
    storage_dir=".aeonrift/event_store"
)

# Define tool function
def update_package_json(path: str):
    with open(path, "w") as f:
        f.write('{"name": "my-app", "version": "1.0.1"}')
    return "Updated package.json"

# Intercept tool call with L2 Filesystem checkpointing
result = runtime.intercept_tool(
    tool_name="write_file",
    tool_func=update_package_json,
    tool_kwargs={"path": "package.json"},
    side_effect_type=SideEffectType.MUTATING_REVERSIBLE,
    reversibility=ReversibilityType.REVERSIBLE
)

print("Tool Result:", result)
```

---

## ⚡️ Complete CLI Command Reference

AEONRIFT provides an advanced CLI interface for time-travel debugging, model training, chaos injection, benchmarking, and state diffing:

```bash
# 1. Initialize AEONRIFT directory in project
aeonrift init

# 2. Inspect execution timeline and checkpoints
aeonrift timeline exec_8219

# 3. Recover a crashed execution safely
aeonrift recover exec_8219

# 4. Train RIFT-Predict ML Recovery Policy on RIFT-FAIL dataset
aeonrift train --samples 1000 --output ml/models/weights.json

# 5. Run RIFT-CHAOS Fault Injection Suite (LLM timeouts, process kills, network partitions)
aeonrift chaos

# 6. Run RIFT-Bench Evaluation Suite
aeonrift benchmark

# 7. Render Terminal State Diff between Checkpoints
aeonrift diff cp_001 cp_002

# 8. Run system health check
aeonrift doctor
```

---

## 🧪 Benchmark Metrics (RIFT-Bench)

AEONRIFT evaluates recovery performance against standard durable execution engines using three research metrics:

1. **Recovery Efficiency (RE)**:
   $$\text{RE} = \frac{\text{Useful Work Preserved}}{\text{Recovery Cost}}$$

2. **Recovery Overhead**:
   $$\text{Recovery Overhead} = \frac{\text{Checkpoint} + \text{Replay} + \text{Diagnosis}}{\text{Fault-Free Execution}}$$

3. **Recovery Correctness**:
   $$\text{Recovery Correctness} = \frac{\text{Safe Recoveries}}{\text{Total Recovery Attempts}}$$

---

## 📜 License & Credits

AEONRIFT is created and authored by **Ansh Rajore** ([@anshrajore](https://github.com/anshrajore)) and licensed under the [Apache 2.0 License](LICENSE).
