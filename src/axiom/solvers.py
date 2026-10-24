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
