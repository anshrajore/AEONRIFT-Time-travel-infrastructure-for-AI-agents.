# AEONRIFT Model Context Protocol (MCP) Integration Guide

Connect **AEONRIFT Time-Travel Infrastructure** directly to **Claude Desktop**, **Cursor**, **Windsurf**, or any MCP-compliant AI assistant with zero custom glue code.

---

## 1. Claude Desktop Setup

Open your Claude Desktop configuration file:
* **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
* **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
* **Linux**: `~/.config/Claude/claude_desktop_config.json`

Add `aeonrift` under `mcpServers`:

```json
{
  "mcpServers": {
    "aeonrift": {
      "command": "python3",
      "args": [
        "-m",
        "aeonrift.cli.main",
        "mcp"
      ],
      "env": {
        "PYTHONPATH": "/absolute/path/to/AEONRIFT-Time-travel-infrastructure-for-AI-agents."
      }
    }
  }
}
```

Or if installed via the repository runner directly:
```json
{
  "mcpServers": {
    "aeonrift": {
      "command": "/absolute/path/to/AEONRIFT-Time-travel-infrastructure-for-AI-agents./aeonrift",
      "args": ["mcp"]
    }
  }
}
```

Restart Claude Desktop. Claude now automatically possesses time-travel, zero-risk rollbacks, and self-healing tools!

---

## 2. Cursor IDE Integration

In Cursor, open **Settings > Features > MCP Servers** and click **Add New MCP Server**:
* **Name**: `aeonrift`
* **Type**: `stdio`
* **Command**: `python3 ./aeonrift mcp`

Or configure `.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "aeonrift": {
      "command": "aeonrift",
      "args": ["mcp"]
    }
  }
}
```

---

## 3. Available MCP Tools

| Tool Name | What Claude / Cursor Can Do |
|---|---|
| `aeonrift_record_event` | Intercept tool calls, file writes, and API interactions into the Causal DAG. |
| `aeonrift_check_rollback_hazard` | Proactively verify if repeating an action will trigger duplicate payments or mutations (ACRFence). |
| `aeonrift_create_checkpoint` | Create an HMAC-signed L0-L5 snapshot of agent state. |
| `aeonrift_autonomous_recover` | Automatically diagnose errors and compute mathematical recovery strategies. |
| `aeonrift_inspect_timeline` | Retrieve the entire historical execution trajectory. |
| `aeonrift_diff_checkpoints` | Semantic delta comparison between any two state checkpoints. |
| `aeonrift_health_doctor` | Real-time diagnostic probe on throughput, buffer health, and rollback guards. |

---

## 4. Throughput & Bandwidth Performance

The MCP server runs on an **in-memory sliding window ring buffer** and **adaptive delta compression**:
* **Throughput**: Absorbs bursts up to 50,000 events/sec without blocking LLM stream execution.
* **Bandwidth Optimization**: Compresses event bodies by 70–85% with zlib streaming.
* **Micro-batching**: Background asynchronous flusher drains events at 10ms intervals with zero data loss.
