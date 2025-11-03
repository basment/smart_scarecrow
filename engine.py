#this class will be the "decision engine" which will decide how to act based on the per-class conf, debouce, and cooldown
import time
import logging
from typing import Dict, List
from datetime import datetime, timedelta
from config import POLICY, TARGET_CLASSES
from hw import HardwareController


class DeterrenceEngine:
    """the engine that processes animal detections and manages deterrent activation"""
    
    def __init__(self):
        self.hw = HardwareController()
        self.last_activation = {}  
        
    def can_activate(self, animal_type: str, confidence: float) -> bool:
        """Check if deterrent can be activated based on policy"""
        if animal_type not in POLICY:
            return False
            
        policy = POLICY[animal_type]
        
        if confidence < policy["confidence_threshold"]:
            return False
            
        last_time = self.last_activation.get(animal_type)
        if last_time:
            cooldown = timedelta(seconds=policy["cooldown_seconds"])
            if datetime.now() - last_time < cooldown:
                return False
                
        return True
    
    def activate_deterrent(self, animal_type: str, confidence: float):
        if not self.can_activate(animal_type, confidence):
            logging.debug(f"deterrent for {animal_type} is in the cooldown period")
            return
            
        policy = POLICY[animal_type]
        method = policy["deterrence_method"]
        duration = policy["duration_seconds"]
        
        logging.info(f"Activating {method} for {animal_type} (conf: {confidence:.2f})")
        
        if method == "laser_with_motor":
            self.hw.activate_laser_with_motor(duration)
            
        elif method == "stepper_motor":
            self.hw.activate_motor_only(duration)
            
        elif method == "buzzer":
            frequency = policy.get("buzzer_frequency", 2000)
            self.hw.activate_buzzer_only(duration, frequency)
 
        self.last_activation[animal_type] = datetime.now()
    
    def process_detections(self, detections: List[Dict]):
        for detection in detections:
            animal_type = detection.get('class_name', '').lower()
            confidence = detection.get('confidence', 0.0)
            
            if animal_type in TARGET_CLASSES:
                self.activate_deterrent(animal_type, confidence)
    
    def cleanup(self):
        """Clean up hardware resources"""
        self.hw.cleanup()



