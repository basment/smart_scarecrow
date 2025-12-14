import time
import os

import onnxruntime as ort
import cv2
import numpy as np
from picamera2 import Picamera2
from config import MODEL_PATH, FRAME_INTERVAL_SEC, POLICY, PROJECT_ROOT
from engine import DeterrenceEngine

class AnimalDeterrenceApp:
	def __init__(self):
		self.model = ort.InferenceSession(MODEL_PATH, providers=['CPUExecutionProvider'])
		self.input_name = self.model.get_inputs()[0].name
		self.engine = DeterrenceEngine()
		self.camera = self.setup_camera()
		self.is_running = False

	def setup_camera(self):
		camera = Picamera2()
		
		config = camera.create_still_configuration(
			main={"format": "RGB888"},
			buffer_count=2
		)
		camera.configure(config)
		camera.start()
		
		time.sleep(2) 
		return camera
	
	def capture_frame(self):
		image_path = os.path.join(PROJECT_ROOT, "demo_testing", "capture.jpg")
		try:
			frame = self.camera.capture_array()
			self.camera.capture_file(image_path)

			return frame
		except Exception as e:
			return None
	
	"""
	Function for letterboxing the image:
		- resize the image to fit within the desired shape while maintaining aspect ratio
		- pad the image to reach the desired shape
		
		Parameters:
			img: input image
			new_shape: desired output shape (width, height)
			color: padding color (default gray)
		Returns:
			img: the letterboxed image 
	"""
	def letterbox_image(self, img, new_shape=(512, 512), color=(114, 114, 114)):
		h, w = img.shape[:2]
		new_w, new_h = new_shape
		scale = min(new_w / w, new_h / h)
		resize_w, resize_h = int(w * scale), int(h * scale)
		resized = cv2.resize(img, (resize_w, resize_h))
		pad_w = new_w - resize_w
		pad_h = new_h - resize_h

		pad_left = pad_w // 2
		pad_right = pad_w - pad_left
		pad_top = pad_h // 2
		pad_bottom = pad_h - pad_top
		img = cv2.copyMakeBorder(
			resized, pad_top, pad_bottom, pad_left, pad_right,
			cv2.BORDER_CONSTANT, value=color
			)

		return img

	def pre_process_frame(self, frame, img_size=512):
		img = self.letterbox_image(frame, (img_size, img_size))
		img = img.astype('float32') / 255.0
		img = img.transpose(2, 0, 1)  # HWC to CHW
		img = np.expand_dims(img, axis=0)
		return img

	def process_frame(self, frame):
		try:
			# Run model
			out = self.model.run(None, {self.input_name: frame})[0]

			# YOLOv8 ONNX format: (1, 8, 5376)
			out = out.squeeze(0)             # (8, 5376)
			out = out.transpose(1, 0)        # (5376, 8)

			# boxes + class scores
			boxes = out[:, :4]
			class_scores = out[:, 4:]        # (5376, 4), already probabilities

			class_names = ['bird', 'bunny', 'deer', 'squirrel']

			# 🔥 DEBUG: print the highest score for each class every frame
			max_per_class = class_scores.max(axis=0)
			debug_str = ", ".join([f"{c}: {max_per_class[i]:.4f}" 
								for i, c in enumerate(class_names)])
			print("Probabilities:", debug_str)

			detections = []
			for idx, cname in enumerate(class_names):
				threshold = POLICY[cname]['confidence_threshold']
				scores = class_scores[:, idx]

				if np.any(scores >= threshold):
					detections.append({
						"class_name": cname,
						"confidence": float(scores.max())
					})

			return detections

		except Exception as e:
			print(f"Error processing frame: {e}")
			return []



	def run(self):
		"""Main application loop"""
		self.is_running = True

		try:
			while self.is_running:
				start_time = time.time()
				
				frame = self.capture_frame()
				if frame is None:
					time.sleep(0.1)
					continue

				model_input = self.pre_process_frame(frame)

				detections = self.process_frame(model_input)
				
				if detections:
					print("DETECTED:", detections)
					self.engine.process_detections(detections)
				else:
					print("NUFFIN YET")

				processing_time = time.time() - start_time
				sleep_time = max(0, FRAME_INTERVAL_SEC - processing_time)
				if sleep_time > 0:
					time.sleep(sleep_time)

		finally:
			self.stop()

	def stop(self):
		"""stop the application and remember to cleanup resources"""
		self.is_running = False
		self.cleanup()

	def cleanup(self):
		"""clean up all resources"""
		try:
			self.engine.cleanup()
			if hasattr(self, 'camera'):
				self.camera.stop()
				self.camera.close()
		except Exception as e:
			return None

def main():
	"""Main entry point for the application"""
	app = AnimalDeterrenceApp()
	app.run()

if __name__ == "__main__":
	main()

