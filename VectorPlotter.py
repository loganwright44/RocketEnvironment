import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

def plotVectors(N: int, vectors: list, axes_of_rotation: list, dt: float):
  fig = plt.figure()
  ax = fig.add_subplot(projection="3d")

  def getVector(index: int):
    v = vectors[index]
    return 0, 0, 0, v[0], v[1], v[2]
  
  def getAxis(index: int):
    a = axes_of_rotation[index]
    return 0, 0, 0, a[0], a[1], a[2]

  LIM = 5
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

  ani = FuncAnimation(fig=fig, func=update, frames=list(range(1000)), interval=dt * 1e3, repeat=False)
  ani.save("rigid_body_motion.mp4", writer="ffmpeg", fps=int(1 / dt))
  
  plt.show()


__all__ = [
  "plotVectors"
]
