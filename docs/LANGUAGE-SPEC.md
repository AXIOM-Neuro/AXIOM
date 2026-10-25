# AXIOM v0.1 Language Specification

This document details the syntax, physical units, execution semantics, and API for AXIOM v0.1.

---

## 1. Syntax & Grammatical Structure

AXIOM source files use the `.ax` file extension. Programs consist of sequential statements separated by newlines.

### Comments and Whitespace
- `#` begins a comment that continues to the end of the line.
- Blank lines and whitespace-only lines are ignored.
- Indentation is used inside `neuron` model definition blocks.

### Identifiers and Reserved Words
- Identifiers begin with an ASCII letter or underscore, followed by letters, digits, or underscores (`[A-Za-z_][A-Za-z0-9_]*`).
- Reserved words: `let`, `show`, `neuron`, `inject`, `simulate`, `save`.

---

## 2. Physical Unit System

AXIOM includes explicit physical units:
- **Time:** `ms` (millisecond), `s` / `sec` / `second` (second), `us` (microsecond)
- **Voltage:** `mV` (millivolt), `V` / `volt` (volt)
- **Current:** `nA` (nanoampere), `pA` (picoampere)
- **Resistance:** `MOhm` / `megaohm` (megaohm)
- **Capacitance:** `nF` (nanofarad)
- **Frequency:** `Hz` / `hertz` (hertz)

### Unit Quantities in Expressions
Unit quantities can be written directly by pairing a number with a unit symbol:
```axiom
let tau = 20 ms
let threshold = -50 mV
let current = 2 nA
let resistance = 10 MOhm
```

Expressions enforce dimensional correctness:
- Addition and subtraction require matching dimensions (`mV + mV`, `ms + ms`).
- Multiplication and division combine or cancel dimensions (`MOhm * nA` produces `mV`).

---

## 3. Statements

### `let name = expression`
Assigns the evaluated result of `expression` to `name`.

### `show expression`
Evaluates `expression` and displays the formatted value in the execution log/output.

### `neuron "Name":`
Defines a Leaky Integrate-and-Fire (LIF) neuron model block. Indented parameter definitions inside the block configure model parameters:
```axiom
neuron "MyNeuron":
    membrane_time = 20 ms
    resting_voltage = -65 mV
    spike_threshold = -50 mV
    reset_voltage = -65 mV
    input_resistance = 10 MOhm
    initial_voltage = -65 mV
    refractory_period = 2 ms
```

### `inject current`
Specifies stimulation pattern:
- **Constant current:** `inject current 2 nA`
- **Step current:** `inject step current 2 nA from 10 ms for 50 ms`
- **Pulse train current:** `inject pulse train current 2 nA starting at 0 ms pulse_duration 1 ms frequency 10 Hz pulses 5`

### `simulate`
Executes simulation for specified duration and parameters:
```axiom
simulate for 100 ms using time_step 0.1 ms using solver rk4
```
Solvers supported: `euler`, `rk2`, `rk4`.

After simulation, special runtime state variables become available:
- `membrane_voltage`: tuple of voltage trace values in mV.
- `spike_times`: tuple of spike timestamps in ms.
- `spike_count`: integer count of recorded spikes.

### `save results to "filename.csv"`
Exports recorded time, voltage, and current traces to CSV format.

---

## 4. CLI Commands

- `axiom run <file.ax>`: Runs script and outputs `show` values.
- `axiom check <file.ax>`: Parses and validates script.
- `axiom inspect <file.ax>`: Prints summary report of declared models and simulation results.
- `axiom --version`: Displays AXIOM version.
