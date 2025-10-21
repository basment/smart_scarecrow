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