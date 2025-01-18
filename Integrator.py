from typing import Tuple
from Quaternion import *
import numpy as np

v, q = 0, 1

def f(dt: float, omega: Vector) -> Quaternion:
  """ A derivative function returning the quaternion waiting to be applied to q, the attitude quaternion tracking orientation

  Args:
      dt (float): a small time step
      omega (Vector): angular velocity vector in inertial frame

  Returns:
      Quaternion: the infinitesimal attitude quaternion to apply to q
  """
  omega_q = omega.extend_to_quaternion() / 2
  
  return exponentiateQuaternion(q=omega_q * dt, ε=dt * 1e-2)

def solver(omega: Vector, q: Quaternion, dt: float):
  """ A Runge-Kutta 3rd order method to compute the next quaternion state given the angular velocity in the inertal frame

  Args:
      omega (Vector): angular velocity in the inertial frame
      q (Quaternion): a quaternion to accumulate a change dq due to omega
      dt (float): a small time step
  """
  coefficients = [1/6, 1/3, 1/3, 1/6]
  qs = []
  
  for c in coefficients:
    qs.append(f(dt=dt * c, omega=omega))
  
  Δq = Quaternion(default=True)
  
  for rotation in qs:
    Δq = hamiltonProduct(q1=rotation, q2=Δq)
  
  return hamiltonProduct(q1=Δq, q2=q)


__all__ = [
  "solver"
]