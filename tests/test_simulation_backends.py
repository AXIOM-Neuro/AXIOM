"""Backend-selection tests for the LIF simulator.

The native call is mocked here so these tests exercise Python orchestration,
spike/reset/refractory handling, and API defaults without requiring a compiler.
The compiled kernel has its own C++ tests under cpp/tests.
"""

import unittest
from unittest.mock import patch

from axiom.neuroscience import LIFParameters, simulate_lif
from axiom.solvers import step_euler, step_rk2, step_rk4
from axiom.units import MS, MV, NA, MOHM, Quantity


def parameters():
    return LIFParameters(
        membrane_time_constant=Quantity(10.0, MS),
        resting_voltage=Quantity(-65.0, MV),
        spike_threshold=Quantity(-50.0, MV),
        reset_voltage=Quantity(-65.0, MV),
        input_resistance=Quantity(10.0, MOHM),
        initial_voltage=Quantity(-65.0, MV),
        refractory_period=Quantity(2.0, MS),
    )


def reference_native_step(
    solver, voltage, current_now, current_mid, current_next,
    dt, tau, rest, resistance,
):
    if solver == "euler":
        return step_euler(voltage, current_now, dt, tau, rest, resistance)
    if solver == "rk2":
        return step_rk2(
            voltage, current_now, current_mid, dt, tau, rest, resistance
        )
    return step_rk4(
        voltage, current_now, current_mid, current_next,
        dt, tau, rest, resistance,
    )


class TestSimulationBackendSelection(unittest.TestCase):
    def test_python_backend_remains_the_default(self):
        result = simulate_lif(
            parameters(), Quantity(2.0, NA), Quantity(5.0, MS), Quantity(1.0, MS)
        )
        self.assertEqual(result.metadata["backend"], "python")

    def test_cpp_backend_routes_each_solver_to_native_kernel(self):
        for solver in ("euler", "rk2", "rk4"):
            with self.subTest(solver=solver):
                with patch(
                    "axiom.native.native_lif_step",
                    side_effect=reference_native_step,
                ) as native_step:
                    result = simulate_lif(
                        parameters(),
                        Quantity(4.0, NA),
                        Quantity(5.0, MS),
                        Quantity(1.0, MS),
                        solver=solver,
                        backend="cpp",
                    )

                self.assertEqual(result.metadata["backend"], "cpp")
                self.assertEqual(result.metadata["solver"], solver)
                self.assertEqual(len(result.times_ms), 6)
                self.assertEqual(len(result.membrane_voltage_mV), 6)
                self.assertEqual(len(result.spike_times_ms), 1)
                self.assertEqual(native_step.call_count, 5)

    def test_invalid_backend_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "backend must be"):
            simulate_lif(
                parameters(),
                Quantity(1.0, NA),
                Quantity(1.0, MS),
                Quantity(1.0, MS),
                backend="gpu",
            )


if __name__ == "__main__":
    unittest.main()
