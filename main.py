from Quaternion import *
from Integrator import *
from VectorPlotter import *

if __name__ == '__main__':
  N = 1000
  omega = Vector(elements=(0, 0, -1))
  omega_list = []
  
  q = Quaternion(default=True)
  q_list = []
  
  v = Vector(elements=(-1, 1, 0))
  v_list = []
  
  t = 0.0
  t_list = []
  
  dt = 1e-2
  
  while t <= dt * N:
    #omega.v -= np.array([0.5, 0.5, 0.5], np.float32) * 1e-2
    omega_list.append(omega.v)
    
    q = solver(omega=omega, q=q, dt=dt)
    q_list.append(q)
    
    v = rotateVector(q=q, v=v)
    v_list.append(v.v)
    
    t += dt
    t_list.append(t)
  
  #for _v, _t in zip(v_list[0::10], t_list[0::10]):
  #  print(f"< {_v[0]:.3f} {_v[1]:.3f} {_v[2]:.3f} > t = {_t:.3f}")
  
  plotVectors(N=N, vectors=v_list, axes_of_rotation=omega_list)
  
  
