from __future__ import annotations
from typing import Tuple, Dict, TypedDict, List
import struct
import serial

from Quaternion import *

# both use little endian implemented by the `<` symbol
QUATERNION_PACKET = "<4d"
SERVO_PACKET = "<2d"


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
  
  def availablePorts(self):
    return [port.device for port in serial.tools.list_ports.comports()]
  
  def startConnection(self) -> bool:
    try:
      self.serial = serial.Serial(port=self.port, baudrate=self.baud_rate, timeout=1)
      print(f"Serial connection successful to port `{self.port}`")
      return True
    except serial.SerialException as e:
      print(f"Error: {e}")
      return False
  
  def readData(self):
    res = self.serial.readline().decode().strip()
    if res:
      return res
    else:
      return None


def serializeQuaternion(q: Quaternion) -> bytes:
  """ packs a quaternion data into a 4-double bytes object to be passed over serial to arduino or other serial device

  Args:
      q (Quaternion): the orientation from simulation for the HIL

  Returns:
      bytes: the packed data ready for serial transmission
  """
  return struct.pack(QUATERNION_PACKET, *(q.q[0], q.q[1][0], q.q[2][1], q.q[3][2]))
