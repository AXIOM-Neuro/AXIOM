# AXIOM Architecture Audit

**Date:** October 2023 / Release v0.1.0
**Baseline Test Results:** 31 passed in 0.19s (`pytest`)

---

## 1. Module and Dependency Structure

AXIOM's Python implementation uses a modular layout under `src/axiom/`:

- `src/axiom/__init__.py`: Package metadata (`__version__ = "0.1.0"`).
- `src/axiom/__main__.py`: CLI entry point supporting `run`, `check`, `inspect`, and `--version`.
- `src/axiom/units.py`: Physical unit system (`Unit`, `Quantity`, `parse_quantity`, `UNITS`).
- `src/axiom/solvers.py`: Ordinary Differential Equation (ODE) integration kernels (`step_euler`, `step_rk2`, `step_rk4`).
- `src/axiom/stimuli.py`: Input stimulus abstractions (`ConstantCurrent`, `StepCurrent`, `PulseTrainCurrent`, `CombinedStimulus`).
- `src/axiom/neuroscience.py`: Neuron model specifications and simulation loops (`LIFParameters`, `simulate_lif`).
- `src/axiom/recording.py`: Recorded output data structure and file export (`LIFResult`, `save_csv`).
- `src/axiom/interpreter.py`: Textual DSL parser and AST evaluator (`InterpreterRuntime`, `run_source`, `run_file`).

### Dependencies
- **Core runtime:** Python $\ge 3.10$ standard library (`ast`, `operator`, `re`, `pathlib`, `argparse`, `csv`, `math`, `dataclasses`). Zero external runtime dependencies required.
- **Testing:** `pytest` (with `pythonpath = ["src"]` configured in `pyproject.toml`).

---

## 2. Language-Processing Pipeline

The `.ax` script compilation and execution pipeline follows a clear sequence:

1. **Source Loading:** `run_file(path)` reads UTF-8 source text.
2. **Line Preprocessing & Block Parsing:** `InterpreterRuntime.run_source()` strips comments (`#`) and processes top-level statements sequentially. Block declarations like `neuron "Name":` consume indented lines.
3. **Implicit Unit Preprocessing:** `_preprocess_units(expr)` transforms unit literals (e.g., `20 ms`, `-65 mV`, `2 nA`) into AST-parseable expressions (`20 * ms`, `-65 * mV`, `2 * nA`).
4. **AST Parsing & Safe Evaluation:** `ast.parse(preprocessed, mode="eval")` produces Python AST nodes. `_evaluate_ast()` safely evaluates `ast.Constant`, `ast.Name`, `ast.BinOp`, `ast.UnaryOp`, `ast.Tuple`, and `ast.List` without invoking untrusted `eval()`.
5. **Model & Simulation Execution:** `simulate_lif()` constructs subthreshold state updates, applies spike detection and refractory resetting, and records time/voltage/current traces.
6. **Output Formatting & Recording:** Outputs from `show` are collected; `save results to "file.csv"` invokes `LIFResult.save_csv()`.

---

## 3. Top Three Identified Improvements

### Improvement 1: Support Adaptive Exponential Integrate-and-Fire (AdEx) Neuron Model
- **Files:** `src/axiom/neuroscience.py`, `src/axiom/solvers.py`, `src/axiom/interpreter.py`
- **Observed Behavior:** Only single-variable LIF models are currently supported. Two-variable spike-frequency adaptation (AdEx) models are widely used in neuroscience literature (Naud et al., 2008).
- **Rationale:** Expanding to AdEx provides realistic adaptation currents ($w$) and exponential subthreshold initiation, significantly broadening AXIOM's scientific utility.

### Improvement 2: Extend DSL Parser to Support AdEx & Advanced Stimulus Declarations
- **Files:** `src/axiom/interpreter.py`
- **Observed Behavior:** DSL interpreter supports basic `neuron` blocks with LIF fields and `inject step current`.
- **Rationale:** Extending `.ax` DSL syntax to parse AdEx parameters (`adaptation_coupling`, `spike_triggered_adaptation`, `slope_factor`) and pulse-train stimuli enables researchers to write expressive scripts for complex neuronal dynamics.

### Improvement 3: Analytical & Numerical Error Estimation Benchmark Suite
- **Files:** `tests/test_solvers.py`, `docs/SCIENTIFIC_VALIDATION_PLAN.md`
- **Observed Behavior:** Current solver tests check RK4 against subthreshold LIF analytical solutions at $t = 20\text{ ms}$.
- **Rationale:** A dedicated convergence benchmark verifying order of accuracy ($O(dt)$ for Euler, $O(dt^2)$ for RK2, $O(dt^4)$ for RK4) across time step refinements provides rigorous numerical guarantees.

---

## 4. Test Baseline Summary

```text
tests/test_cli.py ....                                                   [ 12%]
tests/test_interpreter.py ...........                                    [ 48%]
tests/test_recording.py ..                                               [ 54%]
tests/test_solvers.py ...                                                [ 64%]
tests/test_stimuli.py ....                                               [ 77%]
tests/test_units.py .......                                              [100%]

31 passed in 0.19s
```
