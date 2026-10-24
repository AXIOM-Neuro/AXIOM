# AXIOM Research Bibliography

This document contains an annotated bibliography of scientific publications, textbook references, and software architecture literature supporting AXIOM's models, numerical algorithms, and language design.

---

## 1. Single-Neuron Dynamics & Spike Models

### Brette, R., & Gerstner, W. (2005)
- **Title:** Adaptive exponential integrate-and-fire model as an effective description of neuronal activity.
- **Journal:** *Journal of Neurophysiology*, 94(5), 3637–3642.
- **DOI:** [10.1152/jn.00686.2005](https://doi.org/10.1152/jn.00686.2005)
- **Topic:** Formulation of the two-variable Adaptive Exponential Integrate-and-Fire (AdEx) neuron model.
- **AXIOM Design Impact:** Directly supports AXIOM's `AdExParameters` and `simulate_adex()` implementations, providing parameters for subthreshold adaptation ($a$), spike-triggered adaptation ($b$), and exponential slope factor ($\Delta_T$).

### Naud, R., Marcille, N., Clopath, C., & Gerstner, W. (2008)
- **Title:** Firing patterns in the adaptive exponential integrate-and-fire model.
- **Journal:** *Biological Cybernetics*, 99(4-5), 335–347.
- **DOI:** [10.1007/s00422-008-0264-7](https://doi.org/10.1007/s00422-008-0264-7)
- **Topic:** Classification of firing regimes (tonic spiking, adaptation, bursting, initial bursting) in AdEx models.
- **AXIOM Design Impact:** Used to validate spike train outputs and adaptation current trajectories across different current step inputs.

### Lapicque, L. (1907)
- **Title:** Recherches quantitatives sur l'excitation électrique des nerfs traitée comme une polarization.
- **Journal:** *Journal of Physiologie et de Pathologie Générale*, 9, 620–635.
- **Topic:** Classical Leaky Integrate-and-Fire (LIF) model derivation.
- **AXIOM Design Impact:** Serves as the historical and mathematical baseline for AXIOM's subthreshold membrane equation $\tau_m dV/dt = E_L - V + R_m I(t)$.

---

## 2. Numerical Methods & Scientific Computing

### Press, W. H., Teukolsky, S. A., Vetterling, W. T., & Flannery, B. P. (2007)
- **Title:** *Numerical Recipes: The Art of Scientific Computing* (3rd ed.).
- **Publisher:** Cambridge University Press.
- **Topic:** Numerical integration routines for initial value problems, Runge-Kutta formulations, and stability bounds.
- **AXIOM Design Impact:** Guides the implementation of Forward Euler, RK2 (Midpoint), and classical RK4 integration kernels in `axiom.solvers`.

---

## 3. Computational Neuroscience Software Architectures

### Goodman, D. F., & Brette, R. (2008)
- **Title:** Brian: a simulator for spiking neural networks in Python.
- **Journal:** *Frontiers in Neuroinformatics*, 2, 5.
- **DOI:** [10.3389/neuro.11.005.2008](https://doi.org/10.3389/neuro.11.005.2008)
- **Topic:** Design principles for user-friendly, unit-aware spiking neural network simulation environments in Python.
- **AXIOM Design Impact:** Informs AXIOM's explicit physical unit system and human-readable domain-specific DSL abstractions.
