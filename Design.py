from __future__ import annotations
from typing import Union, TypedDict, List, Dict, Tuple
from numpy.typing import NDArray
from Element import *
from Quaternion import *

X, Y, Z = 0, 1, 2
ELEMENT, QUATERNION, VECTOR = 0, 1, 2

class PartsList(TypedDict):
  Static: List[Element]
  Dynamic: List[Element]


class KinematicData(TypedDict):
  R: Vector
  V: Vector
  Q: Quaternion
  OMEGA: Vector


class Design:
  def __init__(self, parts_list: PartsList):
    self.reduced = False
    
    ########################################## NOTE #############################################
    # these values are strictly measured from the inertial world frame, not from the design frame
    # i.e. no rotation corrections are needed on each iteration
    self.r: Vector = Vector(elements=(0, 0, 0))
    self.v: Vector = Vector(elements=(0, 0, 0))
    self.q: Quaternion = Quaternion(default=True)
    self.omega: Vector = Vector(elements=(0, 0, 0))
    #############################################################################################
    
    static_elements = parts_list["Static"]
    relative_attitudes: List[Quaternion] = [Quaternion(default=True) for _ in range(len(static_elements))]
    relative_positions: List[NDArray] = [np.array([0, 0, 0], dtype=np.float32) for _ in range(len(static_elements))]
    self.static_elements: Dict[int, List[Element, Quaternion, NDArray]] = {_element.id: [_element, _relative_attitude, _relative_position] for (_element, _relative_attitude, _relative_position) in zip(static_elements, relative_attitudes, relative_positions)}
    
    dynamic_elements = parts_list["Dynamic"]
    relative_attitudes: List[Quaternion] = [Quaternion(default=True) for _ in range(len(dynamic_elements))]
    relative_positions: List[NDArray] = [np.array([0, 0, 0], dtype=np.float32) for _ in range(len(dynamic_elements))]
    self.dynamic_elements: Dict[int, List[Element, Quaternion, NDArray]] = {_element.id: [_element, _relative_attitude, _relative_position] for (_element, _relative_attitude, _relative_position) in zip(dynamic_elements, relative_attitudes, relative_positions)}
    
    self.parts = [*parts_list["Static"], *parts_list["Dynamic"]]
    
    del static_elements
    del dynamic_elements
    del relative_attitudes
    del relative_positions
  
  def manipulate_element(self, id: int, displacement: NDArray = None, attitude: Quaternion = None):
    """ a function to settle positions and orientations of elements before starting a simulation

    Args:
        id (int): id of element to adjust
        displacement (NDArray, optional): where to move the element in 3d space. 3D vector with numpy array. Defaults to None.
        attitude (Quaternion, optional): how to change the current attitude quaternion in 3d space. Quaternion to describe change in attitude. Defaults to None.

    Raises:
        KeyError: id not found for element
        AssertionError: once simulation begins, design is locked and static elements cannot be modified
    """
    if displacement is None and attitude is None:
      return None
    elif not self.reduced:
      if id in self.static_elements.keys():
        if attitude is not None:
          self.static_elements[id][QUATERNION] = attitude #hamiltonProduct(q1=attitude, q2=self.static_elements[id][QUATERNION])
        if displacement is not None:
          self.static_elements[id][VECTOR] += displacement
      elif id in self.dynamic_elements.keys():
        if attitude is not None:
          self.dynamic_elements[id][QUATERNION] = attitude #hamiltonProduct(q1=attitude, q2=self.dynamic_elements[id][QUATERNION])
        if displacement is not None:
          self.dynamic_elements[id][VECTOR] += displacement
      else:
        raise KeyError("Id not found for `Element()`")
    else:
      if id in self.dynamic_elements.keys():
        pass
      else:
        raise AssertionError("Cannot manually control static element placement after simplifying the state")
    
  def step(self, dt: float):
    for dynamic_element in self.dynamic_elements.values():
      element, _, _ = dynamic_element
      reduceMass(element=element, dt=dt)
  
  def simplify_static_elements(self) -> None:
    self.reduced = True
    mass = 0.0
    center_of_mass = np.array([0, 0, 0], dtype=np.float32)
    inertia_tensor = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]], dtype=np.float32)
    ΔI: NDArray
    for static_element in self.static_elements.values():
      static_element: Tuple[Element, Quaternion, NDArray]
      element, attitude, position = static_element
      
      mass += element.mass
      
      R = attitude.get_rotation_matrix()
      # rotate I
      ΔI = np.matmul(np.matmul(R, element.I), R.T)
      # then translate I
      ΔI += self.shift_inertia_tensor(position=position, mass=element.mass)
      
      inertia_tensor += ΔI
      
      center_of_mass += element.mass * position
    
    center_of_mass /= mass
    
    self.static_mass = mass
    self.static_CG = np.copy(center_of_mass)
    self.static_inertia_tensor = inertia_tensor
    
    del self.static_elements
  
  def simplify_dynamic_elements(self) -> Tuple[float, NDArray, NDArray]:
    """ sums temporary physical quantities from the dynamic elements at a current time step t

    Returns:
        Tuple[float, NDArray, NDArray]: mass, center_of_gravity vector, and inertia tensor contributions
    """
    mass = 0.0
    center_of_mass = np.array([0, 0, 0], dtype=np.float32)
    inertia_tensor = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]], dtype=np.float32)
    ΔI: NDArray
    for dynamic_element in self.dynamic_elements.values():
      dynamic_element: Tuple[Element, Quaternion, NDArray]
      element, attitude, position = dynamic_element
      
      mass += element.mass
      
      R = attitude.get_rotation_matrix()
      # rotate I
      ΔI = np.matmul(np.matmul(R, element.I), R.T)
      # then translate I
      ΔI += self.shift_inertia_tensor(position=position, mass=element.mass)
      
      inertia_tensor += ΔI
      
      center_of_mass += element.mass * position
    
    center_of_mass /= mass
    
    return (mass, center_of_mass, inertia_tensor)
  
  def get_temporary_properties(self) -> Tuple[float, NDArray, NDArray]:
    """ gets current properties of the design including all transformations necessary to represent the current state

    Returns:
        Tuple[float, NDArray, NDArray]: total mass, total cg coordinate in design coordinate frame, and total inertia tensor about the cg given prior
    """
    if not self.reduced:
      self.simplify_static_elements()
    
    dynamic_mass, dynamic_CG, dynamic_inertia_tensor = self.simplify_dynamic_elements()
    
    true_cg = (dynamic_mass * dynamic_CG + self.static_mass * self.static_CG) / (dynamic_mass + self.static_mass)
    
    true_inertia_tensor = dynamic_inertia_tensor + self.static_inertia_tensor
    
    true_inertia_tensor += self.shift_inertia_tensor(position=true_cg, mass=dynamic_mass + self.static_mass)
    
    rotation_matrix = self.q.get_rotation_matrix()
    true_inertia_tensor = np.matmul(np.matmul(rotation_matrix, true_inertia_tensor), true_inertia_tensor)
    
    return (dynamic_mass + self.static_mass, true_cg, true_inertia_tensor)
  
  def shift_inertia_tensor(self, position: NDArray, mass: float) -> NDArray:
    """ parallel axis theorem - translate all inertia tensor elements to new position

    Args:
        position (NDArray): a 3D vector pointing to the new location of the element
        element (Element): the rigid body element to be translated

    Returns:
        NDArray: a ΔI inertia tensor to be accumulated to the inertia tensor of the element at hand
    """
    IXX = mass * (position[Y] ** 2 + position[Z] ** 2)
    IYY = mass * (position[X] ** 2 + position[Z] ** 2)
    IZZ = mass * (position[X] ** 2 + position[Y] ** 2)
    IXY = IYX = mass * (-position[X] * position[Y])
    IXZ = IZX = mass * (-position[Z] * position[X])
    IYZ = IZY = mass * (-position[Y] * position[Z])
    
    return np.array([
      [IXX, IXY, IXZ],
      [IYX, IYY, IYZ],
      [IZX, IZY, IZZ]
    ], dtype=np.float32)
  
  def __getitem__(self, key: int):
    if key in self.dynamic_elements.keys():
      return self.dynamic_elements[key]
    elif not self.reduced:
      if key in self.static_elements.keys():
        return self.static_elements[key]
      else:
        raise KeyError("Key not found for `Design()` object")
    else:
      raise KeyError("Key not found for `Design()` object because `Design()` was contracted on the static elements")
  
  def __setitem__(self, key: int, value: Element):
    if not self.reduced:
      if isinstance(key, int) and isinstance(value, Element) and key not in self.dynamic_elements.keys() and key not in self.static_elements.keys():
        if value.is_dynamic():
          self.dynamic_elements[key] = (value, Quaternion(default=True), np.array([0, 0, 0], dtype=np.float32))
        else:
          self.static_elements[key] = (value, Quaternion(default=True), np.array([0, 0, 0], dtype=np.float32))
      else:
        raise Exception("Tried to setitem for `Design()` object, but not supported")
  
  def __str__(self):
    _str = f""
    for part in self.parts:
      _str += part.__str__()
      _str += f"\n"
    return _str
  
  def __iadd__(self, other):
    if isinstance(other, dict):
      r, v, q, omega = other.values()
      self.r += r
      self.v += v
      self.q = q
      self.omega = omega
      return self
    else:
      raise ValueError("Addition on `Design()` object only defined on `KinematicData` types")
  

__all__ = [
  "Design",
  "PartsList",
  "KinematicData"
]
