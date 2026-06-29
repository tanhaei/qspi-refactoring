# Q-SPI–Guided Human-in-the-Loop Architecture-Smell Refactoring

Reference implementation and reproducibility package for the paper:

> **Human-in-the-Loop Architecture-Smell Refactoring for Safety-Sensitive Health Information Systems: A Q-SPI–Guided Design-Science Framework**
> Mohammad Tanhaei, Department of Engineering, Ilam University.

This repository turns the paper's equations into runnable, tested Python and
regenerates the worked illustrations (Tables 7–8 and Figures 5–6) directly
from the published formulas and parameters. Every numerical input is
**abstracted from the [BioArc](https://bioarc.ir) operational system for
confidentiality**; the computations themselves are exact and reproducible.

[![CI](https://github.com/USER/qspi-refactoring/actions/workflows/ci.yml/badge.svg)](https://github.com/USER/qspi-refactoring/actions)

---

## What the paper is (and is not)

The paper is a **design-science artifact**, not a completed empirical study.
It does not claim that the framework improves quality, safety, cost, or
delivery; it specifies a method and the evidence a future industrial study
would need to collect. This repository respects that boundary exactly:

- **What the code does:** reproduces the Q-SPI metric, the candidate-level
  utility score, and the worked tables/figures, so anyone can verify the
  arithmetic against the equations.
- **What the code does *not* do:** it runs no LLM, applies no patch to
  production, and reports no measured performance. The inputs are abstracted
  illustrative scenarios, not raw repository measurements.

If you are looking for an empirical benchmark of the framework, it does not
exist yet — by design. See [Future evaluation](#future-evaluation).

---

## Key ideas from the paper

The framework keeps a **human in charge of every merge** while using an LLM
only as a constrained assistant. Four principles hold it together:

1. **Evidence-before-generation.** An LLM may propose a change only after a
   versioned evidence bundle (structural evidence, affected interfaces,
   tests, workflow tags, known invariants, open assumptions) is assembled.
2. **Prioritization-without-authorization.** Q-SPI and the utility score are
   *triage* only. A high rank never grants merge authority and cannot
   override a failed protected-invariant check.
3. **Protected-invariant-first verification.** A rule-based deterministic
   gate executes explicit, versioned checks for interfaces, authorization,
   audit semantics, identity, privacy, availability, and migrations —
   rather than asking a model whether a patch is "safe."
4. **Accountable-human closure.** The final decision rests with an
   accountable reviewer (or review group), and the full evidence bundle and
   decision stay in the audit trail.

### The metrics this repo implements

**Q-SPI** discounts apparent schedule performance when a sprint quietly
introduces remediation debt. A sprint can post `SPI ≥ 1` and still be
storing up future rework; Q-SPI makes that visible:

```
SPI_t   = EV_raw,t / PV_t                                    (Eq. 1)
rho_t   = TD_new,t / (beta * EV_raw,t + epsilon)             (Eq. 2)
QF_t    = exp(-lambda * rho_t)                               (Eq. 3)
Q-SPI_t = SPI_t * exp(-lambda * TD_new,t/(beta*EV_raw,t+eps))(Eq. 4)
```

**Candidate utility** ranks a concrete smell candidate `s`:

```
            Delta_QSPI(s) * C_impact(s)
U(s) = ----------------------------------- * F_exp(s) * R_conf(s)   (Eq. 5)
        omega_E*E_ref(s) + omega_R*R_chg(s) + eps

with  omega_E + omega_R = 1,  omega_E, omega_R >= 0
```

Supporting definitions: `Delta_QSPI` (Eq. 6, projected Q-SPI change over a
horizon), `C_impact` (Eq. 7, a weighted protected-workflow impact), and a
net-benefit *template* `NB(s)` (Eq. 8) that must be filled with an
organization's own audited cost estimates — never invented rates.

---

## Repository layout

```
qspi-refactoring/
├── qspi/                     # the library
│   ├── core.py               # Equations (1)–(8), exact implementation
│   ├── model.py              # Candidate, Iteration, rank_candidates (Alg. 1)
│   └── paper_data.py         # Tables 7–8 inputs, abstracted from BioArc
├── scripts/
│   ├── reproduce_tables.py   # regenerates Tables 7 and 8 -> outputs/*.csv
│   └── reproduce_figures.py  # regenerates Figures 5 and 6 -> figures/*.png
├── tests/
│   ├── test_core.py          # equation checks + property + edge-case tests
│   └── test_smoke.py         # end-to-end smoke test
├── outputs/                  # generated CSVs (Tables 7–8)
├── figures/                  # generated PNGs (Figures 5–6)
├── requirements.txt
├── pyproject.toml
└── .github/workflows/ci.yml  # runs tests on Python 3.9–3.12
```

---

## Quick start

```bash
git clone https://github.com/USER/qspi-refactoring.git
cd qspi-refactoring
python -m pip install -r requirements.txt

# Reproduce the paper's tables (prints them and writes CSVs to outputs/)
python scripts/reproduce_tables.py

# Reproduce the paper's figures (writes PNGs to figures/)
python scripts/reproduce_figures.py

# Run the full test suite
pytest -v
```

### Using the library directly

```python
from qspi import qspi, utility_score
from qspi.model import Candidate, rank_candidates

# A debt-heavy sprint: ahead of plan, but introducing 80h of new debt.
print(qspi(ev_raw=120, pv=100, td_new=80, beta=8, lam=3))   # ~0.93

# Rank two candidates under documented governance weights.
cands = [
    Candidate("Extract encounter boundary", 0.12, 0.95, 0.80, 0.75, 0.35, 0.30),
    Candidate("Isolate shared DTO",         0.10, 0.95, 0.60, 0.65, 0.80, 0.70),
]
for rc in rank_candidates(cands, omega_e=0.60, omega_r=0.40):
    print(rc.rank, rc.candidate.name, round(rc.utility, 3))
```

---

## Reproduced results

Running `reproduce_tables.py` regenerates **Table 7** (worked Q-SPI):

| Scenario | PV | EV_raw | TD_new | SPI | rho | Q-SPI |
|---|---:|---:|---:|---:|---:|---:|
| S1: balanced delivery | 100 | 105 | 10 | 1.05 | 0.012 | 1.01 |
| S2: fast delivery | 100 | 115 | 35 | 1.15 | 0.038 | 1.03 |
| S3: accelerated delivery | 100 | 120 | 55 | 1.20 | 0.057 | 1.01 |
| S4: debt-heavy delivery | 100 | 120 | 80 | 1.20 | 0.083 | 0.93 |
| S5: stabilization | 100 | 85 | 10 | 0.85 | 0.015 | 0.81 |

and **Table 8** (candidate prioritization, `omega_E=0.60`, `omega_R=0.40`):

| Rank | Candidate | U(s) |
|---:|---|---:|
| 1 | Extract encounter coordination boundary | 0.207 |
| 2 | Create reporting read model | 0.112 |
| 3 | Refactor integration gateway hub | 0.067 |
| 4 | Isolate shared patient DTO | 0.049 |
| 5 | Consolidate duplicated clinical rule | 0.039 |

> **Erratum note.** The paper prints the last utility as `0.040`, but the
> exact value from Eq. (5) with the published inputs is `0.0394`, which
> rounds to `0.039`. The code computes the correct value; this is a minor
> display-rounding artifact worth fixing in the manuscript.

Figures 5 (`figures/fig5_qspi_sensitivity.png`) and 6
(`figures/fig6_decision_map.png`) are regenerated the same way.

---

## Testing

The suite (`pytest -v`) covers three things:

- **Paper reproduction** — every Q-SPI and utility value is recomputed from
  the formulas and checked against the published tables, including the
  reported ranking order.
- **Mathematical properties** — Q-SPI is bounded above by SPI, strictly
  decreasing in debt density, and collapses to SPI when there is no new
  debt; the quality factor stays in `(0, 1]`.
- **Input validation** — non-positive `PV`, non-positive `epsilon`/`lambda`,
  and weights that do not sum to 1 are rejected rather than silently
  mishandled.

A separate end-to-end **smoke test** runs both reproduction scripts as a
user would and verifies the generated CSVs and PNGs. CI runs everything on
Python 3.9–3.12.

---

## Future evaluation

Per the paper, a credible empirical study would need to: secure data-use
permission; de-identify repositories and workflow labels; freeze the
detector configuration and a Q-SPI calibration rule (units for `PV`, `EV`,
`TD_new`, `beta`); define baselines (manual triage, static-analysis
severity, a non-LLM heuristic, LLM-without-Q-SPI, LLM-without-the-gate,
full framework); use matched candidates as the unit of analysis; and report
effect sizes, confidence intervals, and a sensitivity analysis for the
Q-SPI parameters — alongside negative results. This repository provides the
exact, audited computation such a study would build on; it does not stand in
for the study itself.

---

## Citing

If you use this code, please cite the paper and link this repository. A
`CITATION.cff` is included for GitHub's "Cite this repository" button.

## License

MIT — see [LICENSE](LICENSE). BioArc is an operational system developed and
owned by the author's team ([bioarc.ir](https://bioarc.ir)); the case
material here is abstracted to protect proprietary architecture and
protected health information.
