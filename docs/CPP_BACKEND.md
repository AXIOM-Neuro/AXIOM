# AXIOM C++ numerical backend

AXIOM keeps its public scientific API, unit system, stimulus abstractions,
recording, and readable `.ax` language in Python. The optional C++ library
provides numerical kernels for performance-sensitive operations.

## Current scope

The first native kernel implements one subthreshold LIF integration step:

```text
dV/dt = (E_rest - V + R_m I) / tau_m
```

It supports Forward Euler, explicit midpoint RK2, and classical RK4. The
language boundary uses a small C ABI so the shared library can be called from
Python through `ctypes` without requiring a third-party binding generator.

All values crossing this boundary use AXIOM's documented base conventions:
time in ms, voltage in mV, current in nA, and resistance in MOhm. Therefore
`MOhm * nA = mV`.

## Build

From the repository root, with CMake and a C++17 compiler installed:

```bash
cmake -S cpp -B build
cmake --build build --config Release
ctest --test-dir build --output-on-failure
```

The resulting shared library is normally named:

- Windows: `axiom_cpp.dll`
- Linux: `libaxiom_cpp.so`
- macOS: `libaxiom_cpp.dylib`

Set `AXIOM_CPP_LIBRARY` to the full path of that file before using the Python
bridge. For example, on Windows PowerShell:

```powershell
$env:AXIOM_CPP_LIBRARY = (Resolve-Path .\build\Release\axiom_cpp.dll).Path
```

The exact output location can vary by generator and build configuration.

## Python bridge

```python
from axiom.native import native_available, native_lif_step

if native_available():
    next_voltage = native_lif_step(
        solver="rk4",
        voltage_mV=-60.0,
        current_now_nA=1.0,
        current_mid_nA=1.0,
        current_next_nA=1.0,
        dt_ms=0.1,
        tau_ms=20.0,
        resting_voltage_mV=-65.0,
        input_resistance_MOhm=10.0,
    )
```

The native backend is opt-in and never compiles code during import or silently
changes the existing Python simulation path. The Python implementation remains
the reference implementation.

## Validation principles

- Keep Python and C++ equations and units explicit.
- Compare native outputs against the Python reference solver in tests.
- Preserve deterministic solver selection and error handling.
- Do not claim a speed improvement until reproducible benchmarks establish it.
- Extend the native boundary to full simulation only after numerical parity is
  demonstrated for stimuli, threshold/reset behavior, and refractory periods.
