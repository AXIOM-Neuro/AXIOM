"""Tests for AXIOM command line interface."""

import io
import sys
import tempfile
import unittest
from pathlib import Path

from axiom.__main__ import main


class TestAxiomCLI(unittest.TestCase):
    def test_version_flag(self):
        with self.assertRaises(SystemExit) as cm:
            main(["--version"])
        self.assertEqual(cm.exception.code, 0)

    def test_check_command(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.ax"
            file_path.write_text("let x = 10 ms\nshow x\n", encoding="utf-8")

            stdout_capture = io.StringIO()
            sys.stdout = stdout_capture
            try:
                exit_code = main(["check", str(file_path)])
                self.assertEqual(exit_code, 0)
                self.assertIn("AXIOM check passed", stdout_capture.getvalue())
            finally:
                sys.stdout = sys.__stdout__

    def test_inspect_command(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_neuron.ax"
            file_path.write_text(
                'neuron "MyNeuron":\n'
                '    membrane_time = 20 ms\n'
                'inject current 2 nA\n'
                'simulate for 10 ms\n',
                encoding="utf-8",
            )

            stdout_capture = io.StringIO()
            sys.stdout = stdout_capture
            try:
                exit_code = main(["inspect", str(file_path)])
                self.assertEqual(exit_code, 0)
                output = stdout_capture.getvalue()
                self.assertIn("Defined Neurons: ['MyNeuron']", output)
                self.assertIn("Spike Count", output)
            finally:
                sys.stdout = sys.__stdout__

    def test_missing_file_returns_error_code(self):
        stderr_capture = io.StringIO()
        sys.stderr = stderr_capture
        try:
            exit_code = main(["run", "nonexistent_file.ax"])
            self.assertEqual(exit_code, 1)
            self.assertIn("File not found", stderr_capture.getvalue())
        finally:
            sys.stderr = sys.__stderr__


if __name__ == "__main__":
    unittest.main()
