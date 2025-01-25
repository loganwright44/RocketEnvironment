from Quaternion import *
from Integrator import *
from VectorPlotter import *
from Design import *
from Element import *
from Builder import *
from ElementTypes import *

def main():
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
  
  #print(design)
  
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
  
  r = Vector(elements=(0, 0, 0))
  v = Vector(elements=(0, 0, 0))
  
  q = Quaternion(default=True)
  omega = Vector(elements=(1, 0, 0))
  
  torque = Vector(elements=(1, 0, 0))
  force = Vector(elements=(0, 0, 3))
  
  alpha = np.matmul(inertia_tensor_inv, torque.v - np.cross(a=omega.v, b=np.matmul(inertia_tensor, omega.v)))
  alpha = Vector(elements=(alpha[0], alpha[1], alpha[2]))
  
  a = force / mass
  a = Vector(elements=(a[0], a[1], a[2]))
  
  q, omega = solver(omega=omega, alpha=alpha, q=q, dt=dt, display=True)
  
  r += v * dt
  v += a * dt
  
  print(f"\nq_t + 1: ", q)
  print("omega_t + 1: ", omega)
  print("r_t + 1: ", r)
  print("v_t + 1: ", v)
  
  """
  Limit is reached: we need a way to modify the heading of the entire design object once the new attitude is
  computed. Above, q is our attitude at t + dt, omega updates properly, displacement is accounted for with r,
  and velocity is accumulated as well.
  """
  
  design += KinematicData(
    R=r,
    V=v,
    Q=q,
    OMEGA=omega
  )
  
  design.step(dt=dt)

if __name__ == '__main__':
  main()
  
  
