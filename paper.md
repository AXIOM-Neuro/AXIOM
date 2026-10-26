# AXIOM: A Python-Powered Domain-Specific Language for Computational Neuroscience

**Folarera Ayobami Kassim**  
*Independent Researcher*  
Email: <folarera.kassim@gmail.com>  
ORCID: [0009-0007-2148-5675](https://orcid.org/0009-0007-2148-5675)  
AXIOM-Neuro · [GitHub repository](https://github.com/AXIOM-Neuro/AXIOM)

## Abstract

Computational neuroscience relies on software for representing neuronal dynamics, defining stimulation protocols, integrating differential equations, and recording simulation outputs. Research workflows can require users to combine scientific models with general-purpose programming interfaces, numerical solvers, and data-management code. AXIOM is an open-source, Python-powered software project intended to provide a neuroscience-oriented interface to these tasks.

The reported version 0.1.0 release includes a domain-specific `.ax` language and a Python interface, alongside a leaky integrate-and-fire neuron model, numerical integration, stimulus definitions, physical quantities, simulation recording, CSV export, and command-line execution. The reported baseline test suite contains 31 tests covering language interpretation, scientific and solver behavior, stimuli, units, command-line functionality, and recording.

These tests provide an initial software-verification baseline, not proof of broad scientific validity. This paper describes AXIOM's design goals, architecture, interfaces, verification status, and current limitations. Numerical convergence, performance relative to established simulation frameworks, usability, and suitability for large-scale network simulations require further evaluation.

**Keywords:** computational neuroscience; scientific software; Python; domain-specific language; neuronal dynamics; numerical simulation

# Introduction

Computational neuroscience uses mathematical and computational models to investigate neuronal activity, neural systems, and mechanisms of information processing. Such work often involves defining model parameters, specifying input currents or stimuli, numerically solving differential equations, and inspecting recorded state variables. Scientific software therefore affects the transparency and reproducibility of computational experiments.

General-purpose programming languages provide flexibility, but researchers may need additional code to express scientific models and manage simulation workflows. Established simulators and modeling environments address many of these needs, with different interfaces and abstractions for different use cases [Brette et al., 2007; Gerstner et al., 2014].

AXIOM is an open-source project exploring a Python-powered, neuroscience-oriented programming interface. Its goal is to make selected computational neuroscience tasks expressible through a readable domain-specific language (DSL), while retaining access to Python’s scientific ecosystem.

This paper describes the reported scope of AXIOM version 0.1.0. It does not claim that AXIOM introduces a new neuronal theory or has demonstrated scientific superiority over established simulators.

The contributions of this paper are:

1. A description of AXIOM’s intended role and architecture.

2. An overview of its language, model, solver, stimulus, unit, and recording components.

3. A summary of the reported software-test baseline.

4. An account of current limitations and further validation needs.

# Design Goals

AXIOM is organized around four design goals.

## Readable scientific expressions

The `.ax` interface is intended to express selected simulation operations in a compact, neuroscience-oriented form. Readability is a design objective; whether the language improves learning or reduces errors requires evaluation with representative users.

## Python interoperability

Python provides access to a mature scientific ecosystem for numerical computing, data analysis, and visualization. AXIOM is designed to work within this ecosystem rather than replace Python as a general-purpose language.

## Explicit simulation workflows

Model definitions, numerical integration, stimulus application, and recording should be identifiable parts of the computational workflow. Making these stages explicit can help users inspect how a simulation is configured and how its outputs are generated.

## Incremental extensibility

The initial release provides a limited foundation on which additional models, analysis utilities, and simulation capabilities may be built. Not every desired computational neuroscience feature is implemented in the current release.

# Software Overview

AXIOM version 0.1.0 is associated with the public repository:

[https://github.com/AXIOM-Neuro/AXIOM](https://github.com/AXIOM-Neuro/AXIOM)

The project identifies its package as `axiom-science` and uses Python as its implementation environment. The reported functional areas include:

- **Language interface:** Interprets supported AXIOM-language input.
- **Neuroscience model:** Provides a leaky integrate-and-fire (LIF) neuron implementation.
- **Numerical solvers:** Includes Forward Euler, RK2, and RK4.
- **Stimuli:** Represents supported stimulus and input definitions.
- **Units:** Provides representations for supported physical quantities.
- **Recording:** Collects simulation outputs and supports CSV export.
- **Command line:** Exposes selected functionality through a CLI.

This list describes the reported release scope. It does not establish that all combinations of components, units, models, and solvers have been exhaustively tested.

# Architecture

AXIOM separates language interpretation from scientific computation and output handling. This separation is intended to support inspection and incremental extension.

## Language interpretation

The interpreter processes AXIOM-language input and connects supported language constructs to Python functionality. The DSL is not assumed to be a complete general-purpose language; its supported syntax and semantics are determined by the implementation.

## Scientific models

The neuroscience component contains the LIF model described in the section *Neuronal Model*. This model provides a tractable starting point for checking simulation behavior against analytical expectations.

## Numerical integration

The solver component provides multiple numerical integration methods. Their accuracy, stability, and computational costs depend on the problem, parameters, and implementation. Availability alone does not establish that the methods are interchangeable or accurate for every model.

## Stimuli and units

Stimulus definitions describe inputs supplied to simulations. The units component represents supported physical quantities. Correct unit handling requires valid representations and appropriate checks at operation boundaries; comprehensive dimensional analysis should not be assumed without dedicated tests.

## Recording and command-line execution

Recording functionality collects selected outputs for inspection and export. The command-line interface provides an alternative to direct Python use for supported workflows. Exact behavior is determined by the corresponding release implementation.

# Installation and Execution

The repository is the authoritative source for installation instructions, dependencies, and supported commands. A typical development installation uses an editable install:

```bash
python -m pip install -e .
```

This command assumes it is run from the project directory containing the package metadata.

Where supported, the command-line interface can be inspected with:

```bash
python -m axiom --help
```

Users should consult the repository for the exact entry points, command syntax, and dependency requirements.

# Language and Python Interfaces

AXIOM provides a domain-specific language intended to represent supported computational neuroscience workflows. A DSL can reduce repetitive syntax for a narrow task, but it also requires precise documentation of parsing rules, types, errors, and execution semantics.

The following is illustrative pseudocode, not a verified example of the exact syntax accepted by version 0.1.0:

    # Illustrative pseudocode; verify against the release grammar.
    neuron = LIF(
        resting_potential = -65 * mV,
        threshold = -50 * mV,
        membrane_time_constant = 20 * ms
    )

    stimulus = ConstantCurrent(0.5 * nA)
    result = simulate(neuron, stimulus, duration=100 * ms)
    record(result, "simulation.csv")

The Python interface allows supported operations to be invoked from Python programs. This can support integration with external analysis and visualization tools, provided the relevant objects and functions are available in the installed release.

Before publication, this illustrative example should be replaced with a verified, executable example from a pinned release.

# Neuronal Model

The LIF neuron is a common simplified model used to represent subthreshold membrane dynamics and threshold-triggered spiking [Gerstner et al., 2014]. One standard formulation is

$$\tau_m \frac{dV}{dt} = E_L - V(t) + R I(t)$$

where $\tau_m$ is the membrane time constant, $E_L$ is the leak or resting potential, $R$ is an effective membrane resistance, and $I(t)$ is the input current.

When membrane voltage reaches a specified threshold $V_{\mathrm{th}}$, the model emits a spike and applies the configured reset and refractory behavior. Exact behavior depends on event detection, reset conventions, and refractory-period semantics.

The equation above describes a standard model formulation; it does not establish that every implementation detail in AXIOM matches every published LIF convention. Those details must be specified and tested explicitly.

# Numerical Integration

AXIOM’s reported solver set includes Forward Euler, RK2, and RK4. For an initial-value problem

$$\frac{dy}{dt}=f(t,y),$$

Forward Euler advances the solution according to

$$y_{n+1}=y_n+h f(t_n,y_n),$$

where $h$ is the integration step.

Higher-order Runge–Kutta methods evaluate the derivative at additional points within a step to improve formal accuracy under appropriate smoothness assumptions [Hairer et al., 1993]. Practical accuracy depends on the problem, step size, implementation, and treatment of discontinuities or threshold events.

Spiking models require particular care because threshold crossings, resets, and refractory intervals can introduce nonsmooth behavior. A solver’s formal order for smooth differential equations does not automatically imply the same order of accuracy for spike times.

Numerical validation should compare simulated trajectories with analytical solutions where available, examine step-size convergence, test threshold-event timing, and detect unstable or non-finite outputs.

# Units and Stimulus Definitions

Physical units can help users identify quantities such as voltage, time, current, and resistance. Dimensional consistency matters because numerically valid operations may still represent physically invalid equations.

Validation of a unit-aware interface should establish which units are supported, how conversions are performed, how incompatible operations are handled, and whether unit metadata is preserved through simulation and export.

Stimulus components provide inputs to modeled systems. Their scientific meaning depends on their mathematical definitions, temporal behavior, parameter conventions, and interaction with the solver. Each supported stimulus type should be documented and tested independently.

# Recording and Reproducibility

AXIOM’s recording and CSV-export functionality provides a route for storing simulation data in a format that can be inspected by external tools.

A reproducible computational experiment should record, where applicable:

- software and dependency versions;

- model parameters and initial conditions;

- stimulus definitions and random seeds, if applicable;

- solver selection and integration step size;

- simulation duration and event-handling conventions;

- recorded variables, units, and output-column meanings.

CSV export alone does not guarantee reproducibility. Metadata needed to interpret an output file should be documented or stored alongside the data.

# Software Verification

The project reports a baseline suite of 31 tests for version 0.1.0, recorded on 24 October 2026. The reported distribution is summarized in Table 1.

**Table 1. Reported baseline test distribution.**

| Area | Number of tests |
|:--|--:|
| Language interpreter | 10 |
| Solvers and scientific behavior | 3 |
| Stimuli | 4 |
| Units | 7 |
| Command-line interface and recording | 7 |
| **Total** | **31** |

The reported scientific tests include analytical agreement for subthreshold behavior, refractory holding, and detection of unstable simulation behavior. These are useful initial checks, but a small test suite cannot establish general correctness across all parameter regimes or use cases.

The test result is reported project evidence, not an independent reproduction performed for this manuscript. Before publication, the authors should rerun the tests against the exact release commit and record the command, environment, output, and commit identifier.

## Known validation concerns

The current development notes identify several points requiring explicit attention:

- An initially threshold-crossing state may have its spike recorded at the first integration step rather than at $t=0$. The intended event-time convention should be documented and tested.

- Refractory-period boundary behavior requires explicit tests.

- Non-finite inputs and broader numerical edge cases require further validation.

- Numerical convergence and accuracy across multiple step sizes have not been established comprehensively.

These concerns are material to scientific interpretation and should be resolved or documented before AXIOM is recommended for research requiring precise event timing or validated numerical accuracy.

# Limitations and Future Work

AXIOM is an early-stage software project. The current release should be distinguished from capabilities that may be planned for future development.

First, the initial model scope is limited. A LIF implementation does not provide the range of conductance-based, multicompartment, stochastic, or network models required by many research questions.

Second, numerical correctness requires more than the availability of multiple solvers. Systematic convergence studies, event-time validation, tests across parameter ranges, and comparisons with independent reference implementations remain necessary.

Third, usability has not been established through a controlled study. Claims that the language improves accessibility, reduces programming errors, or shortens research workflows require suitable user evaluations.

Fourth, performance relative to established simulators has not been measured in this paper. No claims are made about runtime, memory use, scalability, or suitability for large-scale networks.

Fifth, reproducibility depends on versioning, dependency management, complete model specifications, and clear output semantics.

Priority areas for future work include:

1. Formal documentation of the DSL grammar and execution semantics.

2. Verified, executable examples for each supported interface.

3. Expanded tests for event timing, refractory boundaries, invalid inputs, and numerical edge cases.

4. Convergence studies against analytical solutions and trusted reference implementations.

5. Reproducible benchmarks against established tools using equivalent models and simulation settings.

6. User studies evaluating learnability, usability, and error rates.

7. Clearer provenance metadata for simulation outputs.

# Conclusion

AXIOM is an open-source, Python-powered project developing a neuroscience-oriented programming interface for selected simulation tasks. Its reported initial functionality includes a domain-specific language, a Python interface, a leaky integrate-and-fire model, numerical solvers, stimulus definitions, unit-related functionality, recording, and CSV export.

The reported 31-test baseline provides an initial foundation for software verification, but it does not establish broad scientific validity, numerical convergence, usability, or performance advantages. AXIOM should be understood as an early-stage scientific software project whose potential depends on transparent specification, reproducible examples, rigorous numerical validation, and comparison with existing tools.

# Software Availability

- **Project:** AXIOM

- **Repository:** <https://github.com/AXIOM-Neuro/AXIOM>

- **Reported version:** 0.1.0

- **Package name:** `axiom-science`

- **License:** MIT, as identified by the project

For archival publication, provide a version-specific release or immutable commit identifier and confirm the license and package metadata against that exact version.

# Author Contributions

The author contributed to the AXIOM software and manuscript. This statement should be revised if other contributors made substantive contributions to the work.

# Funding

No funding information is asserted in this manuscript. Add an appropriate statement if funding supported the work.

# Competing Interests

The author should declare any relevant competing interests or state that none exist, as appropriate.

# Acknowledgements

Acknowledgements may be added for individuals or organizations that provided substantive assistance.

## References

1. Gerstner, W., Kistler, W. M., Naud, R., & Paninski, L. (2014). *Neuronal Dynamics: From Single Neurons to Networks and Models of Cognition*. Cambridge University Press. [https://neuronaldynamics.epfl.ch/](https://neuronaldynamics.epfl.ch/)
2. Brette, R., et al. (2007). Simulation of networks of spiking neurons: A review of tools and strategies. *Journal of Computational Neuroscience, 23*, 349–398. [https://doi.org/10.1007/s10827-007-0038-6](https://doi.org/10.1007/s10827-007-0038-6)
3. Hairer, E., Nørsett, S. P., & Wanner, G. (1993). *Solving Ordinary Differential Equations I: Nonstiff Problems* (2nd revised ed.). Springer. [https://doi.org/10.1007/978-3-540-78862-1](https://doi.org/10.1007/978-3-540-78862-1)
4. AXIOM-Neuro contributors. *AXIOM: Python-Powered Computational Neuroscience*. Software repository. [https://github.com/AXIOM-Neuro/AXIOM](https://github.com/AXIOM-Neuro/AXIOM)
