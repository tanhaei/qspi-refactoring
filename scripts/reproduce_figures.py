#!/usr/bin/env python3
"""
reproduce_figures.py - Regenerate Figures 5 and 6 of the paper.

Figure 5: Q-SPI sensitivity for an assumed SPI = 1.20, across lambda in
          {1, 3, 5}, as debt density ranges over [0, 0.10].
Figure 6: candidate-decision map -- projected quality-adjusted benefit
          (Delta_QSPI) vs. normalized (E_ref + R_chg), with the fixed
          decision boundaries and four regions shown in the manuscript.

Outputs preview PNGs and the vector PDFs referenced by the manuscript into
figures/.

Run:
    python scripts/reproduce_figures.py
"""

from __future__ import annotations

import os
import sys

import matplotlib

matplotlib.use("Agg")  # headless / CI-safe backend
matplotlib.rcParams.update({
    "pdf.fonttype": 42,  # embedded TrueType text, suitable for journal PDFs
    "ps.fonttype": 42,
    "svg.fonttype": "none",
})
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qspi.core import quality_factor
from qspi.paper_data import (
    CANDIDATES,
    DECISION_BENEFIT_BOUNDARY,
    DECISION_EFFORT_RISK_BOUNDARY,
)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_DIR = os.environ.get("QSPI_FIGURE_DIR", os.path.join(REPO_ROOT, "figures"))

PDF_METADATA = {
    "Title": "Q-SPI reproducibility figure",
    "Author": "Mohammad Tanhaei",
    "Creator": "qspi-refactoring reproduce_figures.py",
    "CreationDate": None,
    "ModDate": None,
}


def _save_figure(fig, preview_name, manuscript_name):
    """Write a deterministic preview PNG and a journal-ready vector PDF."""
    png_path = os.path.join(FIG_DIR, preview_name)
    pdf_path = os.path.join(FIG_DIR, manuscript_name)
    fig.savefig(png_path, dpi=180, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight", metadata=PDF_METADATA)
    print(f"wrote {png_path}")
    print(f"wrote {pdf_path}")


def figure_qspi_sensitivity():
    """Figure 5: Q-SPI = SPI * exp(-lambda * rho) for SPI = 1.20."""
    spi_assumed = 1.20
    rho = np.linspace(0.0, 0.10, 200)

    fig, ax = plt.subplots(figsize=(5.2, 3.35))
    for lam, style in zip([1, 3, 5], ["-", "--", "-."]):
        q = spi_assumed * np.array([quality_factor(r, lam) for r in rho])
        ax.plot(rho, q, style, label=f"$\\lambda={lam}$")

    ax.axhline(1.0, color="#1f77b4", linestyle="--", linewidth=0.9,
               label="Plan threshold (Q-SPI = 1)")
    ax.set_xlabel("Debt density $\\rho$")
    ax.set_ylabel("Q-SPI")
    ax.set_xlim(0, 0.10)
    ax.set_ylim(0.65, 1.24)
    ax.grid(True, color="0.88", linewidth=0.7)
    ax.legend(frameon=True, framealpha=0.9, fontsize=8, loc="lower left")
    fig.tight_layout(pad=0.5)

    _save_figure(fig, "fig5_qspi_sensitivity.png", "qspi_sensitivity.pdf")
    plt.close(fig)


def figure_decision_map():
    """Figure 6: decision map of Delta_QSPI vs. (E_ref + R_chg)."""
    fig, ax = plt.subplots(figsize=(5.4, 3.9))

    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    for i, c in enumerate(CANDIDATES, start=1):
        x = c.e_ref + c.r_chg
        y = c.delta_q
        color = colors[(i - 1) % len(colors)]
        ax.scatter(x, y, s=72, color=color, edgecolor="white", linewidth=0.8,
                   zorder=4)
        ax.text(x, y, str(i), color="white", ha="center", va="center",
                fontsize=7, fontweight="bold", zorder=5)
        ax.annotate(
            c.figure_label or c.name,
            (x, y),
            textcoords="offset points",
            xytext=(7, 3),
            fontsize=7,
            linespacing=0.9,
        )

    # These are the declared scenario boundaries drawn in the current paper,
    # not medians recomputed from whichever candidate set happens to be loaded.
    ax.axvline(DECISION_EFFORT_RISK_BOUNDARY, color="#1f77b4",
               linestyle="--", linewidth=0.9)
    ax.axhline(DECISION_BENEFIT_BOUNDARY, color="#1f77b4",
               linestyle="--", linewidth=0.9)

    ax.text(0.52, 0.122, "Inspect first", fontsize=7)
    ax.text(1.20, 0.122, "Stage / decompose", fontsize=7)
    ax.text(0.50, 0.043, "Lower priority", fontsize=7)
    ax.text(1.22, 0.043, "Gather evidence", fontsize=7)

    ax.set_xlabel("Normalized implementation effort + change risk, "
                  "$E_{ref} + R_{chg}$")
    ax.set_ylabel("Projected quality-adjusted benefit, "
                  "$\\widehat{\\Delta Q}_{SPI}$")
    ax.set_xlim(0.35, 1.72)
    ax.set_ylim(0.035, 0.135)
    ax.grid(True, color="0.88", linewidth=0.7)
    fig.tight_layout(pad=0.5)

    _save_figure(fig, "fig6_decision_map.png", "priority_decision_map.pdf")
    plt.close(fig)


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    figure_qspi_sensitivity()
    figure_decision_map()
    print("Done. Preview PNGs and manuscript PDFs are in figures/.")


if __name__ == "__main__":
    main()
