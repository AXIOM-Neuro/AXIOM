"""Recording and result abstractions for AXIOM simulations."""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class LIFResult:
    """Recorded output of a LIF simulation in milliseconds and millivolts."""

    times_ms: tuple[float, ...]
    membrane_voltage_mV: tuple[float, ...]
    spike_times_ms: tuple[float, ...]
    injected_current_nA: tuple[float, ...] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if len(self.times_ms) != len(self.membrane_voltage_mV):
            raise ValueError("Time and voltage recordings must have equal length.")
        if self.injected_current_nA is not None and len(self.injected_current_nA) != len(self.times_ms):
            raise ValueError("Injected current recording must match time recording length.")

    def to_dict(self) -> dict[str, Any]:
        """Convert recorded simulation results to a Python dictionary."""
        data: dict[str, Any] = {
            "times_ms": list(self.times_ms),
            "membrane_voltage_mV": list(self.membrane_voltage_mV),
            "spike_times_ms": list(self.spike_times_ms),
            "spike_count": len(self.spike_times_ms),
        }
        if self.injected_current_nA is not None:
            data["injected_current_nA"] = list(self.injected_current_nA)
        if self.metadata:
            data["metadata"] = dict(self.metadata)
        return data

    def save_csv(self, filepath: str | Path) -> None:
        """Export simulation results to a CSV file."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["# AXIOM Simulation Result"])
            writer.writerow([f"# Recorded Samples: {len(self.times_ms)}"])
            writer.writerow([f"# Spike Count: {len(self.spike_times_ms)}"])
            if self.spike_times_ms:
                writer.writerow([f"# Spike Times (ms): {', '.join(f'{t:.3f}' for t in self.spike_times_ms)}"])

            if self.injected_current_nA is not None:
                writer.writerow(["time_ms", "membrane_voltage_mV", "injected_current_nA"])
                for t, v, i in zip(self.times_ms, self.membrane_voltage_mV, self.injected_current_nA):
                    writer.writerow([f"{t:.6g}", f"{v:.6g}", f"{i:.6g}"])
            else:
                writer.writerow(["time_ms", "membrane_voltage_mV"])
                for t, v in zip(self.times_ms, self.membrane_voltage_mV):
                    writer.writerow([f"{t:.6g}", f"{v:.6g}"])

    def to_csv(self, filepath: str | Path) -> None:
        """Alias for save_csv."""
        self.save_csv(filepath)


@dataclass(frozen=True)
class AdExResult:
    """Recorded output of an AdEx simulation."""

    times_ms: tuple[float, ...]
    membrane_voltage_mV: tuple[float, ...]
    adaptation_current_nA: tuple[float, ...]
    spike_times_ms: tuple[float, ...]
    injected_current_nA: tuple[float, ...] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if len(self.times_ms) != len(self.membrane_voltage_mV) or len(self.times_ms) != len(self.adaptation_current_nA):
            raise ValueError("Time, voltage, and adaptation recordings must have equal length.")
        if self.injected_current_nA is not None and len(self.injected_current_nA) != len(self.times_ms):
            raise ValueError("Injected current recording must match time recording length.")

    def to_dict(self) -> dict[str, Any]:
        """Convert recorded simulation results to a Python dictionary."""
        data: dict[str, Any] = {
            "times_ms": list(self.times_ms),
            "membrane_voltage_mV": list(self.membrane_voltage_mV),
            "adaptation_current_nA": list(self.adaptation_current_nA),
            "spike_times_ms": list(self.spike_times_ms),
            "spike_count": len(self.spike_times_ms),
        }
        if self.injected_current_nA is not None:
            data["injected_current_nA"] = list(self.injected_current_nA)
        if self.metadata:
            data["metadata"] = dict(self.metadata)
        return data

    def save_csv(self, filepath: str | Path) -> None:
        """Export AdEx simulation results to a CSV file."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["# AXIOM AdEx Simulation Result"])
            writer.writerow([f"# Recorded Samples: {len(self.times_ms)}"])
            writer.writerow([f"# Spike Count: {len(self.spike_times_ms)}"])
            if self.spike_times_ms:
                writer.writerow([f"# Spike Times (ms): {', '.join(f'{t:.3f}' for t in self.spike_times_ms)}"])

            if self.injected_current_nA is not None:
                writer.writerow(["time_ms", "membrane_voltage_mV", "adaptation_current_nA", "injected_current_nA"])
                for t, v, w, i in zip(self.times_ms, self.membrane_voltage_mV, self.adaptation_current_nA, self.injected_current_nA):
                    writer.writerow([f"{t:.6g}", f"{v:.6g}", f"{w:.6g}", f"{i:.6g}"])
            else:
                writer.writerow(["time_ms", "membrane_voltage_mV", "adaptation_current_nA"])
                for t, v, w in zip(self.times_ms, self.membrane_voltage_mV, self.adaptation_current_nA):
                    writer.writerow([f"{t:.6g}", f"{v:.6g}", f"{w:.6g}"])

    def to_csv(self, filepath: str | Path) -> None:
        """Alias for save_csv."""
        self.save_csv(filepath)
