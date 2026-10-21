"""Run a small, illustrative AXIOM LIF simulation.

From the repository root:
    PYTHONPATH=axiom-language/src python examples/lif_demo.py
"""

from axiom.neuroscience import LIFParameters, simulate_lif
from axiom.units import MS, MV, NA, MOHM, Quantity


parameters = LIFParameters(
    membrane_time_constant=Quantity(20, MS),
    resting_voltage=Quantity(-65, MV),
    spike_threshold=Quantity(-50, MV),
    reset_voltage=Quantity(-65, MV),
    input_resistance=Quantity(10, MOHM),
    initial_voltage=Quantity(-65, MV),
)

result = simulate_lif(
    parameters=parameters,
    injected_current=Quantity(2, NA),
    duration=Quantity(100, MS),
    time_step=Quantity(0.1, MS),
)

print(f"Recorded samples: {len(result.times_ms)}")
print(f"Spike count: {len(result.spike_times_ms)}")
print(f"Spike times (ms): {list(result.spike_times_ms)}")
print(f"Final recorded voltage (mV): {result.membrane_voltage_mV[-1]:.3f}")
