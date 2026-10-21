"""Small unit-aware quantities for AXIOM's neuroscience prototypes.

Base units are milliseconds (ms), millivolts (mV), and nanoamperes (nA).
This is deliberately a small, explicit unit system, not a replacement for a
full metrology package.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

# Dimension exponents are ordered as (time, voltage, current).
Dimension = tuple[int, int, int]


@dataclass(frozen=True)
class Unit:
    """A unit with a scale relative to AXIOM's base units."""

    symbol: str
    scale: float
    dimension: Dimension

    def __post_init__(self) -> None:
        if not self.symbol:
            raise ValueError("A unit must have a symbol.")
        if not math.isfinite(self.scale) or self.scale <= 0:
            raise ValueError("Unit scale must be finite and positive.")

    def __mul__(self, other: Unit) -> Unit:
        return Unit(
            f"{self.symbol}*{other.symbol}",
            self.scale * other.scale,
            tuple(a + b for a, b in zip(self.dimension, other.dimension)),
        )

    def __truediv__(self, other: Unit) -> Unit:
        return Unit(
            f"{self.symbol}/{other.symbol}",
            self.scale / other.scale,
            tuple(a - b for a, b in zip(self.dimension, other.dimension)),
        )


DIMENSIONLESS = Unit("1", 1.0, (0, 0, 0))
MS = Unit("ms", 1.0, (1, 0, 0))
SECOND = Unit("s", 1000.0, (1, 0, 0))
US = Unit("us", 0.001, (1, 0, 0))
MV = Unit("mV", 1.0, (0, 1, 0))
VOLT = Unit("V", 1000.0, (0, 1, 0))
NA = Unit("nA", 1.0, (0, 0, 1))
PA = Unit("pA", 0.001, (0, 0, 1))
NF = Unit("nF", 1.0, (1, -1, 1))
MOHM = Unit("MOhm", 1.0, (0, 1, -1))


@dataclass(frozen=True)
class Quantity:
    """A finite numeric value paired with a physical unit."""

    value: float
    unit: Unit = DIMENSIONLESS

    def __post_init__(self) -> None:
        if isinstance(self.value, bool) or not isinstance(self.value, (int, float)):
            raise TypeError("Quantity value must be a real number.")
        if not math.isfinite(float(self.value)):
            raise ValueError("Quantity value must be finite.")

    @property
    def base_value(self) -> float:
        """Return the value expressed in AXIOM base units."""
        return float(self.value) * self.unit.scale

    def to(self, unit: Unit) -> Quantity:
        """Convert to another unit with the same physical dimension."""
        if self.unit.dimension != unit.dimension:
            raise ValueError(
                f"Cannot convert {self.unit.symbol} to incompatible unit {unit.symbol}."
            )
        return Quantity(self.base_value / unit.scale, unit)

    def _same_dimension(self, other: Quantity) -> None:
        if self.unit.dimension != other.unit.dimension:
            raise ValueError(
                f"Incompatible units: {self.unit.symbol} and {other.unit.symbol}."
            )

    def __add__(self, other: Quantity) -> Quantity:
        if not isinstance(other, Quantity):
            return NotImplemented
        self._same_dimension(other)
        return Quantity(self.value + other.to(self.unit).value, self.unit)

    def __sub__(self, other: Quantity) -> Quantity:
        if not isinstance(other, Quantity):
            return NotImplemented
        self._same_dimension(other)
        return Quantity(self.value - other.to(self.unit).value, self.unit)

    def __mul__(self, other: Quantity | float | int) -> Quantity:
        if isinstance(other, Quantity):
            return Quantity(
                self.value * other.value,
                self.unit * other.unit,
            )
        if isinstance(other, bool) or not isinstance(other, (float, int)):
            return NotImplemented
        return Quantity(self.value * other, self.unit)

    def __rmul__(self, other: float | int) -> Quantity:
        return self * other

    def __truediv__(self, other: Quantity | float | int) -> Quantity:
        if isinstance(other, Quantity):
            if other.value == 0:
                raise ZeroDivisionError("Cannot divide by a zero quantity.")
            return Quantity(
                self.value / other.value,
                self.unit / other.unit,
            )
        if isinstance(other, bool) or not isinstance(other, (float, int)):
            return NotImplemented
        if other == 0:
            raise ZeroDivisionError("Cannot divide by zero.")
        return Quantity(self.value / other, self.unit)

    def __neg__(self) -> Quantity:
        return Quantity(-self.value, self.unit)

    def __lt__(self, other: Quantity) -> bool:
        self._same_dimension(other)
        return self.base_value < other.base_value

    def __le__(self, other: Quantity) -> bool:
        self._same_dimension(other)
        return self.base_value <= other.base_value

    def __repr__(self) -> str:
        return f"Quantity({self.value!r}, {self.unit.symbol!r})"


def require_unit(quantity: Quantity, unit: Unit, name: str) -> Quantity:
    """Validate a parameter's dimension and return it in the requested unit."""
    if not isinstance(quantity, Quantity):
        raise TypeError(f"{name} must be a Quantity with units of {unit.symbol}.")
    try:
        return quantity.to(unit)
    except ValueError as error:
        raise ValueError(f"{name} must have units compatible with {unit.symbol}.") from error
