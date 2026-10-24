# AXIOM Scientific Validation Plan

This document establishes the mathematical foundations, differential equations, numerical solver verification criteria, and validation standards for AXIOM neuroscience models.

---

## 1. Implemented Equations & Mathematical Models

### 1.1 Leaky Integrate-and-Fire (LIF) Model

The current-driven LIF subthreshold membrane dynamics are governed by:

\[
\tau_m \frac{dV}{dt} = E_L - V + R_m I(t)
\]

where:
- \(V(t)\): Membrane potential (\(\text{mV}\))
- \(E_L\): Resting potential (\(\text{mV}\))
- \(\tau_m\): Membrane time constant (\(\text{ms}\))
- \(R_m\): Input resistance (\(\text{MOhm}\))
- \(I(t)\): Injected current (\(\text{nA}\))

#### Spike & Reset Event Rule
When \(V(t) \ge V_{\text{th}}\):
1. A spike timestamp \(t_{\text{spike}} = t\) is recorded.
2. Membrane potential resets immediately: \(V(t) \to V_{\text{reset}}\).
3. For refractory duration \(t_{\text{ref}}\), \(V(t)\) remains clamped at \(V_{\text{reset}}\).

#### Analytical Solution (Subthreshold Constant Current \(I_0\))
For constant current injection \(I_0\) without spiking:

\[
V(t) = V_{\text{steady}} + \left(V(0) - V_{\text{steady}}\right) e^{-t / \tau_m}
\]

where \(V_{\text{steady}} = E_L + R_m I_0\).

---

### 1.2 Adaptive Exponential Integrate-and-Fire (AdEx) Model

The two-variable AdEx model (Brette & Gerstner, 2005; Naud et al., 2008) incorporates exponential spike initiation and adaptation dynamics:

\[
C_m \frac{dV}{dt} = -g_L (V - E_L) + g_L \Delta_T \exp\left(\frac{V - V_T}{\Delta_T}\right) - w + I(t)
\]

\[
\tau_w \frac{dw}{dt} = a (V - E_L) - w
\]

where:
- \(C_m\): Membrane capacitance (\(\text{nF}\))
- \(g_L\): Leak conductance (\(\mu\text{S}\) or \(\text{nF}/\text{ms}\))
- \(\Delta_T\): Slope factor (\(\text{mV}\))
- \(V_T\): Effective threshold potential (\(\text{mV}\))
- \(w\): Adaptation current (\(\text{nA}\))
- \(\tau_w\): Adaptation time constant (\(\text{ms}\))
- \(a\): Subthreshold adaptation coupling parameter (\(\mu\text{S}\) or \(\text{nA}/\text{mV}\))
- \(b\): Spike-triggered adaptation increment (\(\text{nA}\))

#### Reset & Adaptation Rule
When \(V(t) \ge V_{\text{peak}}\):
1. Spike timestamp \(t_{\text{spike}} = t\) is recorded.
2. \(V(t) \to V_{\text{reset}}\)
3. \(w(t) \to w(t) + b\)

---

## 2. Numerical Integration & Convergence Standards

AXIOM provides explicit ODE integration routines:

1. **Forward Euler (1st order):** Global error \(O(\Delta t)\).
2. **Explicit Midpoint / RK2 (2nd order):** Global error \(O(\Delta t^2)\).
3. **Runge–Kutta RK4 (4th order):** Global error \(O(\Delta t^4)\).

### Verification Acceptance Criteria
- **Subthreshold Accuracy:** For RK4 with \(\Delta t = 0.01\text{ ms}\), numerical voltage must match the analytical solution to within \(10^{-4}\text{ mV}\).
- **Convergence Verification:** Halving time step \(\Delta t \to \Delta t / 2\) must reduce numerical error proportionally to the solver order.
- **Numerical Stability:** Time steps exceeding numerical stability limits must raise an explicit `ArithmeticError` when non-finite states occur.
