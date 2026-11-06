"""Tests for optional sub-step interpolation of LIF spike timestamps."""

import unittest

from axiom.neuroscience import LIFParameters, simulate_lif
from axiom.units import MS, MV, NA, MOHM, Quantity


def parameters():
    return LIFParameters(
        membrane_time_constant=Quantity(10.0, MS),
        resting_voltage=Quantity(-65.0, MV),
        spike_threshold=Quantity(-60.0, MV),
        reset_voltage=Quantity(-65.0, MV),
        input_resistance=Quantity(10.0, MOHM),
        initial_voltage=Quantity(-65.0, MV),
        refractory_period=Quantity(0.0, MS),
    )


class TestSpikeTimeInterpolation(unittest.TestCase):
    def simulate(self, **kwargs):
        return simulate_lif(
            parameters(),
            Quantity(4.0, NA),
            Quantity(2.0, MS),
            Quantity(2.0, MS),
            solver="euler",
            **kwargs,
        )

    def test_default_keeps_end_of_step_spike_time(self):
        result = self.simulate()
        self.assertEqual(result.spike_times_ms, (2.0,))
        self.assertEqual(result.metadata["spike_time_method"], "grid")

    def test_linear_method_interpolates_crossing_within_step(self):
        # Euler gives -61 mV at 1 ms and -57 mV at 2 ms only if split;
        # over this 2 ms step it advances from -65 to -57 mV. The -60 mV
        # threshold is therefore crossed 5/8 of the way through the step.
        result = self.simulate(spike_time_method="linear")
        self.assertAlmostEqual(result.spike_times_ms[0], 1.25)
        self.assertEqual(result.metadata["spike_time_method"], "linear")

    def test_interpolation_does_not_change_voltage_grid_or_reset(self):
        grid = self.simulate()
        linear = self.simulate(spike_time_method="linear")
        self.assertEqual(grid.times_ms, linear.times_ms)
        self.assertEqual(grid.membrane_voltage_mV, linear.membrane_voltage_mV)
        self.assertEqual(grid.injected_current_nA, linear.injected_current_nA)

    def test_invalid_spike_time_method_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "spike_time_method"):
            self.simulate(spike_time_method="cubic")


if __name__ == "__main__":
    unittest.main()
