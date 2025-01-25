# Table of Contents
1. [Rocket Simulation Environment](#rocket-simulation-environment)
2. [Background](#background)
3. [Usage](#usage)
4. [Report a Problem](#report-a-problem)

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

```{python}
design += KinematicData(
  R=v * dt,
  V=a * dt,
  Q=q,
  OMEGA=omega
)

design.step(dt=dt)
```

## Report a Problem