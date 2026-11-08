"""End-to-end parity tests for AXIOM's Python and optional C++ LIF backends.

These tests exercise the shared simulation orchestration with the real compiled
native step kernel. They deliberately include time-varying stimuli and
non-grid-aligned stimulus edges, not only isolated constant-current steps.
"""

import unittest

from axiom.native import native_available
from axiom.neuroscience import LIFParameters, simulate_lif
from axiom.stimuli import CombinedStimulus, PulseTrainCurrent, StepCurrent
from axiom.units import HZ, MS, MV, NA, MOHM, Quantity


def make_parameters():
    return LIFParameters(
        membrane_time_constant=Quantity(20.0, MS),
        resting_voltage=Quantity(-65.0, MV),
        spike_threshold=Quantity(-50.0, MV),
        reset_voltage=Quantity(-65.0, MV),
        input_resistance=Quantity(10.0, MOHM),
        initial_voltage=Quantity(-65.0, MV),
        refractory_period=Quantity(2.0, MS),
    )


def assert_sequences_close(test_case, left, right, *, places=12):
    test_case.assertEqual(len(left), len(right))
    for index, (a, b) in enumerate(zip(left, right)):
        with test_case.subTest(index=index):
            test_case.assertAlmostEqual(a, b, places=places)


@unittest.skipUnless(
    native_available(),
    "AXIOM C++ shared library is not configured",
)
class TestBackendTrajectoryParity(unittest.TestCase):
    def compare_backends(self, stimulus, *, solver, spike_time_method, duration, dt):
        parameters = make_parameters()
        python_result = simulate_lif(
            parameters,
            stimulus,
            Quantity(duration, MS),
            Quantity(dt, MS),
            solver=solver,
            backend="python",
            spike_time_method=spike_time_method,
        )
        cpp_result = simulate_lif(
            parameters,
            stimulus,
            Quantity(duration, MS),
            Quantity(dt, MS),
            solver=solver,
            backend="cpp",
            spike_time_method=spike_time_method,
        )

        self.assertEqual(python_result.metadata["backend"], "python")
        self.assertEqual(cpp_result.metadata["backend"], "cpp")
        self.assertEqual(
            {key: value for key, value in python_result.metadata.items() if key != "backend"},
            {key: value for key, value in cpp_result.metadata.items() if key != "backend"},
        )
        assert_sequences_close(self, python_result.times_ms, cpp_result.times_ms)
        assert_sequences_close(
            self, python_result.membrane_voltage_mV, cpp_result.membrane_voltage_mV
        )
        assert_sequences_close(
            self, python_result.injected_current_nA, cpp_result.injected_current_nA
        )
        assert_sequences_close(
            self, python_result.spike_times_ms, cpp_result.spike_times_ms
        )
        return python_result

    def test_step_current_with_non_grid_aligned_edges(self):
        stimulus = StepCurrent(
            amplitude=Quantity(2.2, NA),
            start_time=Quantity(3.25, MS),
            duration=Quantity(55.5, MS),
        )
        for solver in ("euler", "rk2", "rk4"):
            with self.subTest(solver=solver):
                result = self.compare_backends(
                    stimulus,
                    solver=solver,
                    spike_time_method="grid",
                    duration=80.0,
                    dt=0.5,
                )
                self.assertGreaterEqual(len(result.spike_times_ms), 2)

    def test_pulse_train_current_with_all_solver_methods(self):
        stimulus = PulseTrainCurrent(
            amplitude=Quantity(2.5, NA),
            start_time=Quantity(2.25, MS),
            pulse_duration=Quantity(3.25, MS),
            frequency=Quantity(100.0, HZ),
            num_pulses=5,
        )
        for solver in ("euler", "rk2", "rk4"):
            with self.subTest(solver=solver):
                self.compare_backends(
                    stimulus,
                    solver=solver,
                    spike_time_method="linear",
                    duration=55.0,
                    dt=0.5,
                )

    def test_combined_stimuli_and_refractory_period(self):
        stimulus = CombinedStimulus(
            [
                StepCurrent(
                    amplitude=Quantity(1.7, NA),
                    start_time=Quantity(1.25, MS),
                    duration=Quantity(65.5, MS),
                ),
                PulseTrainCurrent(
                    amplitude=Quantity(0.8, NA),
                    start_time=Quantity(4.25, MS),
                    pulse_duration=Quantity(2.25, MS),
                    frequency=Quantity(125.0, HZ),
                    num_pulses=6,
                ),
            ]
        )
        for solver in ("euler", "rk2", "rk4"):
            with self.subTest(solver=solver):
                result = self.compare_backends(
                    stimulus,
                    solver=solver,
                    spike_time_method="linear",
                    duration=75.0,
                    dt=0.25,
                )
                self.assertGreaterEqual(len(result.spike_times_ms), 1)

    def test_grid_and_linear_timestamp_modes_preserve_backend_parity(self):
        stimulus = StepCurrent(
            amplitude=Quantity(2.2, NA),
            start_time=Quantity(0.0, MS),
            duration=Quantity(60.0, MS),
        )
        for method in ("grid", "linear"):
            with self.subTest(spike_time_method=method):
                self.compare_backends(
                    stimulus,
                    solver="rk4",
                    spike_time_method=method,
                    duration=65.0,
                    dt=0.5,
                )


if __name__ == "__main__":
    unittest.main()
