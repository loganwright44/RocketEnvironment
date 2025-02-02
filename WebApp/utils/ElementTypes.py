from __future__ import annotations
from typing import Tuple, Dict, TypedDict, Type

####################################################################
######################### DYNAMIC DICTS ############################
####################################################################

class CylinderDictD(TypedDict):
  radius: float
  height: float
  mass: float
  is_static: bool = False
  min_mass: float
  duration: float


class TubeDictD(TypedDict):
  inner_radius: float
  outer_radius: float
  height: float
  mass: float
  is_static: bool = False
  min_mass: float
  duration: float


class ConeDictD(TypedDict):
  radius: float
  height: float
  mass: float
  is_static: bool = False
  min_mass: float
  duration: float


class HollowConeDictD(TypedDict):
  inner_radius: float
  outer_radius: float
  inner_height: float
  outer_height: float
  mass: float
  is_static: bool = False
  min_mass: float
  duration: float


####################################################################
########################## STATIC DICTS ############################
####################################################################

class CylinderDictS(TypedDict):
  radius: float
  height: float
  mass: float
  is_static: bool = True

class TubeDictS(TypedDict):
  inner_radius: float
  outer_radius: float
  height: float
  mass: float
  is_static: bool = True


class ConeDictS(TypedDict):
  radius: float
  height: float
  mass: float
  is_static: bool = True


class HollowConeDictS(TypedDict):
  inner_radius: float
  outer_radius: float
  inner_height: float
  outer_height: float
  mass: float
  is_static: bool = True


__all__ = [
  "CylinderDictD",
  "TubeDictD",
  "ConeDictD",
  "HollowConeDictD",
  "CylinderDictS",
  "TubeDictS",
  "ConeDictS",
  "HollowConeDictS"
]