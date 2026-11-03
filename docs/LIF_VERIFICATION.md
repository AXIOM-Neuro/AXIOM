# LIF mathematical verification

**Scope:** the current-driven leaky integrate-and-fire model in `src/axiom/neuroscience.py` and the integrators in `src/axiom/solvers.py`.
**Verified against:** the closed-form solution of the same ODE, plus a deterministic test suite.
**Environment:** Python 3.12.3, NumPy 2.5.4. `pytest -q` → **46 passed, 6 subtests passed**.

This note verifies that the code solves the equation it claims to solve. It does **not** support any claim of biological realism: a single-compartment point neuron with a hard threshold, instantaneous reset and optional refractory period is a deliberately minimal model.

---

## 1. Model and variables

| Symbol | Meaning | Code | Unit (AXIOM base) |
|---|---|---|---|
| `V` | membrane voltage | `voltage` | mV |
| `t` | time | loop index × `dt` | ms |
| `τ_m` | membrane time constant | `membrane_time_constant` | ms |
| `E_L` | resting/leak potential | `resting_voltage` | mV |
| `R_m` | input resistance | `input_resistance` | MΩ |
| `I` | injected current | `injected_current` | nA |
| `θ` | spike threshold | `spike_threshold` | mV |
| `V_reset` | reset voltage | `reset_voltage` | mV |
| `t_ref` | refractory period | `refractory_period` | ms |
| `dt` | integration step | `time_step` | ms |

## 2. The equation actually integrated

    τ_m dV/dt = (E_L − V) + R_m I          (subthreshold)

In `solvers.py` this appears as

    dv_dt = (rest - v + resistance * current) / tau

which is the same equation divided by `τ_m`. **Verified by inspection and by the closed-form test.**

## 3. Dimensional consistency

Units are millivolt / millisecond / nanoampere / megaohm. The product

    R_m [MΩ] × I [nA] = (10⁶ Ω) × (10⁻⁹ A) = 10⁻³ V = 1 mV

so `R_m · I` is dimensionally a voltage in mV, and `(E_L − V + R_m I)/τ_m` is mV/ms. The code relies on this specific MΩ·nA = mV coincidence and does not perform general dimensional arithmetic inside the solver, so the unit choice is load-bearing and is documented in `LIFParameters.__post_init__` via `require_unit`. Passing a voltage where a time is expected raises `ValueError` (tested).

The `units.py` system does track dimensions explicitly (time, voltage, current exponents) and rejects incompatible conversions on add/subtract/compare. **Note a limitation:** `Quantity.__mul__` combines dimensions but the solver then extracts bare `.value` floats, so dimension checking stops at the solver boundary.

## 4. Closed-form solution and threshold-crossing time

For constant `I`, define the steady state

    V_∞ = E_L + R_m I

Then

    V(t) = V_∞ + (V₀ − V_∞) e^{−t/τ_m}

If `V_∞ > θ` and `V₀ < θ`, the first threshold crossing is

    t* = τ_m ln( (V₀ − V_∞) / (θ − V_∞) )

**Derivation check.** Set `V(t*) = θ`:

    θ − V_∞ = (V₀ − V_∞) e^{−t*/τ_m}
    ⇒ e^{−t*/τ_m} = (θ − V_∞)/(V₀ − V_∞)
    ⇒ t* = −τ_m ln((θ − V_∞)/(V₀ − V_∞)) = τ_m ln((V₀ − V_∞)/(θ − V_∞))  ✓

**Worked case (the repository's example configuration):** `τ=20 ms`, `E_L=−65 mV`, `R=10 MΩ`, `I=2 nA`, `θ=−50 mV`, `V₀=−65 mV`.

    V_∞ = −65 + 20 = −45 mV
    t*  = 20 ln( (−65+45)/(−50+45) ) = 20 ln(20/5) = 20 ln 4 = 27.7259 ms

So with no refractory period and current from `t=0`, spikes fall at **27.73, 55.45, 83.18 ms** — which is what `examples/first_neuron.ax` reports as `(27.7, 55.4, 83.1)`. **Verified.**

With the `StepCurrent` onset at 10 ms and a 2 ms refractory period (the Python demo configuration), the first spike is at `10 + 27.726 = 37.73 ms`, the refractory window runs to `39.73 ms`, and the next spike is at `39.73 + 27.726 = 67.45 ms`. The reported demo values of ≈37.8 and ≈67.6 ms are consistent with this at `dt = 0.1 ms`. **Verified.**

## 5. Boundary cases and behaviour

| Case | Behaviour | Verified by |
|---|---|---|
| `V_∞ ≤ θ` (subthreshold drive) | zero spikes; trace approaches `V_∞` asymptotically | `test_no_spike_when_steady_state_is_subthreshold` |
| `V_∞ > θ` | periodic spiking with period `t*` (+ `t_ref`) | `test_inter_spike_interval_is_period_plus_refractory` |
| `V₀ ≥ θ` | spikes on the first step | `test_refractory_holds_voltage_at_reset` |
| Refractory window | voltage pinned exactly at `V_reset` | same test |
| `θ ≤ V_reset` | rejected at parameter construction | `test_threshold_must_exceed_reset` |
| Non-finite trajectory | raises `ArithmeticError` | existing `test_unstable_simulation_raises_arithmetic_error` |
| `duration` not a multiple of `dt` | `ValueError` rather than silent truncation | `test_duration_must_be_a_multiple_of_step` |
| `dt ≤ 0` | `ValueError` | `test_nonpositive_step_is_rejected` |

## 6. Two documented discretisation limits

1. **Spike times are quantised to the integration step.** The threshold test runs *after* the update, so the recorded spike time is the first sample at or after `t*`. The recorded spike therefore satisfies `|t_spike − t*| ≤ dt`. Measured: the error decreases monotonically as `dt` shrinks (0.5 → 0.1 → 0.01 ms).
2. **The pre-reset peak is never recorded.** `voltages` appends the post-reset value, so the stored trace never contains a value ≥ θ. This is why the test asserts `max(membrane_voltage) < θ` even when spikes occur. Anyone computing a spike-triggered average of "voltage at spike" from this trace would be averaging reset voltages, not threshold crossings — a real trap, now documented.

## 7. Conditions under which the model fails as a model (not as code)

- **No adaptation.** Real neurons show spike-frequency adaptation; this model has none, so sustained current gives a perfectly periodic train.
- **No conductance-based dynamics.** `R_m·I` is a current injection; synaptic input is not modelled, so there is no reversal potential and no shunting inhibition.
- **Hard threshold, instantaneous reset.** No spike shape, no afterhyperpolarisation, no axonal delay.
- **Constant-`τ` leak.** No voltage-dependent channels.
- **Deterministic.** No channel noise; trial-to-trial variability cannot be studied without adding a noise term.
- **Euler instability.** Forward Euler on this linear ODE is stable only for `dt < 2τ_m`; the code does not enforce this, it merely raises when the trajectory becomes non-finite.

## 8. What this supports

> The AXIOM LIF implementation integrates the stated subthreshold ODE correctly, tracks units correctly for the supported base-unit combinations, and implements threshold, reset and refractory bookkeeping with the two discretisation caveats above.

It does not support any statement about biological neurons beyond that.
