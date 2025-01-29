# Table of Contents
1. [Rocket Simulation Environment](#rocket-simulation-environment)
2. [Background](#background)
3. [Assets of the API](#assets-of-the-api)
4. [Usage](#usage)
5. [Example Code](#example-code)
6. [Common Problems and Solutions](#common-problems-and-solutions)
7. [Report a Problem](#report-a-problem)

# Rocket Simulation Environment

This project is intended to support advanced small-scale spacecraft by generating physically accurate simulations for control system analysis. Will add more details about functionality as the project matures.

## Background

The structure of this tool are based on several key ideas, so first, familiarize yourself with them:

- `Element` datatypes for producing massive rigid body parts

- `ElementDict` datatypes for constructing argument structures for creating those objects

- `ConfigDict` which stores the class name of the element and its arguments

- `Builder` which takes the data dictionary containing the above information to put into a `Design`

- `Design`'s are used to actually hold the rigid body elements and allow physical operations on them i.e. moments and forces act upon the inertia tensor and mass, respectively, to produce different accelerations on the body

- A `Design` is also an efficient controller for modifying objects' positions and orientations in a pre-setting to simulation with the `.manipulate_element(id: int, displacement: NDArray, attitude: Quaternion)` method

- The `.manipulate_element(id: int, displacement: NDArray, attitude: Quaternion)` method starts with every `Element` aligned with their centers of mass at the origin, and after manipulation of the `Element`'s is complete, a new center of mass vector is computed as well as the inertia tensor for the sum about the center of mass

- Once a `Design` is complete and all parts have been moved to their respective presets, we call the `.simplify_static_elements()` method, which is also a `.lock()` method and reduces information in the `Design()` by summing the physical effects of the `is_static = True` elements

- When reduction occurs, the `is_static = True` elements are forgotten and can no longer be modified, this is a design choice for efficiency reasons

- If any of the `Element` objects you define have set `is_static = False`, that means that the mass, relative orientation, and position to the `Design` may be modified at any time


**NOTE**: Calling the `.simplify_static_elements()` method on a `Design` will restrict the user from modifying any parameters about all static `Element`'s, so wait to call this before you want to begin the simulation phase

## Assets of the API

Here, I'll keep a list of all of the main `class` elements which are most commonly accessed, their uses, and how to prepare data for each instantiation process. Many of the objects used for this project are singleton instances to minimize memory consumption and to avoid redundant object creation. These will also be specified when listed. As promised:

- `Element` (and its many subclasses) - Represents a massive part of the rocket or general aerospace rigid body. It is an _element_ of a `Design` block

- `Design` - Represents a cluster of `Element`'s and is used to manage the rotations and translations of conslidated reprentations of the inertia tensor and keep track of changing mass for each `DYNAMIC` element. It can be produced automatically by using a `Builder` object

- `Builder`

- `MotorManager`

- `ThrustVectorController`

- `Quaternion`

- `Vector`

## Usage

After getting familiar with the ideas above, we can start learning several of the features to access the power of the simulator. This will just be a standard presentation of how a single loop will produce estimations for the next state:

- Before loops begin, call `.simplify_static_elements()` on the `Design`

- Loop begins and we set/call `mass, cg, inertia_tensor = design.get_temporary_properties()` to collect information about the current physical state of the vehicle. These are gathered automatically in the inertial world frame, not the body frame so no rotations are required

- Compute the inverse of the inertia tensor with `inertia_tensor_inv = np.linalg.inv(inertia_tensor)`

- Get the contributed force and torque from the rocket motor using the `ThrustVectorController` object by calling `.getThrustVector()`. These vectors are in the **BODY FRAME** and must be manually transformed to the world frame using the process shown in the demonstration below

- Use the sum of the forces and moments acting on the body in the world (inertial) frame to approximate the next state - convert to linear and angular accelerations with the following repective formulae: `a = force / mass`, `alpha = np.matmul(inertia_tensor_inv, torque.v - np.cross(a=omega.v, b=np.matmul(inertia_tensor, omega.v)))`

- Convert `angular_acceleration (alpha)` and `linear_acceleration (a)` to `Vector` objects with `alpha = Vector(elements=(alpha[0], alpha[1], alpha[2]))` and `a = Vector(elements=(a[0], a[1], a[2]))`, respectively for proper typing in the `KinematicData` named dictionary

- Use `q, omega = solver(omega=omega, alpha=alpha, q=q, dt=dt, display=True)` to get the new quaternion representing attitude and omega representing the angular velocity vector

- The last thing we need to do is create a `KinematicData` named dictionary with the updates for the `Design`, so we finalize the loop by calling:

```python
design += KinematicData(
  R=v * dt,
  V=a * dt,
  Q=q,
  OMEGA=omega
)

design.step(dt=dt)
```

## **NOTE**
Make it clear that when we add this `KinematicData` `TypedDict` to the design, we are adding the physical values in terms of the world reference frame, and **NOT** in the body (or equivalently the `Design`) frame of reference. This is done to reduce matrix multiplications and increase code efficiency.

## Example Code

Below is a demo of working code for this project to see it in use.

```python
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
  
  print(design) # see the cool looking output of the constituent parts of the design
  
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
    if N == 100: # randomly choose some noise
      tvc.updateSetpoint(targetx=-2.0 * DEGREES_TO_RADIANS, targety=-1.0 * DEGREES_TO_RADIANS)
    
    if N == 125: # raandomly pick some response
      tvc.updateSetpoint(targetx=1.0 * DEGREES_TO_RADIANS, targety=2.0 * DEGREES_TO_RADIANS)
    
    if N == 150: # and randomly choose another reponse at another time
      tvc.updateSetpoint(targetx=0.0 * DEGREES_TO_RADIANS, targety=0.0 * DEGREES_TO_RADIANS)


    design.dynamic_elements[motor_idx][1] = tvc.getAttitude() # rotate the motor mass to the attitude determined by the servo outputs

    t += dt
    
    if N > 100:
      if r.v[2] <= 0.0: # optional simple check for if the rocket has fallen back down to earth; stop if so
        break
  
  # I made a new function to plot the z axis orientation and translate it through space for realistic perspective
  plotMotion(N=N, translation_vectors=r_list, z_body_vectors=z_body_list, dt=dt, save=True)
  
  print("Done")
```

## Common Problems and Solutions

Nothing reported yet, without a bug-fix released.

## Report a Problem

To report a problem, simply start an issue on this repository and be specific. If you have the skillset to make fixes, fork the repository to your local editor, commit changes, and submit a pull request for us to review. If there are concerns about copyright issues or if you'd like to use this project for entrprising uses, contact me directly through GitHub messaging.