import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from typing import List

from Quaternion import *
from Integrator import *

def plotVectors(N: int, vectors: List[Vector], axes_of_rotation: List[Vector], dt: float, save: bool = False):
  fig = plt.figure()
  ax = fig.add_subplot(projection="3d")

  def getVector(index: int):
    v = vectors[index]
    return 0, 0, 0, v[0], v[1], v[2]
  
  def getAxis(index: int):
    a = axes_of_rotation[index]
    return 0, 0, 0, a[0], a[1], a[2]

  LIM = 2
  ax.set_xlim(-LIM, LIM)
  ax.set_ylim(-LIM, LIM)
  ax.set_zlim(-LIM, LIM)
  
  vector = ax.quiver(*getVector(0), color='orange')
  axis = ax.quiver(*getAxis(0), color='green')

  def update(index):
    nonlocal vector
    nonlocal axis
    
    if vector in ax.collections:
      vector.remove()
    
    vector = ax.quiver(*getVector(index=index), color='orange')
    
    if axis in ax.collections:
      axis.remove()
    
    axis = ax.quiver(*getAxis(index=index), color='green')

  ani = FuncAnimation(fig=fig, func=update, frames=list(range(N)), interval=dt * 1e3, repeat=True)
  
  if save:
    ani.save("rigid_body_motion.mp4", writer="ffmpeg", fps=int(1 / dt))
  
  plt.show()


def plotterDemo(save: bool = False):
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
  
  plotVectors(N=N, vectors=v_list, axes_of_rotation=omega_list, dt=dt, save=save)


__all__ = [
  "plotVectors",
  "plotterDemo"
]
