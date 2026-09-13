import unittest,sys
from pathlib import Path
from dataclasses import replace
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from cpes_flocking.model import *

class ModelTests(unittest.TestCase):
 def test_normalization_inverse(self):
  u,_,_=system();x=np.linspace(-1,1,10);np.testing.assert_allclose((u*x)/u,x,atol=1e-15)
 def test_softnorm_slope_and_bound(self):
  z=np.array([-1e8,-1.,0.,1.,1e8]);self.assertTrue(np.all(np.abs(soft_norm(z))<1))
  h=1e-8;self.assertAlmostEqual(float((soft_norm(h)-soft_norm(-h))/(2*h)),5.,places=6)
 def test_separation_jacobian(self):
  p=Parameters();u,S,masks=system();h=1e-9;n=p.n;J=np.empty((n,n));v=np.zeros(n);y=np.ones(n)
  for j in range(n):
   e=np.eye(n)[j]*h
   J[:,j]=(raw_drives(e,v,y,u,masks,p,False)[0]-raw_drives(-e,v,y,u,masks,p,False)[0])/(2*h)
  expected=(np.eye(n)-row_average(masks[0]))/(p.kappa*p.eps_s**2)
  np.testing.assert_allclose(J,expected,rtol=1e-6,atol=1e-6)
 def test_gate_elimination_and_boundary(self):
  p=Parameters();u,S,masks=system();x=np.linspace(-.1,.1,10);v=x*0
  a=raw_drives(x,v,np.ones(10),u,masks,p,True);np.testing.assert_array_equal(a[0],0)
  y=np.ones(10);y[0]=p.y_ref+p.delta+p.stress_tol+1e-12
  a=raw_drives(x,v,y,u,masks,p,True);self.assertTrue(a[5][0,1]);self.assertFalse(a[5][2,3])
 def test_target_clipped_before_difference(self):
  p=Parameters();u,S,masks=system();x=np.full(10,-.8);v=x*0;y=np.full(10,2.)
  np.testing.assert_allclose(raw_drives(x,v,y,u,masks,p,False)[3],-.2)
 def test_invariance_and_rest_bound(self):
  p=Parameters();r=simulate('gated','zero',40,p=p,x0=np.linspace(-3,3,10),v0=np.linspace(-2,2,10))
  self.assertLessEqual(abs(r['trace'][:,:,0]).max(),1);self.assertLessEqual(abs(r['trace'][:,:,1]).max(),p.v_max)
  r=simulate('gated','zero',40,p=p);self.assertLessEqual(abs(r['trace'][:,:,1]).max(),p.beta_rest*p.v_max)
 def test_full_stress_coincidence(self):
  a=simulate('standard','full',100);b=simulate('gated','full',100)
  np.testing.assert_array_equal(a['trace'],b['trace'])
 def test_graph_properties(self):
  for topology in TOPOLOGIES:
   u,S,m=system(topology=topology)
   self.assertTrue(np.all(m[0]<=m[1]) and np.all(m[1]<=m[2]))
   for a in m:self.assertTrue(np.all(a==a.T));self.assertFalse(a.diagonal().any())
 def test_invalid_parameters(self):
  for kw in [{'kappa':0},{'stress_tol':0},{'eps_s':float('nan')},{'beta_rest':1}]:
   with self.assertRaises(ValueError):Parameters(**kw)

if __name__=='__main__':unittest.main()
