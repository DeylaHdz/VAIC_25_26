# The VEX AI Competition (VAIC) System

The VEX AI Competition (VAIC) System is a complete computer vision and robotics platform that enables VEX V5 robots to autonomously detect and interact with game objects using AI-powered vision processing. The system combines an Intel RealSense depth camera, an NVIDIA Jetson Nano or Raspberry Pi 5 with Google Coral Edge TPU for AI inference, and a VEX V5 Brain for robot control.

## Overview

This repository contains the software stack for the 2026-27 VEX AI Competition (Override), adapted from VEX's 2025-26 Push Back example. The system processes live camera feeds to detect Override game elements (Cups and the four Pin color combinations) in real-time, maps their 3D positions on the competition field, and communicates detection data to the VEX V5 Brain via serial communication. The V5 Brain uses this information to autonomously navigate and interact with detected objects.

> **Status**: `JetsonExample/models/override_lite.onnx` is a YOLOv11n model trained locally on a Roboflow-labeled Override dataset (101 images; mAP50 0.932, precision 0.956, recall 0.917 on the validation split). It covers the Jetson/CUDA path. No Coral/TFLite export (`override_lite.tflite`) exists yet - see [JetsonExample/README.md](./JetsonExample/README.md) for details, and note the dataset is small, so expect to retrain as more images are collected.

### Key Features

- **Real-time Object Detection**: Uses a YOLOv11 neural network to detect VEX Override game elements (Cups and color-coded Pins)
- **3D Spatial Mapping**: Converts 2D camera detections into 3D field coordinates using depth camera data
- **Dual Platform Support**: Works on both NVIDIA Jetson Nano (CUDA acceleration) and Raspberry Pi 5 with Coral Edge TPU
- **Web Dashboard**: React-based web interface for real-time monitoring, camera views, detection visualization, and system configuration
- **GPS Integration**: Combines camera-based detections with V5 GPS sensor data for accurate robot positioning
- **Serial Communication**: Binary protocol for efficient data transfer between the vision system and V5 Brain

## System Architecture

```
┌─────────────────┐     ┌──────────────────────┐     ┌──────────────┐
│  Intel          │────▶│  Jetson Nano/        │────▶│  VEX V5      │
│  RealSense D435 │     │  Raspberry Pi 5      │     │  Brain       │
│  Depth Camera   │     │                      │     │              │
└─────────────────┘     │  • AI Inference      │     │  • Robot     │
                        │  • Depth Processing  │     │    Control   │
                        │  • 3D Mapping        │     │  • GPS       │
                        │  • Serial Comm       │     │    Tracking  │
                        └──────────────────────┘     └──────────────┘
                                │
                                │ WebSocket/HTTP
                                ▼
                        ┌─────────────────┐
                        │  Web Dashboard  │
                        │  (React App)    │
                        └─────────────────┘
```

### How It Works

1. **Camera Capture**: The Intel RealSense D435 camera captures synchronized color (RGB) and depth frames at 640x480 resolution, 30 FPS
2. **Image Processing**: RGB frames are color-corrected (HSV adjustment) to improve detection accuracy under various lighting conditions
3. **AI Inference**: Pre-processed images are fed into a YOLOv11-based neural network (ONNX/TFLite format) running on:
   - **Jetson Nano**: CUDA-accelerated TensorRT backend
   - **Raspberry Pi 5**: Google Coral Edge TPU backend
4. **Detection Processing**: Bounding boxes are extracted for detected objects (Cups and Pins) with confidence scores
5. **3D Mapping**: Depth data from RealSense camera is used to project 2D detections into 3D field coordinates (meters from field center)
6. **Position Fusion**: Robot position from V5 GPS sensor is combined with camera offset and GPS offset to calculate absolute field positions
7. **Serial Communication**: Detection data (including robot position and all detected objects) is packaged into a binary protocol and sent to V5 Brain via USB serial
8. **Robot Control**: V5 Brain receives detection data and uses it for autonomous navigation and object interaction

## Components

### [JetsonExample](./JetsonExample/README.md)

The core Python application that runs on the Jetson Nano or Raspberry Pi 5. This component handles:
- **Camera Management** (`Camera` class): Initializes and manages Intel RealSense pipeline
- **AI Inference** (`Model` class): Loads and runs YOLOv11 neural network inference
- **Image Processing** (`Processing` class): Color correction, depth alignment, and 3D projection
- **Serial Communication** (`V5Comm.py`): Binary protocol implementation for V5 Brain communication
- **GPS Integration** (`V5Position.py`): V5 GPS sensor serial communication and position tracking
- **3D Mapping** (`V5MapPosition.py`): Projects 2D detections to 3D field coordinates
- **Web Server** (`V5Web.py`): HTTP/WebSocket server for the web dashboard

**Main Entry Point**: `override.py` - Coordinates all components and runs the main processing loop

### [JetsonImages](./JetsonImages/README.md)

Pre-built SD card images and build-from-source instructions for setting up the hardware platform:
- **Pre-built Images**: Ready-to-use images for Jetson Nano and Raspberry Pi 5 (password: `password`)
- **Jetson Build Instructions**: Step-by-step guide for building Jetson image from scratch
- **Raspberry Pi Instructions**: Guide for setting up Raspberry Pi 5 with Coral Edge TPU from scratch

### [JetsonWebDashboard](./JetsonWebDashboard/README.md)

React-based web application that provides a real-time monitoring and configuration interface:
- **Live Camera View**: Stream color and depth camera feeds
- **Field Visualization**: Interactive 2D top-down view of the field with detected objects and robot position
- **Detection Overlay**: Real-time bounding boxes and confidence scores
- **System Statistics**: CPU/GPU usage, FPS, detection counts
- **Configuration**: Adjust HSV color correction, GPS offset, and camera offset in real-time
- **Access Point Setup**: Instructions for configuring Jetson/Raspberry Pi as a Wi-Fi hotspot

### [V5Example](./V5Example/ai_demo/README.md)

C++ example project for the VEX V5 Brain demonstrating:
- **Serial Communication** (`ai_jetson.cpp`): Receiving and parsing detection data from Jetson/Raspberry Pi
- **Robot Control** (`ai_functions.cpp`): Autonomous navigation and object interaction logic
- **Robot-to-Robot Link** (`ai_robot_link.cpp`): Multi-robot coordination via VEXLink
- **Dashboard Display** (`dashboard.cpp`): Status information display on Brain screen

**Example Behavior**: Searches for cups, drives to them, intakes them, then scores in the nearest corner Alliance Goal.

## Prerequisites

### Hardware Requirements
- **Vision System**: 
  - NVIDIA Jetson Nano Developer Kit OR Raspberry Pi 5 with Google Coral Edge TPU USB Accelerator
  - Intel RealSense D435 depth camera
  - SD card (minimum 32GB)
  - USB Wi-Fi adapter (for access point functionality)
- **Robot System**:
  - VEX V5 Brain
  - VEX GPS Sensor (v1.0 or v2.0)
  - USB-A to Micro-USB cable (for serial communication)

### Software Requirements
- **On Jetson Nano/Raspberry Pi**:
  - Ubuntu-based OS (pre-installed on provided images)
  - Python 3.6+ (Jetson) or Python 3.9 (Raspberry Pi with pyenv)
  - Intel RealSense SDK (librealsense)
  - CUDA/TensorRT (Jetson) OR PyCoral/Coral Runtime (Raspberry Pi)
- **On V5 Brain**:
  - VEXcode Pro V5 (for compiling C++ code)
  - VEX AI Robot Link library (included)

## Getting Started

To get started with the VEX AI Competition system, we recommend exploring the repository's example code in the following order. This sequence builds understanding progressively, from hardware setup through vision processing to robot control integration.

### Recommended Order

1. **[JetsonImages](./JetsonImages/README.md)** - Hardware platform setup
2. **[JetsonExample](./JetsonExample/README.md)** - Core vision processing system
3. **[JetsonWebDashboard](./JetsonWebDashboard/README.md)** - Monitoring and configuration interface
4. **[V5Example](./V5Example/ai_demo/README.md)** - V5 Brain integration

### Why This Order?

**Start with JetsonImages** because it provides the foundation for everything else. You need a working hardware platform (Jetson Nano or Raspberry Pi 5) with all dependencies installed before you can run any vision processing code. Whether you use a pre-built image or build from source, this step ensures your device is ready.

**Then explore JetsonExample** to understand how the vision system works. This is the core of the AI system - it handles camera capture, AI inference, 3D mapping, and communication with the V5 Brain. Understanding this component is essential because it determines what data is available to your robot and how it's structured.

**Next, set up JetsonWebDashboard** to enable real-time monitoring and system configuration. While not strictly required for the system to function, the dashboard provides invaluable debugging capabilities and allows you to fine-tune color correction and offsets without restarting the system. It's best to set this up after understanding the vision system, so you know what you're monitoring.

**Finally, work with V5Example** to integrate AI detections into your robot's autonomous code. This should come last because you need the vision system running and understood before you can effectively use the detection data in your robot's routines. The example code demonstrates the communication protocol and provides helper functions you can build upon.

Each directory contains detailed README files with specific setup instructions, code explanations, and usage examples. Follow the order above to build your understanding progressively, using each example as a foundation for the next.

## Key Configuration Notes

> **⚠️ WARNING**: The GPS offset configured in the Jetson/Raspberry Pi web dashboard does **NOT** automatically sync to your V5 Brain code. You must manually ensure both offsets are aligned so robot positions match between the vision system and V5 Brain.

- **GPS Offset**: Defines the position of the GPS sensor relative to the robot's center
- **Camera Offset**: Defines the position of the camera relative to the GPS sensor
- **HSV Correction**: Adjusts hue, saturation, and value to improve color detection accuracy under different lighting conditions

## Detection Classes

The system detects the following objects (defined in `JetsonExample/labels.txt`, order must match the trained model's class order):
- `blue` (Class ID: 0)
- `blue_yellow` (Class ID: 1)
- `cup` (Class ID: 2)
- `red` (Class ID: 3)
- `red_blue` (Class ID: 4)
- `red_yellow` (Class ID: 5)
- `yellow` (Class ID: 6)
- `yellow_yellow` (Class ID: 7)

## Data Communication Protocol

The system uses a binary serial protocol for efficient communication:

- **Packet Structure**: 12-byte header (sync bytes, length, type, CRC32) + payload
- **Data Format**: Little-endian binary encoding
- **Update Rate**: V5 Brain requests data as needed (polling mechanism)
- **Coordinates**: Field coordinates in meters, with (0, 0) at field center

For detailed protocol specification, see the data structures in:
- `JetsonExample/V5Comm.py` (Python implementation)
- `V5Example/ai_demo/include/ai_jetson.h` (C++ implementation)

## Troubleshooting

- **No V5 Brain detected**: Check USB connection and ensure V5 Brain is powered on
- **Poor detection accuracy**: Adjust HSV color correction values in web dashboard
- **GPS position mismatch**: Verify GPS and camera offsets are set correctly
- **Camera not detected**: Ensure RealSense camera is properly connected via USB 3.0
- **Web dashboard not accessible**: Check Wi-Fi access point configuration

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## Additional Resources

- [VEX AI Competition Documentation](https://kb.vex.com/hc/en-us/articles/360049619171-Coding-the-VEX-AI-Robot)
- [Ultralytics YOLOv11 Docs](https://docs.ultralytics.com/models/yolo11/)
- [Roboflow](https://roboflow.com/)
- [Intel RealSense Documentation](https://dev.intelrealsense.com/)
- [NVIDIA Jetson Developer Center](https://developer.nvidia.com/embedded/jetson-nano-developer-kit)

## Contributing

This is adapted from VEX's official VEX AI Competition example for the 2026-27 (Override) season. For support and questions, refer to the [VEX AI Competition documentation](https://kb.vex.com/hc/en-us/sections/4409408713623-VEX-AI-Competition).
