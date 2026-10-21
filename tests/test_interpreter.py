
"""Tests for the AXIOM v0.1 interpreter."""

import unittest

from axiom.interpreter import AxiomError, run_source


class TestAxiomInterpreter(unittest.TestCase):
    def test_assignment_and_output(self):
        result = run_source(
            "let x = 2\n"
            "let y = x + 3\n"
            "show y\n"
        )
        self.assertEqual(result, [5])

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


if __name__ == "__main__":
    unittest.main()
