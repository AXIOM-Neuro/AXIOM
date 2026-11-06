#include "axiom/lif.hpp"

#include <cmath>

namespace {

bool finite_inputs(
    double voltage,
    double current_now,
    double current_mid,
    double current_next,
    double dt,
    double tau,
    double rest,
    double resistance
) noexcept {
    return std::isfinite(voltage)
        && std::isfinite(current_now)
        && std::isfinite(current_mid)
        && std::isfinite(current_next)
        && std::isfinite(dt)
        && std::isfinite(tau)
        && std::isfinite(rest)
        && std::isfinite(resistance);
}

inline double derivative(
    double voltage,
    double current,
    double tau,
    double rest,
    double resistance
) noexcept {
    // With mV, nA, and MOhm: MOhm * nA = mV.
    return (rest - voltage + resistance * current) / tau;
}

} // namespace

extern "C" AXIOM_API int axiom_lif_step(
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
) noexcept {
    if (output_voltage_mV == nullptr) {
        return 1;
    }

    if (!finite_inputs(
        voltage_mV,
        current_now_nA,
        current_mid_nA,
        current_next_nA,
        dt_ms,
        tau_ms,
        resting_voltage_mV,
        input_resistance_MOhm
    ) || dt_ms <= 0.0 || tau_ms <= 0.0 || input_resistance_MOhm <= 0.0) {
        return 1;
    }

    double next_voltage = voltage_mV;

    switch (solver) {
        case 0: { // Forward Euler
            const double k1 = derivative(
                voltage_mV, current_now_nA, tau_ms,
                resting_voltage_mV, input_resistance_MOhm
            );
            next_voltage = voltage_mV + dt_ms * k1;
            break;
        }
        case 1: { // Explicit midpoint RK2
            const double k1 = derivative(
                voltage_mV, current_now_nA, tau_ms,
                resting_voltage_mV, input_resistance_MOhm
            );
            const double midpoint_voltage = voltage_mV + 0.5 * dt_ms * k1;
            const double k2 = derivative(
                midpoint_voltage, current_mid_nA, tau_ms,
                resting_voltage_mV, input_resistance_MOhm
            );
            next_voltage = voltage_mV + dt_ms * k2;
            break;
        }
        case 2: { // Classical RK4
            const double k1 = derivative(
                voltage_mV, current_now_nA, tau_ms,
                resting_voltage_mV, input_resistance_MOhm
            );
            const double k2 = derivative(
                voltage_mV + 0.5 * dt_ms * k1, current_mid_nA,
                tau_ms, resting_voltage_mV, input_resistance_MOhm
            );
            const double k3 = derivative(
                voltage_mV + 0.5 * dt_ms * k2, current_mid_nA,
                tau_ms, resting_voltage_mV, input_resistance_MOhm
            );
            const double k4 = derivative(
                voltage_mV + dt_ms * k3, current_next_nA,
                tau_ms, resting_voltage_mV, input_resistance_MOhm
            );
            next_voltage = voltage_mV + (dt_ms / 6.0)
                * (k1 + 2.0 * k2 + 2.0 * k3 + k4);
            break;
        }
        default:
            return 2;
    }

    if (!std::isfinite(next_voltage)) {
        return 3;
    }

    *output_voltage_mV = next_voltage;
    return 0;
}
