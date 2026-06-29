#!/usr/bin/env python3
"""
reproduce_figures.py - Regenerate Figures 5 and 6 of the paper.

Figure 5: Q-SPI sensitivity for an assumed SPI = 1.20, across lambda in
          {1, 3, 5}, as debt density ranges over [0, 0.10].
Figure 6: candidate-decision map -- projected quality-adjusted benefit
          (Delta_QSPI) vs. normalized (E_ref + R_chg), with the four
          quadrants the paper describes.

Outputs PNG files into figures/.

Run:
    python scripts/reproduce_figures.py
"""

from __future__ import annotations

import os
import sys

import matplotlib

matplotlib.use("Agg")  # headless / CI-safe backend
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qspi.core import quality_factor
from qspi.paper_data import CANDIDATES

FIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")


def figure_qspi_sensitivity():
    """Figure 5: Q-SPI = SPI * exp(-lambda * rho) for SPI = 1.20."""
    spi_assumed = 1.20
    rho = np.linspace(0.0, 0.10, 200)

    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    for lam, style in zip([1, 3, 5], ["-", "--", "-."]):
        q = spi_assumed * np.array([quality_factor(r, lam) for r in rho])
        ax.plot(rho, q, style, label=f"$\\lambda={lam}$")

    ax.axhline(1.0, color="0.4", linestyle=":", linewidth=1.0,
               label="Plan threshold (Q-SPI = 1)")
    ax.set_xlabel("Debt density $\\rho$")
    ax.set_ylabel("Q-SPI")
    ax.set_title("Q-SPI sensitivity for $SPI = 1.20$")
    ax.set_xlim(0, 0.10)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()

    path = os.path.join(FIG_DIR, "fig5_qspi_sensitivity.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"wrote {path}")


def figure_decision_map():
    """Figure 6: decision map of Delta_QSPI vs. (E_ref + R_chg)."""
    fig, ax = plt.subplots(figsize=(5.6, 4.2))

    xs, ys = [], []
    for i, c in enumerate(CANDIDATES, start=1):
        x = c.e_ref + c.r_chg
        y = c.delta_q
        xs.append(x)
        ys.append(y)
        ax.scatter(x, y, s=60, zorder=3)
        ax.annotate(f"{i}", (x, y), textcoords="offset points",
                    xytext=(6, 4), fontsize=9)

    # Quadrant guides at the medians, echoing the paper's four regions.
    x_mid = float(np.median(xs))
    y_mid = float(np.median(ys))
    ax.axvline(x_mid, color="0.7", linestyle="--", linewidth=1.0)
    ax.axhline(y_mid, color="0.7", linestyle="--", linewidth=1.0)

    ax.set_xlabel("Normalized implementation effort + change risk, "
                  "$E_{ref} + R_{chg}$")
    ax.set_ylabel("Projected quality-adjusted benefit, "
                  "$\\widehat{\\Delta Q}_{SPI}$")
    ax.set_title("Candidate-decision map")

    # Legend mapping numbers to candidate names.
    legend_lines = "\n".join(
        f"{i}. {c.name}" for i, c in enumerate(CANDIDATES, start=1)
    )
    ax.text(1.02, 0.5, legend_lines, transform=ax.transAxes, fontsize=7,
            va="center", ha="left")

    fig.tight_layout()
    path = os.path.join(FIG_DIR, "fig6_decision_map.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {path}")


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    figure_qspi_sensitivity()
    figure_decision_map()
    print("Done. PNGs are in figures/.")


if __name__ == "__main__":
    main()
