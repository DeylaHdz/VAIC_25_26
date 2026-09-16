# JetsonExample - Core Vision Processing System

This directory contains the core Python application that runs on the NVIDIA Jetson Nano or Raspberry Pi 5 to perform real-time AI vision processing for the VEX AI Competition. The system captures camera frames, runs AI inference to detect game objects, processes depth data to determine 3D positions, and communicates detection data to both the VEX V5 Brain and the web dashboard.

## Overview

The JetsonExample system orchestrates multiple components to create a complete vision processing pipeline:

1. **Camera Capture**: Intel RealSense D435 depth camera captures synchronized RGB and depth frames
2. **Image Processing**: Color correction and preprocessing for AI inference
3. **AI Inference**: YOLOv11-based neural network detects Override game elements (Cups and color-coded Pins)
4. **3D Mapping**: Converts 2D detections to 3D field coordinates using depth data
5. **Position Tracking**: Integrates V5 GPS sensor data for robot localization
6. **Data Communication**: Sends detection data to V5 Brain via serial and web dashboard via WebSocket

## Prerequisites

Before running the JetsonExample code, ensure you have:

- **Hardware Platform**: NVIDIA Jetson Nano or Raspberry Pi 5 with SD card image installed (see [JetsonImages](../JetsonImages/README.md))
- **Intel RealSense D435 Camera**: Connected via USB 3.0
- **VEX V5 Brain** (optional, for serial communication): Connected via USB
- **VEX GPS Sensor** (optional, for position tracking): Connected to V5 Brain

If you built from source instead of using a pre-built image, ensure all dependencies are installed (see build instructions in JetsonImages directory).

## Running the System

### Automatic Start (Pre-built Images)

If you're using a pre-built SD card image, the system automatically runs `override.py` as a systemd service (`vexai`) on boot.

**Service Management Commands:**
- Check status: `sudo systemctl status vexai`
- Start service: `sudo systemctl start vexai`
- Stop service: `sudo systemctl stop vexai`
- Restart service: `sudo systemctl restart vexai`
- Disable auto-start: `sudo systemctl disable vexai`
- Enable auto-start: `sudo systemctl enable vexai`

> [!NOTE]
> Stopping the service only stops it for the current session. If auto-start is enabled, the service will restart automatically on the next boot.

### Manual Start

To run the system manually for development or debugging:

1. **Navigate to the JetsonExample directory**:
   ```bash
   cd ~/VAIC_25_26/JetsonExample
   ```

2. **Ensure all required files are present**:
   The directory should contain: `override.py`, `model.py`, `model_backend.py`, `data_processing.py`, `common.py`, `V5Comm.py`, `V5Position.py`, `V5MapPosition.py`, `V5Web.py`, `filter.py`, `labels.txt`, and the `models/` directory with model files.

3. **Run the main application**:
   ```bash
   python3 override.py
   ```

The system will start initializing components, and once ready, begin processing camera frames and detecting objects.

## System Architecture

The application is organized into several key components, each with a specific responsibility:

### Main Application (`override.py`)

The entry point of the system. Contains four main classes:

#### `Camera` Class
- **Purpose**: Manages Intel RealSense camera pipeline
- **Configuration**: Captures depth and color streams at 640x480 resolution, 30 FPS
- **Methods**:
  - `start()`: Initializes and starts the camera pipeline
  - `get_frames()`: Retrieves synchronized depth and color frames
  - `stop()`: Stops the camera pipeline

#### `Processing` Class
- **Purpose**: Handles image processing, AI inference, and depth processing
- **Features**:
  - HSV color correction (hue, saturation, value adjustment)
  - Depth-to-color frame alignment
  - AI model inference via the `Model` class
  - Depth extraction for detected objects
  - 3D coordinate computation
- **Key Methods**:
  - `process_frames()`: Aligns depth to color frames
  - `detect_objects()`: Runs AI inference on color-corrected image
  - `compute_detections()`: Processes detections to create 3D field coordinates
  - `updateHSV()`: Updates color correction values (called by web dashboard)

#### `Rendering` Class
- **Purpose**: Manages data flow to the web dashboard
- **Methods**:
  - `set_images()`: Updates camera and depth images for web dashboard
  - `set_detection_data()`: Updates detection data for web dashboard
  - `set_stats()`: Updates system statistics (FPS, temperature, etc.)

#### `MainApp` Class
- **Purpose**: Orchestrates all components and runs the main processing loop
- **Initialization**: Creates and starts Camera, Processing, V5SerialComms, MapPosition, V5GPS, and V5WebData instances
- **Main Loop**: Continuously captures frames, processes detections, and updates all communication channels

### AI Model Processing (`model.py`, `model_backend.py`, `data_processing.py`)

#### `Model` Class (`model.py`)
- **Purpose**: High-level interface for AI inference
- **Neural Network**: YOLOv11 architecture, trained via [Roboflow](https://roboflow.com/) and exported to ONNX
- **Input Resolution**: 640x640 pixels
- **Backend Selection**: Automatically detects and uses CUDA (Jetson) or Coral Edge TPU (Raspberry Pi)
- **Output**: Bounding boxes, class IDs, and confidence scores for detected objects
- **Status**: `models/override_lite.onnx` is trained on the 8 Override classes (mAP50 0.932 on a small 101-image dataset) and verified end-to-end against this pipeline. `models/override_lite.tflite` (Coral/Raspberry Pi) has not been produced yet - see [Detection Classes](#detection-classes) below

#### `CUDABackend` and `CoralBackend` Classes (`model_backend.py`)
- **Purpose**: Platform-specific AI inference backends
- **CUDABackend**: Uses TensorRT for Jetson (loads `override_lite.onnx`, generates `.trt` engine)
- **CoralBackend**: Uses PyCoral for Raspberry Pi 5 (loads `override_lite.tflite`)
- **Automatic Detection**: The system automatically selects the appropriate backend based on available hardware

#### `PreprocessYOLO` and `PostprocessYOLO` Classes (`data_processing.py`)
- **Purpose**: YOLOv11-specific preprocessing and post-processing
- **Preprocessing**: Resizes input images to 640x640, normalizes pixel values, NCHW layout for the CUDA/TensorRT backend
- **Post-processing**: Confidence filtering and non-maximum suppression (NMS) on YOLOv11's already-decoded anchor-free output
- **Note**: This is a from-scratch rewrite of the previous YOLOv3 anchor-box decoder (fixed anchors, 2 grid scales) used by the 2025-26 Push Back model - YOLOv11 does not use anchors

### V5 Communication (`V5Comm.py`)

Handles serial communication between the Jetson/Raspberry Pi and VEX V5 Brain.

#### `V5SerialComms` Class
- **Purpose**: Binary protocol implementation for sending detection data to V5 Brain
- **Communication**: USB serial connection (115200 baud)
- **Protocol**: Custom binary format with packet header (sync bytes, length, type, CRC32) and payload
- **Threading**: Runs in separate thread, responds to V5 Brain requests
- **Data Structures**:
  - `Detection`: Individual object detection (class ID, probability, depth, screen location, map location)
  - `AIRecord`: Complete detection packet (robot position + all detections)
  - `V5SerialPacket`: Wrapped packet with header and CRC32 checksum

### GPS Integration (`V5Position.py`)

Manages communication with the VEX V5 GPS sensor for robot position tracking.

#### `V5GPS` Class
- **Purpose**: Reads GPS data from V5 Brain via serial connection
- **Connection**: Automatically detects GPS sensor on USB serial ports
- **Data**: Robot position (x, y, z), orientation (azimuth, elevation, rotation), and status flags
- **Filtering**: Uses `LiveFilter` class for position smoothing
- **Offset Support**: Applies GPS offset to correct for sensor mounting position

#### `Position` Class
- **Purpose**: Data structure representing robot position and orientation
- **Fields**: Frame count, status flags, x/y/z coordinates (meters), azimuth/elevation/rotation (degrees)
- **Serialization**: Converts to binary format for communication with V5 Brain

### 3D Mapping (`V5MapPosition.py`)

Converts 2D camera detections to 3D field coordinates.

#### `MapPosition` Class
- **Purpose**: Projects detected objects from camera image space to field coordinate space
- **Process**:
  1. Uses depth data to determine object distance from camera
  2. Applies camera intrinsic parameters (focal length: 610.98 pixels)
  3. Rotates coordinates based on robot orientation (azimuth, elevation, rotation)
  4. Translates to field coordinates using robot GPS position
  5. Applies camera offset to account for camera mounting position
- **Output**: 3D coordinates (x, y, z) in meters, with (0, 0, 0) at field center

### Web Dashboard Server (`V5Web.py`)

Provides HTTP/WebSocket server for the web dashboard.

#### `V5WebData` Class
- **Purpose**: WebSocket server for real-time data streaming to web dashboard
- **Port**: 3030 (default)
- **Endpoints**: 
  - Camera images (color and depth)
  - Detection data
  - System statistics (FPS, temperature, runtime)
  - Configuration (GPS offset, camera offset, HSV correction)
- **Offset Management**: Loads and saves offsets from JSON files (`gps_offsets.json`, `camera_offsets.json`, `color_correction.json`)
- **Live Updates**: Updates offsets in running instances when changed via web dashboard

#### Offset Classes
- **`GPSOffset`**: GPS sensor position relative to robot center (x, y, heading_offset)
- **`CameraOffset`**: Camera position relative to GPS sensor (x, y, z, heading_offset, elevation_offset)
- **`ColorCorrection`**: HSV adjustment values (hue shift, saturation multiplier, value/brightness multiplier)

### Supporting Files

- **`filter.py`**: `LiveFilter` class for smoothing position data (moving average filter)
- **`labels.txt`**: Object class labels (`blue`, `blue_yellow`, `cup`, `red`, `red_blue`, `red_yellow`, `yellow`, `yellow_yellow` - must match the trained model's class order exactly)
- **`common.py`**: NVIDIA-provided utility functions for TensorRT/CUDA operations
- **`models/override_lite.onnx`**: Trained YOLOv11n model for Jetson (ONNX format), 8 Override classes
- **`models/override_lite.tflite`**: Neural network model for Raspberry Pi (TensorFlow Lite format) - not yet produced
- **`models/pushback_lite.*`**: Legacy 2025-26 Push Back model, kept only for reference - not used by the code anymore
- **`assets/`**: Training images showing the visual range the (legacy) model was trained on

## Key Concepts

### Color Correction (HSV Adjustment)

The Intel RealSense D435 camera can misread colors under certain lighting conditions. The system includes HSV (Hue, Saturation, Value) correction to improve detection accuracy:

- **Hue**: Shifts the color spectrum (useful for color temperature adjustments)
- **Saturation**: Adjusts color intensity (multiplier, 0-2x range)
- **Value**: Adjusts brightness (multiplier, 0-2x range)

Color correction can be adjusted:
- **Live via Web Dashboard**: Changes take effect immediately
- **Manually via JSON**: Edit `color_correction.json` in the JetsonExample directory

> [!TIP]
> We recommend tuning HSV values for your specific lighting conditions. The web dashboard provides a convenient interface for real-time adjustment while viewing detection results.

### GPS and Camera Offsets

Offsets define the physical position of sensors relative to your robot's center:

- **GPS Offset**: Position of the GPS sensor relative to robot center (x, y in meters, heading_offset in degrees)
- **Camera Offset**: Position of the camera relative to the GPS sensor (x, y, z in meters, heading_offset and elevation_offset in degrees)

> [!WARNING]
> **CRITICAL**: GPS offsets configured in the Jetson/Raspberry Pi (via web dashboard or JSON files) do **NOT** automatically sync to your V5 Brain code. You must manually ensure both offsets are identical in both systems for accurate positioning.

Offset files are stored in the JetsonExample directory:
- `gps_offsets.json`
- `camera_offsets.json`
- `color_correction.json`

Offsets can be configured:
- **Via Web Dashboard**: Changes apply immediately to running system (stored in JSON files)
- **Manually via JSON**: Edit the JSON files directly (requires restart to take effect)

### Detection Classes

The system detects the following object classes (defined in `labels.txt`, in this order):
- **blue** (Class ID: 0)
- **blue_yellow** (Class ID: 1)
- **cup** (Class ID: 2)
- **red** (Class ID: 3)
- **red_blue** (Class ID: 4)
- **red_yellow** (Class ID: 5)
- **yellow** (Class ID: 6)
- **yellow_yellow** (Class ID: 7)

> [!WARNING]
> This order must match the `names:` list in the trained model's `data.yaml` (from the Roboflow export) exactly - the class index is what gets sent to the V5 Brain as `classID`. If you add, remove, or reorder classes in Roboflow, update `labels.txt` (and the `OBJECT` enum in `V5Example/ai_demo/include/ai_functions.h`) to match.

### Model Performance

The model performs best when:
- The RealSense camera is mounted at a height similar to the training images (see `assets/` directory)
- Lighting conditions are reasonable (not extremely dim or bright)
- Objects are within the camera's field of view
- HSV color correction is tuned for your environment

## System Service Setup (for Building from Source)

If you built the system from source and want to set up the systemd service for auto-start:

1. **Navigate to the Scripts directory**:
   ```bash
   cd ~/VAIC_25_26/JetsonExample/Scripts
   ```

2. **Make scripts executable**:
   ```bash
   sudo chmod +x service.sh
   sudo chmod +x run.sh
   ```

3. **Install the service**:
   ```bash
   sudo bash ./service.sh
   ```

This will:
- Create a systemd service file at `/etc/systemd/system/vexai.service`
- Configure the service to run `override.py` on boot
- Start the service immediately
- Enable auto-start on future boots

The `run.sh` script handles:
- Starting the web dashboard server (serves the React app)
- Setting required environment variables (CUDA paths, Python paths)
- Running `override.py` with proper configuration

## Troubleshooting

### Camera Not Detected
- Ensure RealSense camera is connected via USB 3.0 port
- Check camera permissions: `sudo usermod -a -G dialout $USER` (may require logout/login)
- Verify camera is detected: `rs-enumerate-devices`

### No V5 Brain Detected
- Check USB connection between device and V5 Brain
- Ensure V5 Brain is powered on
- Verify serial port permissions (user should be in `dialout` group)
- System will continue running even if V5 Brain is not connected (detections still available via web dashboard)

### Poor Detection Accuracy
- Adjust HSV color correction values via web dashboard
- Ensure lighting is adequate
- Check camera height and angle match training conditions
- Verify camera lens is clean

### GPS Not Detected
- Ensure GPS sensor is connected to V5 Brain (not directly to Jetson/Raspberry Pi)
- Verify V5 Brain is connected and powered on
- System will continue running with GPS disconnected (uses default position)

### Service Won't Start
- Check service status: `sudo systemctl status vexai`
- View logs: `sudo journalctl -u vexai -n 50`
- Verify all files are in correct location
- Check web dashboard is built (see [JetsonWebDashboard README](../JetsonWebDashboard/README.md))

### Model Engine Issues
- **Jetson**: If you see "Using an engine plan file across different models" warning, delete `models/override_lite.trt` to regenerate
- **Raspberry Pi**: Ensure Coral Edge TPU is properly connected (USB or M.2)

## File Structure

```
JetsonExample/
├── override.py              # Main entry point and application orchestration
├── model.py                 # AI model interface and inference
├── model_backend.py         # Platform-specific inference backends (CUDA/Coral)
├── data_processing.py       # YOLOv11 preprocessing and post-processing
├── common.py                # NVIDIA utility functions for TensorRT
├── V5Comm.py                # Serial communication with V5 Brain
├── V5Position.py            # GPS sensor integration
├── V5MapPosition.py         # 3D coordinate mapping
├── V5Web.py                 # Web dashboard server
├── filter.py                # Position filtering utilities
├── labels.txt               # Object class labels
├── models/
│   ├── override_lite.onnx   # Trained YOLOv11n model (Jetson)
│   ├── override_lite.tflite # Neural network model (Raspberry Pi) - not yet produced
│   └── pushback_lite.*      # Legacy 2025-26 Push Back model (unused, kept for reference)
├── assets/
│   └── training_img_*.jpg   # Training images for reference (legacy Push Back model)
└── Scripts/
    ├── service.sh           # Systemd service installation
    ├── run.sh               # Service startup script
    ├── power.sh             # Power mode configuration (Jetson)
    └── clean.sh             # System cleanup utilities
```

## Next Steps

After understanding how the JetsonExample system works:

1. **Set up Web Dashboard**: Configure monitoring and configuration interface (see [JetsonWebDashboard](../JetsonWebDashboard/README.md))
2. **Upload V5 Code**: Connect your robot to receive detection data (see [V5Example](../V5Example/ai_demo/README.md))
3. **Tune Configuration**: Adjust offsets and color correction for your specific robot and environment
4. **Develop Custom Logic**: Modify or extend the system for your specific needs

## Additional Resources

- [Ultralytics YOLOv11 Docs](https://docs.ultralytics.com/models/yolo11/) - Neural network architecture and export details
- [Roboflow](https://roboflow.com/) - Dataset labeling and model training platform used for the Override detection model
- [Intel RealSense SDK Documentation](https://dev.intelrealsense.com/) - Camera API reference
- [VEX AI Competition Documentation](https://kb.vex.com/hc/en-us/articles/360049619171-Coding-the-VEX-AI-Robot) - VEX AI system overview
