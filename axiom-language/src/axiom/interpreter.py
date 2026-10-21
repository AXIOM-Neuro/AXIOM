
"""A small interpreter for the AXIOM v0.1 language.

Supported statements:
    let name = expression
    show expression

Supported expressions:
    Numbers, variables, +, -, *, /, and parentheses.
"""

from __future__ import annotations

import ast
import operator
import re
from pathlib import Path
from typing import Callable


class AxiomError(Exception):
    """An error caused by an invalid AXIOM program."""


_NUMBER = re.compile(
    r"(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"
)

_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")

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

    if name in {"let", "show"}:
        raise AxiomError(f"Reserved word cannot be a variable: {name}")


def _evaluate(node: ast.AST, variables: dict[str, float]) -> float:
    """Evaluate a restricted Python expression tree safely."""

    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool) or not isinstance(
            node.value, (int, float)
        ):
            raise AxiomError("Only numeric constants are supported.")

        return node.value

    if isinstance(node, ast.Name):
        if node.id not in variables:
            raise AxiomError(f"Unknown variable: {node.id}")

        return variables[node.id]

    if isinstance(node, ast.BinOp):
        operation = _BINARY_OPERATORS.get(type(node.op))

        if operation is None:
            raise AxiomError("Unsupported arithmetic operator.")

        left = _evaluate(node.left, variables)
        right = _evaluate(node.right, variables)

        if isinstance(node.op, ast.Div) and right == 0:
            raise AxiomError("Division by zero.")

        try:
            result = operation(left, right)
        except (ArithmeticError, OverflowError, ValueError) as error:
            raise AxiomError(f"Arithmetic error: {error}") from error

        if isinstance(result, complex):
            raise AxiomError("Complex numbers are not supported.")

        return result

    if isinstance(node, ast.UnaryOp):
        operation = _UNARY_OPERATORS.get(type(node.op))

        if operation is None:
            raise AxiomError("Unsupported unary operator.")

        return operation(_evaluate(node.operand, variables))

    raise AxiomError(
        f"Unsupported expression element: {type(node).__name__}"
    )


def evaluate_expression(
    expression: str, variables: dict[str, float]
) -> float:
    """Parse and evaluate one arithmetic expression."""
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as error:
        raise AxiomError("Invalid arithmetic expression.") from error

    result = _evaluate(tree.body, variables)

    if not isinstance(result, (int, float)) or isinstance(result, bool):
        raise AxiomError("Expression did not produce a real number.")

    return result


def run_source(source: str) -> list[float]:
    """Run AXIOM source code and return values displayed by `show`."""
    variables: dict[str, float] = {}
    output: list[float] = []

    for line_number, original_line in enumerate(source.splitlines(), 1):
        line = original_line.split("#", 1)[0].strip()

        if not line:
            continue

        try:
            if line.startswith("let "):
                assignment = line[4:].strip()

                if "=" not in assignment:
                    raise AxiomError(
                        "Assignment must use: let name = expression"
                    )

                name, expression = assignment.split("=", 1)
                name = name.strip()
                expression = expression.strip()

                _check_name(name)

                if not expression:
                    raise AxiomError("Assignment expression is empty.")

                value = evaluate_expression(expression, variables)
                variables[name] = value

            elif line.startswith("show "):
                expression = line[5:].strip()

                if not expression:
                    raise AxiomError("Show expression is empty.")

                output.append(
                    evaluate_expression(expression, variables)
                )

            else:
                raise AxiomError(
                    "Unknown statement. Expected 'let' or 'show'."
                )

        except AxiomError as error:
            raise AxiomError(
                f"Line {line_number}: {error}"
            ) from error

    return output


def run_file(path: str | Path) -> list[float]:
    """Run an AXIOM program stored in a UTF-8 text file."""
    file_path = Path(path)

    try:
        source = file_path.read_text(encoding="utf-8")
    except OSError as error:
        raise AxiomError(
            f"Cannot read file {file_path}: {error}"
        ) from error

    return run_source(source)
