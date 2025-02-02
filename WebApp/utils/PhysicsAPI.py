"""
Author: Logan Wright
Date: 1/31/2025
All rights reserved.
"""

from typing import Any
import numpy as np

from Design import *
from Builder import *
from MotorManager import *
from Element import *
from ElementTypes import *
from SerialManager import *
from ThrustVectorController import *
from SimulationLoop import simulationLoop


Request = Dict[str, Any]
Response = Dict[str, Any]


class PhysicsAPI:
  _instance = None
  is_consolidated: bool = False
  is_listening: bool = False
  motor_manager: MotorManager = None
  tvc: ThrustVectorController = None
  data_dict: Dict[str, ConfigDict] = {}
  motor_index: int = None
  builder: Builder = None
  design: Design = None
  part_numbers: Dict[str, int] = None
  serial_manager: SerialManager = None
  
  def __new__(cls, *args, **kwargs):
    if cls._instance is None:
      cls._instance = super().__new__(cls)
    return cls._instance
  
  def __init__(self):
    if not hasattr(self, "initialized"):
      self.initialized = True
      print("Retrieved an instance of the PhysicsAPI objects")
    else:
      print("Accessed a running instance of PhysicsAPI")
  
  def postConnectSerial(self, req: Request) -> Response:
    """ creates the serial manager object and attempts to connect

    Args:
        req (Request): {"port": str, "baud_rate": int}

    Returns:
        Response: key: res, value: bool
    """
    if "port" not in req.keys():
      req["port"] = None
    if "baud_rate" not in req.keys():
      req["baud_rate"] = None
    
    self.serial_manager = SerialManager(port=req["port"], baud_rate=req["baud_rate"])
    return {"res": self.serial_manager.startConnection()}
  
  def getAvailablePorts(self, req: Request = None) -> Response:
    """ gets a list of port names available on the device

    Returns:
        Response: key: res, value: list of port names (str)
    """
    self.serial_manager = SerialManager(baud_rate=115200)
    return {"res": self.serial_manager.availablePorts()}
  
  def postStartListening(self, req: Request = None) -> Response:
    """ starts the listener on the serial port

    Args:
        req (Request): empty, None

    Returns:
        Response: key: res, value: bool
    """
    self.serial_manager.activateListener()
    self.is_listening = True
    return {"res": True}
  
  def getFlightComputerPacket(self, req: Request = None) -> Dict[str, List[float]]:
    """ attempts to get a packet of data from the flight computer if available

    Args:
        req (Request, optional): empty, None

    Returns:
        Response: key: res, value: bool
    """
    if not self.serial_manager.queue.empty():
      servo_angles = self.serial_manager.queue.get()
      return {"res": servo_angles}
    else:
      return {"res": []}
  
  def postWriteToFlightComputer(self, req: Request) -> Response:
    """ writes data to the flight computer

    Args:
        req (Request): {"data": q (Quaternion)}

    Returns:
        Response: key: res, value: bool
    """
    if "data" not in req.keys():
      req["data"] = Quaternion(default=True)
    
    self.serial_manager.sendData(q=req["data"])
    
    return {"res": True}
  
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
      if "rocket_motor" in self.data_dict.keys():
        _ = self.data_dict.pop("rocket_motor")
      
      self.motor_index = len(self.data_dict)
      self.motor_manager = MotorManager(motor=req["motor"])
      self.data_dict.update(self.motor_manager.getElementData())
      return {"res": True, "message": None}
    else:
      return {"res": False, "message": None}
  
  def postMakeTVC(self, req: Request = None) -> Response:
    """ makes the thrust vectoring unit if and only if a motor manager has been properly setup

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
    self.data_dict.update(req)
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
    if "rotation" not in req.keys():
      req["rotation"] = None
    if "translation" not in req.keys():
      req["translation"] = None
    
    if req["id"] in self.part_numbers.keys():
      if self.design is None:
        return {"res": False, "message": "to adjust an element's position or rotation, you must first generate the design with the `.postBuildDesign() method`"}
      
      id = self.part_numbers[req["id"]]
      self.design.manipulate_element(id=id, displacement=req["translation"], attitude=req["rotation"])
      return {"res": True}
    else:
      return {"res": False, "message": "id not found in the elements parts list within this API instance"}
  
  def postMotorAdjustment(self, req: Request) -> Response:
    """ translates/rotates the initial motor placement

    Args:
        req (Request): {key: "translation", value: translation (NDArray | Optional), key: "rotation", value: rotation (Quaternion| Optional)]

    Returns:
        Response: key: res, value: bool
    """
    if "rotation" not in req.keys():
      req["rotation"] = None
    if "translation" not in req.keys():
      req["translation"] = None
    
    self.design.manipulate_element(id=self.motor_index, displacement=req["translation"], attitude=req["rotation"])
    self.tvc.moveToMotor(offset=req["translation"])
    return {"res": True}
  
  def postLockStaticElements(self, req: Request = None) -> Response:
    """ irreversible lock on the design, reset requires complete rebuild

    Args:
        req (Request, optional): empty, None

    Returns:
        Response: key: res, value: bool
    """
    self.design.consolidate_static_elements()
  
  def postSetTVC(self, req: Request) -> Response:
    """ sets the angle for the TVC at launch and forces setting regardless servo speed

    Args:
        req (Request): {"x": (float) angle_x, "y": (float) angle_y}

    Returns:
        Response: key: res, value: bool
    """
    self.tvc.updateSetpoint(targetx=req["x"], targety=req["y"])
    self.tvc.forceToTarget()
    return {"res": True}
  
  def getSimulationResults(self, req: Request = {}) -> None:
    """ this function calls the simulation method based on the finalized design - all presets should have been performed already

    Args:
        req (Request, optional): {"save": bool, "filename": str name of file (include .mp4 in the filename)}. Defaults to None.

    Returns:
        None
    """
    if "save" not in req.keys():
      req["save"] = True
    if "filename" not in req.keys():
      req["filename"] = "temp.mp4"
    
    if self.is_listening:
      simulationLoop(serial_manager=self.serial_manager, design=self.design, tvc=self.tvc, motor_idx=self.motor_index, dt=1e-2, save=req["save"], filename=req["filename"])
    else:
      simulationLoop(serial_manager=None, design=self.design, tvc=self.tvc, motor_idx=self.motor_index, dt=1e-2, save=req["save"], filename=req["filename"])
    


__all__ = [
  "PhysicsAPI"
]

if __name__ == "__main__":
  api = PhysicsAPI()
  api.postMotor({"motor": "F15"})
  api.postMakeTVC()
  api.postAddElement({
    "flight_computer": ConfigDict(
      Type=Cylinder,
      Args=CylinderDictS(radius=0.072 / 2, height=0.12, mass=0.18, is_static=True)
    )
  })
  api.postAddElement({
    "nose_cone": ConfigDict(
      Type=Cone,
      Args=ConeDictS(radius=0.074 / 2, height=0.2, mass=0.12, is_static=True)
    )
  })
  api.postAddElement({
    "body_tube": ConfigDict(
      Type=Tube,
      Args=TubeDictS(inner_radius=0.072 / 2, outer_radius=0.074 / 2, height=0.8, mass=0.3, is_static=True)
    )
  })
  
  api.postBuildDesign()
  
  api.postMotorAdjustment({"translation": np.array([0, 0, -0.4])})
  api.postElementAdjustment({"id": "flight_computer", "translation": np.array([0, 0, 0.15])})
  api.postElementAdjustment({"id": "nose_cone", "translation": np.array([0, 0, 0.4])})
  api.postElementAdjustment({"id": "body_tube", "translation": np.array([0.0, 0.0, -0.05])})
  
  api.postLockStaticElements()
  api.postSetTVC({"x": 0.0, "y": 0.0})
  
  res = api.postConnectSerial({"port": None, "baud_rate": 115200})
  if res["res"]:
    api.postStartListening()
  
  api.getSimulationResults()
  
  print("Done!")
