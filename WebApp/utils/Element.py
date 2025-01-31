from __future__ import annotations
from typing import Tuple
from numpy.typing import NDArray
from abc import ABC, abstractmethod

from Quaternion import *

"""
Author: Logan Wright

Description: Element.py is another helper module for generating rigid body components. They can be combined and modified through time
to simulate the dynamic and static properties of true rigid body systems. RigidBody.py will make use of Elements to construct designs
and create entire modular rigid bodies and can perform moment and force summations across the body. These are then used to compute the
solutions of the equations of motion. Different shapes are available from the selection below to construct a design. Will be adding more
geometries as time goes on and the need arises.
"""

class Element(ABC):
  _id_counter: int = 0
  def __init__(self, is_static: bool, name: str, **kwargs):
    # assign a unique id to each instance of this class
    self.id = Element._id_counter
    Element._id_counter += 1
    
    self.is_static = is_static
    self.name = name
    
    self.mass: float
    self.I: NDArray
    self.m_dot: float = None
    
    if not is_static:
      if not "min_mass" in kwargs or not "duration" in kwargs:
        raise SyntaxError("If a mass element is dynamic (not static), `min_mass: float` and `duration: float` must be passed as arguments to the constructor of the Element subclass")
      self.min_mass = kwargs["min_mass"]
      self.duration = kwargs["duration"]
      self.m_dot = (self.mass - self.min_mass) / self.duration
  
  @abstractmethod
  def set_inertia_tensor(self) -> None:
    """ overwrite in derived child classes
    """
    pass
  
  def get_inertia_tensor(self) -> NDArray:
    """ gets the inertia tensor as measured in body-centered coordinates

    Returns:
        NDArray: the inertia tensor in body-centered coordinates
    """
    return self.I
  
  def get_mass(self) -> float:
    """ returns the current mass of the element

    Returns:
        float: mass of the element
    """
    return self.mass
  
  def is_dynamic(self) -> bool:
    return not self.is_static
  
  def __str__(self) -> str:
    class_name = type(self).__name__
    return f"----- Class: {class_name} ----- \n{'STATIC' if self.is_static else 'DYNAMIC'} \nid_number = {self.id} \nM = {self.mass:.3f} kg \nI = \n{self.I} \n{'-' * (len(class_name) + 19)}"



class Cylinder(Element):
  def __init__(self, radius: float, height: float, mass: float, is_static: bool, name: str, **kwargs):
    self.mass = mass
    super().__init__(is_static, name, **kwargs)
    self.height = height
    self.radius = radius
    self.set_inertia_tensor()
  
  def set_inertia_tensor(self):
    """ sets the standard inertia tensor elements in the body frame at the center of mass
    """
    IXX = IYY = self.mass * self.height ** 2 / 12 + self.mass * self.radius ** 2 / 4
    IZZ = self.mass * self.radius ** 2 / 2
    self.I = np.array([
      [IXX, 0, 0],
      [0, IYY, 0],
      [0, 0, IZZ]
    ], dtype=np.float32)


class Tube(Element):
  def __init__(self, inner_radius: float, outer_radius: float, height: float, mass: float, is_static: bool, name: str, **kwargs):
    self.mass = mass
    super().__init__(is_static, name, **kwargs)
    self.height = height
    if outer_radius > inner_radius:
      self.inner_radius = inner_radius
      self.outer_radius = outer_radius
    elif outer_radius == inner_radius:
      raise ValueError("Inner radius must be strictly less than the outer radius for `Tube()` element")
    else:
      self.inner_radius = outer_radius
      self.outer_radius = inner_radius
    
    self.set_inertia_tensor()
  
  def set_inertia_tensor(self):
    """ sets the standard inertia tensor elements in the body frame at the center of mass
    """
    IXX = IYY = self.mass / 12 * (3 * (self.inner_radius ** 2 + self.outer_radius ** 2) + self.height ** 2)
    IZZ = self.mass / 2 * (self.inner_radius ** 2 + self.outer_radius ** 2)
    self.I = np.array([
      [IXX, 0, 0],
      [0, IYY, 0],
      [0, 0, IZZ]
    ], dtype=np.float32)


class Cone(Element):
  def __init__(self, radius: float, height: float, mass: float, is_static: bool, name: str, **kwargs):
    self.mass = mass
    super().__init__(is_static, name, **kwargs)
    self.height = height
    self.radius = radius
    self.set_inertia_tensor()
  
  def set_inertia_tensor(self):
    """ sets the standard inertia tensor elements in the body frame at the center of mass
    """
    IXX = IYY = self.mass * (self.height ** 2 + 4 * self.radius ** 2) * 3 / 80
    IZZ = self.mass * self.radius ** 2 * 3 / 10
    self.I = np.array([
      [IXX, 0, 0],
      [0, IYY, 0],
      [0, 0, IZZ]
    ], dtype=np.float32)

# this is not quite right... will fix the element type below later on but this comment will serve as the reminder
class HollowCone(Element):
  def __init__(self, inner_radius: float, outer_radius: float, inner_height: float, outer_height: float, mass: float, is_static: bool, name: str, **kwargs):
    self.mass = mass
    super().__init__(is_static, name, **kwargs)
    if outer_height > inner_height:
      self.inner_height = inner_height
      self.outer_height = outer_height
    elif outer_height == inner_height:
      raise ValueError("Inner height must strictly be smaller than outer height for `HollowCone()` element")
    else:
      self.inner_height = outer_height
      self.outer_height = inner_height
    
    if outer_radius > inner_radius:
      self.inner_radius = inner_radius
      self.outer_radius = outer_radius
    elif inner_radius == outer_radius:
      raise ValueError("Inner radius must strictly be smaller than outer radius for `HollowCone()` element")
    else:
      self.inner_radius = outer_radius
      self.outer_radius = inner_radius
    
    self.set_inertia_tensor()
  
  def set_inertia_tensor(self):
    """ sets the standard inertia tensor elements in the body frame at the center of mass
    """
    IXX = IYY = self.mass * (self.outer_height ** 2 + 4 * self.outer_radius ** 2) * 3 / 80
    IZZ = self.mass * self.outer_radius ** 2 * 3 / 10
    outer_I = np.array([
      [IXX, 0, 0],
      [0, IYY, 0],
      [0, 0, IZZ]
    ], dtype=np.float32)
    
    IXX = IYY = self.mass * (self.inner_height ** 2 + 4 * self.inner_radius ** 2) * 3 / 80
    IZZ = self.mass * self.inner_radius ** 2 * 3 / 10
    inner_I = np.array([
      [IXX, 0, 0],
      [0, IYY, 0],
      [0, 0, IZZ]
    ], dtype=np.float32)
    
    self.I = np.copy(outer_I - inner_I)
    
    np.delete(outer_I)
    np.delete(inner_I)


def reduceMass(element: Element, dt: float) -> bool:
  """ helper function to instigate a mass element to step down in mass and recompute its inertia tensor in body coordinates

  Args:
      element (Element): an Element subclass object to update
      dt (float): small time step
  
  Returns:
      bool: if successful or not
  """
  if element.is_dynamic():
    if element.mass > element.min_mass:
      element.mass -= element.m_dot * dt
      return True
    else:
      return True
  else:
    return False


__all__ = [
  "Element",
  "Cylinder",
  "Tube",
  "Cone",
  "reduceMass"
]
