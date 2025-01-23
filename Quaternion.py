from __future__ import annotations
from typing import Tuple
import numpy as np
from numpy.typing import NDArray

I = np.array([1, 0, 0], dtype=np.float32)
J = np.array([0, 1, 0], dtype=np.float32)
K = np.array([0, 0, 1], dtype=np.float32)

w, i, j, k = 0, 1, 2, 3

# Setup the datatypes that will be used as models for creating the following mathematical objects
QuaternionElements = Tuple[float, float, float, float]
VectorElements = Tuple[float, float, float]
AngleVector = Tuple[float, NDArray[np.float32]]
QuaternionTuple = Tuple[float, NDArray[np.float32], NDArray[np.float32], NDArray[np.float32]]

class Quaternion:
  def __init__(self, elements: QuaternionElements = None, angle_vector: AngleVector = None, default: bool = False, is_vector: bool = False):
    """ A mathematical object used to rotate vectors

    Args:
        elements (QuaternionElements, optional): Should contain 4 elements: w, x, y, z. Defaults to None.
        angle_vector (AngleVector, optional): Should contain 2 elements: rotation angle in radians, numpy array (3-d) of axis-of-rotation vector. Defaults to None.
        default (bool, optional): sets quaternion to the zero quaternion (1, 0, 0, 0). Defaults to False.
        is_vector (bool, optional): ignores quaternion normalization if it is a vector. Defaults to False.
    """
    self.q: QuaternionTuple = ()
    
    if elements is not None and angle_vector is not None:
      print('Error: Too many arguments passed to `quaternion()` contructor. Defaulting to `elements` argument to build quaternion')
      
      if self.validate_elements(elements=elements):
        self.q = (elements[w], elements[i] * I, elements[j] * J, elements[k] * K)
    
    elif (elements is None and angle_vector is None) or default:
      self.q = (1.0, 0 * I, 0 * J, 0 * K)
    
    elif elements is not None:
      if self.validate_elements(elements=elements):
        self.q = (elements[w], elements[i] * I, elements[j] * J, elements[k] * K)
    
    elif angle_vector is not None:
      if self.validate_angle_vector(angle_vector=angle_vector):
        θ = angle_vector[0]
        vector = angle_vector[1]
        if (N := np.linalg.norm(vector)) > 1e-4:
          vector /= N
          x, y, z = vector[0], vector[1], vector[2]
          self.q = (np.cos(θ /2), x * np.sin(θ / 2) * I, y * np.sin(θ / 2) * J, z * np.sin(θ / 2) * K)
        else:
          self.q = (1.0, 0 * I, 0 * J, 0 * K)
    
    else:
      self.q = (1.0, 0 * I, 0 * J, 0 * K)
    
    if not is_vector:
      self.normalize()
  
  def validate_elements(self, elements: QuaternionElements) -> bool:
    try:
      assert len(elements) == 4
      return True
    except AssertionError as e:
      print(f'Problem with elements set: {e}')
      print('Setting quaternion to default `0` quaternion')
      return False
  
  def validate_angle_vector(self, angle_vector: AngleVector) -> bool:
    try:
      assert len(angle_vector) == 2
      return True
    except AssertionError as e:
      print(f'Problem with elements set: {e}')
      print('Setting quaternion to default `0` quaternion')
      return False
  
  def is_norm(self) -> bool:
    self.normalize()
    return True
  
  def normalize(self) -> None:
    norm = np.sqrt(self.q[w] * self.q[w] + np.dot((self.q[i] + self.q[j] + self.q[k]), (self.q[i] + self.q[j] + self.q[k])))
    self.q = tuple([component / norm for component in self.q])
  
  def get_conjugate(self):
    return Quaternion(elements=(self.q[w], - self.q[i], - self.q[j], - self.q[k]), default=False)
  
  def contract_to_vector(self) -> Vector:
    """ Warning: this method eliminates information about w, the first element of a quaternion when casting to a vector

    Returns:
        Vector: the vector part of the quaternion
    """
    return Vector(elements=(self.q[i][0], self.q[j][1], self.q[k][2]))
  
  def __str__(self):
    _sum = self.q[i] + self.q[j] + self.q[k]
    return f"q = ( {self.q[w]:.4f}, {_sum[0]:.4f} i, {_sum[1]:.4f} j, {_sum[2]:.4f} k ) \t|q| = {((self.q[w] * self.q[w] + np.dot(_sum, _sum)) ** 0.5):.4f}"
  
  def __add__(self, q: Quaternion) -> Quaternion:
    return Quaternion(elements=(self.q[w] + q.q[w], self.q[i] + q.q[i], self.q[j] + q.q[j], self.q[k] + q.q[k]), default=False, is_vector=False)
  
  def __sub__(self, q: Quaternion) -> Quaternion:
    return Quaternion(elements=(self.q[w] - q.q[w], self.q[i] - q.q[i], self.q[j] - q.q[j], self.q[k] - q.q[k]), default=False, is_vector=False)
  
  def __mul__(self, other):
    if isinstance(other, (int, float)):
      return Quaternion(elements=(self.q[w] * other, self.q[i] * other, self.q[j] * other, self.q[k] * other), default=False, is_vector=True)
    else:
      raise TypeError("Unsupported type for `multiplication`")
  
  def __rmul__(self, other) -> Quaternion:
    return self.__mul__(other=other)
  
  def __truediv__(self, other) -> Quaternion:
    if isinstance(other, (int, float)):
      if other == 0 or other == 0.0:
        raise ZeroDivisionError()
      else:
        return Quaternion(elements=(self.q[w] / other, self.q[i] / other, self.q[j] / other, self.q[k] / other))
    else:
      raise TypeError("Unsupported type for `division`")
    
  def __iadd__(self, other):
    if isinstance(other, Quaternion):
      return Quaternion(elements=(self.q[w] + other.q[w], self.q[i] + other.q[i], self.q[j] + other.q[j], self.q[k] + other.q[k]), is_vector=True)
    else:
      raise AssertionError("Unsupported type for addition on `Quaternion`")
  
  def get_vector(self) -> Vector:
    return Vector(elements=(self.q[i][0], self.q[j][1], self.q[k][2]))
  
  def get_scalar(self) -> float:
    return self.q[w]
  
  def get_rotation_matrix(self) -> NDArray:
    _identity = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], np.float32)
    _skewSymmetric = np.array([
      [0, -self.q[k][k - 1], self.q[j][j - 1]],
      [self.q[k][k - 1], 0, -self.q[i][i - 1]],
      [-self.q[j][j - 1], self.q[i][i - 1], 0]
    ], dtype=np.float32)
    
    _rotationMatrix = _identity + 2 * self.q[w] * _skewSymmetric + 2 * np.matmul(_skewSymmetric, _skewSymmetric)
    return _rotationMatrix


class Vector:
  def __init__(self, elements: VectorElements):
    """ A 3 dimensional mathematical object

    Args:
        elements (VectorElements): must be a VectorElements type containing floating point values with length of 3
    """
    if len(elements) == 3:
      self.v = np.array([elements[0], elements[1], elements[2]], dtype=np.float32)
    else:
      raise AssertionError('`elements` attribute not properly specified for `Vector()` constructor. Must be length 3: no more, no less')
  
  def extend_to_quaternion(self) -> Quaternion:
    return Quaternion(elements=(0, self.v[0], self.v[1], self.v[2]), default=False, is_vector=True)
  
  def get_magnitude(self) -> float:
    return np.linalg.norm(self.v)
  
  def normalize(self) -> None:
    self.v = self.v / self.get_magnitude()
  
  def get_unit(self) -> NDArray:
    return np.copy(self.v) / self.get_magnitude()

  def __str__(self):
    return f"v = ( {self.v[0]:.4f}, {self.v[1]:.4f}, {self.v[2]:.4f} ) \t|v| = {(np.dot(self.v, self.v) ** 0.5):.4f} \n"
  
  def __add__(self, v: Vector) -> Vector:
    return Vector(elements=(self.v[0] + v.v[0], self.v[1] + v.v[1], self.v[2] + v.v[2]))
  
  def __mul__(self, other) -> Vector:
    if isinstance(other, (int, float)):
      return Vector(elements=(self.v[0] * other, self.v[1] * other, self.v[2] * other))
    else:
      raise AssertionError("Invalid type attempted to multiply with type `Vector`")
  
  def __rmul__(self, other):
    return self.__mul__(other=other)
  
  def __iadd__(self, other):
    if isinstance(other, Vector):
      return Vector(elements=(self.v[0] + other.v[0], self.v[1] + other.v[1], self.v[2] + other.v[2]))
    else:
      raise AssertionError(f"Vector cannot be added to another variable of type {type(other)}")


# This function will stay in this file locally and is not shared with external imports
def quaternionDot(q1: Quaternion, q2: Quaternion) -> float:
  """ A specialized dot product method for quaternions since last 3 elements are complex valued, so their squares are negative
  
  Args:
      q1 (Quaternion): vector part of the first quaternion
      q2 (Quaternion): vector part of the second quaternion
  
  Returns:
      float: the inner product of quaternion vector parts, makes use of special complex property where its square is equal to -1
  """
  _dot = - q1.q[i][0] * q2.q[i][0] - q1.q[j][1] * q2.q[j][1] - q1.q[k][2] * q2.q[k][2]
  return _dot

def hamiltonProduct(q1: Quaternion, q2: Quaternion) -> Quaternion:
  """ Applies quaternion multiplication between 2 quaternions, q1 applied from the left to q2
  
  Args:
      q1 (Quaternion): a quaternion performing a transformation
      q2 (Quaternion): a quaternion being transformed
  
  Returns:
      Quaternion: the final transformed quaternion
  """
  scalar = q1.q[w] * q2.q[w] + quaternionDot(q1=q1, q2=q2)
  vector = q1.q[w] * (q2.q[i] + q2.q[j] + q2.q[k]) + q2.q[w] * (q1.q[i] + q1.q[j] + q1.q[k]) + np.cross(a=(q1.q[i] + q1.q[j] + q1.q[k]), b=(q2.q[i] + q2.q[j] + q2.q[k]))
  
  return Quaternion(elements=(scalar, vector[0], vector[1], vector[2]), default=False, is_vector=True)

def rotateVector(q: Quaternion, v: Vector) -> Vector:
  """ Rotates a 3-d vector given a quaternion

  Args:
      q (Quaternion): rotation operator
      v (Vector): a vector to be rotated

  Returns:
      Vector: the final rotated vector
  """
  # Convert vector to quaternion form
  v_q = v.extend_to_quaternion()
  
  # And get q conjugate to complete the rotation
  if q.is_norm():
    qinv = q.get_conjugate()

  intermediateV = hamiltonProduct(q1=q, q2=v_q)
  finalV = hamiltonProduct(q1=intermediateV, q2=qinv)
  
  return finalV.contract_to_vector()

def rotateQuaternion(q1: Quaternion, q2: Quaternion) -> Quaternion:
  """ Transforms a quaternion representing a single rotation from one initial frame to the continuously evolving body frame
  
  This process is shorter than transforming a vector, to transform a quaternion it is simple: q_new = p q_old where p is the
  quaternion used to transform q, and q is the orientation quaternion. This can then be used to rotate a vector from inertial
  frame to body frame via the formula: v_new = q v_old q_conjugate

  Args:
      q1 (Quaternion): the rotation quaternion
      q2 (Quaternion): the quaternion keeping track of orientation

  Returns:
      Quaternion: transformed orientation quaternion
  """
  return hamiltonProduct(q1=q1, q2=q2)


def exponentiateQuaternion(q: Quaternion, ε: float = 1e-6) -> Quaternion:
  """ Exponentiation of a quaternion to produce a new quaternion -> for solving differential equations on SO(3)

  Args:
      q (Quaternion): a unit quaternion to be exponentiated
      ε (float): tolerance for minimum vector part magnitude to avoid `Division By Zero Error`

  Returns:
      Quaternion: a new unit quaternion generated by exp(q)
  """
  a = q.get_scalar()
  v = q.get_vector()
  θ = v.get_magnitude()
  
  if θ > ε:
    #v_hat = v.get_unit() -> No longer need to normalize the vector part of AngleVector() type for Quaternion() constructor
    return np.exp(a) * Quaternion(angle_vector=(θ, v.v), is_vector=True)
  else:
    return np.exp(a) * Quaternion(default=True) # return the zero quaternion (1, 0, 0, 0) i.e. no rotation


__all__ = [
  "QuaternionElements",
  "QuaternionTuple",
  "Quaternion",
  "AngleVector",
  "VectorElements",
  "Vector",
  "rotateVector",
  "rotateQuaternion",
  "hamiltonProduct",
  "exponentiateQuaternion",
  "np"
]
