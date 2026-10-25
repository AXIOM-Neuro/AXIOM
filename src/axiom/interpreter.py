"""A readable interpreter for the AXIOM language.

Supports:
    let name = expression
    show expression
    neuron "Name": ...
    inject [step/pulse train] current ...
    simulate for ... using time_step ...
    save results to "filename.csv"
"""

from __future__ import annotations

import ast
import operator
import re
from pathlib import Path
from typing import Any, Callable

from axiom.neuroscience import LIFParameters, simulate_lif
from axiom.recording import LIFResult
from axiom.stimuli import ConstantCurrent, PulseTrainCurrent, StepCurrent, Stimulus
from axiom.units import (
    DIMENSIONLESS,
    HZ,
    MOHM,
    MS,
    MV,
    NA,
    NF,
    PA,
    SECOND,
    US,
    VOLT,
    Quantity,
    parse_quantity,
)


class AxiomError(Exception):
    """An error caused by an invalid AXIOM program."""


_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")

BUILTIN_UNITS: dict[str, Quantity] = {
    "ms": Quantity(1.0, MS),
    "s": Quantity(1.0, SECOND),
    "us": Quantity(1.0, US),
    "mV": Quantity(1.0, MV),
    "V": Quantity(1.0, VOLT),
    "nA": Quantity(1.0, NA),
    "pA": Quantity(1.0, PA),
    "nF": Quantity(1.0, NF),
    "MOhm": Quantity(1.0, MOHM),
    "Hz": Quantity(1.0, HZ),
}

_BINARY_OPERATORS: dict[type[ast.operator], Callable] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}

_UNARY_OPERATORS: dict[type[ast.unaryop], Callable] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _check_name(name: str) -> None:
    """Reject invalid or reserved variable names."""
    if not _IDENTIFIER.fullmatch(name):
        raise AxiomError(f"Invalid variable name: {name!r}")

    if name in {"let", "show", "neuron", "simulate", "inject", "save"}:
        raise AxiomError(f"Reserved word cannot be a variable: {name}")


def _preprocess_units(expression: str) -> str:
    """Insert explicit multiplication between numeric literals and unit identifiers."""

    def replacer(match: re.Match) -> str:
        num, unit_name = match.group(1), match.group(2)
        if unit_name in BUILTIN_UNITS:
            return f"{num} * {unit_name}"
        return match.group(0)

    pattern = r"(?<![A-Za-z0-9_])(\d+(?:\.\d*)?|\.\d+)\s*([A-Za-z_][A-Za-z0-9_]*)"
    return re.sub(pattern, replacer, expression)


def _evaluate_ast(node: ast.AST, variables: dict[str, Any]) -> Any:
    """Evaluate an AST expression node with support for Quantities and basic types."""

    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool) or not isinstance(node.value, (int, float, str)):
            raise AxiomError("Only numeric and string constants are supported.")
        return node.value

    if isinstance(node, ast.Name):
        if node.id in variables:
            return variables[node.id]
        if node.id in BUILTIN_UNITS:
            return BUILTIN_UNITS[node.id]
        raise AxiomError(f"Unknown variable: {node.id}")

    if isinstance(node, ast.BinOp):
        operation = _BINARY_OPERATORS.get(type(node.op))
        if operation is None:
            raise AxiomError("Unsupported arithmetic operator.")

        left = _evaluate_ast(node.left, variables)
        right = _evaluate_ast(node.right, variables)

        if isinstance(node.op, ast.Div):
            if right == 0 or (isinstance(right, Quantity) and right.value == 0):
                raise AxiomError("Division by zero.")

        try:
            result = operation(left, right)
        except ZeroDivisionError as error:
            raise AxiomError("Division by zero.") from error
        except (ArithmeticError, OverflowError, ValueError, TypeError) as error:
            raise AxiomError(f"Arithmetic error: {error}") from error

        if isinstance(result, complex):
            raise AxiomError("Complex numbers are not supported.")

        return result

    if isinstance(node, ast.UnaryOp):
        operation = _UNARY_OPERATORS.get(type(node.op))
        if operation is None:
            raise AxiomError("Unsupported unary operator.")
        return operation(_evaluate_ast(node.operand, variables))

    if isinstance(node, (ast.Tuple, ast.List)):
        return tuple(_evaluate_ast(elt, variables) for elt in node.elts)

    raise AxiomError(f"Unsupported expression element: {type(node).__name__}")


def evaluate_expression(expression: str, variables: dict[str, Any]) -> Any:
    """Parse and evaluate one expression string."""
    preprocessed = _preprocess_units(expression)
    try:
        tree = ast.parse(preprocessed, mode="eval")
    except SyntaxError as error:
        raise AxiomError("Invalid expression.") from error

    return _evaluate_ast(tree.body, variables)


class InterpreterRuntime:
    """Execution environment for an AXIOM script."""

    def __init__(self) -> None:
        self.variables: dict[str, Any] = dict(BUILTIN_UNITS)
        self.neurons: dict[str, LIFParameters] = {}
        self.active_neuron: LIFParameters | None = None
        self.active_stimulus: Stimulus = ConstantCurrent(Quantity(0.0, NA))
        self.last_result: LIFResult | None = None
        self.output: list[Any] = []

    def run_source(self, source: str) -> list[Any]:
        """Execute AXIOM source code and return outputs generated by `show`."""
        lines = source.splitlines()
        line_idx = 0

        while line_idx < len(lines):
            raw_line = lines[line_idx]
            line_num = line_idx + 1

            # Stripping comments
            comment_split = raw_line.split("#", 1)
            line = comment_split[0].strip()

            if not line:
                line_idx += 1
                continue

            try:
                if line.startswith("let "):
                    self._handle_let(line[4:].strip())
                    line_idx += 1

                elif line.startswith("show "):
                    self._handle_show(line[5:].strip())
                    line_idx += 1

                elif line.startswith("neuron "):
                    line_idx = self._handle_neuron_block(lines, line_idx)

                elif line.startswith("inject "):
                    self._handle_inject(line[7:].strip())
                    line_idx += 1

                elif line.startswith("simulate"):
                    self._handle_simulate(line[8:].strip())
                    line_idx += 1

                elif line.startswith("save results to "):
                    self._handle_save(line[16:].strip())
                    line_idx += 1

                else:
                    raise AxiomError(f"Unknown statement: {line!r}")

            except (AxiomError, ValueError, TypeError) as error:
                raise AxiomError(f"Line {line_num}: {error}") from error

        return self.output

    def _handle_let(self, stmt: str) -> None:
        if "=" not in stmt:
            raise AxiomError("Assignment must use: let name = expression")
        name, expr = stmt.split("=", 1)
        name = name.strip()
        expr = expr.strip()
        _check_name(name)
        if not expr:
            raise AxiomError("Assignment expression is empty.")
        val = evaluate_expression(expr, self.variables)
        self.variables[name] = val

    def _handle_show(self, expr: str) -> None:
        if not expr:
            raise AxiomError("Show expression is empty.")
        val = evaluate_expression(expr, self.variables)
        if isinstance(val, Quantity):
            self.output.append(val.value)
        elif isinstance(val, (int, float, list, tuple, str)):
            self.output.append(val)
        else:
            self.output.append(str(val))

    def _handle_neuron_block(self, lines: list[str], start_idx: int) -> int:
        header = lines[start_idx].split("#", 1)[0].strip()
        header_body = header[7:].strip()
        if header_body.endswith(":"):
            header_body = header_body[:-1].strip()

        name = header_body.strip("\"'") or "DefaultNeuron"

        params_dict: dict[str, Quantity] = {
            "membrane_time_constant": Quantity(20.0, MS),
            "resting_voltage": Quantity(-65.0, MV),
            "spike_threshold": Quantity(-50.0, MV),
            "reset_voltage": Quantity(-65.0, MV),
            "input_resistance": Quantity(10.0, MOHM),
            "initial_voltage": Quantity(-65.0, MV),
            "refractory_period": Quantity(0.0, MS),
        }

        next_idx = start_idx + 1
        while next_idx < len(lines):
            raw_next = lines[next_idx]
            line_comment_split = raw_next.split("#", 1)[0]
            if not line_comment_split.strip():
                next_idx += 1
                continue
            if not (raw_next.startswith(" ") or raw_next.startswith("\t")):
                break

            indented = line_comment_split.strip()
            if "=" in indented:
                key, expr = indented.split("=", 1)
                key = key.strip()
                val = evaluate_expression(expr.strip(), self.variables)
                if not isinstance(val, Quantity):
                    if isinstance(val, (int, float)):
                        val = Quantity(float(val), DIMENSIONLESS)
                    else:
                        raise AxiomError(f"Parameter {key} must evaluate to a Quantity.")

                if key in {"membrane_time", "membrane_time_constant", "tau"}:
                    params_dict["membrane_time_constant"] = val.to(MS) if val.unit != DIMENSIONLESS else Quantity(val.value, MS)
                elif key in {"resting_voltage", "rest_voltage", "E_rest"}:
                    params_dict["resting_voltage"] = val.to(MV) if val.unit != DIMENSIONLESS else Quantity(val.value, MV)
                elif key in {"spike_threshold", "threshold", "V_th"}:
                    params_dict["spike_threshold"] = val.to(MV) if val.unit != DIMENSIONLESS else Quantity(val.value, MV)
                elif key in {"reset_voltage", "reset", "V_reset"}:
                    params_dict["reset_voltage"] = val.to(MV) if val.unit != DIMENSIONLESS else Quantity(val.value, MV)
                elif key in {"input_resistance", "resistance", "R_m"}:
                    params_dict["input_resistance"] = val.to(MOHM) if val.unit != DIMENSIONLESS else Quantity(val.value, MOHM)
                elif key in {"initial_voltage", "initial", "V_0", "v0"}:
                    params_dict["initial_voltage"] = val.to(MV) if val.unit != DIMENSIONLESS else Quantity(val.value, MV)
                elif key in {"refractory_period", "t_ref"}:
                    params_dict["refractory_period"] = val.to(MS) if val.unit != DIMENSIONLESS else Quantity(val.value, MS)
                else:
                    raise AxiomError(f"Unknown neuron parameter: {key!r}")

            next_idx += 1

        neuron_obj = LIFParameters(**params_dict)
        self.neurons[name] = neuron_obj
        self.active_neuron = neuron_obj
        return next_idx

    def _handle_inject(self, stmt: str) -> None:
        if stmt.startswith("pulse train current ") or stmt.startswith("pulse_train current "):
            pattern = r"^pulse[_\s]+train\s+current\s+(.+?)\s+starting\s+at\s+(.+?)\s+pulse_duration\s+(.+?)\s+frequency\s+(.+?)\s+pulses\s+(.+)$"
            match = re.match(pattern, stmt)
            if not match:
                raise AxiomError(
                    "Invalid pulse train current syntax. Expected: inject pulse train current <amplitude> starting at <start_time> pulse_duration <duration> frequency <freq> pulses <count>"
                )
            amp_expr, start_expr, pdur_expr, freq_expr, pulses_expr = match.groups()

            amp = evaluate_expression(amp_expr, self.variables)
            start = evaluate_expression(start_expr, self.variables)
            p_dur = evaluate_expression(pdur_expr, self.variables)
            freq = evaluate_expression(freq_expr, self.variables)
            num_pulses_val = evaluate_expression(pulses_expr, self.variables)

            amp_qty = amp if isinstance(amp, Quantity) else Quantity(float(amp), NA)
            start_qty = start if isinstance(start, Quantity) else Quantity(float(start), MS)
            pdur_qty = p_dur if isinstance(p_dur, Quantity) else Quantity(float(p_dur), MS)
            freq_qty = freq if isinstance(freq, Quantity) else Quantity(float(freq), HZ)
            num_pulses = int(num_pulses_val.value if isinstance(num_pulses_val, Quantity) else num_pulses_val)

            self.active_stimulus = PulseTrainCurrent(
                amplitude=amp_qty,
                start_time=start_qty,
                pulse_duration=pdur_qty,
                frequency=freq_qty,
                num_pulses=num_pulses,
            )
        elif stmt.startswith("step current "):
            parts = stmt[13:].split(" from ")
            amp_expr = parts[0].strip()
            rest = parts[1] if len(parts) > 1 else ""
            if " for " in rest:
                start_expr, dur_expr = rest.split(" for ", 1)
            else:
                start_expr, dur_expr = rest, "None"

            amp = evaluate_expression(amp_expr, self.variables)
            start = evaluate_expression(start_expr, self.variables) if start_expr else Quantity(0.0, MS)
            dur = evaluate_expression(dur_expr, self.variables) if dur_expr != "None" else None

            self.active_stimulus = StepCurrent(
                amplitude=amp if isinstance(amp, Quantity) else Quantity(amp, NA),
                start_time=start if isinstance(start, Quantity) else Quantity(start, MS),
                duration=dur if (dur is None or isinstance(dur, Quantity)) else Quantity(dur, MS),
            )
        elif stmt.startswith("current "):
            amp_expr = stmt[8:].strip()
            amp = evaluate_expression(amp_expr, self.variables)
            if isinstance(amp, Stimulus):
                self.active_stimulus = amp
            else:
                self.active_stimulus = ConstantCurrent(
                    amp if isinstance(amp, Quantity) else Quantity(float(amp), NA)
                )
        else:
            raise AxiomError(f"Unsupported stimulus statement: inject {stmt}")

    def _handle_simulate(self, stmt: str) -> None:
        if self.active_neuron is None:
            # Create default neuron if none explicitly defined
            self.active_neuron = LIFParameters(
                membrane_time_constant=Quantity(20.0, MS),
                resting_voltage=Quantity(-65.0, MV),
                spike_threshold=Quantity(-50.0, MV),
                reset_voltage=Quantity(-65.0, MV),
                input_resistance=Quantity(10.0, MOHM),
                initial_voltage=Quantity(-65.0, MV),
            )

        duration = Quantity(100.0, MS)
        dt = Quantity(0.1, MS)
        solver = "euler"

        # Parse clauses like "for 100 ms using time_step 0.1 ms using solver rk4"
        parts = stmt.split("using ")
        for_clause = parts[0].strip()
        if for_clause.startswith("for "):
            dur_val = evaluate_expression(for_clause[4:].strip(), self.variables)
            duration = dur_val if isinstance(dur_val, Quantity) else Quantity(float(dur_val), MS)

        for part in parts[1:]:
            part = part.strip()
            if part.startswith("time_step "):
                dt_val = evaluate_expression(part[10:].strip(), self.variables)
                dt = dt_val if isinstance(dt_val, Quantity) else Quantity(float(dt_val), MS)
            elif part.startswith("solver "):
                solver = part[7:].strip()

        result = simulate_lif(
            parameters=self.active_neuron,
            injected_current=self.active_stimulus,
            duration=duration,
            time_step=dt,
            solver=solver,
        )

        self.last_result = result
        self.variables["membrane_voltage"] = result.membrane_voltage_mV
        self.variables["spike_times"] = result.spike_times_ms
        self.variables["spike_count"] = len(result.spike_times_ms)

    def _handle_save(self, stmt: str) -> None:
        if self.last_result is None:
            raise AxiomError("No simulation result to save.")

        path_str = stmt.strip("\"'")
        self.last_result.save_csv(path_str)


def run_source(source: str) -> list[Any]:
    """Run AXIOM source code and return values displayed by `show`."""
    runtime = InterpreterRuntime()
    return runtime.run_source(source)


def run_file(path: str | Path) -> list[Any]:
    """Run an AXIOM program stored in a UTF-8 text file."""
    file_path = Path(path)
    try:
        source = file_path.read_text(encoding="utf-8")
    except OSError as error:
        raise AxiomError(f"Cannot read file {file_path}: {error}") from error

    return run_source(source)
