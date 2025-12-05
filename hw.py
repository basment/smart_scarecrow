import RPi.GPIO as GPIO
import threading
import time
import logging
from config import STEPPER, LASER, BUZZER

logger = logging.getLogger(__name__)

class StepperMotor:
    def __init__(self):
        self.step_pin = STEPPER["PUL"]
        self.dir_pin = STEPPER["DIR"]
        self.enable_pin = STEPPER["ENA"]
        self.pulse_delay = STEPPER["PULSE_US"] / 1_000_000.0  # SECONDS
        self.steps_per_sec = STEPPER["SPEED_STEPS_S"]

        self.is_moving = False
        self.movement_thread = None
        self.stop_oscillation = False

        self.setup()
        logger.info("Stepper motor initialized")

    def setup(self):
        GPIO.setup(self.step_pin, GPIO.OUT)
        GPIO.setup(self.dir_pin, GPIO.OUT)
        GPIO.setup(self.enable_pin, GPIO.OUT)

    def oscillate(self, duration, steps_per_move=1600, move_delay=0.3):
        if self.is_moving:
            logger.debug("Already oscillating")
            return

        def oscillate_thread():
            try:
                self.is_moving = True
                self.stop_oscillation = False
                start_time = time.time()
                direction = 1
                move_count = 0
                logger.debug(f"Starting the motor for {duration} seconds")

                GPIO.output(self.enable_pin, not STEPPER["ENABLE_ACTIVE_HIGH"])
                while (time.time() - start_time < duration) and not self.stop_oscillation:
                    GPIO.output(self.dir_pin, GPIO.HIGH if direction > 0 else GPIO.LOW)
                    for step in range(steps_per_move):
                        if self.stop_oscillation:
                            break
                        GPIO.output(self.step_pin, GPIO.HIGH)
                        time.sleep(self.pulse_delay / 2)
                        GPIO.output(self.step_pin, GPIO.LOW)
                        time.sleep(self.pulse_delay / 2)
                        GPIO.output(self.step_pin, GPIO.LOW)
                        time.sleep(self.pulse_delay / 2)
                        GPIO.output(self.step_pin, GPIO.HIGH)
                        time.sleep(self.pulse_delay / 2)
                       
                    direction *= -1
                    move_count += 1
                    if not self.stop_oscillation and (time.time() - start_time < duration):
                        time.sleep(move_delay)
                GPIO.output(self.enable_pin, not STEPPER["ENABLE_ACTIVE_HIGH"])
                self.is_moving = False
                self.stop_oscillation = False
                logger.debug(f"Motor movement complete, the motor has made {move_count} moves")
            except Exception as e:
                logger.error(f"Motor error: {e}")
                self.is_moving = False
                self.stop_oscillation = False
                GPIO.output(self.enable_pin, not STEPPER["ENABLE_ACTIVE_HIGH"])

        self.movement_thread = threading.Thread(target=oscillate_thread, daemon=True)
        self.movement_thread.start()

    def stop(self):
        self.stop_oscillation = True

class Laser:
    def __init__(self, motor=None):
        self.pin = LASER["PIN"]
        self.active_high = LASER["ACTIVE_HIGH"]
        self.is_running = False
        GPIO.setup(self.pin, GPIO.OUT)
        self.off()
        logger.info("Laser initialized")

    def on(self):
        GPIO.output(self.pin, self.active_high)
        logger.debug("Laser turned on")
        
    def off(self):
        GPIO.output(self.pin, not self.active_high)
        self.is_running = False
        logger.debug("Laser turned off")

    def pulse(self, duration):
        def pulse_thread():
            self.on()
            time.sleep(duration)
            self.off()
        thread = threading.Thread(target=pulse_thread, daemon=True)
        thread.start()

class Buzzer:
    def __init__(self):
        self.pin = BUZZER["PIN"]
        self.active_high = BUZZER["ACTIVE_HIGH"]
        self.is_running = False
        GPIO.setup(self.pin, GPIO.OUT)
        self.off()
        logger.info("BUZZER initialized")

    def on(self):
        GPIO.output(self.pin, self.active_high)
        logger.debug("BUZZER turned on")
        
    def off(self):
        GPIO.output(self.pin, not self.active_high)
        self.is_running = False
        logger.debug("BUZZER turned off")

    def beep(self, duration):
        def beep_thread():
            self.on()
            time.sleep(duration)
            self.off()
        thread = threading.Thread(target=beep_thread, daemon=True)
        thread.start()


class HardwareController:
    
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        self.stepper = StepperMotor()
        self.laser = Laser()
        self.buzzer = Buzzer()
        
        logger.info("HardwareController has been initilized")
    
    def activate_laser_with_motor(self, duration):
        
        def combined_activation():
            try:
                logger.info(f"Activating laser+motor combo for {duration} seconds")
                
                self.laser.on()
                self.stepper.oscillate(duration, steps_per_move=200, move_delay=0.15)
                time.sleep(duration)
                self.laser.off()
                
                logger.info("Laser+motor combo completed")
                
            except Exception as e:
                logger.error(f"Laser+motor combo error: {e}")
                self.laser.off()
                self.stepper.stop()
            
        thread = threading.Thread(target=combined_activation, daemon=True)
        thread.start()
    
    def activate_motor_only(self, duration):
        """activate only the motor (for deer deterrent)"""
        logger.info(f"Activating motor only for {duration} seconds")
        self.stepper.oscillate(duration, steps_per_move=200, move_delay=0.15)
    
    def activate_buzzer_only(self, duration, frequency=None):
        """activate only the buzzer (for squirrels/rabbits)"""
        logger.info(f"Activating buzzer for {duration} seconds")
        self.buzzer.beep(duration)
    
    def cleanup(self):
        """clean up all hardware resources and GPIO states"""
        logger.info("Cleaning up hardware resources...")
        self.laser.off()
        self.buzzer.off()
        self.stepper.stop()
        time.sleep(0.5)
        GPIO.cleanup()
        logger.info("Hardware cleanup completed")
