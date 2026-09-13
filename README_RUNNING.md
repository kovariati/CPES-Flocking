# Running the CPES numerical experiments

The tested environment is Python 3.12.14, NumPy 2.3.5 and Matplotlib 3.10.8 on Linux x86_64. The lock file lists direct and transitive plotting dependencies. All computations use float64.

On Windows PowerShell, create the environment with `py -3.12 -m venv .venv` and activate with `.\.venv\Scripts\Activate.ps1`. On Linux/macOS use `python3.12 -m venv .venv` and `source .venv/bin/activate`. Then run `python -m pip install -r requirements-lock.txt`.

## Execution

Run commands from the repository root. `python demo.py` is an alias for the canonical suite. The replacement entry point exports results by default; the former v1.0.0 `--export` option is no longer required.

```bash
python scripts/reproduce.py --suite canonical --output rerun/results
python scripts/reproduce.py --suite sensitivity --output rerun/results --no-plots
python scripts/reproduce.py --suite monte-carlo --output rerun/results --no-plots
python tools/validate_results.py --regenerated rerun/results
```

`--suite all` performs all suites. Figures are written to a sibling `figures/` directory. No files are uploaded by these commands. Canonical CSV traces include each post-update x, v and y, plus J, D, aggregate stress, absolute coordinate movement and active directed separation-pair count. Pair counts are controller diagnostics, not measured communication traffic.

## Experiment definitions

Canonical: three disturbances, four controller modes, seed 42, 300/100/200 updates. Only zero disturbance uses a random initial state. Sensitivity: six parameters, three values each, three disturbances and two modes (108 runs including repeated canonical settings). All other parameters are held fixed; weights are not renormalized.

Topology trials: five explicitly defined graphs, ten seeds 0 through 9, zero and partial disturbance, two modes and 2100 updates (200 runs). Both disturbances use paired random initial states in these trials. Graphs and coupling matrices are deterministic; only initial coordinates are random. Normal standard deviation is 0.01, not variance 0.01. Runtime is machine-dependent; the complete suite is small enough for a CPU and requires no accelerator.

## Numerical reproducibility

The target is clipped before the target-minus-state error. This order differs from v1.0.0 when the requested target exceeds a unit's capability. Long clipped trajectories can be sensitive to floating-point details. The shipped hashes verify the supplied bytes; canonical regenerated CSV validation uses rtol=1e-7 and atol=1e-9. Any mismatch must be reported with the environment and result files, not hidden by changing the tolerance. For long-horizon sensitivity or topology differences, compare reproducible metrics and the recorded environment before interpreting a failed byte comparison.
