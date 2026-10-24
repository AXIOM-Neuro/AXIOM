"""Tests for simulation recording and CSV export functionality."""

import csv
import tempfile
import unittest
from pathlib import Path

from axiom.recording import LIFResult


class TestAxiomRecording(unittest.TestCase):
    def test_to_dict(self):
        res = LIFResult(
            times_ms=(0.0, 0.1, 0.2),
            membrane_voltage_mV=(-65.0, -64.9, -64.8),
            spike_times_ms=(0.1,),
            injected_current_nA=(2.0, 2.0, 2.0),
            metadata={"test_key": "test_val"},
        )

        d = res.to_dict()
        self.assertEqual(d["times_ms"], [0.0, 0.1, 0.2])
        self.assertEqual(d["membrane_voltage_mV"], [-65.0, -64.9, -64.8])
        self.assertEqual(d["spike_times_ms"], [0.1])
        self.assertEqual(d["spike_count"], 1)
        self.assertEqual(d["injected_current_nA"], [2.0, 2.0, 2.0])
        self.assertEqual(d["metadata"]["test_key"], "test_val")

    def test_csv_export(self):
        res = LIFResult(
            times_ms=(0.0, 0.1, 0.2),
            membrane_voltage_mV=(-65.0, -64.9, -64.8),
            spike_times_ms=(0.1,),
            injected_current_nA=(2.0, 2.0, 2.0),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "out.csv"
            res.save_csv(csv_path)

            self.assertTrue(csv_path.exists())
            text = csv_path.read_text(encoding="utf-8")
            self.assertIn("time_ms", text)
            self.assertIn("membrane_voltage_mV", text)
            self.assertIn("injected_current_nA", text)
            self.assertIn("-65", text)


if __name__ == "__main__":
    unittest.main()
