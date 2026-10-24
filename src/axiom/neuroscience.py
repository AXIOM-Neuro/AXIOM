"""Small, explicit computational-neuroscience models for AXIOM.

Includes current-driven leaky integrate-and-fire (LIF) neuron models with
configurable numerical solvers (Forward Euler, RK2, RK4) and refractory periods.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math

from axiom.recording import LIFResult
from axiom.solvers import step_euler, step_rk2, step_rk4
from axiom.stimuli import ConstantCurrent, Stimulus
from axiom.units import MS, MV, NA, MOHM, Quantity, require_unit

__all__ = ["LIFParameters", "LIFResult", "simulate_lif"]


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
    refractory_period: Quantity = field(default_factory=lambda: Quantity(0.0, MS))

    def __post_init__(self) -> None:
        positive_tau = require_unit(
            self.membrane_time_constant, MS, "membrane_time_constant"
        )
        require_unit(self.resting_voltage, MV, "resting_voltage")
        threshold = require_unit(self.spike_threshold, MV, "spike_threshold")
        reset = require_unit(self.reset_voltage, MV, "reset_voltage")
        require_unit(self.input_resistance, MOHM, "input_resistance")
        require_unit(self.initial_voltage, MV, "initial_voltage")
        refractory = require_unit(self.refractory_period, MS, "refractory_period")

        if positive_tau.value <= 0:
            raise ValueError("membrane_time_constant must be positive.")
        if self.input_resistance.value <= 0:
            raise ValueError("input_resistance must be positive.")
        if threshold.value <= reset.value:
            raise ValueError("spike_threshold must be greater than reset_voltage.")
        if refractory.value < 0:
            raise ValueError("refractory_period cannot be negative.")


def simulate_lif(
    parameters: LIFParameters,
    injected_current: Quantity | Stimulus,
    duration: Quantity,
    time_step: Quantity,
    solver: str = "euler",
) -> LIFResult:
    """Simulate a current-driven LIF neuron.

    Subthreshold equation:
        dV/dt = (E_rest - V + R * I) / tau_m

    Supports refractory period and solvers: 'euler', 'rk2', 'rk4'.
    """
    if not isinstance(parameters, LIFParameters):
        raise TypeError("parameters must be an LIFParameters instance.")

    if isinstance(injected_current, Quantity):
        stimulus: Stimulus = ConstantCurrent(injected_current)
    elif isinstance(injected_current, Stimulus) or hasattr(injected_current, "current_at"):
        stimulus = injected_current
    else:
        raise TypeError("injected_current must be a Quantity or a Stimulus object.")

    solver_lower = solver.lower().strip()
    if solver_lower not in {"euler", "rk2", "rk4"}:
        raise ValueError(f"Unsupported solver: {solver!r}. Choose from 'euler', 'rk2', 'rk4'.")

    total_time = require_unit(duration, MS, "duration")
    dt = require_unit(time_step, MS, "time_step")
    tau = require_unit(parameters.membrane_time_constant, MS, "membrane_time_constant")
    rest = require_unit(parameters.resting_voltage, MV, "resting_voltage")
    threshold = require_unit(parameters.spike_threshold, MV, "spike_threshold")
    reset = require_unit(parameters.reset_voltage, MV, "reset_voltage")
    resistance = require_unit(parameters.input_resistance, MOHM, "input_resistance")
    refractory = require_unit(parameters.refractory_period, MS, "refractory_period")
    voltage = require_unit(parameters.initial_voltage, MV, "initial_voltage").value

    if total_time.value < 0:
        raise ValueError("duration cannot be negative.")
    if dt.value <= 0:
        raise ValueError("time_step must be positive.")

    exact_steps = total_time.value / dt.value
    steps = round(exact_steps)
    if not math.isclose(exact_steps, steps, rel_tol=1e-10, abs_tol=1e-10):
        raise ValueError("duration must be an integer multiple of time_step.")

    times: list[float] = [0.0]
    voltages: list[float] = [voltage]
    currents: list[float] = [stimulus.current_at(Quantity(0.0, MS)).to(NA).value]
    spikes: list[float] = []

    last_spike_time: float = -math.inf

    for step in range(1, steps + 1):
        prev_time_ms = (step - 1) * dt.value
        current_time_ms = step * dt.value

        # Check refractory state
        if prev_time_ms < last_spike_time + refractory.value:
            voltage = reset.value
            current_i = stimulus.current_at(Quantity(current_time_ms, MS)).to(NA).value
        else:
            if solver_lower == "euler":
                curr_val = stimulus.current_at(Quantity(prev_time_ms, MS)).to(NA).value
                voltage = step_euler(
                    voltage, curr_val, dt.value, tau.value, rest.value, resistance.value
                )
            elif solver_lower == "rk2":
                c_now = stimulus.current_at(Quantity(prev_time_ms, MS)).to(NA).value
                c_mid = stimulus.current_at(Quantity(prev_time_ms + 0.5 * dt.value, MS)).to(NA).value
                voltage = step_rk2(
                    voltage, c_now, c_mid, dt.value, tau.value, rest.value, resistance.value
                )
            elif solver_lower == "rk4":
                c_now = stimulus.current_at(Quantity(prev_time_ms, MS)).to(NA).value
                c_mid = stimulus.current_at(Quantity(prev_time_ms + 0.5 * dt.value, MS)).to(NA).value
                c_next = stimulus.current_at(Quantity(current_time_ms, MS)).to(NA).value
                voltage = step_rk4(
                    voltage, c_now, c_mid, c_next, dt.value, tau.value, rest.value, resistance.value
                )

            current_i = stimulus.current_at(Quantity(current_time_ms, MS)).to(NA).value

        if voltage >= threshold.value:
            spikes.append(current_time_ms)
            last_spike_time = current_time_ms
            voltage = reset.value

        if not math.isfinite(voltage):
            raise ArithmeticError("Simulation produced a non-finite membrane voltage.")

        times.append(current_time_ms)
        voltages.append(voltage)
        currents.append(current_i)

    metadata = {
        "model": "LIF",
        "solver": solver_lower,
        "time_step_ms": dt.value,
        "duration_ms": total_time.value,
        "membrane_time_constant_ms": tau.value,
        "resting_voltage_mV": rest.value,
        "spike_threshold_mV": threshold.value,
        "reset_voltage_mV": reset.value,
        "input_resistance_MOhm": resistance.value,
        "refractory_period_ms": refractory.value,
    }

    return LIFResult(
        times_ms=tuple(times),
        membrane_voltage_mV=tuple(voltages),
        spike_times_ms=tuple(spikes),
        injected_current_nA=tuple(currents),
        metadata=metadata,
    )
