Revamp of system logic.
Added the following:
- Letterboxing function to scale down images to the correct size for inference while keeping aspect ratio
- Changed inference from pt to ONNX for disk space efficiency and inference speeds (No longer need to save image to storage)
- Removed CAPTURE_SIZE vairable as the PiCamera does not respect aspect ratio and will distort the image
- Added a pre processing function to convert the NumPy output to be compatible with ONNX's run()
- Rewrote the process_frame function
- Changed the class constructor to use ONNX format
- Rewrote the AnimalDeterrenceApp function run() to correctly include new functions
- Other formatting, spelling, and bug fixes.
