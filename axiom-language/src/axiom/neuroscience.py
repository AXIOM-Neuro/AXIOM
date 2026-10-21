"""Small, explicit computational-neuroscience models for AXIOM.

The first model is a current-driven leaky integrate-and-fire (LIF) neuron
with forward-Euler integration. It is a teaching/research prototype, not a
biologically validated neuron model.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from axiom.units import MS, MV, NA, MOHM, Quantity, require_unit


@dataclass(frozen=True)
class LIFParameters:
    """Parameters for a current-driven leaky integrate-and-fire neuron.

    All fields are explicit quantities. Resistance in megaohms multiplied by
    current in nanoamperes gives a voltage in millivolts.
    """

    membrane_time_constant: Quantity
    resting_voltage: Quantity
    spike_threshold: Quantity
    reset_voltage: Quantity
    input_resistance: Quantity
    initial_voltage: Quantity

    def __post_init__(self) -> None:
        positive_tau = require_unit(
            self.membrane_time_constant, MS, "membrane_time_constant"
        )
        require_unit(self.resting_voltage, MV, "resting_voltage")
        threshold = require_unit(self.spike_threshold, MV, "spike_threshold")
        reset = require_unit(self.reset_voltage, MV, "reset_voltage")
        require_unit(self.input_resistance, MOHM, "input_resistance")
        require_unit(self.initial_voltage, MV, "initial_voltage")

        if positive_tau.value <= 0:
            raise ValueError("membrane_time_constant must be positive.")
        if self.input_resistance.value <= 0:
            raise ValueError("input_resistance must be positive.")
        if threshold.value <= reset.value:
            raise ValueError("spike_threshold must be greater than reset_voltage.")


@dataclass(frozen=True)
class LIFResult:
    """Recorded output of a LIF simulation in milliseconds and millivolts."""

    times_ms: tuple[float, ...]
    membrane_voltage_mV: tuple[float, ...]
    spike_times_ms: tuple[float, ...]

    def __post_init__(self) -> None:
        if len(self.times_ms) != len(self.membrane_voltage_mV):
            raise ValueError("Time and voltage recordings must have equal length.")


def simulate_lif(
    parameters: LIFParameters,
    injected_current: Quantity,
    duration: Quantity,
    time_step: Quantity,
) -> LIFResult:
    """Simulate a current-driven LIF neuron with forward-Euler integration.

    The subthreshold equation is

        dV/dt = (E_rest - V + R * I) / tau_m

    When voltage reaches the threshold at an integration step, a spike event
    is recorded at that step and voltage is reset immediately. The returned
    voltage trace therefore contains the post-reset value at spike times.
    Duration must be an integer multiple of the time step to keep the time
    grid unambiguous.
    """
    if not isinstance(parameters, LIFParameters):
        raise TypeError("parameters must be an LIFParameters instance.")

    current = require_unit(injected_current, NA, "injected_current")
    total_time = require_unit(duration, MS, "duration")
    dt = require_unit(time_step, MS, "time_step")
    tau = require_unit(parameters.membrane_time_constant, MS, "membrane_time_constant")
    rest = require_unit(parameters.resting_voltage, MV, "resting_voltage")
    threshold = require_unit(parameters.spike_threshold, MV, "spike_threshold")
    reset = require_unit(parameters.reset_voltage, MV, "reset_voltage")
    resistance = require_unit(parameters.input_resistance, MOHM, "input_resistance")
    voltage = require_unit(parameters.initial_voltage, MV, "initial_voltage").value

    if total_time.value < 0:
        raise ValueError("duration cannot be negative.")
    if dt.value <= 0:
        raise ValueError("time_step must be positive.")
    if tau.value <= 0 or resistance.value <= 0:
        raise ValueError("membrane_time_constant and input_resistance must be positive.")

    exact_steps = total_time.value / dt.value
    steps = round(exact_steps)
    if not math.isclose(exact_steps, steps, rel_tol=1e-10, abs_tol=1e-10):
        raise ValueError("duration must be an integer multiple of time_step.")

    times = [0.0]
    voltages = [voltage]
    spikes: list[float] = []
    steady_voltage = rest.value + resistance.value * current.value

    for step in range(1, steps + 1):
        # Forward Euler update; every term in the numerator is in mV.
        voltage += (steady_voltage - voltage) * (dt.value / tau.value)
        time_ms = step * dt.value

        if voltage >= threshold.value:
            spikes.append(time_ms)
            voltage = reset.value

        if not math.isfinite(voltage):
            raise ArithmeticError("Simulation produced a non-finite membrane voltage.")

        times.append(time_ms)
        voltages.append(voltage)

    return LIFResult(tuple(times), tuple(voltages), tuple(spikes))
