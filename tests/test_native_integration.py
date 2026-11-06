"""Numerical parity checks against the compiled C++ LIF step kernel.

These tests are skipped when AXIOM_CPP_LIBRARY is not configured. The C++
workflow builds the shared library and runs them with the native path set.
"""

import unittest

from axiom.native import native_available, native_lif_step
from axiom.solvers import step_euler, step_rk2, step_rk4


@unittest.skipUnless(native_available(), "AXIOM C++ shared library is not configured")
class TestNativeNumericalParity(unittest.TestCase):
    def test_cpp_steps_match_python_reference(self):
        cases = [
            (-65.0, 0.0, 0.0, 0.0, 0.1, 20.0, -65.0, 10.0),
            (-62.5, 1.2, 1.4, 1.1, 0.05, 15.0, -67.0, 8.0),
            (-48.0, 2.0, 0.5, 1.0, 0.2, 30.0, -70.0, 12.0),
        ]
        references = {
            "euler": lambda v, a, b, c, dt, tau, rest, resistance:
                step_euler(v, a, dt, tau, rest, resistance),
            "rk2": lambda v, a, b, c, dt, tau, rest, resistance:
                step_rk2(v, a, b, dt, tau, rest, resistance),
            "rk4": lambda v, a, b, c, dt, tau, rest, resistance:
                step_rk4(v, a, b, c, dt, tau, rest, resistance),
        }

        for solver, reference in references.items():
            for case in cases:
                with self.subTest(solver=solver, case=case):
                    expected = reference(*case)
                    actual = native_lif_step(solver, *case)
                    self.assertAlmostEqual(actual, expected, places=12)


if __name__ == "__main__":
    unittest.main()
