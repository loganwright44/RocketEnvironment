# Table of Contents
1. [Rocket Simulation Environment](#rocket-simulation-environment)
2. [Background](#background)
3. [Usage](#usage)
4. [Example Code](#example-code)
5. [Common Problems and Solutions](#common-problems-and-solutions)
5. [Report a Problem](#report-a-problem)

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

## Usage

After getting familiar with the ideas above, we can start learning several of the features to access the power of the simulator. This will just be a standard presentation of how a single loop will produce estimations for the next state:

- Before loops begin, call `.simplify_static_elements()` on the `Design`

- Loop begins and we set/call `mass, cg, inertia_tensor = design.get_temporary_properties()` to collect information about the current physical state of the vehicle

- Compute the inverse of the inertia tensor with `inertia_tensor_inv = np.linalg.inv(inertia_tensor)`

- Calculate the forces and moments on the body in the world (inertial) frame - convert to linear and angular accelerations with the following repective formulae: `a = force / mass`, `alpha = np.matmul(inertia_tensor_inv, torque.v - np.cross(a=omega.v, b=np.matmul(inertia_tensor, omega.v)))`

- Convert `alpha` and `a` to `Vector` objects with `alpha = Vector(elements=(alpha[0], alpha[1], alpha[2]))` and `a = Vector(elements=(a[0], a[1], a[2]))`, respectively

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

names = [
  "body_tube",
  "nose_cone",
  "flight_computer",
  "rocket_motor"
]

data_dict = {
  "body_tube": ConfigDict(
    Type=Tube,
    Args=TubeDictS(inner_radius=0.072, outer_radius=0.074, height=0.8, mass=0.42, is_static=True)
  ),
  "nose_cone": ConfigDict(
    Type=Cone,
    Args=ConeDictS(radius=0.074, height=0.2, mass=0.08, is_static=True)
  ),
  "flight_computer": ConfigDict(
    Type=Cylinder,
    Args=CylinderDictS(radius=0.072, height=0.12, mass=0.18, is_static=True)
  ),
  "rocket_motor": ConfigDict(
    Type=Cylinder,
    Args=CylinderDictD(radius=0.029, height=0.129, mass=0.13, is_static=False, min_mass=0.084, duration=3.5)
  )
}

builder = Builder(data_dict=data_dict)

design, part_numbers = builder.generate_design()

print(design)

design.manipulate_element(part_numbers["rocket_motor"], np.array([0, 0, -0.4])) #, Quaternion(angle_vector=(np.pi / 2, np.array([0, 1, 0.]))))
design.manipulate_element(part_numbers["nose_cone"], np.array([0, 0, 0.4]))
design.manipulate_element(part_numbers["flight_computer"], np.array([0, 0, 0.15]))

design.simplify_static_elements()
mass, cg, inertia_tensor = design.get_temporary_properties()

print(f"M: {mass:.4f} kg")
print(f"CG: {cg}")
print(f"IT: {inertia_tensor}")

inertia_tensor_inv = np.linalg.inv(inertia_tensor)
print(f"IT_INV: {inertia_tensor_inv}")

dt = 1e-2

r = design.r
v = design.v

q = design.q
omega = design.omega

torque = Vector(elements=(1, 0, 0))
force = Vector(elements=(0, 0, 3))

alpha = np.matmul(inertia_tensor_inv, torque.v - np.cross(a=omega.v, b=np.matmul(inertia_tensor, omega.v)))
alpha = Vector(elements=(alpha[0], alpha[1], alpha[2]))

a = force / mass

q, omega = solver(omega=omega, alpha=alpha, q=q, dt=dt, display=False)

r += v * dt
v += a * dt

print(f"\nq_t + 1: ", q)
print("omega_t + 1: ", omega)
print("r_t + 1: ", r)
print("v_t + 1: ", v)

design += KinematicData(
  R=r,
  V=v,
  Q=q,
  OMEGA=omega
)
  
design.step(dt=dt)
print(design)
```

## Common Problems and Solutions

## Report a Problem

To report a problem, simply start an issue on this repository and be specific. If you have the skillset to make fixes, fork the repository to your local editor, commit changes, and submit a pull request for us to review. If there are concerns about copyright issues or if you'd like to use this project for entrprising uses, contact me directly through GitHub messaging.