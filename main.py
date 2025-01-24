from Quaternion import *
from Integrator import *
from VectorPlotter import *

if __name__ == '__main__':
  N = 10000
  
  alpha = lambda t: Vector(elements=(0, np.cos(t), np.sin(t)))
  
  omega = Vector(elements=(0, 1, 1))
  omega_list = []
  
  q = Quaternion(default=True)
  q_list = []
  
  v = Vector(elements=(1, 1, 0))
  v_list = []
  
  t = 0.0
  t_list = []
  
  dt = 1e-2
  counter = 1
  while t <= dt * N:
    omega_list.append(omega.v)
    
    q, omega = solver(omega=omega, alpha=alpha(t), q=q, dt=dt, index=counter)
    q_list.append(q)
    
    v_list.append(rotateVector(q=q, v=v).v)
    
    t += dt
    t_list.append(t)
    
    counter += 1
  
  plotVectors(N=N, vectors=v_list, axes_of_rotation=omega_list, dt=dt)
  
  
