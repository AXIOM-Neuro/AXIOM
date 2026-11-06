"""Tests for AXIOM's optional native numerical backend."""

import os
import unittest
from unittest.mock import patch

from axiom.native import NativeBackendError, native_available, native_lif_step


class TestNativeBackend(unittest.TestCase):
    def test_native_backend_is_optional_when_unconfigured(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(native_available())

    def test_missing_library_has_actionable_error(self):
        with patch.dict(os.environ, {"AXIOM_CPP_LIBRARY": "/path/that/does/not/exist"}):
            with self.assertRaisesRegex(NativeBackendError, "does not exist"):
                native_lif_step(
                    "euler", -60.0, 1.0, 1.0, 1.0,
                    0.1, 20.0, -65.0, 10.0,
                )

    def test_unknown_solver_is_rejected_before_loading_library(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "solver must be"):
                native_lif_step(
                    "bogus", -60.0, 1.0, 1.0, 1.0,
                    0.1, 20.0, -65.0, 10.0,
                )


if __name__ == "__main__":
    unittest.main()
