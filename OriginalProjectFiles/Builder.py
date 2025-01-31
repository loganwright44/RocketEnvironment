from __future__ import annotations
from typing import Tuple, List, TypedDict, Type, Dict, Any

from Design import *
from Element import *


class ConfigDict(TypedDict):
  Type: Type[Element]
  Args: Dict[str, Any]


class Builder:
  _instance = None
  
  def __new__(cls, data_dict: Dict[str, ConfigDict]):
    if cls._instance is None:
      cls._instance = super().__new__(cls)
    return cls._instance
  
  def __init__(self, data_dict: Dict[str, ConfigDict]):
    if not hasattr(self, "initialized"):
      self.initialized = True
      self.elements = objectFactory(data_dict=data_dict)
      self.part_numbers = {}
      statics = []
      dynamics = []
      name: str
      element: Element
      for name, element in self.elements.items():
        self.part_numbers[name] = element.id
        if element.is_dynamic():
          dynamics.append(element)
        else:
          statics.append(element)
      
      self.parts_list = PartsList(Static=statics, Dynamic=dynamics)
      
      del dynamics
      del statics
    
    else:
      pass
  
  def generate_design(self) -> Tuple[Design, Dict[str, int]]:
    return (Design(parts_list=self.parts_list), self.part_numbers)


def objectFactory(data_dict: Dict[str, ConfigDict]) -> dict:
  instances = {}
  for unique_name, config in data_dict.items():
    cls = config["Type"]
    args = config.get("Args", {})
    instances[unique_name] = cls(name=unique_name, **args)
  
  return instances


__all__ = [
  "ConfigDict",
  "Builder"
]