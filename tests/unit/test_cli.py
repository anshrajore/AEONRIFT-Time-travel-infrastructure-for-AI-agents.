"""
AEONRIFT CLI Cross-Platform Unit Test Suite

Tests all CLI commands, cross-platform terminal formatting,
and export functionality across OS environments.
"""

import unittest
import sys
import os
import json
import platform
import subprocess

# Path setup
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "packages", "core"))
sys.path.insert(0, os.path.join(ROOT, "packages", "runtime"))
sys.path.insert(0, os.path.join(ROOT, "packages", "cli"))
sys.path.insert(0, os.path.join(ROOT, "services", "checkpoint"))
sys.path.insert(0, os.path.join(ROOT, "services", "recovery"))
sys.path.insert(0, os.path.join(ROOT, "services", "state"))
sys.path.insert(0, os.path.join(ROOT, "services", "coordinator"))
sys.path.insert(0, os.path.join(ROOT, "services", "gateway"))
sys.path.insert(0, os.path.join(ROOT, "storage", "event-log"))
sys.path.insert(0, os.path.join(ROOT, "benchmarks"))
sys.path.insert(0, os.path.join(ROOT, "ml", "training"))
sys.path.insert(0, os.path.join(ROOT, "ml", "datasets"))
sys.path.insert(0, os.path.join(ROOT, "ml", "models"))
sys.path.insert(0, os.path.join(ROOT, "tests", "chaos"))
sys.path.insert(0, os.path.join(ROOT, "apps", "dashboard"))
sys.path.insert(0, os.path.join(ROOT, "adapters"))


class TestCLIUtils(unittest.TestCase):
    """Test cross-platform terminal utilities."""

    def test_supports_color_returns_bool(self):
        from aeonrift.cli.utils import supports_color
        result = supports_color()
        self.assertIsInstance(result, bool)

    def test_is_utf8_terminal_returns_bool(self):
        from aeonrift.cli.utils import is_utf8_terminal
        result = is_utf8_terminal()
        self.assertIsInstance(result, bool)

    def test_style_returns_string(self):
        from aeonrift.cli.utils import style
        result = style("hello", "green", bold=True)
        self.assertIsInstance(result, str)
        self.assertIn("hello", result)

    def test_style_no_color(self):
        from aeonrift.cli.utils import style
        os.environ["NO_COLOR"] = "1"
        result = style("plain text", "red")
        self.assertEqual(result, "plain text")
        del os.environ["NO_COLOR"]

    def test_symbol_ok(self):
        from aeonrift.cli.utils import symbol
        result = symbol("ok")
        self.assertIn(result, ["✓", "[OK]"])

    def test_symbol_fail(self):
        from aeonrift.cli.utils import symbol
        result = symbol("fail")
        self.assertIn(result, ["✗", "[FAIL]"])

    def test_symbol_unknown_returns_empty(self):
        from aeonrift.cli.utils import symbol
        result = symbol("nonexistent_symbol_name")
        self.assertEqual(result, "")

    def test_normalize_path_returns_absolute(self):
        from aeonrift.cli.utils import normalize_path
        result = normalize_path("some/relative/path")
        self.assertTrue(os.path.isabs(result))

    def test_normalize_path_handles_dots(self):
        from aeonrift.cli.utils import normalize_path
        result = normalize_path("./foo/../bar")
        self.assertNotIn("..", result)


class TestCLIDoctor(unittest.TestCase):
    """Test the doctor command."""

    def test_doctor_runs_without_error(self):
        result = subprocess.run(
            [sys.executable, os.path.join(ROOT, "aeonrift"), "doctor"],
            capture_output=True, text=True, cwd=ROOT
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("healthy", result.stdout)
        self.assertIn(platform.python_version(), result.stdout)


class TestCLIVersion(unittest.TestCase):
    """Test the version command."""

    def test_version_shows_info(self):
        result = subprocess.run(
            [sys.executable, os.path.join(ROOT, "aeonrift"), "version"],
            capture_output=True, text=True, cwd=ROOT
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("v0.1.0", result.stdout)
        self.assertIn("Ansh Rajore", result.stdout)
        self.assertIn(platform.system(), result.stdout)
        self.assertIn(platform.machine(), result.stdout)


class TestCLIInit(unittest.TestCase):
    """Test the init command."""

    def test_init_creates_directory_structure(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                [sys.executable, os.path.join(ROOT, "aeonrift"), "init", "--dir", tmpdir],
                capture_output=True, text=True, cwd=ROOT
            )
            self.assertEqual(result.returncode, 0)
            self.assertTrue(os.path.isdir(os.path.join(tmpdir, ".aeonrift", "event_store")))
            self.assertTrue(os.path.isdir(os.path.join(tmpdir, ".aeonrift", "checkpoints")))


class TestCLIHelp(unittest.TestCase):
    """Test help output lists all commands."""

    def test_help_lists_all_commands(self):
        result = subprocess.run(
            [sys.executable, os.path.join(ROOT, "aeonrift"), "--help"],
            capture_output=True, text=True, cwd=ROOT
        )
        self.assertEqual(result.returncode, 0)
        for cmd in ["init", "timeline", "recover", "gateway", "export",
                     "replay", "train", "chaos", "benchmark", "diff",
                     "doctor", "version"]:
            self.assertIn(cmd, result.stdout, f"Command '{cmd}' not found in help output")


class TestCLIBenchmark(unittest.TestCase):
    """Test the benchmark command."""

    def test_benchmark_runs(self):
        result = subprocess.run(
            [sys.executable, os.path.join(ROOT, "aeonrift"), "benchmark"],
            capture_output=True, text=True, cwd=ROOT
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("RIFT-BENCH", result.stdout)
        self.assertIn("RE Score", result.stdout)


class TestCLIGateway(unittest.TestCase):
    """Test the gateway command."""

    def test_gateway_starts(self):
        result = subprocess.run(
            [sys.executable, os.path.join(ROOT, "aeonrift"), "gateway", "--port", "9999"],
            capture_output=True, text=True, cwd=ROOT
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("9999", result.stdout)
        self.assertIn("Ingest Engine Initialized", result.stdout)


class TestCLIExportAndReplay(unittest.TestCase):
    """Test export and replay against a live trajectory."""

    def _create_trajectory(self):
        """Create a small test trajectory for export/replay tests."""
        from aeonrift.runtime.interceptor import AeonriftRuntime
        from aeonrift.core.events import SideEffectType, ReversibilityType
        import tempfile
        tmpdir = tempfile.mkdtemp()
        store_path = os.path.join(tmpdir, "event_store")
        os.makedirs(store_path, exist_ok=True)
        rt = AeonriftRuntime(agent_id="test_agent", execution_id="exec_cli_test", storage_dir=store_path)
        rt.intercept_tool("fetch_data", lambda **kw: {"result": "ok"}, {}, SideEffectType.READ_ONLY, ReversibilityType.REVERSIBLE)
        rt.intercept_tool("write_db", lambda **kw: {"written": True}, {}, SideEffectType.MUTATING_REVERSIBLE, ReversibilityType.REVERSIBLE)
        return tmpdir, store_path

    def test_export_json(self):
        tmpdir, store_path = self._create_trajectory()
        result = subprocess.run(
            [sys.executable, os.path.join(ROOT, "aeonrift"), "export", "exec_cli_test",
             "--format", "json", "--storage-dir", store_path],
            capture_output=True, text=True, cwd=ROOT
        )
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertIn("event_type", data[0])

    def test_export_dot(self):
        tmpdir, store_path = self._create_trajectory()
        result = subprocess.run(
            [sys.executable, os.path.join(ROOT, "aeonrift"), "export", "exec_cli_test",
             "--format", "dot", "--storage-dir", store_path],
            capture_output=True, text=True, cwd=ROOT
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("digraph CausalGraph", result.stdout)

    def test_export_to_file(self):
        import tempfile
        tmpdir, store_path = self._create_trajectory()
        out_file = os.path.join(tmpdir, "export_output.json")
        result = subprocess.run(
            [sys.executable, os.path.join(ROOT, "aeonrift"), "export", "exec_cli_test",
             "--format", "json", "--output", out_file, "--storage-dir", store_path],
            capture_output=True, text=True, cwd=ROOT
        )
        self.assertEqual(result.returncode, 0)
        self.assertTrue(os.path.isfile(out_file))
        with open(out_file) as f:
            data = json.load(f)
        self.assertIsInstance(data, list)

    def test_replay_runs(self):
        tmpdir, store_path = self._create_trajectory()
        result = subprocess.run(
            [sys.executable, os.path.join(ROOT, "aeonrift"), "replay", "exec_cli_test",
             "--storage-dir", store_path],
            capture_output=True, text=True, cwd=ROOT
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Replaying Step", result.stdout)
        self.assertIn("Replay completed", result.stdout)


class TestCLICrossPlatformPaths(unittest.TestCase):
    """Test that path normalization works across platforms."""

    def test_relative_path_resolved(self):
        from aeonrift.cli.utils import normalize_path
        p = normalize_path("./foo/bar/../baz")
        self.assertNotIn("..", p)
        self.assertTrue(os.path.isabs(p))

    def test_path_separator_native(self):
        from aeonrift.cli.utils import normalize_path
        p = normalize_path("a/b/c")
        self.assertEqual(p, os.path.normpath(os.path.abspath("a/b/c")))


if __name__ == "__main__":
    unittest.main()
