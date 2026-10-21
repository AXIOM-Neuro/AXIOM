# AXIOM language and runtime notes

This document separates currently implemented behavior from planned language features.

## `.ax` interpreter (implemented)

### Comments and blank lines

- Blank lines are ignored.
- A `#` starts a comment extending to the end of the line.
- The prototype has no string syntax, so `#` cannot be used inside a string literal.

### Statements

- Assignment: `let variable_name = expression`
- Display: `show expression`

Names begin with a letter or underscore and continue with letters, digits, or underscores. Values are numeric.

### Expressions

Supported: numeric literals, previously assigned variables, parentheses, unary `+` and `-`, and binary `+`, `-`, `*`, and `/`. Arithmetic precedence follows standard conventions. Division by zero and unsupported syntax are reported as AXIOM errors.

## Python runtime API (implemented in Sprint 01)

The interpreter's `.ax` grammar does **not** yet expose units or simulation statements. The Python runtime API is an initial implementation target for future language integration.

### Units

`axiom.units.Quantity` stores a finite numeric value and a `Unit`. The initial unit system uses milliseconds (`MS`), millivolts (`MV`), and nanoamperes (`NA`) as base units. It also defines seconds (`SECOND`), microseconds (`US`), volts (`VOLT`), picoamperes (`PA`), nanofarads (`NF`), and megaohms (`MOHM`). Unit conversion checks dimensional compatibility; addition and subtraction reject incompatible dimensions. Multiplication and division combine dimensions.

The system is deliberately small and is not a general-purpose metrology library. It does not currently provide uncertainty propagation, prefixes beyond the listed units, or symbolic simplification of unit expressions.

### Current-driven LIF model

`axiom.neuroscience.LIFParameters` holds the membrane time constant, resting voltage, threshold, reset voltage, input resistance, and initial voltage as explicit quantities. `simulate_lif(parameters, injected_current, duration, time_step)` returns an `LIFResult` containing time samples in milliseconds, membrane voltage in millivolts, and spike times in milliseconds.

The subthreshold equation is

\[
\frac{dV}{dt} = \frac{E_{rest} - V + R I}{\tau_m}.
\]

The implementation uses forward-Euler integration. Duration must be a non-negative integer multiple of a positive time step; the time constant and input resistance must be positive; threshold must exceed reset voltage. A threshold crossing records a spike at that integration step and immediately resets the voltage. The recorded voltage at that timestamp is therefore the post-reset value.

This is a minimal illustrative model. It is not evidence of biological accuracy and has not yet undergone independent numerical convergence validation.

## Not implemented yet

Native `.ax` physical-unit syntax, neuron declarations, simulation statements, functions, conditionals, loops, plots, CSV export, conductance-based synapses, neural populations, and EEG/BCI analysis are not yet implemented.

## Development rule

A feature should be described as supported only after its behavior is specified, tested, and reflected in the documentation. Planned syntax examples must be labelled as sketches rather than executable AXIOM programs.
