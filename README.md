# AXIOM

### Readable scientific programming for computational neuroscience.

AXIOM is an experimental, Python-powered programming language designed to make computational neuroscience and scientific computing easier to express, understand, and validate.

Our goal is simple: **scientific code should be readable by humans, precise enough for computers, and transparent about its assumptions.**

> **Development status:** Early development. The language specification and initial interpreter are being developed. Features will be documented as they are implemented and tested.

## Why AXIOM?

Scientific programming often requires researchers to combine mathematical models, numerical methods, data analysis, and experimental workflows. AXIOM aims to bring these elements together in a language designed around the way scientists think and work.

- **Readable by design** — express scientific procedures using clear, descriptive syntax.
- **Neuroscience-focused** — build toward neuron models, neural networks, and brain-signal analysis.
- **Reproducible experiments** — make parameters, simulation settings, and outputs explicit.
- **Scientific transparency** — document assumptions, numerical methods, limitations, and validation results.
- **Python-powered** — build on the Python ecosystem for numerical computing and scientific data analysis.

## Design philosophy

AXIOM is being developed around five principles:

1. **Clarity over cleverness.** Code should communicate its purpose without unnecessary syntactic complexity.
2. **Explicit assumptions.** Models and experiments should make important choices visible.
3. **Validation over assertion.** Numerical results should be checked against appropriate references and tests.
4. **Reproducibility by design.** Experiments should record the settings needed to understand and reproduce their results.
5. **Honest scientific claims.** A successful program execution is not, by itself, evidence that a scientific model accurately describes reality.

## A glimpse of the intended syntax

The following example illustrates the readability we want AXIOM to achieve. It is a design sketch, not yet executable AXIOM code.

```
experiment "My First Neuron"

neuron "Example Neuron":
    membrane_time = 20 ms
    spike_threshold = 1 mV
    reset_voltage = 0 mV

simulate for 1 second
    using time_step 1 ms

show membrane_voltage
show spike_times

save results to "neuron_results.csv"
```

The intended experience is straightforward: define a model, specify an experiment, observe its behavior, and save the results.

## Initial development goals

The first development milestones are:

- [ ] Define the language grammar and syntax.
- [ ] Implement a tokenizer, parser, and interpreter in Python.
- [ ] Support basic expressions, parameters, and useful error messages.
- [ ] Implement a minimal leaky integrate-and-fire neuron model.
- [ ] Record membrane voltage and spike events.
- [ ] Export simulation results to CSV.
- [ ] Add automated tests and independent numerical reference checks.
- [ ] Document installation, usage, limitations, and validation results.

These are development goals, not claims that the features are already implemented.

## Technology

AXIOM is being developed using Python. As the project evolves, it may integrate established scientific libraries for numerical computation, data processing, and visualization.

The language itself will have its own syntax and execution rules rather than simply renaming ordinary Python code.

## Intended applications

AXIOM is being designed to support future work in:

- Computational neuroscience and neuron modeling
- Neural network simulations
- EEG and brain–computer interface data analysis
- Scientific experiments and parameter sweeps
- Numerical analysis and reproducible computational research

These are intended application areas; their inclusion here does not imply that each is currently supported.

## Project structure

The repository is expected to grow toward a structure like this:

```text
axiom-language/
├── README.md
├── axiom.py
├── examples/
│   └── first_neuron.ax
├── tests/
│   └── test_axiom.py
└── docs/
    └── LANGUAGE_SPEC.md
```

Files will be added as their implementations become available.

## Contributing

AXIOM is in its early stages, and its language design is still evolving. Contributions and constructive feedback on readability, scientific correctness, numerical methods, and software architecture will be valuable as the project develops.

Before proposing a feature, consider:

- Does it make scientific code easier to understand?
- Can its behavior be specified unambiguously?
- Can its implementation be tested?
- Are its scientific assumptions and limitations documented?

## Scientific responsibility

AXIOM is a research and software-development project. Its outputs must be interpreted according to the underlying model, numerical method, data quality, and validation evidence. Simulations are not automatically biological evidence, and numerical agreement with a reference does not establish that a model is biologically accurate.

## License

MIT License

---

**AXIOM — Make scientific computation clearer.**
