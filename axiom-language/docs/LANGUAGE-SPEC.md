# AXIOM language notes — prototype 0.1

This document describes only behavior implemented in the starter interpreter.

## Comments and blank lines

- Blank lines are ignored.
- A `#` starts a comment extending to the end of the line.
- The prototype does not support `#` inside strings because it has no string syntax yet.

## Statements

Assignment: `let variable_name = expression`

Names begin with a letter or underscore and continue with letters, digits, or underscores. Values are numeric.

Display: `show expression`. Each `show` statement produces one output line.

## Expressions

Supported: numeric literals; previously assigned variables; parentheses; unary `+` and `-`; binary `+`, `-`, `*`, and `/`. Arithmetic precedence follows standard conventions. Division by zero is reported as an AXIOM error.

## Not supported yet

Physical units, strings, functions, conditionals, loops, neuron declarations, simulation commands, plots, and file export are not implemented.

## Design direction

Future versions may add unit-aware quantities and neuroscience-specific statements. Those features must be specified and tested before being described as supported.
