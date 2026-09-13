# Reproduction levels

| Level | Command | Evidence |
|---|---|---|
| Source and analytic checks | `python -m unittest discover -s tests -v` | Clipping order, derivative and graph/invariance checks |
| Repository metadata | `python tools/validate_repository.py` | Metadata and configuration consistency |
| Canonical rerun | `python scripts/reproduce.py --suite canonical --output rerun/results` then `python tools/validate_results.py --regenerated rerun/results` | Twelve canonical scenarios/ablations |
| Complete experiment | `python scripts/reproduce.py --suite all --output rerun/results` | Canonical, OAT and 200 graph/seed trials |

Validation establishes consistency of this synthetic implementation. It does not certify a physical controller. No release asset or external dataset is required at any level.
