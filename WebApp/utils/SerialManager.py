from __future__ import annotations
from typing import Tuple, Dict, TypedDict, List
import struct
import serial
from queue import Queue
import threading
from glob import glob

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
  
  def __init__(self, port: str = None, baud_rate: int = 9600):
    if not hasattr(self, "initialized"):
      self.queue = Queue(maxsize=20)
      self.initialized = True
      self.port = port
      self.baud_rate = baud_rate
    else:
      pass
  
  def availablePorts(self) -> list:
    """ lists the ports that are available

    Returns:
        list: list of port names as a string
    """
    return [port for port in glob("/dev/tty.*")]
  
  def startConnection(self) -> bool:
    """ attempts to connect to the set port

    Returns:
        bool: success or failure to connect
    """
    if self.port is None or self.baud_rate is None:
      return False
    
    try:
      self.serial = serial.Serial(port=self.port, baudrate=self.baud_rate, timeout=5)
      if self.serial.is_open:
        print(f"Serial connection successful to port `{self.port}`")
        return True
    except serial.SerialException as e:
      print(f"Error: {e}")
      return False
  
  def readData(self):
    """ a function reading servo outputs from flight computer, runs on a thread
    """
    while True:
      if self.serial.in_waiting > 0:
        data = self.serial.readline().decode("utf-8").strip()
        values = list(map(float, data.split(",")))
        if len(values) == 2:
          self.queue.put(values)
  
  def activateListener(self) -> None:
    """ starts listening on the port connected to for flight computer outputs
    """
    self.listening_thread = threading.Thread(target=self.readData, daemon=True)
    self.listening_thread.start()
    print(f"Listening in port {self.port}")
  
  def sendData(self, q: Quaternion) -> bool:
    """ sends a quaternion state to the flight computer

    Args:
        q (Quaternion): orientation of the vehicle

    Returns:
        bool: success or failure to send
    """
    w, x, y, z = q.q[0], q.q[1][0], q.q[2][1], q.q[3][2]
    data = f"{w},{x},{y},{z}\n".encode("utf-8")
    self.serial.write(data)
    print(f"Sent: {data.decode("utf-8").strip()}")
    return True


def serializeQuaternion(q: Quaternion) -> bytes:
  """ packs a quaternion data into a 4-double bytes object to be passed over serial to arduino or other serial device

  Args:
      q (Quaternion): the orientation from simulation for the HIL

  Returns:
      bytes: the packed data ready for serial transmission
  """
  return struct.pack(QUATERNION_PACKET, *(q.q[0], q.q[1][0], q.q[2][1], q.q[3][2]))

if __name__ == "__main__":
  ser = SerialManager("/dev/tty.usbserial-210", 115200)
  ser.startConnection()