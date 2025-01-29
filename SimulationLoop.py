from Quaternion import *
from Integrator import *
from VectorPlotter import *
from Design import *
from Element import *
from Builder import *
from ElementTypes import *
from MotorManager import *
from ThrustVectorController import *


def demoSim():
  motor = MotorManager(motor="E12")
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

    # use the conjugate quaternion to rotate from body frame to world frame - both vectors are computed in body centered frame initially
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
  
  plotMotion(N=N, translation_vectors=r_list, z_body_vectors=z_body_list, dt=dt, save=True)
  
  print("Done")


__all__ = [
  "demoSim"
]