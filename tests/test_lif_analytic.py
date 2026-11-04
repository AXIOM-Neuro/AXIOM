"""Deterministic checks of the LIF implementation against its closed-form solution.

For a constant injected current I the subthreshold dynamics

    tau dV/dt = (E_L - V) + R I

have the exact solution

    V(t) = V_inf + (V_0 - V_inf) exp(-t / tau),      V_inf = E_L + R I

so if V_inf > theta the first threshold crossing occurs at

    t* = tau * ln( (V_0 - V_inf) / (theta - V_inf) ).

That closed form is the independent reference used below. It validates the
integrator, the unit handling and the spike-time bookkeeping together.

Two implementation limits are asserted explicitly rather than glossed over:

1. Spike times are quantised to the integration step, because the threshold test
   happens after the step. The recorded spike is therefore the first sample at or
   after t*, not t* itself.
2. The recorded membrane voltage at a spike is the reset value; the pre-reset
   peak is not stored in the trace. The trace never shows a value >= threshold.

This is a single-compartment point neuron model. Nothing here supports a claim of
biological realism.
"""

import math
import unittest

from axiom.neuroscience import LIFParameters, simulate_lif
from axiom.units import MS, MV, NA, MOHM, Quantity


def closed_form_spike_time_ms(v0, v_inf, theta, tau):
    """First threshold-crossing time from the exact solution, or None."""
    if v_inf <= theta:
        return None
    if v0 >= theta:
        return 0.0
    return tau * math.log((v0 - v_inf) / (theta - v_inf))


def make_params(**overrides):
    base = dict(
        membrane_time_constant=Quantity(20, MS),
        resting_voltage=Quantity(-65, MV),
        spike_threshold=Quantity(-50, MV),
        reset_voltage=Quantity(-65, MV),
        input_resistance=Quantity(10, MOHM),
        initial_voltage=Quantity(-65, MV),
        refractory_period=Quantity(0, MS),
    )
    base.update(overrides)
    return LIFParameters(**base)


class TestLifAgainstClosedForm(unittest.TestCase):
    def test_first_spike_time_matches_closed_form(self):
        # V_inf = -65 + 10 * 2 = -45 mV, so t* = 20 ln(20/5) = 27.7259 ms
        expected = closed_form_spike_time_ms(-65.0, -45.0, -50.0, 20.0)
        self.assertAlmostEqual(expected, 27.725887, places=5)

        for dt in (0.1, 0.05, 0.01):
            with self.subTest(dt=dt):
                result = simulate_lif(
                    make_params(), Quantity(2, NA), Quantity(60, MS), Quantity(dt, MS),
                    solver="rk4",
                )
                first = result.spike_times_ms[0]
                # Post-step detection quantises the event to the sample grid.
                self.assertLessEqual(abs(first - expected), dt + 1e-9)
                # Exactly on the sample grid (compare in units of dt; a raw
                # float modulo is not a valid equality test here).
                self.assertAlmostEqual(first / dt, round(first / dt), places=9)

    def test_spike_time_error_decreases_with_smaller_step(self):
        expected = closed_form_spike_time_ms(-65.0, -45.0, -50.0, 20.0)
        errors = []
        for dt in (0.5, 0.1, 0.01):
            result = simulate_lif(
                make_params(), Quantity(2, NA), Quantity(40, MS), Quantity(dt, MS),
                solver="euler",
            )
            errors.append(abs(result.spike_times_ms[0] - expected))
        self.assertTrue(errors[0] >= errors[1] >= errors[2], errors)

    def test_inter_spike_interval_is_period_plus_refractory(self):
        period = closed_form_spike_time_ms(-65.0, -45.0, -50.0, 20.0)
        refract = 2.0
        result = simulate_lif(
            make_params(refractory_period=Quantity(refract, MS)),
            Quantity(2, NA), Quantity(120, MS), Quantity(0.01, MS), solver="rk4",
        )
        self.assertGreaterEqual(len(result.spike_times_ms), 3)
        isi = [
            b - a
            for a, b in zip(result.spike_times_ms, result.spike_times_ms[1:])
        ]
        for interval in isi:
            self.assertLessEqual(abs(interval - (period + refract)), 0.02)

    def test_step_current_onset_offsets_the_spike(self):
        # Pulse starts at 10 ms, so the first spike is at 10 + t*.
        expected = 10.0 + closed_form_spike_time_ms(-65.0, -45.0, -50.0, 20.0)
        from axiom.stimuli import StepCurrent

        stim = StepCurrent(
            amplitude=Quantity(2, NA),
            start_time=Quantity(10, MS),
            duration=Quantity(80, MS),
        )
        result = simulate_lif(
            make_params(), stim, Quantity(100, MS), Quantity(0.01, MS), solver="rk4",
        )
        self.assertLessEqual(abs(result.spike_times_ms[0] - expected), 0.02)

    def test_no_spike_when_steady_state_is_subthreshold(self):
        # R I = 10 * 1 = 10 mV -> V_inf = -55 mV, below the -50 mV threshold.
        result = simulate_lif(
            make_params(), Quantity(1, NA), Quantity(200, MS), Quantity(0.05, MS),
            solver="rk4",
        )
        self.assertEqual(result.spike_times_ms, ())
        self.assertLess(max(result.membrane_voltage_mV), -50.0)
        # ... and the trace approaches -55 mV without crossing it.
        self.assertAlmostEqual(result.membrane_voltage_mV[-1], -55.0, delta=0.5)

    def test_recorded_trace_never_shows_a_suprathreshold_sample(self):
        result = simulate_lif(
            make_params(), Quantity(2, NA), Quantity(100, MS), Quantity(0.1, MS)
        )
        self.assertTrue(result.spike_times_ms)
        self.assertLess(max(result.membrane_voltage_mV), -50.0)
        # Documented consequence: the pre-reset peak is not stored.
        self.assertNotIn(-50.0, result.membrane_voltage_mV)

    def test_refractory_holds_voltage_at_reset(self):
        params = make_params(
            spike_threshold=Quantity(-50, MV),
            reset_voltage=Quantity(-70, MV),
            initial_voltage=Quantity(-50, MV),
            refractory_period=Quantity(5, MS),
        )
        result = simulate_lif(
            params, Quantity(2, NA), Quantity(8, MS), Quantity(0.1, MS)
        )
        spike = result.spike_times_ms[0]
        held = [
            v for t, v in zip(result.times_ms, result.membrane_voltage_mV)
            if spike < t <= spike + 5.0
        ]
        self.assertTrue(held)
        self.assertTrue(all(v == -70.0 for v in held))

    def test_solver_agreement_on_a_subthreshold_trajectory(self):
        # Below threshold throughout: all three solvers must agree closely.
        results = {
            solver: simulate_lif(
                make_params(), Quantity(0.5, NA), Quantity(60, MS), Quantity(0.01, MS),
                solver=solver,
            )
            for solver in ("euler", "rk2", "rk4")
        }
        for solver, result in results.items():
            with self.subTest(solver=solver):
                self.assertEqual(result.spike_times_ms, ())
        rk4 = results["rk4"].membrane_voltage_mV[-1]
        for solver in ("euler", "rk2"):
            self.assertAlmostEqual(results[solver].membrane_voltage_mV[-1], rk4, delta=0.02)


class TestLifInputValidation(unittest.TestCase):
    def test_wrong_dimension_is_rejected(self):
        with self.assertRaises(ValueError):
            simulate_lif(
                make_params(), Quantity(2, NA), Quantity(100, MV), Quantity(0.1, MS)
            )

    def test_duration_must_be_a_multiple_of_step(self):
        with self.assertRaises(ValueError):
            simulate_lif(
                make_params(), Quantity(2, NA), Quantity(10, MS), Quantity(0.3, MS)
            )

    def test_nonpositive_step_is_rejected(self):
        with self.assertRaises(ValueError):
            simulate_lif(
                make_params(), Quantity(2, NA), Quantity(10, MS), Quantity(0, MS)
            )

    def test_unknown_solver_is_rejected(self):
        with self.assertRaises(ValueError):
            simulate_lif(
                make_params(), Quantity(2, NA), Quantity(10, MS), Quantity(0.1, MS),
                solver="adams",
            )

    def test_threshold_must_exceed_reset(self):
        with self.assertRaises(ValueError):
            make_params(
                spike_threshold=Quantity(-65, MV), reset_voltage=Quantity(-65, MV)
            )


if __name__ == "__main__":
    unittest.main()
