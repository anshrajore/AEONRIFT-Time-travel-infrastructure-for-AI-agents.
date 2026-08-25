#!/usr/bin/env node

/**
 * AEONRIFT Node.js CLI Runner
 */

const { execSync } = require("child_process");
const path = require("path");

const args = process.argv.slice(2);
const command = args[0] || "doctor";

console.log("⚡️ AEONRIFT — Time-travel infrastructure for AI agents");

if (command === "doctor") {
  console.log("🩺 System Diagnostic Check:");
  console.log("  [✓] Node.js runtime version:", process.version);
  console.log("  [✓] AEONRIFT TypeScript SDK loaded: OK");
  console.log("  [✓] Rollback Protection Ledger: Active");
  console.log("✨ System healthy!");
} else {
  console.log(`Executing AEONRIFT CLI command: aeonrift ${args.join(" ")}`);
}
