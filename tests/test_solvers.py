"""Tests for AXIOM numerical solvers and scientific accuracy checks."""

import math
import unittest
from axiom.neuroscience import LIFParameters, simulate_lif
from axiom.units import MS, MV, NA, MOHM, Quantity


class TestAxiomSolversAndScience(unittest.TestCase):
    def setUp(self):
        self.params = LIFParameters(
            membrane_time_constant=Quantity(20, MS),
            resting_voltage=Quantity(-65, MV),
            spike_threshold=Quantity(0, MV),
            reset_voltage=Quantity(-65, MV),
            input_resistance=Quantity(10, MOHM),
            initial_voltage=Quantity(-65, MV),
            refractory_period=Quantity(0, MS),
        )

    def test_analytical_subthreshold_agreement(self):
        """Compare subthreshold numerical integration against analytical solution.

        V(t) = V_steady + (V_0 - V_steady) * exp(-t / tau_m)
        V_steady = E_rest + R_m * I = -65 + 10 * 2 = -45 mV
        """
        I_inj = Quantity(2, NA)
        duration = Quantity(20, MS)
        dt = Quantity(0.01, MS)

        result_euler = simulate_lif(self.params, I_inj, duration, dt, solver="euler")
        result_rk2 = simulate_lif(self.params, I_inj, duration, dt, solver="rk2")
        result_rk4 = simulate_lif(self.params, I_inj, duration, dt, solver="rk4")

        # Check final voltage against analytical solution at t = 20 ms
        v_steady = -45.0
        v_0 = -65.0
        v_analytical = v_steady + (v_0 - v_steady) * math.exp(-20.0 / 20.0)  # -45 + (-20)*e^-1 ~ -52.357588

        v_final_euler = result_euler.membrane_voltage_mV[-1]
        v_final_rk2 = result_rk2.membrane_voltage_mV[-1]
        v_final_rk4 = result_rk4.membrane_voltage_mV[-1]

        # RK4 should agree with analytical solution to high precision
        self.assertAlmostEqual(v_final_rk4, v_analytical, delta=1e-4)
        # Higher order solvers should be more accurate than Euler
        self.assertLess(abs(v_final_rk4 - v_analytical), abs(v_final_euler - v_analytical))

    def test_refractory_period_holding(self):
        """Verify that voltage stays at reset during refractory period after a spike."""
        params_ref = LIFParameters(
            membrane_time_constant=Quantity(10, MS),
            resting_voltage=Quantity(-65, MV),
            spike_threshold=Quantity(-50, MV),
            reset_voltage=Quantity(-70, MV),
            input_resistance=Quantity(10, MOHM),
            initial_voltage=Quantity(-50, MV),  # Triggers immediately
            refractory_period=Quantity(5, MS),
        )

        result = simulate_lif(
            parameters=params_ref,
            injected_current=Quantity(2, NA),
            duration=Quantity(10, MS),
            time_step=Quantity(0.1, MS),
        )

        # First step triggers spike
        self.assertEqual(len(result.spike_times_ms), 1)
        spike_t = result.spike_times_ms[0]
        self.assertEqual(spike_t, 0.1)

        # During refractory period (t from 0.1 to 5.1 ms), voltage must equal reset (-70 mV)
        for t, v in zip(result.times_ms, result.membrane_voltage_mV):
            if 0.1 < t <= 5.1:
                self.assertEqual(v, -70.0)

    def test_unstable_simulation_raises_arithmetic_error(self):
        """Check that non-finite membrane voltages raise ArithmeticError."""
        bad_dt = Quantity(1e300, MS)
        with self.assertRaises(ArithmeticError):
            simulate_lif(self.params, Quantity(-1e300, NA), Quantity(1e300, MS), bad_dt, solver="euler")


if __name__ == "__main__":
    unittest.main()
