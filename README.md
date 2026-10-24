# AXIOM

### Readable scientific programming for computational neuroscience.

AXIOM is a Python-powered programming language designed specifically for computational neuroscience, making neural modeling, brain-signal analysis, and scientific simulations readable, intuitive, and accessible.

Our goal is simple: **scientific code should be readable by humans, precise enough for computers, and transparent about its assumptions.**

> **Development status:** Release v0.1.0. AXIOM features a readable domain-specific language (DSL) interpreter, unit-aware quantities, Leaky Integrate-and-Fire (LIF) and Adaptive Exponential Integrate-and-Fire (AdEx) neuron models, ODE solvers (Euler, RK2, RK4), stimulus abstractions, simulation recording, CSV export, CLI tools, and scientific validation documentation.

---

## Quick Start & Installation

Install AXIOM in editable mode from the repository root:

```bash
pip install -e .
```

Run tests to verify installation:

```bash
pytest
```

---

## Executing AXIOM Programs

AXIOM programs use the `.ax` file extension.

### Command Line Interface (CLI)

- Run an `.ax` program:
  ```bash
  axiom run examples/first_neuron.ax
  ```

- Run an AdEx model script:
  ```bash
  axiom run examples/adex_neuron.ax
  ```

- Check syntax and validate a script without running:
  ```bash
  axiom check examples/first_neuron.ax
  ```

- Inspect model declarations and simulation summary:
  ```bash
  axiom inspect examples/adex_neuron.ax
  ```

- Print version:
  ```bash
  axiom --version
  ```

---

## Example AXIOM Scripts

### 1. Leaky Integrate-and-Fire (LIF) Neuron (`examples/first_neuron.ax`)

```axiom
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

### 2. Adaptive Exponential (AdEx) Neuron (`examples/adex_neuron.ax`)

```axiom
# AdEx Neuron Adaptation Experiment
adex_neuron "Adapting Cortical Cell":
    capacitance = 200 pF
    leak_conductance = 10 nS
    resting_voltage = -70 mV
    slope_factor = 2 mV
    threshold_voltage = -50 mV
    peak_voltage = 0 mV
    reset_voltage = -58 mV
    adaptation_coupling = 2 nS
    spike_triggered_adaptation = 0.01 nA
    adaptation_time_constant = 30 ms

inject step current 0.5 nA from 10 ms for 80 ms

simulate for 100 ms using time_step 0.1 ms using solver rk4

show spike_count
show spike_times

save results to "adex_neuron_results.csv"
```

---

## Python API Usage

```python
from axiom.neuroscience import AdExParameters, simulate_adex
from axiom.stimuli import StepCurrent
from axiom.units import MS, MV, NA, NS, PF, Quantity

params = AdExParameters(
    capacitance=Quantity(200, PF),
    leak_conductance=Quantity(10, NS),
    resting_voltage=Quantity(-70, MV),
    slope_factor=Quantity(2, MV),
    threshold_voltage=Quantity(-50, MV),
    peak_voltage=Quantity(0, MV),
    reset_voltage=Quantity(-58, MV),
    adaptation_coupling=Quantity(2, NS),
    spike_triggered_adaptation=Quantity(0.01, NA),
    adaptation_time_constant=Quantity(30, MS),
)

stimulus = StepCurrent(
    amplitude=Quantity(0.5, NA),
    start_time=Quantity(10, MS),
    duration=Quantity(80, MS),
)

result = simulate_adex(
    parameters=params,
    injected_current=stimulus,
    duration=Quantity(100, MS),
    time_step=Quantity(0.1, MS),
    solver="rk4",
)

print(f"Recorded AdEx samples: {len(result.times_ms)}")
print(f"Spike count: {len(result.spike_times_ms)}")
result.save_csv("adex_output.csv")
```

---

## Features & Scientific Foundation

- **Physical Units**: Time (`ms`, `s`, `us`), voltage (`mV`, `V`), current (`nA`, `pA`), resistance (`MOhm`), capacitance (`nF`, `pF`, `uF`), conductance (`uS`, `nS`, `pS`), and frequency (`Hz`).
- **Explicit Numerical Integration**: Choice of Forward Euler, Midpoint (RK2), or classical RK4 solvers with order-of-accuracy convergence verification.
- **Supported Models**: Single-variable LIF and two-variable Adaptive Exponential Integrate-and-Fire (AdEx).
- **Scientific Documentation**: Architecture audits (`docs/ARCHITECTURE_AUDIT.md`), validation plans (`docs/SCIENTIFIC_VALIDATION_PLAN.md`), and annotated bibliography (`docs/RESEARCH_BIBLIOGRAPHY.md`).

---

## Project Structure

```text
.
├── src/
│   └── axiom/
│       ├── __init__.py
│       ├── __main__.py          # CLI entry points
│       ├── interpreter.py       # DSL lexer/parser/interpreter
│       ├── neuroscience.py      # LIF and AdEx model implementations
│       ├── recording.py         # LIF and AdEx results & CSV exports
│       ├── solvers.py           # Euler, RK2, RK4 integration routines
│       ├── stimuli.py           # Input current abstractions
│       └── units.py             # Physical unit system
├── tests/                       # Unit, integration, CLI, and convergence tests
├── examples/                    # Runnable .ax and .py examples
├── docs/                        # Language specification, audit, validation plan & bibliography
├── pyproject.toml
├── README.md
└── LICENSE
```

---

## License

MIT License
