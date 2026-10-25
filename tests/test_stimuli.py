"""Tests for AXIOM stimulation patterns."""

import unittest
from axiom.stimuli import ConstantCurrent, StepCurrent, PulseTrainCurrent, CombinedStimulus
from axiom.units import MS, NA, HZ, Quantity


class TestAxiomStimuli(unittest.TestCase):
    def test_constant_current(self):
        stim = ConstantCurrent(Quantity(2.5, NA))
        self.assertEqual(stim.current_at(Quantity(0, MS)), Quantity(2.5, NA))
        self.assertEqual(stim.current_at(Quantity(100, MS)), Quantity(2.5, NA))

    def test_step_current(self):
        stim = StepCurrent(
            amplitude=Quantity(5, NA),
            start_time=Quantity(10, MS),
            duration=Quantity(20, MS),
        )
        self.assertEqual(stim.current_at(Quantity(5, MS)), Quantity(0, NA))
        self.assertEqual(stim.current_at(Quantity(10, MS)), Quantity(5, NA))
        self.assertEqual(stim.current_at(Quantity(25, MS)), Quantity(5, NA))
        self.assertEqual(stim.current_at(Quantity(30, MS)), Quantity(0, NA))

    def test_pulse_train_current(self):
        stim = PulseTrainCurrent(
            amplitude=Quantity(3, NA),
            start_time=Quantity(10, MS),
            pulse_duration=Quantity(5, MS),
            frequency=Quantity(20, HZ),  # Period = 50 ms
            num_pulses=2,
        )
        # Before start
        self.assertEqual(stim.current_at(Quantity(5, MS)), Quantity(0, NA))
        # Pulse 1: 10ms to 15ms
        self.assertEqual(stim.current_at(Quantity(10, MS)), Quantity(3, NA))
        self.assertEqual(stim.current_at(Quantity(12, MS)), Quantity(3, NA))
        self.assertEqual(stim.current_at(Quantity(15, MS)), Quantity(0, NA))
        self.assertEqual(stim.current_at(Quantity(20, MS)), Quantity(0, NA))
        # Pulse 2: 60ms to 65ms
        self.assertEqual(stim.current_at(Quantity(60, MS)), Quantity(3, NA))
        self.assertEqual(stim.current_at(Quantity(62, MS)), Quantity(3, NA))
        self.assertEqual(stim.current_at(Quantity(65, MS)), Quantity(0, NA))
        # After pulse train
        self.assertEqual(stim.current_at(Quantity(120, MS)), Quantity(0, NA))

    def test_pulse_train_validation(self):
        # Negative start time
        with self.assertRaises(ValueError):
            PulseTrainCurrent(Quantity(1, NA), Quantity(-1, MS), Quantity(1, MS), Quantity(10, HZ), 2)
        # Zero pulse duration
        with self.assertRaises(ValueError):
            PulseTrainCurrent(Quantity(1, NA), Quantity(0, MS), Quantity(0, MS), Quantity(10, HZ), 2)
        # Zero frequency
        with self.assertRaises(ValueError):
            PulseTrainCurrent(Quantity(1, NA), Quantity(0, MS), Quantity(1, MS), Quantity(0, HZ), 2)
        # Invalid num_pulses
        with self.assertRaises(ValueError):
            PulseTrainCurrent(Quantity(1, NA), Quantity(0, MS), Quantity(1, MS), Quantity(10, HZ), 0)
        # Pulse duration exceeds period (period = 100ms for 10Hz, dur = 150ms)
        with self.assertRaises(ValueError):
            PulseTrainCurrent(Quantity(1, NA), Quantity(0, MS), Quantity(150, MS), Quantity(10, HZ), 2)

    def test_combined_stimulus(self):
        s1 = StepCurrent(Quantity(2, NA), start_time=Quantity(0, MS), duration=Quantity(50, MS))
        s2 = StepCurrent(Quantity(3, NA), start_time=Quantity(10, MS), duration=Quantity(50, MS))
        combined = CombinedStimulus([s1, s2])

        self.assertEqual(combined.current_at(Quantity(5, MS)), Quantity(2, NA))
        self.assertEqual(combined.current_at(Quantity(20, MS)), Quantity(5, NA))
        self.assertEqual(combined.current_at(Quantity(55, MS)), Quantity(3, NA))


if __name__ == "__main__":
    unittest.main()
