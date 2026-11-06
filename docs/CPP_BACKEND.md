# AXIOM C++ numerical backend

AXIOM keeps its public scientific API, unit system, stimulus abstractions,
recording, spike threshold/reset logic, refractory handling, and readable
`.ax` language in Python. The optional C++ library provides subthreshold
numerical integration kernels.

## Current scope

The native kernel implements one subthreshold LIF integration step:

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

Set `AXIOM_CPP_LIBRARY` to the full path of that file before using the native
backend. For example, on Windows PowerShell:

```powershell
$env:AXIOM_CPP_LIBRARY = (Resolve-Path .\build\Release\axiom_cpp.dll).Path
```

The exact output location can vary by generator and build configuration.

## Selecting the backend in Python

The default remains the pure-Python reference implementation:

```python
result = simulate_lif(
    parameters,
    injected_current,
    duration,
    time_step,
    solver="rk4",
)
```

To explicitly select the optional C++ subthreshold kernel:

```python
result = simulate_lif(
    parameters,
    injected_current,
    duration,
    time_step,
    solver="rk4",
    backend="cpp",
)
```

The `backend` argument accepts `"python"` or `"cpp"`. Selecting `"cpp"`
requires `AXIOM_CPP_LIBRARY` to point to a compatible compiled library.
Missing or invalid libraries produce an explicit error; there is no silent
fallback. Both paths return the same `LIFResult` structure and identify the
selected backend in result metadata.

Python continues to manage stimulus evaluation, threshold crossing, spike
recording, voltage reset, refractory periods, and result construction. Only
the subthreshold integration step is delegated to C++.

## Validation

- `cpp/tests` checks the native kernel's numerical outputs and invalid-input
  handling.
- `tests/test_native_integration.py` compares compiled C++ Euler, RK2, and RK4
  steps with the Python reference solvers over multiple input cases.
- `tests/test_simulation_backends.py` checks backend selection and Python-side
  spike/reset orchestration using a mocked native call.
- The backend CI workflow builds the C++ library, runs CTest, installs the
  Python package, and runs the Python tests with the compiled library enabled.

These tests are not a substitute for broader validation across time-varying
stimuli, threshold-crossing edge cases, and refractory-boundary conditions.
The Python implementation remains the reference implementation.

## Performance

No speed improvement is claimed. The current interface crosses the Python/C++
boundary once per integration step; that call overhead may outweigh the cost
of this small scalar calculation. Meaningful acceleration may require a
batched or full-trajectory native interface, which should only be considered
after numerical parity and reproducible benchmarks.
