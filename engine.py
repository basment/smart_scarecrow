#this class will be the "decision engine" which will decide how to act based on the per-class conf, debouce, and cooldown
import time
from collections import defaultdict, deque
from typing import Dict, List, Tuple, Optional, Set


class DecisiomEngine:
	"""
			UMMMMMMM
			this class will act as the brain of the program, it should decide when and what the action should be
			but will have to collect detections from the AI model
			inputs fro this class will be the animal classification from the AI model as well as the policy for each class which will 
			defined in the config file.
			will have to apply cooldown as well to prevent overtriggering the deterrance actions
	""" 



