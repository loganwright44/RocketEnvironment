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
      Quaternion: the infinitesimal attitude adjustment quaternion to apply to q
  """
  omega_q = omega.extend_to_quaternion() / 2
  
  return exponentiateQuaternion(q=omega_q * dt, ε=dt * 1e-2)

def solver(omega: Vector, alpha: Vector, q: Quaternion, dt: float, display: bool = False, index: int = None) -> Tuple[Quaternion, Vector]:
  """ A Runge-Kutta 3rd order method to compute the next quaternion state given the angular velocity in the inertal frame

  Args:
      omega (Vector): angular velocity in the inertial frame
      alpha (Vector): angular acceleration vector in inertial frame
      q (Quaternion): a quaternion to accumulate a change dq due to omega
      dt (float): a small time step
      display (bool): choose to display the qFinal and omega_q. Defaults to False
      index (int): the iteration step number. Defaults to None
  
  Returns:
      Tuple[Quaternion, Vector]: new attitude quaternion q after infinitesimal rotation, and new omega after alpha integration
  """
  omega += alpha * dt
  #Δq = 0.5 * hamiltonProduct(q1=omega.extend_to_quaternion() * dt, q2=q)
  #print(Δq)
  #qFinal = q + Δq
  #qFinal.normalize()
  
  qFinal = hamiltonProduct(q1=exponentiateQuaternion(q=omega.extend_to_quaternion() * dt, ε=dt * 1e-3), q2=q)
  
  if display:
    if index is not None:
      print(index, qFinal, omega.extend_to_quaternion())
    else:
      print(qFinal, omega.extend_to_quaternion())
  
  return qFinal, omega


__all__ = [
  "solver"
]