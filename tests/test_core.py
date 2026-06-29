"""
test_core.py - Unit tests for Equations (1)-(8) and their stated properties.

These tests check three things:
  1. the code reproduces the paper's published numbers (Tables 7-8);
  2. the mathematical properties the paper claims actually hold
     (monotonicity, the SPI upper bound, etc.);
  3. invalid inputs are rejected rather than silently mishandled.
"""

import math

import pytest

from qspi.core import (
    DEFAULT_EPSILON,
    debt_density,
    delta_qspi,
    impact_score,
    net_benefit,
    qspi,
    quality_factor,
    spi,
    utility_score,
)
from qspi.model import Candidate, Iteration, rank_candidates
from qspi import paper_data as pd


# --------------------------------------------------------------------------
# 1. Reproduction of the paper's numbers
# --------------------------------------------------------------------------

def test_table7_qspi_matches_paper():
    """Recomputed Q-SPI matches Table 7 to 2 decimal places."""
    for it in pd.ITERATIONS:
        q = it.qspi(pd.BETA, pd.LAMBDA, pd.EPSILON)
        expected = pd.PAPER_QSPI_ROUNDED[it.name]
        assert round(q, 2) == expected, f"{it.name}: {q} vs {expected}"


def test_table7_spi_values():
    """SPI column of Table 7."""
    expected = {
        "S1: balanced delivery": 1.05,
        "S2: fast delivery": 1.15,
        "S3: accelerated delivery": 1.20,
        "S4: debt-heavy delivery": 1.20,
        "S5: stabilization": 0.85,
    }
    for it in pd.ITERATIONS:
        assert round(it.spi(), 2) == expected[it.name]


def test_table8_utility_matches_paper():
    """Recomputed utility matches Table 8 to 3 decimal places.

    Note: the paper prints the last candidate as 0.040, but the exact value
    is 0.0394 -> 0.039. paper_data records the correct 0.039.
    """
    for c in pd.CANDIDATES:
        u = c.utility(pd.OMEGA_E, pd.OMEGA_R, pd.EPSILON)
        expected = pd.PAPER_UTILITY_ROUNDED[c.name]
        assert round(u, 3) == expected, f"{c.name}: {u} vs {expected}"


def test_table8_ranking_order():
    """The ranking the paper reports (encounter > reporting > gateway >
    DTO > rule) is reproduced."""
    ranked = rank_candidates(list(pd.CANDIDATES), pd.OMEGA_E, pd.OMEGA_R)
    names = [rc.candidate.name for rc in ranked]
    assert names == [
        "Extract encounter coordination boundary",
        "Create reporting read model",
        "Refactor integration gateway hub",
        "Isolate shared patient DTO",
        "Consolidate duplicated clinical rule",
    ]


# --------------------------------------------------------------------------
# 2. Mathematical properties claimed in the paper
# --------------------------------------------------------------------------

def test_qspi_bounded_above_by_spi():
    """Paper: Q-SPI is 'bounded above by SPI_t'."""
    for ev, pv, td in [(105, 100, 10), (120, 100, 80), (85, 100, 10)]:
        s = spi(ev, pv)
        q = qspi(ev, pv, td, beta=8, lam=3)
        assert q <= s + 1e-12


def test_qspi_monotonic_decreasing_in_debt():
    """Paper: Q-SPI is 'increasingly sensitive to higher debt density' --
    i.e. strictly decreasing as TD_new grows, all else equal."""
    prev = float("inf")
    for td in [0, 10, 25, 50, 100, 200]:
        q = qspi(ev_raw=120, pv=100, td_new=td, beta=8, lam=3)
        assert q < prev
        prev = q


def test_quality_factor_in_unit_interval():
    """QF = exp(-lambda*rho) lies in (0, 1] for rho >= 0."""
    for rho in [0.0, 0.01, 0.05, 0.2, 1.0]:
        qf = quality_factor(rho, lam=3)
        assert 0.0 < qf <= 1.0


def test_zero_debt_gives_qspi_equals_spi():
    """With no new debt, Q-SPI collapses to SPI (QF ~ 1)."""
    q = qspi(ev_raw=100, pv=100, td_new=0, beta=8, lam=3)
    assert math.isclose(q, 1.0, abs_tol=1e-3)


def test_delta_qspi_is_difference():
    assert delta_qspi(1.05, 0.95) == pytest.approx(0.10)


def test_impact_score_weighted_sum():
    indicators = [0.9, 0.8, 0.7, 0.6, 0.5]
    weights = [0.2, 0.2, 0.2, 0.2, 0.2]
    assert impact_score(indicators, weights) == pytest.approx(0.70)


def test_net_benefit_template():
    nb = net_benefit(10, 5, 3, 4, 2, 1, 1)
    assert nb == pytest.approx(10 + 5 + 3 - 4 - 2 - 1 - 1)


# --------------------------------------------------------------------------
# 3. Input validation / edge cases
# --------------------------------------------------------------------------

def test_spi_rejects_nonpositive_pv():
    with pytest.raises(ValueError):
        spi(100, 0)
    with pytest.raises(ValueError):
        spi(100, -5)


def test_debt_density_rejects_nonpositive_epsilon():
    with pytest.raises(ValueError):
        debt_density(10, 100, beta=8, epsilon=0)


def test_quality_factor_rejects_nonpositive_lambda():
    with pytest.raises(ValueError):
        quality_factor(0.05, lam=0)


def test_impact_weights_must_sum_to_one():
    with pytest.raises(ValueError):
        impact_score([0.5, 0.5], [0.5, 0.4])


def test_impact_weights_must_be_nonnegative():
    with pytest.raises(ValueError):
        impact_score([0.5, 0.5], [1.5, -0.5])


def test_utility_weights_must_sum_to_one():
    with pytest.raises(ValueError):
        utility_score(0.1, 0.9, 0.8, 0.75, 0.35, 0.30,
                      omega_e=0.6, omega_r=0.5)


def test_utility_weights_must_be_nonnegative():
    with pytest.raises(ValueError):
        utility_score(0.1, 0.9, 0.8, 0.75, 0.35, 0.30,
                      omega_e=1.2, omega_r=-0.2)


def test_default_epsilon_value():
    """The default epsilon matches the paper's worked table (1e-3)."""
    assert DEFAULT_EPSILON == 1e-3
