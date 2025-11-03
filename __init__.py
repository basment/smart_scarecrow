#project package iniitalization 

__version__ = "1.0"
__author__ = "Senior Design (Fall 25) - Group 2"
__title__ = "The Smart Scarecrow"

from app import AnimalDeterrenceApp
from engine import DecisionEngine
from hw import HardwareController

__all__ = ['AnimalDeterrenceApp', 'DeterrenceEngine', 'HardwareController']