# AXIOM v0.1 Language Specification

This document details the syntax, physical units, execution semantics, and API for AXIOM v0.1.

---

## 1. Syntax & Grammatical Structure

AXIOM source files use the `.ax` file extension. Programs consist of sequential statements separated by newlines.

### Comments and Whitespace
- `#` begins a comment that continues to the end of the line.
- Blank lines and whitespace-only lines are ignored.
- Indentation is used inside `neuron` and `adex_neuron` model definition blocks.

### Identifiers and Reserved Words
- Identifiers begin with an ASCII letter or underscore, followed by letters, digits, or underscores (`[A-Za-z_][A-Za-z0-9_]*`).
- Reserved words: `let`, `show`, `neuron`, `adex_neuron`, `inject`, `simulate`, `save`.

---

## 2. Physical Unit System

AXIOM includes explicit physical units:
- **Time:** `ms`, `s`, `us`
- **Voltage:** `mV`, `V`
- **Current:** `nA`, `pA`
- **Resistance:** `MOhm`
- **Capacitance:** `nF`, `pF`, `uF`
- **Conductance:** `uS`, `nS`, `pS`
- **Frequency:** `Hz`

### Unit Quantities in Expressions
Unit quantities can be written directly by pairing a number with a unit symbol:
```axiom
let capacitance = 200 pF
let threshold = -50 mV
let current = 0.5 nA
let conductance = 10 nS
```

Expressions enforce dimensional correctness:
- Addition and subtraction require matching dimensions.
- Multiplication and division combine or cancel dimensions (`uS * mV` produces `nA`).

---

## 3. Statements

### `let name = expression`
Assigns the evaluated result of `expression` to `name`.

### `show expression`
Evaluates `expression` and displays the formatted value in the execution log/output.

### `neuron "Name":`
Defines a Leaky Integrate-and-Fire (LIF) neuron model block:
```axiom
neuron "MyNeuron":
    membrane_time = 20 ms
    resting_voltage = -65 mV
    spike_threshold = -50 mV
    reset_voltage = -65 mV
    input_resistance = 10 MOhm
```

### `adex_neuron "Name":`
Defines an Adaptive Exponential Integrate-and-Fire (AdEx) neuron model block:
```axiom
adex_neuron "Adapting Cell":
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
```

### `inject current`
Specifies stimulation pattern:
- **Constant current:** `inject current 0.5 nA`
- **Step current:** `inject step current 0.5 nA from 10 ms for 80 ms`

### `simulate`
Executes simulation for specified duration and parameters:
```axiom
simulate for 100 ms using time_step 0.1 ms using solver rk4
```
Solvers supported: `euler`, `rk2`, `rk4`.

After simulation, special runtime state variables become available:
- `membrane_voltage`: tuple of voltage trace values in mV.
- `adaptation_current`: tuple of adaptation current values in nA (for AdEx).
- `spike_times`: tuple of spike timestamps in ms.
- `spike_count`: integer count of recorded spikes.

### `save results to "filename.csv"`
Exports recorded time, voltage, adaptation, and current traces to CSV format.

---

## 4. CLI Commands

- `axiom run <file.ax>`: Runs script and outputs `show` values.
- `axiom check <file.ax>`: Parses and validates script.
- `axiom inspect <file.ax>`: Prints summary report of declared models and simulation results.
- `axiom --version`: Displays AXIOM version.
