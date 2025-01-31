import matplotlib.pyplot as plt
from MotorManager import *

def just_making_sure():
  motor = MotorManager(motor="E12")

  t_list = []
  T_list = []
  for n in range(1000):
    t = n * 1e-2
    T_list.append(motor.getThrust(t=t))
    t_list.append(t)

  plt.plot(t_list, T_list)
  plt.show()


if __name__ == "__main__":
  just_making_sure()