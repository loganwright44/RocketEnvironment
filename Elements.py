from __future__ import annotations
from typing import Tuple
import numpy as np
from numpy.typing import NDArray
from abc import ABC, abstractmethod

from Quaternion import *

class Element(ABC):
  def __init__(self, is_time_dependent: bool, mass: float = None, position: NDArray = None, orientation: Quaternion = None, inertia_tensor: NDArray = None):
    self.is_time_dependent: bool = is_time_dependent
    self.mass: float = mass
    self.position: NDArray = position
    self.orientation: Quaternion = orientation
    self.I: NDArray = inertia_tensor
  
  @abstractmethod
  def set_inertia_tensor(self) -> None:
    """ overwrite in derived child classes
    """
    pass
  
  @abstractmethod
  def translate(self, position: NDArray) -> None:
    """ overwrite in derived child classes
    """
    pass
  
  @abstractmethod
  def rotate(self, quaternion: Quaternion) -> None:
    """ overwrite in derived child classes
    """
    pass
  
  @abstractmethod
  def parallel_axis_shift(self, center_of_mass: NDArray) -> None:
    """ overwrite in derived child classes
    """
    pass
  
  def is_time_dependent(self) -> bool:
    """ in spacecraft, mass is time dependent in many of the elements of its composition

    Returns:
        bool: whether or not this element has any quantities which change with time
    """
    return self.is_time_dependent
  
  def __add__(self, other):
    if isinstance(other, Element):
      if other.is_time_dependent():
        raise AssertionError("Cannot combine time dependent mass elements normally. Instead, add inertia tensors after rotation/translation operations.")
      else:
        return Element()


class Cylinder(Element):
  def __init__(self, radius: float, height: float, mass: float, is_time_dependent: bool = False):
    super().__init__(is_time_dependent=is_time_dependent)
    self.mass = mass
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
  
  def parallel_axis_shift(self, center_of_mass: NDArray) -> None:
    """ shift the inertia tensor using the parallel axis theorem

    Args:
        center_of_mass (NDArray): vector pointing to the center of mass about which this element rotates
    """
    self.I += np.array([
      [self.mass * center_of_mass[0] ** 2, 0, 0],
      [0, self.mass * center_of_mass[1] ** 2, 0],
      [0, 0, self.mass * center_of_mass[2] ** 2]
    ], dtype=np.float32)
  
  def translate(self, position: NDArray):
    """ moves the element into a new position in some world frame, but does not affect inertia tensor components

    Args:
        position (NDArray): a 3D numpy vector (array)
    """
    self.position = position
  
  def rotate(self, quaternion: Quaternion):
    """ rotates the inertia tensor into a new orientation given by the quaternion

    Args:
        quaternion (Quaternion): the attitude quaternion to base our orientation off of
    """
    rotationMatrix = quaternion.get_rotation_matrix()
    self.I = np.matmul(np.matmul(rotationMatrix, self.I), rotationMatrix.T)


class ElementsTuple:
  def __init__(self, elements: Tuple[Element, ...]):
    pass


