"""Tests for the AXIOM language interpreter and runtime."""

import tempfile
import unittest
from pathlib import Path

from axiom.interpreter import AxiomError, run_source


class TestAxiomInterpreter(unittest.TestCase):
    def test_assignment_and_output(self):
        result = run_source(
            "let x = 2\n"
            "let y = x + 3\n"
            "show y\n"
        )
        self.assertEqual(result, [5])

    def test_unit_expression_evaluation(self):
        result = run_source(
            "let tau = 20 ms\n"
            "let dur = 100 ms\n"
            "show dur / tau\n"
        )
        self.assertEqual(result, [5.0])

    def test_operator_precedence(self):
        result = run_source("show 2 + 3 * 4\n")
        self.assertEqual(result, [14])

    def test_parentheses(self):
        result = run_source("show (2 + 3) * 4\n")
        self.assertEqual(result, [20])

    def test_comments_and_blank_lines(self):
        result = run_source(
            "# A comment\n"
            "\n"
            "let x = 7 # inline comment\n"
            "show x\n"
        )
        self.assertEqual(result, [7])

    def test_neuron_block_and_simulation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "results.csv"
            source = (
                'neuron "TestNeuron":\n'
                '    membrane_time = 20 ms\n'
                '    resting_voltage = -65 mV\n'
                '    spike_threshold = -50 mV\n'
                '    reset_voltage = -65 mV\n'
                '    input_resistance = 10 MOhm\n'
                '\n'
                'inject current 2 nA\n'
                'simulate for 100 ms using time_step 0.1 ms\n'
                'show spike_count\n'
                f'save results to "{csv_path}"\n'
            )
            result = run_source(source)
            self.assertEqual(result, [3])
            self.assertTrue(csv_path.exists())

    def test_unknown_variable_reports_line(self):
        with self.assertRaisesRegex(
            AxiomError, r"Line 2: Unknown variable: missing"
        ):
            run_source("let x = 1\nshow missing\n")

    def test_division_by_zero(self):
        with self.assertRaisesRegex(AxiomError, "Division by zero"):
            run_source("show 10 / 0\n")

    def test_unknown_statement(self):
        with self.assertRaisesRegex(AxiomError, "Unknown statement"):
            run_source("plot voltage\n")

    def test_untrusted_python_syntax_is_rejected(self):
        with self.assertRaises(AxiomError):
            run_source("show __import__('os')\n")

    def test_unary_negative(self):
        result = run_source("show -5\n")
        self.assertEqual(result, [-5])

    def test_pulse_train_injection(self):
        source = (
            'neuron "PulseNeuron":\n'
            '    membrane_time = 20 ms\n'
            '    resting_voltage = -65 mV\n'
            '    spike_threshold = -50 mV\n'
            '    reset_voltage = -65 mV\n'
            '    input_resistance = 10 MOhm\n'
            '\n'
            'inject pulse train current 2 nA starting at 0 ms pulse_duration 1 ms frequency 10 Hz pulses 5\n'
            'simulate for 500 ms using time_step 0.1 ms using solver rk4\n'
            'show spike_count\n'
        )
        result = run_source(source)
        self.assertIsInstance(result[0], int)


if __name__ == "__main__":
    unittest.main()
