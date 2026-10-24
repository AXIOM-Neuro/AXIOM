"""Run a small, illustrative AXIOM LIF simulation using the Python API.

From the repository root:
    python examples/lif_demo.py
"""

from axiom.neuroscience import LIFParameters, simulate_lif
from axiom.stimuli import StepCurrent
from axiom.units import MS, MV, NA, MOHM, Quantity


parameters = LIFParameters(
    membrane_time_constant=Quantity(20, MS),
    resting_voltage=Quantity(-65, MV),
    spike_threshold=Quantity(-50, MV),
    reset_voltage=Quantity(-65, MV),
    input_resistance=Quantity(10, MOHM),
    initial_voltage=Quantity(-65, MV),
    refractory_period=Quantity(2, MS),
)

stimulus = StepCurrent(
    amplitude=Quantity(2, NA),
    start_time=Quantity(10, MS),
    duration=Quantity(80, MS),
)

result = simulate_lif(
    parameters=parameters,
    injected_current=stimulus,
    duration=Quantity(100, MS),
    time_step=Quantity(0.1, MS),
    solver="rk4",
)

print(f"Recorded samples: {len(result.times_ms)}")
print(f"Spike count: {len(result.spike_times_ms)}")
print(f"Spike times (ms): {list(result.spike_times_ms)}")
print(f"Final recorded voltage (mV): {result.membrane_voltage_mV[-1]:.3f}")

result.save_csv("lif_demo_results.csv")
print("Saved results to lif_demo_results.csv")
