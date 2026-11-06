#include "axiom/lif.hpp"

#include <cassert>
#include <cmath>
#include <iostream>
#include <limits>

int main() {
    double output = 0.0;

    // Euler: dV/dt = (-65 - (-60) + 10*1) / 20 = 0.25 mV/ms.
    int status = axiom_lif_step(
        0, -60.0, 1.0, 1.0, 1.0,
        0.1, 20.0, -65.0, 10.0, &output
    );
    assert(status == 0);
    assert(std::abs(output - (-59.975)) < 1e-12);

    // Constant-current RK2 and RK4 agree for this linear autonomous ODE
    // to within their expected numerical truncation error.
    double rk2 = 0.0;
    double rk4 = 0.0;
    assert(axiom_lif_step(
        1, -60.0, 1.0, 1.0, 1.0,
        0.1, 20.0, -65.0, 10.0, &rk2
    ) == 0);
    assert(axiom_lif_step(
        2, -60.0, 1.0, 1.0, 1.0,
        0.1, 20.0, -65.0, 10.0, &rk4
    ) == 0);
    assert(std::abs(rk2 - rk4) < 1e-6);

    assert(axiom_lif_step(
        9, -60.0, 1.0, 1.0, 1.0,
        0.1, 20.0, -65.0, 10.0, &output
    ) == 2);
    assert(axiom_lif_step(
        0, -60.0, 1.0, 1.0, 1.0,
        0.0, 20.0, -65.0, 10.0, &output
    ) == 1);
    assert(axiom_lif_step(
        0, std::numeric_limits<double>::quiet_NaN(), 1.0, 1.0, 1.0,
        0.1, 20.0, -65.0, 10.0, &output
    ) == 1);
    assert(axiom_lif_step(
        0, -60.0, 1.0, 1.0, 1.0,
        0.1, 20.0, -65.0, 10.0, nullptr
    ) == 1);

    std::cout << "AXIOM C++ kernel tests passed\\n";
    return 0;
}
