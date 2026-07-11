"""
model.py - Data structures and the candidate-selection logic.

`Iteration` corresponds to one row of the worked Q-SPI table (Table 7).
`Candidate` corresponds to one row of the prioritization table (Table 8).
`rank_candidates` implements the numerical scoring-and-sorting portion of
Algorithm 1. Evidence collection, policy versioning, the deterministic
safety gate, and accountable review remain organizational controls and are
deliberately not simulated by this numerical reference package.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from .core import DEFAULT_EPSILON, qspi, utility_score


@dataclass(frozen=True)
class Iteration:
    """One sprint/iteration of delivery and debt data (Table 7).

    Attributes
    ----------
    name    : human-readable scenario label.
    pv      : planned value.
    ev_raw  : conventional earned value.
    td_new  : estimated remediation effort (person-hours) for newly
              introduced debt.
    interpretation : explanatory text printed in the worked paper table.
    """

    name: str
    pv: float
    ev_raw: float
    td_new: float
    interpretation: str = ""

    def spi(self) -> float:
        from .core import spi as _spi
        return _spi(self.ev_raw, self.pv)

    def debt_density(self, beta: float, epsilon: float = DEFAULT_EPSILON) -> float:
        from .core import debt_density as _dd
        return _dd(self.td_new, self.ev_raw, beta, epsilon)

    def qspi(self, beta: float, lam: float, epsilon: float = DEFAULT_EPSILON) -> float:
        return qspi(self.ev_raw, self.pv, self.td_new, beta, lam, epsilon)


@dataclass(frozen=True)
class Candidate:
    """One architecture-smell candidate (Table 8).

    All six evidence inputs are on a normalized 0-1 scale, exactly as the
    paper specifies in its operationalization table (Table 4).

    Attributes
    ----------
    name      : candidate label.
    delta_q   : projected Q-SPI change over the declared horizon
                (Delta_QSPI, Eq. 6), normalized.
    c_impact  : protected-workflow impact (Eq. 7), in [0, 1].
    f_exp     : workflow / change exposure, in [0, 1].
    r_conf    : evidence confidence, in [0, 1].
    e_ref     : normalized refactoring effort, in [0, 1].
    r_chg     : normalized change risk, in [0, 1].
    action    : optional suggested action text from the paper's Table 8.
    figure_label : optional compact label used in the paper's decision map.
    """

    name: str
    delta_q: float
    c_impact: float
    f_exp: float
    r_conf: float
    e_ref: float
    r_chg: float
    action: str = ""
    figure_label: str = ""

    def utility(
        self,
        omega_e: float,
        omega_r: float,
        epsilon: float = DEFAULT_EPSILON,
    ) -> float:
        """Utility score U(s) for this candidate (Eq. 5)."""
        return utility_score(
            delta_q=self.delta_q,
            c_impact=self.c_impact,
            f_exp=self.f_exp,
            r_conf=self.r_conf,
            e_ref=self.e_ref,
            r_chg=self.r_chg,
            omega_e=omega_e,
            omega_r=omega_r,
            epsilon=epsilon,
        )


@dataclass
class RankedCandidate:
    """A candidate paired with its computed utility, for reporting."""

    candidate: Candidate
    utility: float
    rank: int = 0


def rank_candidates(
    candidates: Sequence[Candidate],
    omega_e: float,
    omega_r: float,
    epsilon: float = DEFAULT_EPSILON,
) -> List[RankedCandidate]:
    """Score and sort the candidate rows used by Algorithm 1.

    This function covers only the numerical portion of the published
    algorithm. It returns a ranked backlog, not an evidence bundle, gate
    result, or merge authorization. Per the paper, its output remains
    subject to deterministic safety-gate and accountable-review rules.
    """
    scored = [
        RankedCandidate(candidate=c, utility=c.utility(omega_e, omega_r, epsilon))
        for c in candidates
    ]
    scored.sort(key=lambda rc: rc.utility, reverse=True)
    for i, rc in enumerate(scored, start=1):
        rc.rank = i
    return scored
