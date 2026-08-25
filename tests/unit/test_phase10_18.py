"""
Unit tests for AEONRIFT State Reconciliation, Recovery Validation, Chaos Engine, Benchmarks, and Security
"""

import os
import shutil
import tempfile
import unittest
import sys

sys.path.insert(0, os.path.abspath("packages/core"))
sys.path.insert(0, os.path.abspath("packages/runtime"))
sys.path.insert(0, os.path.abspath("services/checkpoint"))
sys.path.insert(0, os.path.abspath("services/recovery"))
sys.path.insert(0, os.path.abspath("services/state"))
sys.path.insert(0, os.path.abspath("storage/event-log"))
sys.path.insert(0, os.path.abspath("tests/chaos"))
sys.path.insert(0, os.path.abspath("benchmarks"))

from aeonrift.core.checkpoint import LayeredCheckpoint, CheckpointMetadata, CheckpointLevel
from aeonrift.core.ledger import SideEffectLedger
from aeonrift.runtime.interceptor import AeonriftRuntime
from reconciler import StateReconciler, EnvironmentFingerprint
from validator import RecoveryValidator
from chaos_engine import RiftChaosEngine, ChaosFailureType
from bench_runner import RiftBenchRunner
from security import CheckpointSecurityGuard


class TestPhase10To18(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_state_reconciler_and_validator(self):
        cp_meta = CheckpointMetadata(
            checkpoint_id="cp_test_01", execution_id="ex_1", step_number=1, level=CheckpointLevel.L1_APP_STATE
        )
        checkpoint = LayeredCheckpoint(metadata=cp_meta, memory_variables={"var1": "val1"})
        checkpoint.compute_state_hash()

        validator = RecoveryValidator()
        ledger = SideEffectLedger()

        val_result = validator.validate_recovery_state(checkpoint, ledger, workdir=self.test_dir)
        self.assertTrue(val_result.is_valid)
        self.assertGreaterEqual(val_result.confidence_score, 0.85)

    def test_checkpoint_security_signing_and_scrubbing(self):
        guard = CheckpointSecurityGuard(secret_key="my_secret_key")
        cp_meta = CheckpointMetadata(
            checkpoint_id="cp_sec_01", execution_id="ex_sec", step_number=2, level=CheckpointLevel.L1_APP_STATE
        )
        cp = LayeredCheckpoint(metadata=cp_meta, memory_variables={"user": "admin"})

        sig = guard.sign_checkpoint(cp)
        self.assertTrue(guard.verify_checkpoint_signature(cp))

        payload = {"api_key": "sk_mock_1234567890abcdef12345678", "normal_field": "hello"}
        scrubbed = guard.scrub_credentials(payload)
        self.assertEqual(scrubbed["api_key"], "[REDACTED_CREDENTIAL]")
        self.assertEqual(scrubbed["normal_field"], "hello")

    def test_chaos_engine_experiment(self):
        runtime = AeonriftRuntime(agent_id="agent_c", execution_id="exec_c", storage_dir=self.test_dir)
        chaos = RiftChaosEngine()

        res = chaos.run_chaos_experiment(runtime, ChaosFailureType.TOOL_FAILURE, at_step=3)
        self.assertTrue(res.recovery_successful)

    def test_bench_runner(self):
        runner = RiftBenchRunner()
        results = runner.run_benchmark_suite()
        self.assertEqual(len(results), 3)
        self.assertTrue(all(r.recovery_success for r in results))


if __name__ == '__main__':
    unittest.main()
