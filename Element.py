from __future__ import annotations
from typing import Tuple
import numpy as np
from numpy.typing import NDArray
from abc import ABC, abstractmethod

from Quaternion import *

class Element(ABC):
  def __init__(self):
    self.mass: float
    self.position: NDArray
    self.orientation: Quaternion
    self.I: NDArray
  
  @abstractmethod
  def set_inertia_tensor(self) -> None:
    """ overwrite in derived child classes
    """
    pass
  
  @abstractmethod
  def recalculate_inertia_tensor(self) -> None:
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
  
  def get_inertia_tensor(self) -> NDArray:
    """ gets the inertia tensor as measured in body-centered coordinates

    Returns:
        NDArray: the inertia tensor in body-centered coordinates
    """
    return self.I


class Cylinder(Element):
  def __init__(self, radius: float, height: float, mass: float, position: NDArray, orientation: Quaternion):
    super().__init__()
    self.mass = mass
    self.height = height
    self.radius = radius
    self.position = position
    self.orientation = orientation
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
  
  def recalculate_inertia_tensor(self):
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


class Tube(Element):
  def __init__(self, inner_radius: float, outer_radius: float, height: float, mass: float, position: NDArray, orientation: Quaternion):
    super().__init__()
    self.mass = mass
    self.height = height
    self.inner_radius = inner_radius
    self.outer_radius = outer_radius
    self.position = position
    self.orientation = orientation
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
  
  def recalculate_inertia_tensor(self):
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


class Cone(Element):
  def __init__(self, radius: float, height: float, mass: float, position: NDArray, orientation: Quaternion):
    super().__init__()
    self.mass = mass
    self.height = height
    self.radius = radius
    self.position = position
    self.orientation = orientation
    self.set_inertia_tensor()
  
  def set_inertia_tensor(self):
    """ sets the standard inertia tensor elements in the body frame at the center of mass
    """
    IXX = IYY = self.mass * self.height ** 2 / 10 + self.mass * self.radius ** 2 * 3 / 20
    IZZ = self.mass * self.radius ** 2 * 3 / 10
    self.I = np.array([
      [IXX, 0, 0],
      [0, IYY, 0],
      [0, 0, IZZ]
    ], dtype=np.float32)
  
  def recalculate_inertia_tensor(self):
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


def reduceMass(element: Element, dm: float):
  """ helper function to instigate a mass element to step down in mass and recompute its inertia tensor in body coordinates

  Args:
      element (Element): _description_
      dm (float): _description_
  """
  element.mass -= dm
  element.recalculate_inertia_tensor()


__all__ = [
  "Element",
  "Cylinder",
  "Tube",
  "Cone",
  "reduceMass"
]
