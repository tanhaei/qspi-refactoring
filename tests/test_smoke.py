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

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(REPO_ROOT, "scripts")


def _run(script, **environment):
    """Run a script with the repo root on PYTHONPATH; return CompletedProcess."""
    env = dict(os.environ, PYTHONPATH=REPO_ROOT, **environment)
    return subprocess.run(
        [sys.executable, os.path.join(SCRIPTS, script)],
        capture_output=True, text=True, env=env, cwd=REPO_ROOT,
    )


def test_reproduce_tables_runs_and_writes_csv(tmp_path):
    result = _run("reproduce_tables.py", QSPI_OUTPUT_DIR=str(tmp_path))
    assert result.returncode == 0, result.stderr

    t7 = tmp_path / "table7_qspi.csv"
    t8 = tmp_path / "table8_priority.csv"
    assert t7.exists()
    assert t8.exists()

    # Table 7 should have 5 scenarios, Q-SPI present and finite.
    with t7.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 5
    for r in rows:
        assert float(r["Q_SPI"]) > 0
        assert r["interpretation"]

    # Table 8 should have 5 candidates, sorted by descending utility.
    with t8.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 5
    utils = [float(r["utility"]) for r in rows]
    assert utils == sorted(utils, reverse=True)
    assert rows[0]["candidate"] == "Extract encounter coordination boundary"


def test_reproduce_figures_runs_and_writes_png_and_pdf(tmp_path):
    result = _run("reproduce_figures.py", QSPI_FIGURE_DIR=str(tmp_path),
                  MPLCONFIGDIR=str(tmp_path / "mpl"))
    assert result.returncode == 0, result.stderr

    files = [
        tmp_path / "fig5_qspi_sensitivity.png",
        tmp_path / "fig6_decision_map.png",
        tmp_path / "qspi_sensitivity.pdf",
        tmp_path / "priority_decision_map.pdf",
    ]
    for path in files:
        assert path.exists()
        assert path.stat().st_size > 1000
    for path in files[2:]:
        assert path.read_bytes().startswith(b"%PDF-")


def test_package_imports_cleanly():
    """The public API named in __init__ is importable."""
    import qspi
    for name in [
        "spi", "debt_density", "quality_factor", "qspi", "delta_qspi",
        "impact_score", "utility_score", "net_benefit",
        "Candidate", "Iteration", "rank_candidates",
    ]:
        assert hasattr(qspi, name), f"missing public symbol: {name}"
