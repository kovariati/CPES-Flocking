"""Scalar stress-gated CPES mechanism model; synthetic plant, synchronous updates."""
from dataclasses import dataclass, asdict
import numpy as np

MODES = ('standard', 'gate_only', 'decay_only', 'gated')
TOPOLOGIES = ('chain', 'ring', 'star', 'complete', 'branched')

@dataclass(frozen=True)
class Parameters:
    n: int = 10
    y_ref: float = 1.0
    delta: float = 0.01
    stress_tol: float = 0.001
    droop: float = 80.0
    kappa: float = 0.2
    eps_s: float = 0.1
    f_max: float = 0.15
    v_max: float = 0.12
    mass: float = 1.0
    dt: float = 1.0
    lambda_r: float = 0.5
    lambda_t: float = 1.0
    w_s: float = 0.5
    w_a: float = 0.3
    w_c: float = 0.2
    beta_rest: float = 0.2
    coupling: float = 0.0005
    background_ratio: float = 0.1

    def __post_init__(self):
        if self.n != 10:
            raise ValueError('This experiment fixes n=10; new sizes require new disturbances and graphs.')
        for key, val in asdict(self).items():
            if not np.isfinite(val): raise ValueError(f'{key} must be finite')
        for key in ('delta','stress_tol','kappa','eps_s','f_max','v_max','mass','dt','lambda_r','lambda_t'):
            if getattr(self,key) <= 0: raise ValueError(f'{key} must be positive')
        if not 0 < self.beta_rest < 1: raise ValueError('beta_rest must lie in (0,1)')
        if any(getattr(self,k)<0 for k in ('droop','w_s','w_a','w_c','coupling','background_ratio')):
            raise ValueError('weights, droop and coupling must be nonnegative')


def soft_norm(z, kappa=0.2):
    if not np.isfinite(kappa) or kappa <= 0: raise ValueError('kappa must be finite and positive')
    z=np.asarray(z,dtype=float)
    return z/(np.abs(z)+kappa)


def graph_distances(topology='chain', n=10):
    if topology not in TOPOLOGIES: raise ValueError(f'unknown topology {topology}')
    edges = [(i,i+1) for i in range(n-1)]
    if topology=='ring': edges += [(n-1,0)]
    if topology=='star': edges=[(0,i) for i in range(1,n)]
    if topology=='complete': edges=[(i,j) for i in range(n) for j in range(i+1,n)]
    if topology=='branched': edges=[((i-1)//2,i) for i in range(1,n)]
    dist=np.full((n,n),np.inf); np.fill_diagonal(dist,0)
    for i,j in edges: dist[i,j]=dist[j,i]=1
    for k in range(n): dist=np.minimum(dist,dist[:,k,None]+dist[None,k,:])
    return dist


def row_average(mask):
    degree=mask.sum(axis=1,keepdims=True)
    return np.divide(mask,degree,out=np.zeros(mask.shape,dtype=float),where=degree>0)


def system(p=Parameters(), topology='chain'):
    dist=graph_distances(topology,p.n)
    masks=[(dist>0)&(dist<=hop) for hop in (1,2,4)]
    # Synthetic coupling follows hop distance; never a calibrated power-flow model.
    coupling=np.where(dist<=2,p.coupling,p.coupling*p.background_ratio)
    return np.array([3+0.5*i for i in range(p.n)]), coupling, masks


def disturbance(kind, n=10):
    if kind=='zero': return np.zeros(n)
    if kind=='full': return np.array([0.02*(i%5+1) for i in range(n)])
    if kind=='partial': return np.array([0.0]*5+[0.03*(i-4) for i in range(5,n)])
    raise ValueError(f'unknown scenario {kind}')


def raw_drives(x,v,y,u_max,masks,p,gate):
    sigma=np.maximum(0,np.abs(y-p.y_ref)-p.delta)
    ns,na,nc=masks
    active=ns & ((sigma[:,None]>=p.stress_tol)|(sigma[None,:]>=p.stress_tol)) if gate else ns
    dx=x[:,None]-x[None,:]
    s=np.sum(row_average(active)*dx/(dx*dx+p.eps_s**2),axis=1)
    da=soft_norm(row_average(na)@v-v,p.kappa)
    dc=soft_norm(row_average(nc)@x-x,p.kappa)
    da=np.where(na.any(axis=1),da,0); dc=np.where(nc.any(axis=1),dc,0)
    r=-np.sign(y-p.y_ref)*sigma*p.droop
    # Target is clipped BEFORE its difference from the current state, as in the paper.
    target=np.clip(r/u_max,-1,1)
    dt=np.clip(target-x,-1,1)
    return soft_norm(s,p.kappa), da, dc, dt, sigma, active


def simulate(mode='gated', kind='zero', steps=300, seed=42, perturb=None,
             p=Parameters(), topology='chain', x0=None, v0=None):
    if mode not in MODES: raise ValueError(f'unknown mode {mode}')
    if not isinstance(steps,int) or steps<1: raise ValueError('steps must be a positive integer')
    u_max,S,masks=system(p,topology)
    if perturb is None: perturb=(kind=='zero')
    rng=np.random.RandomState(seed)
    x=(rng.normal(0,0.01,p.n) if perturb else np.zeros(p.n)) if x0 is None else np.asarray(x0,dtype=float).copy()
    v=np.zeros(p.n) if v0 is None else np.asarray(v0,dtype=float).copy()
    for z in (x,v):
        if z.shape!=(p.n,) or not np.all(np.isfinite(z)): raise ValueError('invalid initial state')
    initial_x=x.copy(); d=disturbance(kind,p.n)
    gate=mode in ('gate_only','gated'); decay=mode in ('decay_only','gated')
    trace=np.empty((steps,p.n,3)); aggregate=np.empty((steps,5))
    for t in range(steps):
        y=p.y_ref+S@(u_max*x)+d
        ds,da,dc,dt,sigma,active=raw_drives(x,v,y,u_max,masks,p,gate)
        a=p.lambda_r*(p.w_s*ds+p.w_a*da+p.w_c*dc)+p.lambda_t*dt
        v_new=np.clip(v+p.dt/p.mass*np.clip(a,-p.f_max,p.f_max),-p.v_max,p.v_max)
        calm=(sigma<p.stress_tol)&(~(masks[2]&(sigma[None,:]>=p.stress_tol)).any(axis=1))
        if decay: v_new=np.where(calm,p.beta_rest*v_new,v_new)
        x_new=np.clip(x+p.dt*v_new,-1,1)
        movement=np.sum(np.abs(x_new-x))
        x,v=x_new,v_new
        y=p.y_ref+S@(u_max*x)+d
        trace[t]=np.stack((x,v,y),axis=1)
        aggregate[t]=[np.sum(np.abs(x)),np.sum((x-x.mean())**2),
                      np.maximum(0,np.abs(y-p.y_ref)-p.delta).sum(),movement,active.sum()]
    return {'trace':trace,'aggregate':aggregate,'initial_x':initial_x}


def summary(result):
    a=result['aggregate']; x=result['initial_x']
    return dict(J_initial=float(np.abs(x).sum()),D_initial=float(((x-x.mean())**2).sum()),
                J_after_update_1=float(a[0,0]),J_final=float(a[-1,0]),
                D_after_update_1=float(a[0,1]),D_final=float(a[-1,1]),stress_final=float(a[-1,2]),
                J_mean=float(a[:,0].mean()),D_mean=float(a[:,1].mean()),stress_mean=float(a[:,2].mean()),
                movement_total=float(a[:,3].sum()),max_abs_x=float(np.abs(result['trace'][:,:,0]).max()),
                max_abs_v=float(np.abs(result['trace'][:,:,1]).max()))
