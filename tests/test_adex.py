"""Tests for AXIOM Adaptive Exponential Integrate-and-Fire (AdEx) neuron model."""

import tempfile
import unittest
from pathlib import Path

from axiom.interpreter import run_source
from axiom.neuroscience import AdExParameters, simulate_adex
from axiom.stimuli import ConstantCurrent, StepCurrent
from axiom.units import MS, MV, NA, NF, NS, PF, US, Quantity


class TestAxiomAdExModel(unittest.TestCase):
    def setUp(self):
        self.params = AdExParameters(
            capacitance=Quantity(200, PF),  # 0.2 nF
            leak_conductance=Quantity(10, NS),  # 10 nS = 0.01 uS
            resting_voltage=Quantity(-70, MV),
            slope_factor=Quantity(2, MV),
            threshold_voltage=Quantity(-50, MV),
            peak_voltage=Quantity(0, MV),
            reset_voltage=Quantity(-58, MV),
            adaptation_coupling=Quantity(2, NS),  # 2 nS
            spike_triggered_adaptation=Quantity(0.01, NA),
            adaptation_time_constant=Quantity(30, MS),
            initial_voltage=Quantity(-70, MV),
            initial_adaptation=Quantity(0, NA),
            refractory_period=Quantity(0, MS),
        )

    def test_adex_simulation_runs(self):
        stim = StepCurrent(amplitude=Quantity(0.5, NA), start_time=Quantity(10, MS), duration=Quantity(80, MS))
        res = simulate_adex(self.params, stim, duration=Quantity(100, MS), time_step=Quantity(0.1, MS), solver="rk4")

        self.assertEqual(len(res.times_ms), 1001)
        self.assertEqual(len(res.membrane_voltage_mV), 1001)
        self.assertEqual(len(res.adaptation_current_nA), 1001)
        self.assertGreater(len(res.spike_times_ms), 0)

    def test_adex_result_to_dict_and_csv(self):
        stim = ConstantCurrent(Quantity(0.2, NA))
        res = simulate_adex(self.params, stim, duration=Quantity(20, MS), time_step=Quantity(0.1, MS))

        d = res.to_dict()
        self.assertIn("adaptation_current_nA", d)
        self.assertEqual(len(d["adaptation_current_nA"]), 201)

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_file = Path(tmpdir) / "adex_out.csv"
            res.save_csv(csv_file)
            self.assertTrue(csv_file.exists())
            content = csv_file.read_text(encoding="utf-8")
            self.assertIn("adaptation_current_nA", content)

    def test_adex_dsl_interpreter_script(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "adex_dsl.csv"
            script = (
                'adex_neuron "AdaptNeuron":\n'
                '    capacitance = 200 pF\n'
                '    resting_voltage = -70 mV\n'
                '    threshold_voltage = -50 mV\n'
                '    reset_voltage = -58 mV\n'
                '\n'
                'inject step current 0.5 nA from 10 ms for 80 ms\n'
                'simulate for 50 ms using time_step 0.1 ms using solver rk4\n'
                'show spike_count\n'
                f'save results to "{csv_path}"\n'
            )
            out = run_source(script)
            self.assertIsInstance(out[0], int)
            self.assertTrue(csv_path.exists())


if __name__ == "__main__":
    unittest.main()
