from Quaternion import *
from Integrator import *
from VectorPlotter import *
from RigidBody import *
from Element import *

def main():
  #plotterDemo()
  part_numbers = {
    "body_tube": 0,
    "nose_cone": 1,
    "flight_computer": 2,
    "rocket_motor": 3
  }
  
  body_tube = Tube(inner_radius=0.072, outer_radius=0.074, height=0.8, mass=0.42, is_static=True)
  nose_cone = Cone(radius=0.074, height=0.2, mass=0.08, is_static=True)
  flight_computer = Cylinder(radius=0.072, height=0.12, mass=0.18, is_static=True)
  rocket_motor = Cylinder(radius=0.029, height=0.129, mass=0.13, is_static=False, min_mass=0.084, duration=3.5)
  
  parts = BodyDict(Static=[nose_cone, flight_computer, body_tube], Dynamic=[rocket_motor])
  
  design = Design(elements=parts)
  #print(design)
  
  design.manipulate_element(part_numbers["rocket_motor"], np.array([0, 0, -0.4]), Quaternion(angle_vector=(np.pi / 2, np.array([0, 1, 0.]))))
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
  
  r = Vector(elements=(0, 0, 0))
  v = Vector(elements=(0, 0, 0))
  
  q = Quaternion(default=True)
  omega = Vector(elements=(0, 0, 0))
  
  torque = Vector(elements=(1, 0, 0))
  force = Vector(elements=(0, 0, 3))
  
  alpha = np.matmul(inertia_tensor_inv, torque.v.T - np.cross(omega, np.matmul(inertia_tensor, omega.v.T)))
  a = force / mass
  
  q, omega = solver(omega=omega, alpha=alpha, q=q, dt=dt, display=True)
  
  r += v * dt
  v += a * dt
  
  print(q)
  print(omega)
  print(r)
  print(v)
  
  """
  Limit is reached: we need a way to modify the heading of the entire design object once the new attitude is
  computed. Above, q is our attitude at t + dt, omega updates properly, displacement is accounted for with r,
  and velocity is accumulated as well.
  """

if __name__ == '__main__':
  main()
  
  
