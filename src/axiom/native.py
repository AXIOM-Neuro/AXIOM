"""Optional ctypes bridge to AXIOM's compiled C++ numerical kernels.

The C++ library is built separately with CMake. Set AXIOM_CPP_LIBRARY to the
resulting shared-library path; importing AXIOM never compiles native code.
"""

from __future__ import annotations

import ctypes
import os
from pathlib import Path
from typing import Final

__all__ = ["NativeBackendError", "native_available", "native_lif_step"]

_SOLVERS: Final[dict[str, int]] = {"euler": 0, "rk2": 1, "rk4": 2}


class NativeBackendError(RuntimeError):
    """Raised when the optional AXIOM C++ backend cannot be used."""


def _library_path() -> Path:
    configured = os.environ.get("AXIOM_CPP_LIBRARY")
    if not configured:
        raise NativeBackendError(
            "AXIOM_CPP_LIBRARY is not set. Build cpp/ with CMake and point "
            "the variable to the generated shared library."
        )
    path = Path(configured).expanduser()
    if not path.is_file():
        raise NativeBackendError(f"AXIOM C++ library does not exist: {path}")
    return path


def _load_library() -> ctypes.CDLL:
    try:
        library = ctypes.CDLL(str(_library_path()))
    except OSError as error:
        raise NativeBackendError(f"Could not load AXIOM C++ library: {error}") from error

    function = library.axiom_lif_step
    double_pointer = ctypes.POINTER(ctypes.c_double)
    function.argtypes = [
        ctypes.c_int,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.c_double,
        double_pointer,
    ]
    function.restype = ctypes.c_int
    return library


def native_available() -> bool:
    """Return whether the configured native library can be loaded."""
    try:
        _load_library()
    except NativeBackendError:
        return False
    return True


def native_lif_step(
    solver: str,
    voltage_mV: float,
    current_now_nA: float,
    current_mid_nA: float,
    current_next_nA: float,
    dt_ms: float,
    tau_ms: float,
    resting_voltage_mV: float,
    input_resistance_MOhm: float,
) -> float:
    """Compute one LIF integration step using the compiled C++ kernel."""
    solver_name = solver.strip().lower()
    if solver_name not in _SOLVERS:
        raise ValueError("solver must be 'euler', 'rk2', or 'rk4'.")

    library = _load_library()
    output = ctypes.c_double()
    status = library.axiom_lif_step(
        _SOLVERS[solver_name],
        float(voltage_mV),
        float(current_now_nA),
        float(current_mid_nA),
        float(current_next_nA),
        float(dt_ms),
        float(tau_ms),
        float(resting_voltage_mV),
        float(input_resistance_MOhm),
        ctypes.byref(output),
    )

    if status == 1:
        raise ValueError("The C++ LIF kernel received invalid or non-finite inputs.")
    if status == 2:
        raise ValueError(f"Unsupported solver code for {solver_name!r}.")
    if status == 3:
        raise ArithmeticError("The C++ LIF kernel produced a non-finite voltage.")
    if status != 0:
        raise NativeBackendError(f"The C++ LIF kernel returned unknown status {status}.")

    return output.value
