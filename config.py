#this class will handle the configuration of the pins for the detterance methods
#Motor -> GPIO17 (pul+) GPIO22 (dir+) and GPIO 27 (enb+)
#laser....?
#buzzer???
import os 
 
#runtime toggles (TAKE OUT AFTER TESTING) 
TEST_MODE =os.environ.get("TEST_MODE", "0") == "1"
SHOW_DEBUG = True
#ADD THE PROJECT ROOT AND MODEL PATH 
PROJECT_ROOT = ""
MODEL_PATH = "CropGuardian.onnx"

FRAME_INTERVAL_SEC = 1.0 

#TARGET CLASSES (THE ANIMALS)
TARGET_CLASSES = {"deer", "bird", "squirrel", "bunny"}

#Policy def for each of teh target classes, we will have to define the conf, debounce, cooldown, duration
POLICY = {
	"bird": {
		"confidence_threshold": 0.5, 
		"cooldown_seconds": 5, 
		"duration_seconds": 4, 
		"deterrence_method": "laser_with_motor"
	},
	"deer":{
		"confidence_threshold": 0.5, 
		"cooldown_seconds": 5, 
		"duration_seconds": 4, 
		"deterrence_method": "stepper_motor"
	},
	"bunny":{
		"confidence_threshold": 0.5, 
		"cooldown_seconds": 4, 
		"duration_seconds": 3, 
		"deterrence_method": "buzzer"
	},
	"squirrel":{
		"confidence_threshold": 0.5, 
		"cooldown_seconds": 4, 
		"duration_seconds": 3, 
		"deterrence_method": "buzzer"
	}

}
# === hardware pins (gpio) ====
STEPPER = {
	"ENA" : 22,
	"DIR" : 27, 
	"PUL" : 17, 
	"PULSE_US" : 800, #might have to tweak
	"SPEED_STEPS_S" : 400, #step rate
	"ENABLE_ACTIVE_HIGH" : True, #will have to check if we are able to enable it per our driver.
}
#gpio 1
LASER = {
	"PIN": 1, 
	"ACTIVE_HIGH": True
	}
#gpio 26
BUZZER = {
	"PIN":26, 
	"ACTIVE_HIGH": True, 
	"DEFAULT_FREQUENCY":2000 #dont think we can control frequency with the buzzer we have but will test it anyway
	}




