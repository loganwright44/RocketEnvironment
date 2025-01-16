import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

def plotVectors(N: int, vectors: list, axes_of_rotation: list):
  fig = plt.figure()
  ax = fig.add_subplot(projection="3d")

  def getVector(index: int):
    v = vectors[index]
    return 0, 0, 0, v[0], v[1], v[2]
  
  def getAxis(index: int):
    a = axes_of_rotation[index]
    return 0, 0, 0, a[0], a[1], a[2]

  ax.set_xlim(-2, 2)
  ax.set_ylim(-2, 2)
  ax.set_zlim(-2, 2)
  
  vector = ax.quiver(*getVector(0))
  axis = ax.quiver(*getAxis(0))

  def update(index):
    nonlocal vector
    nonlocal axis
    
    if vector in ax.collections:
      vector.remove()
    
    vector = ax.quiver(*getVector(index=index))
    
    if axis in ax.collections:
      axis.remove()
    
    axis = ax.quiver(*getAxis(index=index))

  ani = FuncAnimation(fig=fig, func=update, frames=list(range(1000)), interval=50)
  plt.show()


__all__ = [
  "plotVectors"
]
