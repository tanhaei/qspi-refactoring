#!/usr/bin/env python3
"""
reproduce_tables.py - Regenerate Tables 7 and 8 of the paper.

Recomputes every derived quantity (SPI, rho, Q-SPI, utility) directly from
the published formulas and inputs, prints them as readable tables, and
writes machine-readable CSVs to outputs/. The explanatory/action columns
are carried through as well, so the CSVs reproduce the complete paper rows.

Run:
    python scripts/reproduce_tables.py
"""

from __future__ import annotations

import csv
import os
import sys

# Allow running as `python scripts/reproduce_tables.py` from repo root.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qspi.model import rank_candidates
from qspi.paper_data import (
    BETA,
    CANDIDATES,
    EPSILON,
    ITERATIONS,
    LAMBDA,
    OMEGA_E,
    OMEGA_R,
)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.environ.get("QSPI_OUTPUT_DIR", os.path.join(REPO_ROOT, "outputs"))


def reproduce_qspi_table():
    print("=" * 78)
    print("Table 7  -  Worked Q-SPI illustration")
    print(f"(beta={BETA}, lambda={LAMBDA}, epsilon={EPSILON})")
    print("=" * 78)
    header = (
        f"{'Scenario':30} {'PV':>5} {'EV':>5} {'TD_new':>7} "
        f"{'SPI':>6} {'rho':>8} {'Q-SPI':>7}  Interpretation"
    )
    print(header)
    print("-" * 78)

    rows = []
    for it in ITERATIONS:
        s = it.spi()
        rho = it.debt_density(BETA, EPSILON)
        q = it.qspi(BETA, LAMBDA, EPSILON)
        print(
            f"{it.name:30} {it.pv:5.0f} {it.ev_raw:5.0f} {it.td_new:7.0f} "
            f"{s:6.2f} {rho:8.4f} {q:7.2f}  {it.interpretation}"
        )
        rows.append({
            "scenario": it.name, "PV": it.pv, "EV_raw": it.ev_raw,
            "TD_new": it.td_new, "SPI": round(s, 4),
            "rho": round(rho, 6), "Q_SPI": round(q, 4),
            "interpretation": it.interpretation,
        })

    path = os.path.join(OUT_DIR, "table7_qspi.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\nwrote {path}")
    return rows


def reproduce_priority_table():
    print("\n" + "=" * 78)
    print("Table 8  -  Candidate prioritization")
    print(f"(omega_E={OMEGA_E}, omega_R={OMEGA_R}, epsilon={EPSILON})")
    print("=" * 78)
    header = (f"{'Candidate':40} {'dQ':>5} {'Cimp':>5} {'Fexp':>5} "
              f"{'Rconf':>6} {'Eref':>5} {'Rchg':>5} {'U(s)':>6} {'rank':>4}")
    print(header)
    print("-" * 92)

    ranked = rank_candidates(list(CANDIDATES), OMEGA_E, OMEGA_R, EPSILON)
    rows = []
    for rc in ranked:
        c = rc.candidate
        print(f"{c.name:40} {c.delta_q:5.2f} {c.c_impact:5.2f} {c.f_exp:5.2f} "
              f"{c.r_conf:6.2f} {c.e_ref:5.2f} {c.r_chg:5.2f} "
              f"{rc.utility:6.3f} {rc.rank:4d}")
        rows.append({
            "rank": rc.rank, "candidate": c.name,
            "delta_QSPI": c.delta_q, "C_impact": c.c_impact,
            "F_exp": c.f_exp, "R_conf": c.r_conf, "E_ref": c.e_ref,
            "R_chg": c.r_chg, "utility": round(rc.utility, 4),
            "suggested_action": c.action,
        })

    path = os.path.join(OUT_DIR, "table8_priority.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\nwrote {path}")
    return rows


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    reproduce_qspi_table()
    reproduce_priority_table()
    print("\nDone. CSVs are in outputs/.")


if __name__ == "__main__":
    main()
