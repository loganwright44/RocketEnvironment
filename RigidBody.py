from __future__ import annotations
from typing import Union, TypedDict, List, NewType
from Element import *
from Quaternion import *


class ElementData(TypedDict):
  Name: str
  Element: Element
  TimeDependent: bool = None
  MaxMass: float = None
  MinMass: float = None
  Duration: float = None
  StartTime: float = None


class BodyDict(TypedDict):
  All: List[ElementData]


class RigidBody:
  def __init__(self, elements: BodyDict):
    self.elements = elements
    self.init_mass()
  
  def init_mass(self) -> None:
    self.mass = 0.0
    for element_data in self.elements["All"]:
      self.mass += element_data["Element"].mass
  
  def init_cg(self) -> None:
    
    pass
    
  def update_mass(self, t: float, dt: float) -> None:
    pass
        
  


