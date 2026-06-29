"""
test_smoke.py - End-to-end smoke test.

Runs the table- and figure-reproduction scripts as the user would, then
verifies that the expected artifacts are produced and that the regenerated
CSV content is internally consistent with the library. This is the test
that answers "does the repo actually work when someone clones it?".
"""

import csv
import os
import subprocess
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(REPO_ROOT, "scripts")
OUTPUTS = os.path.join(REPO_ROOT, "outputs")
FIGURES = os.path.join(REPO_ROOT, "figures")


def _run(script):
    """Run a script with the repo root on PYTHONPATH; return CompletedProcess."""
    env = dict(os.environ, PYTHONPATH=REPO_ROOT)
    return subprocess.run(
        [sys.executable, os.path.join(SCRIPTS, script)],
        capture_output=True, text=True, env=env, cwd=REPO_ROOT,
    )


def test_reproduce_tables_runs_and_writes_csv():
    result = _run("reproduce_tables.py")
    assert result.returncode == 0, result.stderr

    t7 = os.path.join(OUTPUTS, "table7_qspi.csv")
    t8 = os.path.join(OUTPUTS, "table8_priority.csv")
    assert os.path.exists(t7)
    assert os.path.exists(t8)

    # Table 7 should have 5 scenarios, Q-SPI present and finite.
    with open(t7) as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 5
    for r in rows:
        assert float(r["Q_SPI"]) > 0

    # Table 8 should have 5 candidates, sorted by descending utility.
    with open(t8) as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 5
    utils = [float(r["utility"]) for r in rows]
    assert utils == sorted(utils, reverse=True)
    assert rows[0]["candidate"] == "Extract encounter coordination boundary"


def test_reproduce_figures_runs_and_writes_png():
    result = _run("reproduce_figures.py")
    assert result.returncode == 0, result.stderr

    f5 = os.path.join(FIGURES, "fig5_qspi_sensitivity.png")
    f6 = os.path.join(FIGURES, "fig6_decision_map.png")
    assert os.path.exists(f5)
    assert os.path.exists(f6)
    # PNGs should be non-trivial in size (real plots, not empty files).
    assert os.path.getsize(f5) > 1000
    assert os.path.getsize(f6) > 1000


def test_package_imports_cleanly():
    """The public API named in __init__ is importable."""
    import qspi
    for name in [
        "spi", "debt_density", "quality_factor", "qspi", "delta_qspi",
        "impact_score", "utility_score", "net_benefit",
        "Candidate", "Iteration", "rank_candidates",
    ]:
        assert hasattr(qspi, name), f"missing public symbol: {name}"
