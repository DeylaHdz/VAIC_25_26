# V5Example - VEX V5 Brain Integration

This directory contains a VEX V5 C++ project that demonstrates how to integrate the V5 Brain with the Jetson Nano or Raspberry Pi 5 vision processing system. The example project showcases how to receive detection data from the vision system, use GPS positioning, and implement autonomous routines for the 2026-27 VEX AI Competition (Override).

## Overview

The `ai_demo` project is a complete VEX V5 C++ application that:

- **Receives Detection Data**: Communicates with Jetson/Raspberry Pi via USB serial to receive AI detection data
- **GPS Integration**: Uses VEX GPS sensor for accurate robot positioning on the field
- **Object Interaction**: Searches for, approaches, and interacts with detected game objects
- **Autonomous Routines**: Implements example autonomous code for Isolation and Interaction phases
- **Robot-to-Robot Communication**: Demonstrates VEXLink communication between partner robots
- **Status Display**: Shows communication statistics and detection data on the Brain screen

### Example Behavior

This demo is written against a placeholder Override robot with a game element pre-loaded. When the program runs, the robot will:

1. **Search for a Cup**: Continuously polls for detection data and searches for cups
2. **Navigate to Cup**: Uses GPS positioning and helper functions to drive to the detected cup
3. **Intake Cup**: Activates intake and belt systems to collect it
4. **Navigate to Goal**: Calculates which of the closest corner Alliance Goals to drive to
5. **Score**: Drives to the goal, extends to score, then backs away

> This routine is a minimal illustration of the communication protocol, not a competitive Override strategy - `goToGoal()`'s coordinates are placeholders (see the comment above it in `ai_functions.cpp`) and should be re-measured against the official Override field drawing, and a real strategy should account for the game's other goal types (Short neutral Goals, the Tall neutral Goal, and Toggles).

## Prerequisites

Before working with this project, ensure you have:

- **VEXcode Pro V5**: Latest version installed on your computer
- **VEX V5 Brain**: Connected and powered on
- **VEX GPS Sensor**: Connected to V5 Brain (required for positioning)
- **Hardware Platform**: Jetson Nano or Raspberry Pi 5 running the vision system (see [JetsonImages](../../JetsonImages/README.md))
- **USB Connection**: V5 Brain connected to Jetson/Raspberry Pi via USB (for serial communication)
- **Vision System Running**: Jetson/Raspberry Pi vision processing system running (see [JetsonExample](../../JetsonExample/README.md))

## Project Structure

The project is organized into several key files:

### Source Files (`src/`)

#### `main.cpp`
- **Purpose**: Entry point of the program and main control loop
- **Responsibilities**:
  - Configures V5 devices (motors, sensors, drivetrain)
  - Sets up competition callbacks (autonomous, driver control)
  - Main loop polls Jetson/Raspberry Pi for detection data (15 Hz)
  - Manages robot-to-robot communication via VEXLink
  - Starts dashboard display task
- **Key Components**:
  - `auto_Isolation()`: Autonomous routine for Isolation phase
  - `auto_Interaction()`: Autonomous routine for Interaction phase
  - Main loop: Requests detection data from vision system

#### `ai_jetson.cpp`
- **Purpose**: Handles serial communication with Jetson/Raspberry Pi
- **Responsibilities**:
  - Parses binary protocol packets from vision system
  - Implements state machine for packet reception
  - CRC32 checksum validation
  - Thread-safe data access
  - Sends data requests to vision system
- **Protocol Details**:
  - **Sync Bytes**: 0xAA, 0x55, 0xCC, 0x33 (4-byte header)
  - **Packet Structure**: 12-byte header (sync, length, type, CRC32) + payload
  - **Request Format**: ASCII string "AA55CC3301\r\n" sent via serial
  - **Response**: Binary AI_RECORD packet with robot position and detections

#### `ai_functions.cpp`
- **Purpose**: Helper functions for robot navigation and object interaction
- **Key Functions**:
  - `distanceTo()`: Calculates distance to target coordinates
  - `calculateBearing()`: Calculates angle to target position
  - `turnTo()`: Turns robot to face specific angle
  - `driveFor()`: Drives robot in specified direction
  - `moveToPosition()`: Moves robot to target (x, y) position
  - `findTarget()`: Finds closest detected object of specified type
  - `goToObject()`: Drives to closest detected object
  - `runIntake()`: Controls intake and belt motors
  - `goToGoal()`: Navigates to nearest goal end

#### `ai_robot_link.cpp`
- **Purpose**: Robot-to-robot communication via VEXLink
- **Responsibilities**:
  - Implements wireless serial communication between partner robots
  - Sends robot position data to partner robot
  - Receives partner robot position data
  - Packet protocol implementation with CRC checksums
- **Usage**: Shares robot position (x, y, heading) between manager and worker robots

#### `dashboard.cpp`
- **Purpose**: Status display on V5 Brain screen
- **Responsibilities**:
  - Displays Jetson/Raspberry Pi communication statistics (packets, errors, timeouts, data rate)
  - Shows detection data (count, positions, probabilities, class IDs)
  - Displays VEXLink communication status and statistics
  - Shows robot positions (local and remote)
  - Updates at 30 Hz in separate task

### Header Files (`include/`)

#### `ai_jetson.h`
- **Purpose**: Data structures and class definition for Jetson communication
- **Key Structures**:
  - `POS_RECORD`: Robot position (x, y, z, azimuth, elevation, rotation)
  - `IMAGE_DETECTION`: 2D screen coordinates of detected object
  - `MAP_DETECTION`: 3D field coordinates of detected object (meters)
  - `DETECTION_OBJECT`: Complete detection data (class ID, probability, depth, locations)
  - `AI_RECORD`: Complete data packet (robot position + array of detections)
- **Class**: `ai::jetson` - Communication interface

#### `ai_functions.h`
- **Purpose**: Function declarations for navigation and object interaction
- **Enums**: `OBJECT` (Blue, BlueYellow, Cup, Red, RedBlue, RedYellow, Yellow, YellowYellow)
- **Functions**: All helper functions for robot movement and object interaction

#### `ai_robot_link.h`
- **Purpose**: Robot-to-robot communication interface
- **Class**: `ai::robot_link` - VEXLink communication interface

#### `robot-config.h`
- **Purpose**: Robot hardware configuration
- **Contents**: Device declarations (motors, sensors, drivetrain)
- **Note**: Must be configured for your specific robot setup

#### `vex.h`
- **Purpose**: VEX V5 API header
- **Source**: Provided by VEXcode Pro V5

## Setup Instructions

### Step 1: Open Project in VEXcode Pro V5

1. **Launch VEXcode Pro V5**
2. **Open Project**: File → Open Project
3. **Navigate to**: `VAIC_25_26/V5Example/ai_demo`
4. **Select**: The project folder

The project should load with all source files visible.

### Step 2: Configure Robot Hardware

**Edit `robot-config.h` or use the Device Configuration tool:**

1. **Motors**: Configure motor ports and settings
   - Left drive motor (default: PORT1)
   - Right drive motor (default: PORT2)
   - Intake motor (default: PORT4)
   - Belt motor (default: PORT3)

2. **GPS Sensor**: Configure GPS sensor port and offsets
   - GPS port (default: PORT9)
   - **GPS Offset**: Critical - must match offset configured in Jetson/Raspberry Pi
   - Default example: `gps(PORT9, 0, -165, distanceUnits::mm, 180)`
     - X offset: 0 mm
     - Y offset: -165 mm (GPS sensor position relative to robot center)
     - Heading offset: 180 degrees

3. **Drivetrain**: Configure smartdrive parameters
   - Wheel diameter: 319.19 mm
   - Track width: 320 mm
   - Other parameters as needed

> [!WARNING]
> **CRITICAL**: GPS offset values in `robot-config.h` must **exactly match** the GPS offset configured in the Jetson/Raspberry Pi (via web dashboard or JSON files). If offsets don't match, robot positions will be misaligned between the vision system and V5 Brain.

### Step 3: Configure Robot-to-Robot Communication (Optional)

For multi-robot setups:

1. **Choose Robot Type**:
   - **Manager Robot**: Uncomment `#define MANAGER_ROBOT 1` in `main.cpp`
   - **Worker Robot**: Comment out the `MANAGER_ROBOT` definition

2. **Configure VEXLink Port**:
   - Manager: PORT15 (default)
   - Worker: PORT10 (default)

3. **Set Unique Robot Name**:
   - Default: `"robot_32456_1"`
   - Should incorporate team number
   - Must be at least 12 characters for good hash
   - Must match between manager and worker robots

### Step 4: Verify Vision System Connection

Before compiling, ensure:

1. **Vision System Running**: Jetson/Raspberry Pi is running `override.py`
2. **USB Connected**: V5 Brain connected to Jetson/Raspberry Pi via USB
3. **GPS Connected**: GPS sensor connected to V5 Brain
4. **Ports Correct**: Motor and sensor ports match your robot configuration

### Step 5: Build and Upload

1. **Build Project**: 
   - Click "Build" button or press Ctrl+B
   - Check for compilation errors

2. **Upload to Brain**:
   - Connect V5 Brain via USB or wireless
   - Click "Download" button
   - Wait for upload to complete

3. **Run Program**:
   - Program starts automatically after upload
   - Robot will begin polling for detection data
   - Dashboard displays on Brain screen

## Code Architecture

### Communication Flow

```
V5 Brain                    Jetson/Raspberry Pi
--------                    -------------------
    |                               |
    |  "AA55CC3301\r\n" (request)  |
    |<------------------------------|
    |                               |
    |  Binary Packet (AI_RECORD)    |
    |------------------------------>|
    |                               |
```

**Request-Response Pattern**:
1. V5 Brain sends ASCII request string: `"AA55CC3301\r\n"`
2. Jetson/Raspberry Pi responds with binary packet containing:
   - Robot position (GPS data)
   - Detection count
   - Array of detected objects (up to 50)
3. V5 Brain parses packet and updates local data
4. Main loop processes detection data for autonomous routines

### Data Structures

#### AI_RECORD Structure
```cpp
typedef struct {
    int32_t detectionCount;        // Number of detections (0-50)
    POS_RECORD pos;                // Robot position
    DETECTION_OBJECT detections[50]; // Array of detections
} AI_RECORD;
```

#### DETECTION_OBJECT Structure
```cpp
typedef struct {
    int32_t classID;               // see Detection Class IDs below (must match JetsonExample/labels.txt order)
    float probability;              // Confidence (0.0 - 1.0)
    float depth;                    // Distance in meters
    IMAGE_DETECTION screenLocation; // 2D screen coordinates
    MAP_DETECTION mapLocation;      // 3D field coordinates (meters)
} DETECTION_OBJECT;
```

#### POS_RECORD Structure
```cpp
typedef struct {
    int32_t framecnt;              // Frame counter
    int32_t status;                // Status flags
    float x, y, z;                 // Position (meters, 0,0 at field center)
    float az;                      // Azimuth/Heading (degrees)
    float el;                      // Elevation/Pitch (degrees)
    float rot;                     // Rotation/Roll (degrees)
} POS_RECORD;
```

### Main Program Flow

1. **Initialization**:
   - Configure devices (motors, sensors, drivetrain)
   - Create `jetson_comms` instance (starts receive thread)
   - Create `robot_link` instance (for robot-to-robot communication)
   - Start dashboard display task
   - Set up competition callbacks

2. **Main Loop** (runs at ~15 Hz):
   - Request detection data: `jetson_comms.request_map()`
   - Get latest data: `jetson_comms.get_data(&local_map)`
   - Update robot-to-robot communication: `link.set_remote_location(...)`
   - Process data for autonomous routines (when in autonomous mode)
   - Sleep for loop period (33ms)

3. **Autonomous Routines**:
   - **Isolation Phase**: Runs `auto_Isolation()` function
   - **Interaction Phase**: Runs `auto_Interaction()` function (when field re-enables)

## Example Autonomous Routine

### Isolation Phase Example

The example `auto_Isolation()` function demonstrates:

```cpp
void auto_Isolation(void) {
  // Calibrate GPS Sensor
  GPS.calibrate();
  waitUntil(!(GPS.isCalibrating()));

  // Search for and drive to a cup
  goToObject(OBJECT::Cup);
  
  // Intake the cup (3 rotations while driving forward)
  runIntake(directionType::fwd, 3, true);
  
  // Navigate to nearest goal
  goToGoal();
  
  // Drive into goal
  Drivetrain.driveFor(-115, distanceUnits::cm);
  
  // Score
  Belt.setVelocity(70, pct);
  runIntake(directionType::fwd, 5, false);
  
  // Back away from goal
  Drivetrain.driveFor(30, distanceUnits::cm);
}
```

**Behavior Breakdown**:
1. **GPS Calibration**: Ensures accurate positioning
2. **Object Search**: `goToObject()` finds closest cup and drives to it
3. **Intake**: Intake and belt run while robot drives forward
4. **Goal Navigation**: `goToGoal()` calculates closest corner goal and navigates
5. **Scoring**: Robot extends into goal, activates belt to score
6. **Retreat**: Robot backs away from goal

### Helper Functions Explained

#### Navigation Functions

- **`distanceTo(target_x, target_y)`**: Calculates Euclidean distance to target (cm)
- **`calculateBearing(currX, currY, targetX, targetY)`**: Calculates angle to target (degrees, 0-360)
- **`turnTo(angle, tolerance, speed)`**: Turns robot to face specified angle
- **`driveFor(heading, distance, speed)`**: Drives robot in specified direction
- **`moveToPosition(x, y, theta)`**: Moves robot to target position with orientation

#### Object Interaction Functions

- **`findTarget(type)`**: Finds closest detected object of the specified `OBJECT` type
- **`goToObject(type)`**: Drives to closest detected object, searches if not found
- **`runIntake(dir)`**: Runs intake and belt motors
- **`runIntake(dir, rotations, driveForward)`**: Runs intake for specified rotations
- **`goToGoal()`**: Calculates closest corner Alliance Goal (placeholder coordinates - see the comment in `ai_functions.cpp`) and navigates to it

## Troubleshooting

### No Detection Data Received

**Issue**: Dashboard shows 0 packets, no detections

**Solutions**:
- Verify Jetson/Raspberry Pi is running (`override.py` running)
- Check USB connection between V5 Brain and Jetson/Raspberry Pi
- Verify serial port permissions on Jetson/Raspberry Pi
- Check for compilation errors in vision system
- Verify V5 Brain is powered on
- Check dashboard for error/timeout counts

### GPS Position Mismatch

**Issue**: Robot positions don't match between vision system and V5 Brain

**Solutions**:
- **Verify GPS offsets match exactly** in both systems:
  - V5 Brain: Check `robot-config.h` GPS offset values
  - Jetson/Raspberry Pi: Check `gps_offsets.json` or web dashboard
- Ensure GPS sensor is properly calibrated
- Verify GPS sensor port is correct
- Check GPS sensor mounting position matches offset configuration

### Robot Not Moving

**Issue**: Robot doesn't respond to commands

**Solutions**:
- Check motor ports are correct in `robot-config.h`
- Verify motors are connected and powered
- Check for motor faults on Brain screen
- Verify drivetrain configuration (wheel diameter, track width)
- Check GPS sensor is calibrated and reporting valid position

### Compilation Errors

**Issue**: Project won't compile

**Solutions**:
- Ensure VEXcode Pro V5 is up to date
- Check all include files are present
- Verify robot-config.h is properly configured
- Check for syntax errors in modified code
- Try rebuilding project (Build → Clean and Build)

### VEXLink Not Working

**Issue**: Robot-to-robot communication fails

**Solutions**:
- Verify both robots have VEXLink radios enabled
- Check robot names match between manager and worker
- Verify port assignments (PORT15 for manager, PORT10 for worker)
- Ensure robots are within wireless range
- Check dashboard for VEXLink status (should show "Good")

### Detection Accuracy Issues

**Issue**: Robot can't find objects or finds wrong objects

**Solutions**:
- Verify vision system is detecting objects (check web dashboard)
- Check HSV color correction is tuned for lighting conditions
- Ensure camera is mounted correctly
- Verify object classes match the Detection Class IDs table below
- Check detection confidence thresholds (may need to filter low-confidence detections)

## Key Configuration Notes

### GPS Offset Configuration

> [!WARNING]
> GPS offset values must be **identical** in both the V5 Brain code and Jetson/Raspberry Pi configuration. If they don't match, robot positions will be misaligned.

**V5 Brain Configuration** (`robot-config.h`):
```cpp
gps GPS = gps(PORT9, x_offset, y_offset, distanceUnits::mm, heading_offset);
```

**Jetson/Raspberry Pi Configuration**:
- Web Dashboard: Settings → GPS Offset
- JSON File: `JetsonExample/gps_offsets.json`

**Example**: If GPS sensor is 165mm forward and 0mm left of robot center:
- V5 Brain: `gps(PORT9, 0, -165, distanceUnits::mm, 180)`
- Jetson/Raspberry Pi: X: 0 mm, Y: -165 mm, Heading: 180 degrees

### Detection Class IDs

- **0**: Blue
- **1**: BlueYellow
- **2**: Cup
- **3**: Red
- **4**: RedBlue
- **5**: RedYellow
- **6**: Yellow
- **7**: YellowYellow

These must match the classes (and order) defined in `JetsonExample/labels.txt`, which in turn must match the `names:` list in the trained model's Roboflow `data.yaml` export - if any of the three drift out of sync, classIDs silently point at the wrong object.

### Coordinate System

- **Origin**: Field center (0, 0, 0)
- **Units**: Meters (for map coordinates), Centimeters (for GPS positions)
- **X-axis**: Positive = right, Negative = left
- **Y-axis**: Positive = forward, Negative = backward
- **Z-axis**: Positive = up, Negative = down
- **Heading**: 0° = forward, increases clockwise (90° = right, 180° = back, 270° = left)

### Communication Timing

- **Poll Rate**: ~15 Hz (33ms loop time)
- **Request Timeout**: 250ms (if no response, state resets)
- **Maximum Detections**: 50 objects per frame
- **Dashboard Update**: 30 Hz (separate task)

## Development Tips

### Modifying Autonomous Routines

1. **Test in Steps**: Break down autonomous routine into testable segments
2. **Use Dashboard**: Monitor detection data and GPS position on Brain screen
3. **Test Navigation**: Use `moveToPosition()` with known coordinates first
4. **Verify Object Detection**: Use `findTarget()` to check if objects are detected
5. **Tune Speeds**: Adjust motor speeds for your robot's performance

### Adding Custom Functions

1. **Declare in Header**: Add function declaration to `ai_functions.h`
2. **Implement in Source**: Add function implementation to `ai_functions.cpp`
3. **Use GPS Positioning**: Use GPS sensor for field-relative navigation
4. **Access Detection Data**: Use `jetson_comms.get_data(&local_map)` to get latest detections
5. **Thread Safety**: Detection data is thread-safe (uses mutex internally)

### Debugging

1. **Brain Screen**: Use `Brain.Screen.print()` for debugging output
2. **Dashboard**: Monitor communication statistics and detection data
3. **Serial Output**: Can use controller serial output (if not using USB for Jetson)
4. **Status Flags**: Check GPS status flags for sensor issues
5. **Error Counts**: Monitor error and timeout counts in dashboard

## File Structure

```
ai_demo/
├── src/
│   ├── main.cpp           # Main program entry point
│   ├── ai_jetson.cpp      # Jetson/Raspberry Pi communication
│   ├── ai_functions.cpp   # Navigation and object interaction
│   ├── ai_robot_link.cpp  # Robot-to-robot communication
│   └── dashboard.cpp      # Status display
├── include/
│   ├── ai_jetson.h        # Communication data structures
│   ├── ai_functions.h     # Function declarations
│   ├── ai_robot_link.h    # VEXLink interface
│   ├── robot-config.h     # Robot hardware configuration
│   └── vex.h              # VEX API (provided by VEXcode)
├── vex/
│   ├── mkenv.mk           # Build environment (provided)
│   └── mkrules.mk         # Build rules (provided)
├── makefile               # Build configuration
└── README.md              # This file
```

## Additional Resources

- [VEX AI Competition Documentation](https://kb.vex.com/hc/en-us/articles/360049619171-Coding-the-VEX-AI-Robot) - Official VEX AI documentation
- [VEXcode Pro V5 Documentation](https://kb.vex.com/hc/en-us/categories/115000307783-VEXcode-Pro-V5) - VEXcode Pro V5 API reference
- [JetsonExample README](../../JetsonExample/README.md) - Vision processing system documentation
- [JetsonWebDashboard README](../../JetsonWebDashboard/README.md) - Web dashboard documentation

## Next Steps

After understanding the example code:

1. **Configure Your Robot**: Update `robot-config.h` with your robot's hardware configuration
2. **Match Offsets**: Ensure GPS and camera offsets match between V5 Brain and vision system
3. **Test Communication**: Verify detection data is being received (check dashboard)
4. **Customize Autonomous**: Modify autonomous routines for your strategy
5. **Test and Tune**: Test on field, tune navigation parameters, and optimize performance
6. **Extend Functionality**: Add custom functions for your specific game strategy
