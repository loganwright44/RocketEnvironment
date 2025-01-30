from __future__ import annotations
from typing import Tuple, Dict, TypedDict, List
import struct
import serial

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
  
  def getAvailablePorts(self):
    return [port.device for port in serial.tools.list_ports.comports()]
  
  def isConnected(self) -> bool:
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
  
if __name__ == "__main__":
  se = SerialManager(port="/dev/cu.usbserial-210", baud_rate=115200)
  if se.isConnected():
    while True:
      print(se.readData())
