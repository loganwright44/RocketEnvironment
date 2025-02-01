from __future__ import annotations
from typing import Any, Dict
import pandas as pd

from Quaternion import *
from Integrator import *
from VectorPlotter import *
from Design import *
from Element import *
from Builder import *
from ElementTypes import *
from MotorManager import *
from ThrustVectorController import *


async def simulationLoop(
    design: Design,
    tvc: ThrustVectorController,
    motor_idx: int,
    dt: float = 1e-2,
    save: bool = False,
    filename: str = None
  ) -> Dict[str, bool]:
  """ performs a generic model rocket flight simulation and produces solutions to the equations of motion

  - assumes all presets have been completed prior to call. verify this in the api or webapp side to prevent failures
  
  Args:
      design (Design): a design containing all information about the rocket
      tvc (ThrustVectorController): the thrust vector controller object
      motor_idx (int): the index of the motor in the design
  
  Returns:
      Dict[str, bool]: {"res": bool, "data": pd.DataFrame}
  """
  t = 0.0
  dt = dt
  tFinal = 20.0
  n = 0

  positions = []
  headings = []
  targetx = []
  targety = []
  thetax = []
  thetay = []
  velocities = []
  accelerations = []
  omegas = []
  
  z_body_axis = Vector(elements=(0, 0, 1))
  r = design.r
  v = design.v
  q = design.q
  omega = design.omega
  
  while t < tFinal:
    n += 1
    mass, cg, inertia_tensor = design.get_temporary_properties()
    inertia_tensor_inv = np.linalg.inv(inertia_tensor)
    F, M = tvc.getThrustVector(t=t, cg=cg)
    F = rotateVector(q=q, v=Vector(elements=(F[0], F[1], F[2])))
    M = rotateVector(q=q, v=Vector(elements=(M[0],M[1], M[2])))
    
    F = np.array([F[0], F[1], F[2]])
    M = np.array([M[0], M[1], M[2]])
    
    F += mass * np.array([0.0, 0.0, -9.8])
    
    alpha = np.matmul(inertia_tensor_inv, M - np.cross(a=omega.v, b=np.matmul(inertia_tensor, omega.v)))
    alpha = Vector(elements=(alpha[0], alpha[1], alpha[2]))
    
    a = F / mass
    a = Vector(elements=(a[0], a[1], a[2]))
    
    if n < 10 and a.v[2] < 0.0:
      # if the motor is starting, do not acclerate down because of gravity - the earth provides a normal force equal to gravity
      a.v[2] = 0.0
    
    q, omega = solver(omega=omega, alpha=alpha, q=q, dt=dt, display=False)
    r += v * dt
    v += a * dt
    design += KinematicData(
      R=r,
      V=v,
      Q=q,
      OMEGA=omega
    )
    
    headings.append(rotateVector(q=q, v=z_body_axis))
    positions.append(r)
    targetx.append(tvc.targetx)
    targety.append(tvc.targety)
    thetax.append(tvc.thetax)
    thetay.append(tvc.thetay)
    velocities.append(v)
    accelerations.append(Vector(elements=(a[0], a[1], a[2])))
    omegas.append(omega)
    
    design.step(dt=dt)
    tvc.step(dt=dt)
    
    design.dynamic_elements[motor_idx][1] = tvc.getAttitude()

    t += dt
    
    if n > 100:
      if r.v[2] <= 0.0:
        break
  
  plotMotion(N=n, translation_vectors=positions, z_body_vectors=headings, dt=dt, burn_time=tvc.burn_time, save=save, filename=filename)
  
  data = pd.DataFrame({
    "position": positions,
    "heading": headings,
    "targetx": targetx,
    "targety": targety,
    "thetax": thetax,
    "thetay": thetay,
    "velocity": velocities,
    "acceleration": accelerations,
    "omega": omegas
  })
  
  data.to_csv("temp.csv", sep=",")

  return {"res": True}






def demoSim():
  motor = MotorManager(motor="F15")
  tvc = ThrustVectorController(motor_manager=motor)
  
  data_dict = {
    "body_tube": ConfigDict(
      Type=Tube,
      Args=TubeDictS(inner_radius=0.072 / 2, outer_radius=0.074 / 2, height=0.8, mass=0.3, is_static=True)
    ),
    "nose_cone": ConfigDict(
      Type=Cone,
      Args=ConeDictS(radius=0.074 / 2, height=0.2, mass=0.12, is_static=True)
    ),
    "flight_computer": ConfigDict(
      Type=Cylinder,
      Args=CylinderDictS(radius=0.072 / 2, height=0.12, mass=0.18, is_static=True)
    )
  }
  
  motor_idx = len(data_dict)
  
  # let the motor manager produce the data for us and add it to the constraints dictionary
  data_dict.update(motor.getElementData())
  builder = Builder(data_dict=data_dict)
  design, part_numbers = builder.generate_design()
  
  # make sure the motor and the tvc are lined up, the tvc has a specific function to do this which must be performed
  design.manipulate_element(part_numbers["rocket_motor"], np.array([0, 0, -0.4]))
  tvc.moveToMotor(offset=np.array([0, 0, -0.4]))
  
  design.manipulate_element(part_numbers["nose_cone"], np.array([0, 0, 0.4]))
  design.manipulate_element(part_numbers["flight_computer"], np.array([0, 0, 0.15]), attitude=Quaternion(angle_vector=(0.12, np.array([0, 1, 1], dtype=np.float32)), is_vector=False))
  
  print(design)
  
  t = 0.0
  tFinal = 20.0
  dt = 1e-2
  
  N = 0
  
  u = Vector(elements=(0, 0, 1))
  
  r_list = []
  z_body_list = []
  
  # consolidate the static elements to prepare for simulation loop
  design.consolidate_static_elements()
  
  tvc.updateSetpoint(targetx=0.0 * DEGREES_TO_RADIANS, targety=0.0 * DEGREES_TO_RADIANS)
  tvc.forceToTarget()
  
  r = design.r
  v = design.v
  q = design.q
  omega = design.omega
  
  while t < tFinal:
    N += 1
    
    mass, cg, inertia_tensor = design.get_temporary_properties()

    inertia_tensor_inv = np.linalg.inv(inertia_tensor)

    F, M = tvc.getThrustVector(t=t, cg=cg)
    F = rotateVector(q=design.q, v=Vector(elements=(F[0], F[1], F[2])))
    M = rotateVector(q=design.q, v=Vector(elements=(M[0], M[1], M[2])))

    F = np.array([F[0], F[1], F[2]])
    M = np.array([M[0], M[1], M[2]])

    M = M
    F = F - mass * np.array([0.0, 0.0, 9.8]) # simple gravity force term pulls down on rocket in inertial-frame z direction

    alpha = np.matmul(inertia_tensor_inv, M - np.cross(a=omega.v, b=np.matmul(inertia_tensor, omega.v)))
    alpha = Vector(elements=(alpha[0], alpha[1], alpha[2]))

    a = F / mass
    a = Vector(elements=(a[0], a[1], a[2]))
    
    if N < 10 and a.v[2] < 0.0:
      # if the motor is starting, do not acclerate down because of gravity - the earth provides a normal force equal to gravity
      a.v[2] = 0.0

    q, omega = solver(omega=omega, alpha=alpha, q=q, dt=dt, display=False)

    # add position increment first, then velocity increment next
    r += v * dt
    v += a * dt

    design += KinematicData(
      R=r,
      V=v,
      Q=q,
      OMEGA=omega
    )
    
    z_body_list.append(rotateVector(q=q, v=u))
    r_list.append(r)

    design.step(dt=dt) # reduce the mass of the dynamic elements according to their specs
    tvc.step(dt=dt)

    # compute error in orientation - ideally non-zero in a real situation, but the error is computed with yaw-pitch-roll angle differences
    if N == 100:
      tvc.updateSetpoint(targetx=-2.0 * DEGREES_TO_RADIANS, targety=-1.0 * DEGREES_TO_RADIANS)
    
    if N == 125:
      tvc.updateSetpoint(targetx=1.0 * DEGREES_TO_RADIANS, targety=2.0 * DEGREES_TO_RADIANS)
    
    if N == 150:
      tvc.updateSetpoint(targetx=0.0 * DEGREES_TO_RADIANS, targety=0.0 * DEGREES_TO_RADIANS)

    design.dynamic_elements[motor_idx][1] = tvc.getAttitude() # rotate the motor mass to the attitude determined by the servo outputs

    t += dt
    
    if N > 100:
      if r.v[2] <= 0.0:
        break
  
  plotMotion(N=N, translation_vectors=r_list, z_body_vectors=z_body_list, dt=dt, burn_time=tvc.burn_time, save=False)
  
  print("Done")


__all__ = [
  "demoSim",
  "simulationLoop"
]