"""
paper_data.py - The numerical scenarios published in the paper.

Every value here is abstracted from the BioArc operational system for
confidentiality, exactly as stated in the manuscript. They are reproduced
so that anyone can regenerate Tables 7-8 and the figures and check the
arithmetic against Equations (1)-(5).

Scenario parameters (Section 6.3 / Table 7 caption):
    beta    = 8     person-hours per unit of earned value
    lambda  = 3
    epsilon = 1e-3

Governance weights (Table 8 caption):
    omega_E = 0.60
    omega_R = 0.40
"""

from .model import Candidate, Iteration

# --- Scenario parameters (Table 7 caption) ---------------------------------
BETA: float = 8.0
LAMBDA: float = 3.0
EPSILON: float = 1e-3

# --- Governance weights (Table 8 caption) ----------------------------------
OMEGA_E: float = 0.60
OMEGA_R: float = 0.40


# --- Table 7: worked Q-SPI illustration ------------------------------------
# Columns: name, PV, EV_raw, TD_new (person-hours).
# The paper also prints SPI, rho and Q-SPI; those are recomputed by the code
# rather than hard-coded, so the table is a genuine reproduction.
ITERATIONS = [
    Iteration(name="S1: balanced delivery", pv=100, ev_raw=105, td_new=10),
    Iteration(name="S2: fast delivery", pv=100, ev_raw=115, td_new=35),
    Iteration(name="S3: accelerated delivery", pv=100, ev_raw=120, td_new=55),
    Iteration(name="S4: debt-heavy delivery", pv=100, ev_raw=120, td_new=80),
    Iteration(name="S5: stabilization", pv=100, ev_raw=85, td_new=10),
]

# Q-SPI values as rounded for display in the paper's Table 7. Used only by
# the test-suite as a cross-check that our recomputation matches the
# published figures (to 2 decimal places).
PAPER_QSPI_ROUNDED = {
    "S1: balanced delivery": 1.01,
    "S2: fast delivery": 1.03,
    "S3: accelerated delivery": 1.01,
    "S4: debt-heavy delivery": 0.93,
    "S5: stabilization": 0.81,
}


# --- Table 8: illustrative candidate prioritization ------------------------
# Columns: name, Delta_QSPI, C_impact, F_exp, R_conf, E_ref, R_chg, action.
CANDIDATES = [
    Candidate(
        name="Extract encounter coordination boundary",
        delta_q=0.12, c_impact=0.95, f_exp=0.80, r_conf=0.75,
        e_ref=0.35, r_chg=0.30,
        action="inspect first, but require contract and audit tests.",
    ),
    Candidate(
        name="Create reporting read model",
        delta_q=0.08, c_impact=0.70, f_exp=0.70, r_conf=0.80,
        e_ref=0.30, r_chg=0.25,
        action="phased candidate; preserve authorization and audit semantics.",
    ),
    Candidate(
        name="Refactor integration gateway hub",
        delta_q=0.07, c_impact=0.85, f_exp=0.90, r_conf=0.70,
        e_ref=0.60, r_chg=0.50,
        action="investigate after dependency and ownership evidence improves.",
    ),
    Candidate(
        name="Isolate shared patient DTO",
        delta_q=0.10, c_impact=0.95, f_exp=0.60, r_conf=0.65,
        e_ref=0.80, r_chg=0.70,
        action="high impact but higher risk; use staged boundary extraction.",
    ),
    Candidate(
        name="Consolidate duplicated clinical rule",
        delta_q=0.06, c_impact=0.90, f_exp=0.50, r_conf=0.60,
        e_ref=0.45, r_chg=0.35,
        action="candidate for controlled rule-provenance work.",
    ),
]

# Relative utility values printed in the paper's Table 8 (rounded to 3 dp).
# Cross-checked by the test-suite.
#
# NOTE: the last candidate is printed as 0.040 in the paper, but the exact
# value from Eq. (5) with the published inputs is 0.0394, which rounds to
# 0.039. The code computes the correct 0.039; the 0.040 in the manuscript
# is a minor display-rounding artifact worth fixing before submission.
PAPER_UTILITY_ROUNDED = {
    "Extract encounter coordination boundary": 0.207,
    "Create reporting read model": 0.112,
    "Refactor integration gateway hub": 0.067,
    "Isolate shared patient DTO": 0.049,
    "Consolidate duplicated clinical rule": 0.039,  # paper prints 0.040
}
