"""
from ultralytics import YOLO
from gpiozero import LED, Buzzer
from picamera2 import Picamera2
import time, os

PROJECT_ROOT = "/home/scarecrow/Documents/Scarecrow"
model_path = os.path.join(PROJECT_ROOT, "yolov8n.pt")
image_path = os.path.join(PROJECT_ROOT, "demo_testing", "capture.jpg")

model = YOLO(model_path)
print(model.names)
deterrent = LED(17)

#Creates a Picamera2 object
picam2 = Picamera2()

config = picam2.create_still_configuration()
picam2.configure(config)
picam2.start()
time.sleep(2)

while True:
    #Takes the image and saves it at param; ie. image_path
    picam2.capture_file(image_path)
    print(f"✅ Saved image to {image_path}")

    #Runs predict function on the img specified in source and adds bounding boxes
    #Saves the image into a list, one object for each image -> results; 

    results = model.predict(source=image_path, show=True)

    bird_detected = False

    #Each object in the list has the following attributes:
    #results[0].boxes - A list of detected bounding boxes (each with coordinates, confidence, and class).
    #results[0].masks - Segmentation masks (if using a segmentation model).
    #results[0].keypoints - Keypoints (for pose estimation models).
    #results[0].names - A dictionary mapping class IDs to readable names.
    #results[0].orig_img - The original input image (NumPy array).
    #results[0].plot() - A rendered version of the image with boxes drawn on it.

    for box in results[0].boxes:
        cls = int(box.cls) #cls - class ID
        conf = float(box.conf) #conf - confidence level out of 1.0
        print(f"Detected class {model.names[cls]} with confidence {conf:.2f}")
        class_name = model.names[cls]

        if class_name.lower() == "deer" and conf > 0.5:
            bird_detected = True
            print("What the deer doin")
        else:
            print("Where the deer at???")

    picam2.close()

    if bird_detected:
        print("Deer detected! Activating deterrent...")
        deterrent.on()
        time.sleep(2)   # keep deterrent active for 2 seconds
        deterrent.off()

    time.sleep(10)


    """
    # hardware_selftest.py
import time
import logging
import argparse

# Import your existing controller (no edits to app/engine/hw needed)
from hw import HardwareController

def main():
    parser = argparse.ArgumentParser(description="Smart Scarecrow hardware self-test (no camera/model).")
    parser.add_argument("--laser", type=float, default=0.0, help="Seconds to run laser (coupled with motor).")
    parser.add_argument("--motor", type=float, default=0.0, help="Seconds to run motor only.")
    parser.add_argument("--buzzer", type=float, default=0.0, help="Seconds to run buzzer only.")
    parser.add_argument("--all", action="store_true", help="Run a short sequence of all tests.")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        force=True,
    )

    ctrl = HardwareController()
    logging.info("HardwareController ready.")

    try:
        if args.all:
            logging.info("=== SEQUENCE: laser+motor (1.5s) ===")
            ctrl.activate_laser_with_motor(1.5)
            time.sleep(2.0)

            logging.info("=== SEQUENCE: motor only (1.5s) ===")
            ctrl.activate_motor_only(1.5)
            time.sleep(2.0)

            logging.info("=== SEQUENCE: buzzer only (1.0s) ===")
            ctrl.activate_buzzer_only(1.0, frequency=None)
            time.sleep(1.0)

        if args.laser > 0:
            logging.info(f"Laser+motor for {args.laser}s")
            ctrl.activate_laser_with_motor(args.laser)
            time.sleep(args.laser + 0.5)

        if args.motor > 0:
            logging.info(f"Motor only for {args.motor}s")
            ctrl.activate_motor_only(args.motor)
            time.sleep(args.motor + 0.5)

        if args.buzzer > 0:
            logging.info(f"Buzzer only for {args.buzzer}s")
            ctrl.activate_buzzer_only(args.buzzer)
            time.sleep(args.buzzer + 0.5)

        logging.info("Self-test finished.")

    except KeyboardInterrupt:
        logging.info("Interrupted by user.")
    finally:
        logging.info("Cleaning up hardware…")
        ctrl.cleanup()
        logging.info("Cleanup complete.")

if __name__ == "__main__":
    main()
