"""
core.py - Exact implementation of the paper's equations.

Each function maps to a numbered equation in the manuscript. Equation
numbers are given in the docstrings so a reader can check the code against
the paper line by line.

Default numerical constant epsilon = 1e-3, matching the worked Q-SPI
illustration (Table 7), where beta = 8 and lambda = 3.
"""

from __future__ import annotations

import math
from typing import Sequence

# Small numerical constant used in the debt-density denominator (Eq. 2).
# The paper's worked Q-SPI table uses epsilon = 1e-3.
DEFAULT_EPSILON: float = 1e-3


def spi(ev_raw: float, pv: float) -> float:
    """Conventional schedule performance index, Equation (1).

        SPI_t = EV_raw,t / PV_t          (PV_t > 0)

    Parameters
    ----------
    ev_raw : conventional earned value for the iteration.
    pv     : planned value for the iteration (must be > 0).

    Raises
    ------
    ValueError if pv <= 0. The paper notes that iterations with PV = 0
    (or EV_raw = 0) must be handled separately rather than interpreted
    through an inflated ratio.
    """
    if pv <= 0:
        raise ValueError("PV must be > 0 to compute SPI (Eq. 1).")
    return ev_raw / pv


def debt_density(
    td_new: float,
    ev_raw: float,
    beta: float,
    epsilon: float = DEFAULT_EPSILON,
) -> float:
    """Debt-density term rho_t, Equation (2).

        rho_t = TD_new,t / (beta * EV_raw,t + epsilon)

    Parameters
    ----------
    td_new  : estimated remediation effort (person-hours) for debt
              introduced during the iteration.
    ev_raw  : conventional earned value for the iteration.
    beta    : converts one unit of earned value into estimated engineering
              person-hours.
    epsilon : small numerical constant (> 0).

    Notes
    -----
    The paper states that iterations with EV_raw = 0 should be handled
    separately. We do not silently divide; if beta*EV_raw + epsilon would
    be non-positive we raise.
    """
    if epsilon <= 0:
        raise ValueError("epsilon must be > 0 (Eq. 2).")
    denom = beta * ev_raw + epsilon
    if denom <= 0:
        raise ValueError(
            "Non-positive denominator in debt density; handle EV_raw = 0 "
            "iterations separately (Eq. 2)."
        )
    return td_new / denom


def quality_factor(rho: float, lam: float) -> float:
    """Quality factor QF_t, Equation (3).

        QF_t = exp(-lambda * rho_t),   lambda > 0
    """
    if lam <= 0:
        raise ValueError("lambda must be > 0 (Eq. 3).")
    return math.exp(-lam * rho)


def qspi(
    ev_raw: float,
    pv: float,
    td_new: float,
    beta: float,
    lam: float,
    epsilon: float = DEFAULT_EPSILON,
) -> float:
    """Quality-Adjusted Schedule Performance Index, Equation (4).

        Q-SPI_t = SPI_t * exp(-lambda * TD_new,t / (beta*EV_raw,t + eps))

    This is SPI_t (Eq. 1) multiplied by the quality factor (Eq. 3) whose
    argument is the debt density (Eq. 2). The result is monotonic in debt
    density and bounded above by SPI_t.
    """
    s = spi(ev_raw, pv)
    rho = debt_density(td_new, ev_raw, beta, epsilon)
    return s * quality_factor(rho, lam)


def delta_qspi(qspi_candidate: float, qspi_baseline: float) -> float:
    """Projected Q-SPI change over a horizon H, Equation (6).

        Delta_QSPI(s; H) = Q-SPI^(s)_{t+H} - Q-SPI^(baseline)_{t+H}

    Both arguments are projected Q-SPI values at the end of the horizon:
    one for the candidate scenario, one for the baseline scenario.
    """
    return qspi_candidate - qspi_baseline


def impact_score(indicators: Sequence[float], weights: Sequence[float]) -> float:
    """Protected-workflow impact, Equation (7).

        C_impact(s) = sum_j w_j * I_j(s),   sum_j w_j = 1

    Parameters
    ----------
    indicators : indicator values I_j (e.g. patient-data sensitivity,
                 external-integration exposure, audit relevance, privacy
                 impact, availability impact).
    weights    : non-negative weights w_j that must sum to 1.
    """
    if len(indicators) != len(weights):
        raise ValueError("indicators and weights must have equal length (Eq. 7).")
    if any(w < 0 for w in weights):
        raise ValueError("weights must be non-negative (Eq. 7).")
    if not math.isclose(sum(weights), 1.0, abs_tol=1e-9):
        raise ValueError("weights must sum to 1 (Eq. 7).")
    return sum(w * i for w, i in zip(weights, indicators))


def utility_score(
    delta_q: float,
    c_impact: float,
    f_exp: float,
    r_conf: float,
    e_ref: float,
    r_chg: float,
    omega_e: float,
    omega_r: float,
    epsilon: float = DEFAULT_EPSILON,
) -> float:
    """Candidate-level utility score U(s), Equation (5).

        U(s) = [ Delta_QSPI(s) * C_impact(s) ]
               / [ omega_E * E_ref(s) + omega_R * R_chg(s) + eps ]
               * F_exp(s) * R_conf(s)

        with omega_E + omega_R = 1 and omega_E, omega_R >= 0.

    The score is a triage aid only; per the paper it confers no authority
    to merge a change.
    """
    if omega_e < 0 or omega_r < 0:
        raise ValueError("omega_E and omega_R must be non-negative (Eq. 5).")
    if not math.isclose(omega_e + omega_r, 1.0, abs_tol=1e-9):
        raise ValueError("omega_E + omega_R must equal 1 (Eq. 5).")
    denom = omega_e * e_ref + omega_r * r_chg + epsilon
    return (delta_q * c_impact / denom) * f_exp * r_conf


def net_benefit(
    b_maint: float,
    b_speed: float,
    b_risk: float,
    c_llm: float,
    c_review: float,
    c_test: float,
    c_rollback: float,
) -> float:
    """Candidate-level net-benefit template, Equation (8).

        NB(s) = B_maint + B_speed + B_risk
                - C_llm - C_review - C_test - C_rollback

    The paper stresses that this is a decision *template*: it must not be
    populated with invented rates. It is provided here so that an adopting
    organization can plug in its own audited estimates.
    """
    return (
        b_maint
        + b_speed
        + b_risk
        - c_llm
        - c_review
        - c_test
        - c_rollback
    )
