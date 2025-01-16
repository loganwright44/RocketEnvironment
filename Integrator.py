from typing import Tuple
from Quaternion import *
import numpy as np

v, q = 0, 1

def f(dt: float, r: Quaternion, omega: Vector, alpha: Vector = None) -> Quaternion:
  """ A function returning the differential dq for integration

  Args:
      dt (float): time step to evaluate over
      r (IntegratorPair): a pair containing (Vector: omega, Quaternion: orientation) representing the state of the system
  """
  if alpha is not None:
    # first order Euler integration on omega given alpha
    omega = omega + alpha * dt
  else:
    pass
  
  omega_q = omega.extend_to_quaternion()
  
  #k1 = exponentiateQuaternion(q=omega_q * (dt / 4), ε=dt * 1e-2)
  #k2 = exponentiateQuaternion(q=k1 * (dt / 2), ε=dt * 1e-2)
  #k3 = exponentiateQuaternion(q=k2 * (3 * dt / 4), ε=dt * 1e-2)
  #k4 = exponentiateQuaternion(q=k3 * dt, ε=dt * 1e-2)
  #
  #Δq = (1 / 6) * (2 * k1 + 2 * k2 + k3 + k4)
  #Δq.normalize()
  #print(Δq)
  
  Δq = exponentiateQuaternion(q=omega_q * dt, ε=dt * 1e-2)
  
  return Δq

  #######################################################################################################################
  ######################## Code below is a redundant rewrite of the exponentiation function #############################
  #######################################################################################################################
  #if (M := omega.get_magnitude()) > 1e-4:
  #  omega_mag = M * 2.0 # This needs to be doubled since Quaternion constructor halves the angle, where this differential equation requires that this not be doubled
  #  omega_hat = omega.get_unit() # Times 2 because normalizing the time derivative of a quaternion
  #  print(exponentiateQuaternion(q=omega_q * dt))
  #  omega_q = Quaternion(angle_vector=(omega_mag * dt, omega_hat), is_vector=True)
  #  print(omega_q)
  #  return hamiltonProduct(q1=omega_q, q2=r)
  #else:
  #  return r

def solver(omega: Vector, q: Quaternion, t: float, dt: float):
  """ A Runge-Kutta 3rd order method to compute the next quaternion state given the angular velocity in the inertal frame

  Args:
      omega (Vector): angular velocity in the inertial frame
      q (Quaternion): a quaternion to accumulate a change dq due to omega
      dt (float): a small time step
  """
  #k1 = f(dt=0, r=q, omega=omega)
  #k2 = f(dt=dt / 2, r=hamiltonProduct(q1=exponentiateQuaternion(q=(dt / 2) * k1), q2=q), omega=omega)
  #k3 = f(dt=dt, r=hamiltonProduct(q1=exponentiateQuaternion(q=(-dt * k1 + 2 * dt * k2)), q2=q), omega=omega)
  #
  #Δ = (dt / 6) * (k1 + 4 * k2 + k3)
  #Δ = exponentiateQuaternion(q=Δ)
  #print(Δ)
  
  #k1 = f(dt=0, r=q, omega=omega)
  #k2 = f(dt=dt / 2, r=hamiltonProduct(q1=))
  
  Δq = f(dt=dt, r=q, omega=omega)
  
  return hamiltonProduct(q1=Δq, q2=q)


__all__ = [
  "solver"
]