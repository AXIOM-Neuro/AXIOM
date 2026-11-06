#pragma once

// Stable C ABI for AXIOM's optional C++ numerical backend.
// Units: time in ms, voltage in mV, current in nA, resistance in MOhm.

#if defined(_WIN32)
  #if defined(AXIOM_CPP_BUILD)
    #define AXIOM_API __declspec(dllexport)
  #else
    #define AXIOM_API __declspec(dllimport)
  #endif
#else
  #define AXIOM_API __attribute__((visibility("default")))
#endif

#ifdef __cplusplus
extern "C" {
#endif

// solver: 0 = Forward Euler, 1 = RK2 midpoint, 2 = RK4.
// Returns 0 on success; nonzero values indicate invalid input, an unsupported
// solver, or a non-finite result. output_voltage must point to writable memory.
AXIOM_API int axiom_lif_step(
    int solver,
    double voltage_mV,
    double current_now_nA,
    double current_mid_nA,
    double current_next_nA,
    double dt_ms,
    double tau_ms,
    double resting_voltage_mV,
    double input_resistance_MOhm,
    double* output_voltage_mV
) noexcept;

#ifdef __cplusplus
}
#endif
