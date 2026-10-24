"""Tests for AXIOM unit system and physical quantities."""

import unittest
from axiom.units import (
    MS,
    MV,
    NA,
    MOHM,
    SECOND,
    HZ,
    DIMENSIONLESS,
    Quantity,
    parse_quantity,
    require_unit,
)


class TestAxiomUnits(unittest.TestCase):
    def test_quantity_creation_and_conversion(self):
        q = Quantity(20, MS)
        self.assertEqual(q.value, 20)
        self.assertEqual(q.unit, MS)
        self.assertEqual(q.base_value, 20.0)

        # Convert 1 second to ms
        sec = Quantity(1, SECOND)
        self.assertEqual(sec.to(MS).value, 1000.0)

    def test_incompatible_unit_conversion_raises(self):
        q_time = Quantity(10, MS)
        with self.assertRaises(ValueError):
            q_time.to(MV)

    def test_quantity_arithmetic(self):
        q1 = Quantity(10, MV)
        q2 = Quantity(5, MV)

        self.assertEqual((q1 + q2).value, 15)
        self.assertEqual((q1 - q2).value, 5)

        # Resistance * Current = Voltage
        resistance = Quantity(10, MOHM)
        current = Quantity(2, NA)
        voltage = resistance * current
        self.assertEqual(voltage.to(MV).value, 20.0)

        # Division
        self.assertEqual((Quantity(100, MS) / Quantity(2, MS)).value, 50.0)

    def test_quantity_comparisons(self):
        q1 = Quantity(10, MS)
        q2 = Quantity(1, SECOND)  # 1000 ms
        self.assertTrue(q1 < q2)
        self.assertTrue(q1 <= q2)
        self.assertTrue(q2 > q1)
        self.assertTrue(q2 >= q1)
        self.assertEqual(Quantity(1000, MS), Quantity(1, SECOND))

    def test_parse_quantity(self):
        self.assertEqual(parse_quantity("20 ms"), Quantity(20, MS))
        self.assertEqual(parse_quantity("-65 mV"), Quantity(-65, MV))
        self.assertEqual(parse_quantity("2 nA"), Quantity(2, NA))
        self.assertEqual(parse_quantity("10 MOhm"), Quantity(10, MOHM))
        self.assertEqual(parse_quantity("50 Hz"), Quantity(50, HZ))
        self.assertEqual(parse_quantity("2.5"), Quantity(2.5, DIMENSIONLESS))

    def test_invalid_quantity_parsing(self):
        with self.assertRaises(ValueError):
            parse_quantity("invalid_text")
        with self.assertRaises(ValueError):
            parse_quantity("10 unknown_unit")

    def test_require_unit_helper(self):
        q = Quantity(5, MS)
        valid = require_unit(q, MS, "test_param")
        self.assertEqual(valid.value, 5.0)

        with self.assertRaises(ValueError):
            require_unit(Quantity(5, MV), MS, "test_param")


if __name__ == "__main__":
    unittest.main()
