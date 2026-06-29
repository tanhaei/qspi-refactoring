"""
qspi: Reference implementation of the Q-SPI metric and candidate-level
utility score from:

    M. Tanhaei, "Human-in-the-Loop Architecture-Smell Refactoring for
    Safety-Sensitive Health Information Systems: A Q-SPI-Guided
    Design-Science Framework."

This package implements Equations (1)-(8) of the paper and reproduces the
worked illustrations (Tables 7-8 and the sensitivity / decision-map
figures). All numerical inputs are abstracted from the BioArc operational
system for confidentiality; the computations themselves are exact and
reproducible from the published formulas.
"""

from .core import (
    spi,
    debt_density,
    quality_factor,
    qspi,
    delta_qspi,
    impact_score,
    utility_score,
    net_benefit,
)
from .model import Candidate, Iteration, rank_candidates

__all__ = [
    "spi",
    "debt_density",
    "quality_factor",
    "qspi",
    "delta_qspi",
    "impact_score",
    "utility_score",
    "net_benefit",
    "Candidate",
    "Iteration",
    "rank_candidates",
]

__version__ = "1.0.0"
