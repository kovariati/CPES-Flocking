# Method to code map

| Manuscript component | Implementation | Verification |
|---|---|---|
| Normalized state and inverse output | `system`, `simulate`: u_max*x | Normalization inverse test |
| Stress and clipped reference | `raw_drives` | Zero stress and target-order regression |
| Graph-hop neighborhoods | `graph_distances`, `system` | Symmetry, nesting, no self neighbors |
| Soft-normalized drives | `soft_norm`, `raw_drives` | Derivative 5 and separation Jacobian |
| Force, velocity and state clipping | `simulate` | State invariance test |
| Rest-state velocity attenuation | `simulate`, widest-neighborhood condition | Calm velocity bound |
| Theorem 2 separation coefficient | `raw_drives`, finite-difference test | Jacobian equals (I-P_s)/(kappa*eps_s²) before lambda_r*w_s |
| Canonical Figure 1 and numerical table | `scripts/reproduce.py --suite canonical` | All 12 mode/scenario rows and traces |
| Component ablations | `gate_only`, `decay_only` modes | Shared model and old-state measurements |
| Parameter sensitivity | `SWEEPS` in `scripts/reproduce.py` | `configs/experiment_matrix.json` |
| Topology and initial-condition trials | `--suite monte-carlo` | 200 rows, 5 graphs, 10 seeds, 2100 updates |

Theorems concern fixed positive ratings and a scalar behavioral state. The source does not implement the suggested affine or sensitivity-weighted extensions, continuous/hysteretic gates, economic valuation, or learning.
