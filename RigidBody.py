from __future__ import annotations
from typing import Union, TypedDict, List, Dict, Tuple
from numpy.typing import NDArray
from Element import *
from Quaternion import *

class BodyDict(TypedDict):
  Static: List[Element]
  Dynamic: List[Element]


class Design:
  def __init__(self, elements: BodyDict):
    self.reduced = False
    
    static_elements = elements["Static"]
    relative_attitudes: List[Quaternion] = [Quaternion(default=True) for _ in range(len(static_elements))]
    relative_positions: List[NDArray] = [np.array([0, 0, 0], dtype=np.float32) for _ in range(len(static_elements))]
    self.static_elements: Dict[int, Tuple[Element, Quaternion, NDArray]] = {_element.id: (_element, _relative_attitude, _relative_position) for (_element, _relative_attitude, _relative_position) in zip(static_elements, relative_attitudes, relative_positions)}
    
    dynamic_elements = elements["Dynamic"]
    relative_attitudes: List[Quaternion] = [Quaternion(default=True) for _ in range(len(dynamic_elements))]
    relative_positions: List[NDArray] = [np.array([0, 0, 0], dtype=np.float32) for _ in range(len(dynamic_elements))]
    self.dynamic_elements: Dict[int, Tuple[Element, Quaternion, NDArray]] = {_element.id: (_element, _relative_attitude, _relative_position) for (_element, _relative_attitude, _relative_position) in zip(dynamic_elements, relative_attitudes, relative_positions)}
    
    del static_elements
    del dynamic_elements
    del relative_attitudes
    del relative_positions
  
  def manipulate_element(self, id: int, displacement: NDArray = None, rotation: Quaternion = None):
    if self.reduced:
      if id in self.static_elements.keys():
        pass
      elif id in self.dynamic_elements.keys():
        pass
      else:
        raise KeyError("Id not found for `Element()`")
    else:
      if id in self.dynamic_elements.keys():
        pass
      else:
        raise AssertionError("Cannot manually control static element placement after simplifying the state")
  
  def simplify_static_elements(self) -> None:
    self.reduced = True
    X, Y, Z = 0, 1, 2
    mass = 0.0
    center_of_mass = np.array([0, 0, 0], dtype=np.float32)
    inertia_tensor = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]], dtype=np.float32)
    for static_element in self.static_elements.values:
      static_element: Tuple[Element, Quaternion, NDArray]
      element, attitude, position = static_element
      
      mass += element.mass
      
      R = attitude.get_rotation_matrix()
      ΔI = np.matmul(np.matmul(R, element.I), R.T)
      
      IXX = element.mass * (position[Y] ** 2 + position[Z] ** 2)
      IYY = element.mass * (position[X] ** 2 + position[Z] ** 2)
      IZZ = element.mass * (position[X] ** 2 + position[Y] ** 2)
      IXY = IYX = element.mass * (-position[X] * position[Y])
      IXZ = IZX = element.mass * (-position[Z] * position[X])
      IYZ = IZY = element.mass * (-position[Y] * position[Z])
      
      ΔI += np.array([
        [IXX, IXY, IXZ],
        [IYX, IYY, IYZ],
        [IZX, IZY, IZZ]
      ], dtype=np.float32)
      
      inertia_tensor += ΔI
      
      center_of_mass += element.mass * position
    
    center_of_mass /= mass
    
    self.static_mass = mass
    self.static_CG = np.copy(center_of_mass)
    self.static_inertia_tensor = inertia_tensor
    
    del self.static_elements
  
  def get_parallel_axis_translation(self, id: int) -> None:
    pass
        
  


