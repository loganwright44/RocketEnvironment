from __future__ import annotations
from typing import Tuple, Dict, TypedDict, List
import struct

QUATERNION_PACKET = "4d"
SERVO_PACKET = "2d"


class SerialManager:
  _instance = None
  def __new__(cls, *args, **kwargs):
    if cls._instance is None:
      cls._instance = super().__new__(cls)
    return cls._instance
  
  def __init__(self, port: str, baud_rate: int = 9600):
    if not hasattr(self, "initialized"):
      self.initialized = True
      self.port = port
      self.baud_rate = baud_rate
    else:
      pass
  
  
