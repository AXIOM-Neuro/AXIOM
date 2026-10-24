"""Simulate an Adaptive Exponential Integrate-and-Fire (AdEx) neuron in Python."""

from axiom.neuroscience import AdExParameters, simulate_adex
from axiom.stimuli import StepCurrent
from axiom.units import MS, MV, NA, NS, PF, Quantity

params = AdExParameters(
    capacitance=Quantity(200, PF),
    leak_conductance=Quantity(10, NS),
    resting_voltage=Quantity(-70, MV),
    slope_factor=Quantity(2, MV),
    threshold_voltage=Quantity(-50, MV),
    peak_voltage=Quantity(0, MV),
    reset_voltage=Quantity(-58, MV),
    adaptation_coupling=Quantity(2, NS),
    spike_triggered_adaptation=Quantity(0.01, NA),
    adaptation_time_constant=Quantity(30, MS),
)

stimulus = StepCurrent(
    amplitude=Quantity(0.5, NA),
    start_time=Quantity(10, MS),
    duration=Quantity(80, MS),
)

result = simulate_adex(
    parameters=params,
    injected_current=stimulus,
    duration=Quantity(100, MS),
    time_step=Quantity(0.1, MS),
    solver="rk4",
)

print(f"Recorded AdEx samples: {len(result.times_ms)}")
print(f"Spike count: {len(result.spike_times_ms)}")
print(f"Spike times (ms): {list(result.spike_times_ms)}")

result.save_csv("adex_demo_results.csv")
print("Saved results to adex_demo_results.csv")
