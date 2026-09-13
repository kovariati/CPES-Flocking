"""Compare independently regenerated canonical summaries and traces to shipped results."""
from pathlib import Path
import argparse,csv
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--regenerated',type=Path,required=True);a=ap.parse_args()
paths=[Path('scenario_summary.csv')]+[p.relative_to(ROOT/'results') for p in sorted((ROOT/'results/traces').glob('*.csv'))]
for rel in paths:
 with (ROOT/'results'/rel).open() as f:r=list(csv.DictReader(f))
 with (a.regenerated/rel).open() as f:s=list(csv.DictReader(f))
 assert len(r)==len(s),(rel,'row count')
 for x,y in zip(r,s):
  assert x.keys()==y.keys(),rel
  for k in x:
   try: xf=float(x[k]);yf=float(y[k])
   except ValueError:assert x[k]==y[k],(rel,k);continue
   assert np.isfinite(xf) and np.isfinite(yf),(rel,k,'nonfinite')
   assert np.isclose(xf,yf,rtol=1e-7,atol=1e-9),(rel,k,xf,yf)
print(f'PASS: {len(paths)} canonical summary/trace files (rtol=1e-7, atol=1e-9)')
