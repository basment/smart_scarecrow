#this class will handle the configuration of the pins for the detterance methods
#Motor -> GPIO17 (pul+) GPIO22 (dir+) and GPIO 27 (enb+)
#laser....?
#buzzer???

import os 
 
#runtime toggles (TAKE OUT AFTER TESTING) 
TEST_MODE =os.environ.get("TEST_MODE", "0") == "1"
SHOW_DUBUG = True
#ADD THE PROJECT ROOT AND MODEL PATH 
PROJECT_ROOT = ""
MODEL_PATH = ""

#camera loop (need to ask ali if the capure size and frame has been defined or not yet
CAPTURE_SIZE = (420, 420)
FRAME_INTERVAL_SEC = 0.5

#TARGET CLASSES (THE ANIMALS)
TARGET_CLASSES = {"deer", "bird", "squirrl", "rabbit"}

#Policy def for each of teh target classes, we will have to define the conf, debounce, cooldown, duration
POLICY = {
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
LASER = {}
BUZZER = {}




