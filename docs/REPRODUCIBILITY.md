# Reproducibility specification

The numerical plant is y=1+S@(u_max*x)+d. Ratings are 3+0.5*i for i=0,...,9. The canonical chain uses S_ij=0.0005 for |i-j|<=2 and 0.00005 otherwise. In topology trials this distance is graph-hop distance. Reference, stress, limits and all drive gains are in `configs/canonical.json` and checked against the model defaults.

All drives use a synchronous snapshot. A stress flag is active at sigma>=0.001 and inactive below it. A rest decision requires the focal unit and all cohesion neighbors to be inactive. The correction clips x_star to [-1,1] before forming D_t=clip(x_star-x,-1,1). Output metrics use post-update y. The row `step=1` is not the initial condition.

J=sum(abs(x)) is normalized output utilization, D=sum((x-mean(x))²) is arithmetic-mean dispersion, and stress is the sum of positive deadband excesses. Final J is not a rate, energy consumption or a cycling count. Degree-weighted graph analysis must not be inferred solely from monotonicity of D on an irregular graph.

The parameter kappa=0.2 gives soft_norm derivative 5 at zero. lambda_r=0.5, w_s=0.5 and eps_s=0.1 give coefficient 125 in the separation position operator. This number excludes the graph eigenvalue and full velocity/plant dynamics.
