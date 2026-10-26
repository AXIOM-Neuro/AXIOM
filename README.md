# AXIOM

### Readable scientific programming for computational neuroscience.

AXIOM is a Python-powered programming language designed specifically for computational neuroscience, making neural modeling, brain-signal analysis, and scientific simulations readable, intuitive, and accessible.

Our goal is simple: **scientific code should be readable by humans, precise enough for computers, and transparent about its assumptions.**

> **Development status:** Initial v0.1 Release. AXIOM features a readable domain-specific language (DSL) interpreter, unit-aware quantities, current-driven Leaky Integrate-and-Fire (LIF) models, multiple ODE numerical solvers (Euler, RK2, RK4), stimulus abstractions, simulation recording, and CSV export.

---

## Quick Start & Installation

Install AXIOM in editable mode from the repository root:

```
pip install -e .
```

Run tests to verify installation:

```
pytest
```

---

## Executing AXIOM Programs

AXIOM programs use the `.ax` file extension.

### Command Line Interface (CLI)

- Run an `.ax` program:
  ```
  axiom run examples/first_neuron.ax
  ```
  *(or simply `axiom examples/first_neuron.ax`)*

- Check syntax and validate a script without running:
  ```
  axiom check examples/first_neuron.ax
  ```

- Inspect declarations and simulation results:
  ```
  axiom inspect examples/first_neuron.ax
  ```

- Print version:
  ```
  axiom --version
  ```

---

## Example AXIOM Script

Here is a complete, executable AXIOM program (`examples/first_neuron.ax`):

```
# My first AXIOM neuron experiment
neuron "Example Neuron":
    membrane_time = 20 ms
    resting_voltage = -65 mV
    spike_threshold = -50 mV
    reset_voltage = -65 mV
    input_resistance = 10 MOhm
    initial_voltage = -65 mV

inject current 2 nA

simulate for 100 ms using time_step 0.1 ms

show spike_count
show spike_times

save results to "neuron_results.csv"
```

Running `axiom run examples/first_neuron.ax` outputs:

```
3
(27.7, 55.4, 83.1)
```

and generates `neuron_results.csv` containing recorded time samples, membrane voltages, and injected currents.

---

## Python API Usage

You can also use AXIOM directly from Python:

```
from axiom.neuroscience import LIFParameters, simulate_lif
from axiom.stimuli import StepCurrent
from axiom.units import MS, MV, NA, MOHM, Quantity

# Define model parameters
params = LIFParameters(
    membrane_time_constant=Quantity(20, MS),
    resting_voltage=Quantity(-65, MV),
    spike_threshold=Quantity(-50, MV),
    reset_voltage=Quantity(-65, MV),
    input_resistance=Quantity(10, MOHM),
    initial_voltage=Quantity(-65, MV),
    refractory_period=Quantity(2, MS),
)

# Define step current stimulus
stimulus = StepCurrent(
    amplitude=Quantity(2, NA),
    start_time=Quantity(10, MS),
    duration=Quantity(80, MS),
)

# Or pulse train stimulus:
# from axiom.stimuli import PulseTrainCurrent
# stimulus = PulseTrainCurrent(
#     amplitude=Quantity(2, NA),
#     start_time=Quantity(0, MS),
#     pulse_duration=Quantity(1, MS),
#     frequency=Quantity(10, HZ),
#     num_pulses=5,
# )

# Run simulation with RK4 numerical integration
result = simulate_lif(
    parameters=params,
    injected_current=stimulus,
    duration=Quantity(100, MS),
    time_step=Quantity(0.1, MS),
    solver="rk4",
)

print(f"Spike count: {len(result.spike_times_ms)}")
print(f"Spike times (ms): {list(result.spike_times_ms)}")

# Export to CSV
result.save_csv("python_lif_output.csv")
```

---

## Features & Philosophy

- **Physical Units**: Built-in support for time (`ms`, `s`, `us`), voltage (`mV`, `V`), current (`nA`, `pA`), resistance (`MOhm`), capacitance (`nF`), and frequency (`Hz`).
- **Explicit Numerical Integration**: Choice of Forward Euler, Midpoint (RK2), or RK4 solvers with step size stability validation.
- **Stimulus Abstractions**: Constant current, step current, pulse trains, and linear superposition.
- **Reproducible Outputs**: Structured recording of voltage traces, spike event times, and export to CSV or Python dicts.

---

## Project Structure

```
.
├── src/
│   └── axiom/
│       ├── __init__.py
│       ├── __main__.py          # CLI entry points
│       ├── interpreter.py       # DSL lexer/parser/interpreter
│       ├── neuroscience.py      # LIF model implementation
│       ├── recording.py         # Results & CSV export
│       ├── solvers.py           # Numerical ODE integration
│       ├── stimuli.py           # Input current abstractions
│       └── units.py             # Physical unit system
├── tests/                       # Unit, integration & scientific tests
├── examples/                    # Runnable .ax and .py examples
├── docs/                        # Language specification & docs
├── pyproject.toml
├── README.md
└── LICENSE
```

---

## Contributing & Community Guidelines

We welcome contributions from the computational neuroscience and open-science communities! Whether you want to fix a bug, add a new numerical solver, or suggest syntax improvements for the DSL, please follow these steps:

### Contributing Code
1. Fork the repository on GitHub.
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. Ensure your changes are fully covered by unit tests in the `tests/` directory.
4. Run `pytest` to verify all test suites pass.
5. Commit your changes using descriptive commit messages and open a Pull Request.

### Reporting Issues & Getting Support
- **Bug Reports & Feature Requests:** Please open a detailed issue on the [GitHub Issues](https://github.com/AXIOM-Neuro/AXIOM/issues) page. Include your `.ax` script setup, your operating system, and the exact error trace.
- **General Support:** If you have questions about implementing a specific biophysical equation or configuring custom current stimuli, please start a discussion thread in our repository's discussion tab or contact the maintainer at `folarera.kassim@gmail.com`.

---


## License

AXIOM is free, open-source, and licensed under the MIT License
