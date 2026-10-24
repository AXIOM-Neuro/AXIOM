"""Numerical solvers for ordinary differential equations in AXIOM."""

from __future__ import annotations

import math
from typing import Callable


def step_euler(
    v: float,
    current: float,
    dt: float,
    tau: float,
    rest: float,
    resistance: float,
) -> float:
    """Perform one Forward-Euler integration step for subthreshold LIF."""
    dv_dt = (rest - v + resistance * current) / tau
    return v + dv_dt * dt


def step_rk2(
    v: float,
    current_now: float,
    current_mid: float,
    dt: float,
    tau: float,
    rest: float,
    resistance: float,
) -> float:
    """Perform one RK2 (Midpoint) integration step for subthreshold LIF."""
    k1 = (rest - v + resistance * current_now) / tau
    v_mid = v + 0.5 * dt * k1
    k2 = (rest - v_mid + resistance * current_mid) / tau
    return v + dt * k2


def step_rk4(
    v: float,
    current_now: float,
    current_mid: float,
    current_next: float,
    dt: float,
    tau: float,
    rest: float,
    resistance: float,
) -> float:
    """Perform one RK4 integration step for subthreshold LIF."""
    k1 = (rest - v + resistance * current_now) / tau
    v_k2 = v + 0.5 * dt * k1
    k2 = (rest - v_k2 + resistance * current_mid) / tau
    v_k3 = v + 0.5 * dt * k2
    k3 = (rest - v_k3 + resistance * current_mid) / tau
    v_k4 = v + dt * k3
    k4 = (rest - v_k4 + resistance * current_next) / tau
    return v + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


def adex_derivatives(
    v: float,
    w: float,
    current: float,
    c_m: float,
    g_l: float,
    e_l: float,
    delta_t: float,
    v_t: float,
    a: float,
    tau_w: float,
) -> tuple[float, float]:
    """Compute derivatives (dV/dt, dw/dt) for the AdEx model."""
    if delta_t > 0:
        exp_arg = min((v - v_t) / delta_t, 100.0)
        exp_term = g_l * delta_t * math.exp(exp_arg)
    else:
        exp_term = 0.0

    dv_dt = (-g_l * (v - e_l) + exp_term - w + current) / c_m
    dw_dt = (a * (v - e_l) - w) / tau_w
    return dv_dt, dw_dt


def step_adex_euler(
    v: float,
    w: float,
    current: float,
    dt: float,
    c_m: float,
    g_l: float,
    e_l: float,
    delta_t: float,
    v_t: float,
    a: float,
    tau_w: float,
) -> tuple[float, float]:
    """Perform one Forward-Euler integration step for AdEx."""
    dv_dt, dw_dt = adex_derivatives(
        v, w, current, c_m, g_l, e_l, delta_t, v_t, a, tau_w
    )
    return v + dv_dt * dt, w + dw_dt * dt


def step_adex_rk2(
    v: float,
    w: float,
    current_now: float,
    current_mid: float,
    dt: float,
    c_m: float,
    g_l: float,
    e_l: float,
    delta_t: float,
    v_t: float,
    a: float,
    tau_w: float,
) -> tuple[float, float]:
    """Perform one RK2 (Midpoint) integration step for AdEx."""
    kv1, kw1 = adex_derivatives(
        v, w, current_now, c_m, g_l, e_l, delta_t, v_t, a, tau_w
    )
    v_mid = v + 0.5 * dt * kv1
    w_mid = w + 0.5 * dt * kw1
    kv2, kw2 = adex_derivatives(
        v_mid, w_mid, current_mid, c_m, g_l, e_l, delta_t, v_t, a, tau_w
    )
    return v + dt * kv2, w + dt * kw2


def step_adex_rk4(
    v: float,
    w: float,
    current_now: float,
    current_mid: float,
    current_next: float,
    dt: float,
    c_m: float,
    g_l: float,
    e_l: float,
    delta_t: float,
    v_t: float,
    a: float,
    tau_w: float,
) -> tuple[float, float]:
    """Perform one RK4 integration step for AdEx."""
    kv1, kw1 = adex_derivatives(
        v, w, current_now, c_m, g_l, e_l, delta_t, v_t, a, tau_w
    )
    v2, w2 = v + 0.5 * dt * kv1, w + 0.5 * dt * kw1
    kv2, kw2 = adex_derivatives(
        v2, w2, current_mid, c_m, g_l, e_l, delta_t, v_t, a, tau_w
    )
    v3, w3 = v + 0.5 * dt * kv2, w + 0.5 * dt * kw2
    kv3, kw3 = adex_derivatives(
        v3, w3, current_mid, c_m, g_l, e_l, delta_t, v_t, a, tau_w
    )
    v4, w4 = v + dt * kv3, w + dt * kw3
    kv4, kw4 = adex_derivatives(
        v4, w4, current_next, c_m, g_l, e_l, delta_t, v_t, a, tau_w
    )

    v_next = v + (dt / 6.0) * (kv1 + 2.0 * kv2 + 2.0 * kv3 + kv4)
    w_next = w + (dt / 6.0) * (kw1 + 2.0 * kw2 + 2.0 * kw3 + kw4)
    return v_next, w_next
