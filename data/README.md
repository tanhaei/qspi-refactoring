# Data

All numerical scenarios live in `qspi/paper_data.py` as typed Python
objects, so they are version-controlled, importable, and checked by the
test suite rather than parsed from loose files.

**Provenance.** Every value is *abstracted from the BioArc operational
system* for confidentiality and research-ethics reasons, exactly as the
paper states. Module names, dependency structures, smell candidates, and
numerical scenarios convey the genuine coupling and remediation patterns of
the system, but are simplified and re-scaled so that nothing confidential
(raw code, patient data, production logs, audited measurements) is
disclosed. The Q-SPI and utility computations applied to these inputs are
exact and reproducible from the published formulas.

This folder is kept for users who wish to drop in their own organization's
audited inputs (e.g. as CSV) for a real deployment; the library functions
in `qspi/` accept any such values directly.
