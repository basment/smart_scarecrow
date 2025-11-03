import time
import logging
from ultralytics import YOLO
from picamera2 import Picamera2
from config import MODEL_PATH, CAPTURE_SIZE, FRAME_INTERVAL_SEC, TEST_MODE, TARGET_CLASSES
from engine import DeterrenceEngine

logging.basicConfig(
    level=logging.DEBUG if TEST_MODE else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class AnimalDeterrenceApp:
    
    def __init__(self):
        self.model = YOLO(MODEL_PATH)
        self.engine = DeterrenceEngine()
        self.camera = self.setup_camera()
        self.is_running = False
        
        logging.info(f"Loaded model with classes: {self.model.names}")
        logging.info(f"Target classes: {TARGET_CLASSES}")
        
    def setup_camera(self):
        camera = Picamera2()
        
        config = camera.create_still_configuration(
            main={"size": CAPTURE_SIZE, "format": "RGB888"},
            buffer_count=2
        )
        camera.configure(config)
        camera.start()
        
        time.sleep(2) 
        logging.info("Camera initialized successfully")
        return camera
    
    def capture_frame(self):
        try:
            frame = self.camera.capture_array()
            return frame
        except Exception as e:
            logging.error(f"Frame capture error: {e}")
            return None
    
    def process_frame(self, frame):
        try:
            results = self.model(frame, verbose=False)
            
            detections = []
            for result in results:
                if result.boxes is not None:
                    for box in result.boxes:
                        class_id = int(box.cls)
                        confidence = float(box.conf)
                        class_name = self.model.names[class_id]
                        
                        if class_name in TARGET_CLASSES:
                            detections.append({
                                'class_name': class_name,
                                'confidence': confidence,
                                'bbox': box.xyxy[0].cpu().numpy() if box.xyxy is not None else None
                            })
            
            return detections
            
        except Exception as e:
            logging.error(f"Detection error: {e}")
            return []
    
    def run(self):
        """Main application loop"""
        self.is_running = True
        logging.info("Starting Animal Deterrence System")
        
        try:
            while self.is_running:
                start_time = time.time()
                
                frame = self.capture_frame()
                if frame is None:
                    time.sleep(FRAME_INTERVAL_SEC)
                    continue
                
                detections = self.process_frame(frame)
                
                if detections:
                    for det in detections:
                        logging.info(f"Detected {det['class_name']} with confidence {det['confidence']:.2f}")
                
                self.engine.process_detections(detections)
                
                processing_time = time.time() - start_time
                sleep_time = max(0, FRAME_INTERVAL_SEC - processing_time)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            logging.info("System stopped by user")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """stop the application and remember to cleanup resources"""
        self.is_running = False
        logging.info("Stopping Animal Deterrence System")
        self.cleanup()
    
    def cleanup(self):
        """clean up all resources"""
        try:
            self.engine.cleanup()
            if hasattr(self, 'camera'):
                self.camera.stop()
                self.camera.close()
            logging.info("Cleanup completed")
        except Exception as e:
            logging.error(f"Cleanup error: {e}")

def main():
    """Main entry point for the application"""
    app = AnimalDeterrenceApp()
    app.run()

if __name__ == "__main__":
    main()

