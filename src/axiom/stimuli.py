"""Stimulus abstractions for AXIOM simulations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import math

from axiom.units import HZ, MS, NA, Quantity, require_unit


class Stimulus(ABC):
    """Abstract base class for all stimulation patterns."""

    @abstractmethod
    def current_at(self, time: Quantity) -> Quantity:
        """Return the injected current at the specified time quantity."""


@dataclass(frozen=True)
class ConstantCurrent(Stimulus):
    """Constant input current over the entire simulation duration."""

    amplitude: Quantity

    def __post_init__(self) -> None:
        require_unit(self.amplitude, NA, "amplitude")

    def current_at(self, time: Quantity) -> Quantity:
        require_unit(time, MS, "time")
        return self.amplitude


@dataclass(frozen=True)
class StepCurrent(Stimulus):
    """Current step starting at start_time and lasting for duration."""

    amplitude: Quantity
    start_time: Quantity = Quantity(0, MS)
    duration: Quantity | None = None

    def __post_init__(self) -> None:
        require_unit(self.amplitude, NA, "amplitude")
        t_start = require_unit(self.start_time, MS, "start_time")
        if t_start.value < 0:
            raise ValueError("start_time cannot be negative.")
        if self.duration is not None:
            dur = require_unit(self.duration, MS, "duration")
            if dur.value < 0:
                raise ValueError("duration cannot be negative.")

    def current_at(self, time: Quantity) -> Quantity:
        t = require_unit(time, MS, "time").value
        t_start = require_unit(self.start_time, MS, "start_time").value

        if t < t_start:
            return Quantity(0.0, NA)

        if self.duration is not None:
            dur = require_unit(self.duration, MS, "duration").value
            if t >= t_start + dur:
                return Quantity(0.0, NA)

        return self.amplitude


@dataclass(frozen=True)
class PulseTrainCurrent(Stimulus):
    """Train of current pulses."""

    amplitude: Quantity
    start_time: Quantity
    pulse_duration: Quantity
    frequency: Quantity
    num_pulses: int

    def __post_init__(self) -> None:
        require_unit(self.amplitude, NA, "amplitude")
        t_start = require_unit(self.start_time, MS, "start_time")
        p_dur = require_unit(self.pulse_duration, MS, "pulse_duration")
        require_unit(self.frequency, HZ, "frequency")

        freq = require_unit(self.frequency, HZ, "frequency")

        if t_start.value < 0:
            raise ValueError("start_time cannot be negative.")
        if p_dur.value <= 0:
            raise ValueError("pulse_duration must be positive.")
        if freq.value <= 0:
            raise ValueError("frequency must be positive.")
        if self.num_pulses <= 0:
            raise ValueError("num_pulses must be a positive integer.")

        period_ms = 1000.0 / freq.to(HZ).value
        if p_dur.to(MS).value > period_ms + 1e-9:
            raise ValueError(
                f"pulse_duration ({p_dur.to(MS).value} ms) cannot exceed pulse period ({period_ms} ms)."
            )

    def current_at(self, time: Quantity) -> Quantity:
        t = require_unit(time, MS, "time").value
        t_start = require_unit(self.start_time, MS, "start_time").value
        p_dur = require_unit(self.pulse_duration, MS, "pulse_duration").value

        freq_hz = self.frequency.to(HZ).value
        if freq_hz <= 0:
            return Quantity(0.0, NA)

        period_ms = 1000.0 / freq_hz

        if t < t_start:
            return Quantity(0.0, NA)

        time_since_start = t - t_start
        # Use small rounding epsilon to avoid floating-point floor errors at exact pulse period multiples
        pulse_index = int(math.floor(round(time_since_start / period_ms, 9)))

        if 0 <= pulse_index < self.num_pulses:
            time_in_pulse = time_since_start - pulse_index * period_ms
            # Boundary convention: [t_k, t_k + pulse_duration)
            if 0 <= time_in_pulse < p_dur - 1e-12:
                return self.amplitude

        return Quantity(0.0, NA)


@dataclass(frozen=True)
class CombinedStimulus(Stimulus):
    """Linear superposition of multiple stimuli."""

    stimuli: tuple[Stimulus, ...]

    def __init__(self, stimuli: list[Stimulus] | tuple[Stimulus, ...]) -> None:
        object.__setattr__(self, "stimuli", tuple(stimuli))

    def current_at(self, time: Quantity) -> Quantity:
        total_value = 0.0
        for s in self.stimuli:
            total_value += s.current_at(time).to(NA).value
        return Quantity(total_value, NA)
