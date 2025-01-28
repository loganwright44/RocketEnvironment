from __future__ import annotations
from typing import Tuple, TypedDict, Type, Dict, List
import pandas as pd
from pandas import DataFrame
from numpy.random import randn as normal_random_variable
import os
import json


from Element import Cylinder
from Builder import ConfigDict
from ElementTypes import *


DATA_FOLDER = "./MotorData/"
AVAILABLE = [name[0] for name in [[file.split(".")[0] for file in files if len(files) > 0 and file.endswith("json")] for _, _, files in os.walk(DATA_FOLDER)] if len(name) > 0]


def getMotorData(motor: str) -> Tuple[DataFrame, Dict[str, List[int]]]:
  motor_csv = "Estes" + motor + ".csv"
  motor_json = motor + ".json"
  
  for _dir, _, _files in os.walk(DATA_FOLDER):
    if motor_csv in _files:
      return (pd.read_csv(_dir + "/" + motor_csv), json.load(open(_dir + "/" + motor_json)))
  

def getLinearInterpolations(data: DataFrame) -> Tuple[List[float], List[float], List[float]]:
  """ a function to compute the elements required to approximate thrust as a function of time based on a preset motor type
  
  - Usage: Thrust(time) = Thrust_intercept + slope(time) * (time - time_intercept)

  Args:
      data (DataFrame): the loaded csv data into a pandas dataframe

  Returns:
      Tuple[List[float], List[float], List[float]]: slopes, time_intercepts, and the thrust_intercepts
  """
  M = []
  T = []
  THRUST = []
  for index in range(len(data) - 1):
    m = (data["Thrust (N)"][index + 1] - data["Thrust (N)"][index]) / (data["Time (s)"][index + 1] - data["Time (s)"][index])
    t = data["Time (s)"][index]
    thrust = data["Thrust (N)"][index]
    
    M.append(m)
    T.append(t)
    THRUST.append(thrust)
  
  return (M, T, THRUST)
    


class MotorManager:
  _instance = None
  
  def __new__(cls, *args, **kwargs):
    if cls._instance is None:
      cls._instance = super().__new__(cls)
    return cls._instance
  
  def __init__(self, motor: str):
    if not hasattr(self, "initialized"):
      self.initialized = True
      if motor in AVAILABLE:
        self.motor = motor
        self.initialize()
      else:
        raise KeyError(f"Motor type must be one of {AVAILABLE}")
    else:
      pass
  
  def initialize(self):
    self.data_frame, self.params = getMotorData(motor=self.motor)
    self.slopes, self.time_intercepts, self.thrust_intercepts = getLinearInterpolations(data=self.data_frame)
  
  def getThrust(self, t: float) -> float:
    """ computes the scalar thrust of the motor at time t

    Args:
        t (float): time in seconds

    Returns:
        float: thrust in Newtons
    """
    for index, _t in enumerate(self.time_intercepts):
      if t <= _t:
        index -= 1
        T = self.thrust_intercepts[index] + self.slopes[index] * (t - self.time_intercepts[index])
        return T if T >= 0 else 0.0
      else:
        pass
    
    return 0.0
  
  def getElementData(self) -> Dict[str, ConfigDict]:
    """ forms a single element of the design constraints for the motor, only requiring repositioning and rotating to initial setup

    Returns:
        Dict[str, ConfigDict]: the `rocket_motor` element of a design
    """
    radius = (self.params["diameter"][0] + normal_random_variable() * self.params["diameter"][1]) * 1e-3 / 2
    height = (self.params["length"][0] + normal_random_variable() * self.params["length"][1]) * 1e-3
    initial_mass = (self.params["total mass"][0] + normal_random_variable() * self.params["total mass"][1]) * 1e-3
    propellant_mass = (self.params["propellant mass"][0] + normal_random_variable() * self.params["propellant mass"][1]) * 1e-3
    final_mass = initial_mass - propellant_mass
    burn_time = (self.params["burn time"][0] + normal_random_variable() * self.params["burn time"][1])
    config_dict = ConfigDict(
      Type=Cylinder,
      Args=CylinderDictD(radius=radius, height=height, mass=initial_mass, is_static=False, min_mass=final_mass, duration=burn_time)
    )
    
    return {"rocket_motor": config_dict}
    
  
  

__all__ = [
  "MotorManager"
]