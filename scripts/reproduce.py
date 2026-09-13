"""Reproduce canonical scenarios, component ablations, OAT sensitivity and graph trials."""
import argparse,csv,json,sys,platform
from pathlib import Path
from dataclasses import asdict,replace
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from cpes_flocking.model import Parameters,MODES,TOPOLOGIES,simulate,summary,system

STEPS={'zero':300,'full':100,'partial':200}
SWEEPS={'kappa':[0.1,0.2,0.4], 'eps_s':[0.05,0.1,0.2],
        'w_s':[0.25,0.5,0.75], 'beta_rest':[0.1,0.2,0.5],
        'stress_tol':[0.0001,0.001,0.01], 'dt':[0.5,1.0,1.5]}

def write_csv(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def plots(results,out):
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':12,'axes.labelsize':13,'xtick.labelsize':11,'ytick.labelsize':11,'legend.fontsize':10,'pdf.fonttype':42})
    fig,axes=plt.subplots(3,2,figsize=(10,9.4),layout='constrained')
    panels=[('zero',1,'Disagreement D'),('zero',0,'Utilization J'),('full',1,'Disagreement D'),('full',2,'Aggregate stress (pu)'),('partial',0,'Utilization J'),('partial',2,'Aggregate stress (pu)')]
    for k,(ax,(kind,idx,ylabel)) in enumerate(zip(axes.flat,panels)):
        for mode,style,color,label in [('standard','-','#2864a5','Standard'),('gated','--','#c54c37','Gate + decay')]:
            a=results[(kind,mode)]['aggregate']
            ax.plot(np.arange(1,len(a)+1),a[:,idx],style,color=color,lw=1.5,label=label)
        ax.set(xlabel='Update index',ylabel=ylabel)
        ax.set_title(f'({chr(97+k)}) Scenario {1+list(STEPS).index(kind)}',loc='left',fontsize=13)
        ax.legend(loc='best');ax.grid(alpha=0.2)
    out.mkdir(parents=True,exist_ok=True)
    fig.savefig(out/'figure1.png',dpi=300);fig.savefig(out/'figure1.pdf');plt.close(fig)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--suite',choices=['canonical','sensitivity','monte-carlo','all'],default='canonical');ap.add_argument('--output',type=Path,default=ROOT/'results');ap.add_argument('--no-plots',action='store_true');args=ap.parse_args()
    p=Parameters();out=args.output;out.mkdir(parents=True,exist_ok=True)
    if args.suite in ('all','canonical'):
        rows=[];results={}
        for kind,steps in STEPS.items():
            for mode in MODES:
                r=simulate(mode,kind,steps,p=p); results[(kind,mode)]=r
                rows.append(dict(scenario=kind,mode=mode,steps=steps,seed=42,**summary(r)))
                a=r['aggregate'];names=['J','D','stress','movement','active_directed_pairs']
                write_csv(out/'traces'/f'{kind}_{mode}.csv',[dict(step=t+1,**dict(zip(names,a[t])),**{f'{var}_{i}':r['trace'][t,i,c] for c,var in enumerate(['x','v','y']) for i in range(p.n)}) for t in range(steps)])
        write_csv(out/'scenario_summary.csv',rows)
        if not args.no_plots: plots(results,out.parent/'figures')
        (out/'parameters.json').write_text(json.dumps(asdict(p),indent=2)+'\n')
        for row in rows: print(row['scenario'],row['mode'],round(row['J_final'],6),round(row['D_final'],6),round(row['stress_final'],6),flush=True)
    if args.suite in ('all','sensitivity'):
        rows=[]
        for param,values in SWEEPS.items():
            for value in values:
                q=replace(p,**{param:value})
                for kind,steps in STEPS.items():
                    for mode in ('standard','gated'):
                        rows.append(dict(parameter=param,value=value,scenario=kind,mode=mode,steps=steps,seed=42,**summary(simulate(mode,kind,steps,p=q))))
        write_csv(out/'sensitivity.csv',rows);print('Sensitivity complete',flush=True)
    if args.suite in ('all','monte-carlo'):
        rows=[]
        for topology in TOPOLOGIES:
            for seed in range(10):
                for kind in ('zero','partial'):
                    for mode in ('standard','gated'):
                        rows.append(dict(topology=topology,seed=seed,scenario=kind,mode=mode,steps=2100,**summary(simulate(mode,kind,2100,seed=seed,perturb=True,p=p,topology=topology))))
            print('Completed topology',topology,flush=True)
        write_csv(out/'monte_carlo.csv',rows)
    env={'python':platform.python_version(),'numpy':np.__version__,'platform':platform.system(),'machine':platform.machine(),'float':'float64','rng':'numpy.random.RandomState (MT19937)','canonical_seed':42,'monte_carlo_seeds':list(range(10))}
    (out/'environment.json').write_text(json.dumps(env,indent=2)+'\n')

if __name__=='__main__':main()
