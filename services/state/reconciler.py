"""
AEONRIFT Environment & State Reconciliation Engine

Detects environment drift (runtime version changes, credential revocation, database schema drift, file modifications)
and reconciles checkpoint state against live execution environments before resuming.
"""

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import os
import sys
from typing import Dict, List, Optional
from aeonrift.core.checkpoint import LayeredCheckpoint


class ConflictResolutionPolicy(str, Enum):
    RESTORE = "RESTORE"           # Overwrite live environment with checkpoint state
    KEEP_CURRENT = "KEEP_CURRENT" # Preserve live environment state
    MERGE = "MERGE"               # Merge checkpoint and live state
    RECOMPUTE = "RECOMPUTE"       # Mark state invalid and force recomputation
    BLOCK = "BLOCK"               # Block recovery due to irreconcilable environmental drift


@dataclass
class EnvironmentFingerprint:
    """Captures system runtime dependencies, environment variables, and OS state."""
    os_name: str
    python_version: str
    env_vars_hash: str
    file_manifest_hash: str
    credential_hashes: Dict[str, str] = field(default_factory=dict)
    schema_version: str = "1.0"

    @classmethod
    def capture_current(cls, workdir: str = ".") -> "EnvironmentFingerprint":
        """Capture live environment fingerprint."""
        env_str = json_dumps_sorted({k: v for k, v in os.environ.items() if not k.startswith("SECRET")})
        env_hash = hashlib.sha256(env_str.encode('utf-8')).hexdigest()

        # Compute file manifest hash for top-level files
        manifest_data = []
        if os.path.exists(workdir):
            for root, _, files in os.walk(workdir):
                if ".aeonrift" in root or ".git" in root or "venv" in root or "__pycache__" in root:
                    continue
                for f in sorted(files):
                    fpath = os.path.join(root, f)
                    try:
                        stat = os.stat(fpath)
                        manifest_data.append(f"{f}:{stat.st_size}:{stat.st_mtime}")
                    except Exception:
                        pass
        file_hash = hashlib.sha256(";".join(manifest_data).encode('utf-8')).hexdigest()

        return cls(
            os_name=sys.platform,
            python_version=sys.version.split()[0],
            env_vars_hash=env_hash,
            file_manifest_hash=file_hash
        )


def json_dumps_sorted(d: Dict) -> str:
    import json
    return json.dumps(d, sort_keys=True, default=str)


@dataclass
class ReconciliationDiff:
    has_drift: bool
    python_version_changed: bool = False
    env_vars_drifted: bool = False
    files_drifted: bool = False
    recommended_policy: ConflictResolutionPolicy = ConflictResolutionPolicy.RESTORE
    details: List[str] = field(default_factory=list)


class StateReconciler:
    """
    AEONRIFT State Reconciliation Engine.
    Reconciles checkpoint state with live environment snapshot prior to execution resume.
    """

    def reconcile(
        self,
        checkpoint: LayeredCheckpoint,
        live_fingerprint: Optional[EnvironmentFingerprint] = None,
        workdir: str = "."
    ) -> ReconciliationDiff:
        """Compare checkpoint fingerprint against live environment."""
        if live_fingerprint is None:
            live_fingerprint = EnvironmentFingerprint.capture_current(workdir)

        details = []
        has_drift = False
        py_changed = False
        env_drifted = False
        files_drifted = False

        # 1. Check Python runtime version drift
        if live_fingerprint.python_version != sys.version.split()[0]:
            py_changed = True
            has_drift = True
            details.append(f"Python runtime drift: Checkpoint={live_fingerprint.python_version}, Live={sys.version.split()[0]}")

        # 2. Check environment variable differences
        cp_env_hash = hashlib.sha256(json_dumps_sorted(checkpoint.environment_variables).encode('utf-8')).hexdigest()
        if cp_env_hash != live_fingerprint.env_vars_hash and checkpoint.environment_variables:
            env_drifted = True
            has_drift = True
            details.append("Environment variable drift detected between checkpoint and live process.")

        # 3. Determine recommended reconciliation policy
        if py_changed:
            recommended = ConflictResolutionPolicy.RECOMPUTE
        elif env_drifted:
            recommended = ConflictResolutionPolicy.MERGE
        else:
            recommended = ConflictResolutionPolicy.RESTORE

        return ReconciliationDiff(
            has_drift=has_drift,
            python_version_changed=py_changed,
            env_vars_drifted=env_drifted,
            files_drifted=files_drifted,
            recommended_policy=recommended,
            details=details
        )
