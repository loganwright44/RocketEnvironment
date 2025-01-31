"""
Author: Logan Wright
Date: 1/31/2025
All rights reserved.
"""

from typing import Any

from Design import *
from Builder import *
from MotorManager import *
from Element import *
from ElementTypes import *
from Quaternion import *
from SerialManager import *
from ThrustVectorController import *
from VectorPlotter import *
from Integrator import *


Request = Dict[str, Any]
Response = Dict[str, Any]


class PhysicsAPI(object):
  is_consolidated: bool = None
  motor_manager: MotorManager = None
  tvc: ThrustVectorController = None
  data_dict: Dict[str, ConfigDict] = None
  motor_index: int = None
  builder: Builder = None
  design: Design = None
  part_numbers: Dict[str, int] = None
  
  def __init__(self):
    print("Retrieved an instance of the PhysicsAPI objects")
  
  def getMotorOptions(self, req: Request) -> Response:
    """ gets the list of supported solid motor boosters

    Returns:
        dict: response containing key: res, and values: list of available motors (str)
    """
    return {"res": AVAILABLE, "message": None}
  
  def postMotor(self, req: Request) -> Response:
    """ change/set the motor to be used

    Args:
        req (dict): key: "motor", value: (str) motor id e.g. E12, F15

    Returns:
        Dict[str, bool]: key: res, value: bool
    """
    if self.motor_manager is not None:
      self.motor_manager._instance = None # a simple way to reset the singleton instance
    
    if req["motor"] in AVAILABLE:
      self.motor_manager = MotorManager(motor=req["motor"])
      return {"res": True, "message": None}
    else:
      return {"res": False, "message": None}
  
  def postLockTVC(self, req: Request = None) -> Response:
    """ locks the thrust vectoring unit if and only if a motor manager has been properly setup

    Args:
        req (Request): a request, ignored

    Returns:
        Response: _description_
    """
    if self.motor_manager is not None:
      self.tvc = ThrustVectorController(motor_manager=self.motor_manager)
      return {"res": True, "message": None}
    else:
      return {"res": False, "message": "Motor not yet set, or incorrectly set"}
  
  def postAddElement(self, req: Request) -> Response:
    """ unions another dictionary with a key: name and value: ConfigDict of data to the API design

    Args:
        req (Request): a request containing key: req, value: Dict["name": ConfigDict(...)]

    Returns:
        Response: key: res, value: None
    """
    self.data_dict.update(req["req"])
    return {"res": None}
  
  def deleteElement(self, req: Request) -> Response:
    """ deletes an Element from the design list

    Args:
        req (Request): key: req, value: (str) name of the element

    Returns:
        Response: _description_
    """
    if not self.is_consolidated:
      if req["name"] in self.data_dict.keys():
        _ = self.data_dict.pop(req["name"])
        return {"res": True}
      else:
        return {"res": False}
    else:
      return {"res": False, "message": "Cannot change design when the design is already consolidated"}
  
  def deleteAllElements(self, req: Request = None) -> Response:
    """ resets the element list

    Args:
        req (Request): empty, None

    Returns:
        Response: key: res, value: bool
    """
    self.data_dict = None
    return {"res": True}
  
  def postBuildDesign(self, req: Request = None) -> Response:
    """ set the builder to not None and build the design

    Args:
        req (Request): empty, None

    Returns:
        Response: key: res, value: bool
    """
    if self.builder is None and self.design is None:
      self.builder = Builder(data_dict=self.data_dict)
      self.design, self.part_numbers = self.builder.generate_design()
      return {"res": True}
    else:
      return {"res": False, "message": "Design is already built, cannot regenerate"}
  
  def deleteBuilder(self, req: Request = None) -> Response:
    """ deletes the builder class and resets the singleton instance to uninitialized

    Args:
        req (Request): empty, None

    Returns:
        Response: key: res, value: bool
    """
    if self.builder is not None:
      self.builder._instance = None
      self.builder = None
    
    return {"res": True}
  
  def deleteDesign(self, req: Request = None) -> Response:
    """ deletes an entire design permanently and causes a reset

    Args:
        req (Request): empty, None

    Returns:
        Response: key: res, value: bool
    """
    if self.design is not None:
      self.design = None
    
    _ = self.deleteBuilder()
    
    return {"res": True}

  def getAllPartNumbers(self, req: Request = None) -> Response:
    """ returns the part numbers and names in the API

    Args:
        req (Request): empty, None

    Returns:
        Response: key: res, value: (dict) containing {part_name: part_index}
    """
    return {"res": self.part_numbers} if self.part_numbers is not None else {"res": {}}
  
  def getDesignSummary(self, req: Request = None) -> Response:
    """ returns a format string of the design summary

    Args:
        req (Request): empty, None

    Returns:
        Response: key: res, value: str
    """
    if self.design is not None:
      return {"res": self.design.__str__()}
    else:
      return {"res": ""}
  
  def postElementAdjustment(self, req: Request) -> Response:
    """ translates/rotates an element body in design before consolidation

    Args:
        req (Request): {key: (str) id, value: (str) id, key: "translation", value: translation (NDArray | Optional), key: "rotation", value: rotation (Quaternion| Optional)]

    Returns:
        Response: key: res, value: bool
    """
    if req["id"] in self.part_numbers.keys():
      if self.design is None:
        return {"res": False, "message": "to adjust an element's position or rotation, you must first generate the design with the `.postBuildDesign() method`"}
      
      id = self.part_numbers[req["id"]]
      self.design.manipulate_element(id=id, displacement=req["translation"], attitude=req["rotation"])
      return {"res": True}
    else:
      return {"res": False, "message": "id not found in the elements parts list within this API instance"}
      
  
  


__all__ = [
  "PhysicsAPI"
]
