# JetsonWebDashboard - Web Dashboard Interface

This directory contains the VEX AI Web Dashboard, a React-based web application that provides a real-time interface for monitoring and configuring the VEX AI vision processing system. The dashboard connects to the Jetson Nano or Raspberry Pi 5 via WebSocket to display camera feeds, detection data, system statistics, and configuration options.

## Overview

The VEX AI Web Dashboard provides a comprehensive interface for:

- **Real-time Camera Visualization**: Live color and depth camera feeds from the Intel RealSense D435 camera
- **Detection Overlay**: Visual representation of detected objects with bounding boxes and confidence scores
- **Field Visualization**: Interactive 2D top-down view of the competition field showing robot position and detected objects
- **System Statistics**: Real-time performance metrics (FPS, inference time, CPU temperature, runtime, GPS connection status)
- **Configuration Management**: Adjust GPS offset, camera offset, and HSV color correction values in real-time
- **Multi-view Support**: Switch between different views (field-only, camera-only, combined views)

The dashboard communicates with the vision processing system (`V5Web.py` in JetsonExample) via WebSocket on port 3030, and the web application is served via HTTP on port 3000.

## Architecture

### Communication Protocol

The dashboard uses WebSocket (WS) for real-time bidirectional communication:

- **WebSocket Server**: Runs on the Jetson/Raspberry Pi via `V5Web.py` (port 3030)
- **WebSocket Client**: React application connects to `ws://10.42.0.1:3030` (or device IP)
- **HTTP Server**: Static files served via `serve` on port 3000
- **Polling**: Dashboard polls for data at 60ms intervals (configurable)

### Data Flow

1. **WebSocket Connection**: Dashboard establishes WebSocket connection to Jetson/Raspberry Pi
2. **Data Requests**: Dashboard sends command requests (`g_pos`, `g_detect`, `g_color`, `g_depth`, `g_stats`)
3. **Data Response**: Server responds with requested data (JSON format)
4. **Real-time Updates**: Dashboard updates UI with received data
5. **Configuration Changes**: Dashboard sends offset/color correction updates, which apply immediately

### Technology Stack

- **Frontend Framework**: React 18 with TypeScript
- **State Management**: Redux Toolkit
- **UI Components**: Material-UI (MUI) v5
- **Canvas Rendering**: Konva (for field visualization)
- **Routing**: React Router v6
- **Build Tool**: React Scripts (Create React App)
- **HTTP Server**: `serve` (static file serving)

## Prerequisites

### Using Pre-built Image (No Setup Required)

If you're using a pre-built SD card image, the web dashboard is **already built and configured**. The system automatically:

- Builds the React application
- Serves the static files via `serve` on port 3000
- Starts the WebSocket server on port 3030
- Configures the device to run on boot

You can skip the build setup and go directly to [Accessing the Dashboard](#accessing-the-dashboard).

### Building from Source

If you built your system from source, you'll need to set up the web dashboard manually:

**Required Software:**
- Node.js (version 16 recommended)
- npm (Node Package Manager)
- `serve` package (for serving static files)

**Platform Requirements:**
- Jetson Nano or Raspberry Pi 5 with internet connection
- Wi-Fi adapter (for access point functionality)

## Setup Instructions (For Building from Source)

> [!NOTE]
> If you're using a pre-built SD card image, you can skip this section. The dashboard is already built and configured.

### Step 1: Install Node.js and npm

**Install Node.js and npm:**
```bash
sudo apt-get update
sudo apt-get upgrade
sudo apt install nodejs
sudo apt install npm
```

**Upgrade to Node.js 16 (recommended):**
```bash
sudo npm cache clean -f
sudo npm install -g n
sudo n 16
```

**Install serve package:**
```bash
sudo npm install -g serve
```

> [!TIP]
> The `n` package allows you to easily switch between Node.js versions. Node.js 16 is recommended for compatibility with the React application.

### Step 2: Install Dependencies

**Navigate to the web dashboard directory:**
```bash
cd ~/VAIC_25_26/JetsonWebDashboard/vexai-web-dashboard-react
```

**Install npm packages:**
```bash
npm install
```

This will install all required dependencies listed in `package.json`, including React, Redux, Material-UI, Konva, and other dependencies.

### Step 3: Build the Application

**Build the React application:**
```bash
npm run build
```

This creates an optimized production build in the `build/` directory. The build process:
- Compiles TypeScript to JavaScript
- Bundles and minifies JavaScript and CSS
- Optimizes assets
- Creates a production-ready static file set

**Build Time:** The build process typically takes 1-3 minutes depending on your hardware.

### Step 4: Serve the Application

**Start the HTTP server:**
```bash
serve -s build
```

This starts a static file server serving the built application. The server will:
- Listen on port 3000 (default)
- Serve the React application
- Handle routing for the React Router

**Alternative:** To serve on a different port:
```bash
serve -s build -l 3000
```

> [!NOTE]
> The `-s` flag enables single-page application (SPA) mode, which is required for React Router to work correctly.

### Step 5: Access the Dashboard

Once the server is running, you can access the dashboard:

- **Local Access**: If viewing from the Jetson/Raspberry Pi desktop, navigate to `http://localhost:3000/#/`
- **Network Access**: If connecting via Wi-Fi access point, navigate to `http://10.42.0.1:3000/#/`

See [Accessing the Dashboard](#accessing-the-dashboard) for detailed connection instructions.

## Accessing the Dashboard

### Setting Up Wi-Fi Access Point

To access the dashboard wirelessly from another device (laptop, tablet, phone), configure your Jetson Nano or Raspberry Pi as a Wi-Fi access point (hotspot).

> [!NOTE]
> Raspberry Pi 5 users should refer to the [PiInstructions.md](../JetsonImages/PiInstructions.md) for command-line hotspot setup. The GUI method below is primarily for Jetson Nano.

#### Jetson Nano: GUI Method

**Prerequisites:**
- Wi-Fi adapter installed in Jetson Nano
- Desktop environment running

**Step-by-Step Instructions:**

1. **Open Connections Menu**
   - Click the network icon in the top menu bar
   - Select the connections menu

   ![Connections Menu](tutorial/image1.png)

2. **Create New Wi-Fi Network**
   - Select "Create New Wi-Fi Network" or "Wi-Fi" option
   - Choose to create a new connection

   ![Wi-Fi Network](tutorial/image2.png)

3. **Configure Network**
   - Enter a network name (SSID)
   - Select Wi-Fi security level (None recommended for ease of use, or WPA2 for security)
   - Click "Create"

   ![Wi-Fi](tutorial/image3.png)

4. **Edit Connection Settings**
   - Open "Edit Connections" from the network menu
   - Select your newly created network

   ![Edit Connections](tutorial/image7.png)

5. **Change Mode to Hotspot**
   - Click the gear icon to open settings
   - Change the "Mode" from "Ad-hoc" to "Hotspot"
   - Click "Save"

   ![Ad-hoc](tutorial/image9.png)

   ![Hotspot](tutorial/image10.png)

6. **Connect to Network**
   - Click the network icon in the menu bar
   - Select your Wi-Fi network name
   - Connect to it

   ![Connect to Wi-Fi](tutorial/image4.png)

   ![Connect](tutorial/image5.png)

7. **Verify Connection**
   - You should see your network name showing as "Connected"
   - The Jetson is now broadcasting as a Wi-Fi access point

   ![Confirm](tutorial/image6.png)

#### Raspberry Pi 5: Command-Line Method

For Raspberry Pi 5, use the command-line method described in [PiInstructions.md](../JetsonImages/PiInstructions.md). The command creates a hotspot named "VexAI" with password "vexrobotics" by default.

### Connecting to the Dashboard

Once your device is configured as an access point:

1. **Connect to Wi-Fi Network**
   - On your laptop/tablet/phone, open Wi-Fi settings
   - Find and connect to the network you created (or "VexAI" for Raspberry Pi)
   - Enter password if required

2. **Open Web Browser**
   - Open your web browser (Chrome, Firefox, Safari, Edge)
   - Navigate to: `http://10.42.0.1:3000/#/`

3. **Dashboard Should Load**
   - The dashboard should connect automatically
   - You should see the interface with camera feeds and field visualization

> [!NOTE]
> The default IP address for the access point is `10.42.0.1`. This is the standard IP for many Linux access point configurations.

## Dashboard Features

### View Modes

The dashboard provides several view modes accessible via navigation:

- **Field View**: Interactive 2D top-down field visualization with robot position and detections
- **Color Camera View**: Live RGB camera feed with detection overlays
- **Depth Camera View**: Depth camera visualization with color mapping
- **Field and Camera View**: Combined view showing both field map and camera feed

### Configuration Settings

Access settings via the settings modal (gear icon or settings button):

- **GPS Offset**: Configure GPS sensor position relative to robot center (x, y, heading_offset)
- **Camera Offset**: Configure camera position relative to GPS sensor (x, y, z, heading_offset, elevation_offset)
- **Color Correction**: Adjust HSV values (hue shift, saturation multiplier, value/brightness multiplier)
- **Socket Configuration**: Change WebSocket IP and port (default: 10.42.0.1:3030)

> [!WARNING]
> GPS offsets configured in the dashboard do **NOT** automatically sync to your V5 Brain code. You must manually ensure both offsets match for accurate positioning.

### System Statistics

The dashboard displays real-time statistics:

- **FPS**: Frames per second (processing rate)
- **Inference Time**: Time taken for AI model inference (milliseconds)
- **CPU Temperature**: Device temperature (Celsius)
- **Runtime**: System uptime (seconds)
- **GPS Connected**: Connection status of GPS sensor

### Detection Visualization

- **Bounding Boxes**: Overlaid on camera feed showing detected objects
- **Confidence Scores**: Displayed with each detection
- **Field Positions**: Objects shown on field map in real-time
- **Color Coding**: Blue and red balls shown in respective colors

## Troubleshooting

### Dashboard Won't Load

**Issue**: Browser shows connection error or blank page

**Solutions:**
- Verify device is connected to Wi-Fi access point
- Check IP address is correct: `http://10.42.0.1:3000/#/`
- Ensure `serve -s build` is running on the Jetson/Raspberry Pi
- Check firewall isn't blocking port 3000
- Try refreshing the page (Ctrl+R or Cmd+R)

### WebSocket Connection Failed

**Issue**: Dashboard loads but shows "Disconnected" or no data

**Solutions:**
- Verify `override.py` is running (WebSocket server is part of the vision system)
- Check WebSocket port 3030 is accessible
- Verify WebSocket server is listening: `netstat -tuln | grep 3030`
- Check system logs: `sudo journalctl -u vexai -n 50`
- Ensure vision processing system is running

### Can't Connect to Wi-Fi Access Point

**Issue**: Wi-Fi network not visible or connection fails

**Solutions:**
- Verify Wi-Fi adapter is installed and working
- Check network mode is set to "Hotspot" (not "Ad-hoc")
- Restart network manager: `sudo systemctl restart NetworkManager`
- Check Wi-Fi adapter: `iwconfig` or `nmcli device status`
- For Raspberry Pi: Verify hotspot command completed successfully

### Dashboard Loads Slowly or Freezes

**Issue**: Dashboard is sluggish or unresponsive

**Solutions:**
- Check system resources: `htop` or `top`
- Verify sufficient RAM available
- Reduce browser window size
- Close other browser tabs/applications
- Check network connection quality
- Verify WebSocket polling rate (default: 60ms)

### Configuration Changes Not Applied

**Issue**: Settings changes don't take effect

**Solutions:**
- Verify changes are saved (check JSON files in JetsonExample directory)
- Restart vision processing system: `sudo systemctl restart vexai`
- Check WebSocket connection is active
- Verify file permissions allow writing JSON files
- Check system logs for errors

### Build Errors

**Issue**: `npm run build` fails

**Solutions:**
- Verify Node.js version: `node --version` (should be 16 or higher)
- Clear npm cache: `npm cache clean --force`
- Remove `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Check disk space: `df -h`
- Verify all dependencies installed: `npm install`
- Check for error messages in build output

## Development (Optional)

### Running in Development Mode

For development and testing:

```bash
cd ~/VAIC_25_26/JetsonWebDashboard/vexai-web-dashboard-react
npm run dev
```

This starts a development server with hot-reloading at `http://localhost:9000/#/`.

### Project Structure

```
JetsonWebDashboard/
├── vexai-web-dashboard-react/
│   ├── build/              # Production build (generated)
│   ├── public/             # Static assets
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── cameras/    # Camera view components
│   │   │   ├── field/      # Field visualization components
│   │   │   ├── modals/     # Settings modal
│   │   │   └── navigation/ # Navigation component
│   │   ├── routes/         # Route components (views)
│   │   ├── services/       # WebSocket data service
│   │   ├── state/          # Redux state management
│   │   ├── lib/            # Utilities and types
│   │   └── util/           # Configuration and helpers
│   ├── package.json        # Dependencies and scripts
│   └── tsconfig.json       # TypeScript configuration
└── tutorial/               # Access point setup images
```

## File Locations

### Configuration Files

Offset and color correction files are stored in the JetsonExample directory:

- `~/VAIC_25_26/JetsonExample/gps_offsets.json`
- `~/VAIC_25_26/JetsonExample/camera_offsets.json`
- `~/VAIC_25_26/JetsonExample/color_correction.json`

These files are automatically updated when you change settings in the dashboard.

### Build Files

- **Build Directory**: `~/VAIC_25_26/JetsonWebDashboard/vexai-web-dashboard-react/build/`
- **Source Code**: `~/VAIC_25_26/JetsonWebDashboard/vexai-web-dashboard-react/src/`

## Integration with Vision System

The web dashboard integrates with the vision processing system (`JetsonExample`):

- **WebSocket Server**: `V5Web.py` provides WebSocket server (port 3030)
- **Data Updates**: Vision system continuously updates detection data, images, and statistics
- **Configuration**: Dashboard changes apply immediately to running vision system
- **Auto-start**: Pre-built images automatically start both vision system and web server on boot

For more information on the vision processing system, see [JetsonExample README](../JetsonExample/README.md).

## Next Steps

After setting up the web dashboard:

1. **Connect Your Robot**: Upload V5 code to receive detection data (see [V5Example](../V5Example/ai_demo/README.md))
2. **Configure Offsets**: Adjust GPS and camera offsets to match your robot's physical layout
3. **Tune Color Correction**: Adjust HSV values for your lighting conditions
4. **Monitor Performance**: Use statistics to optimize system performance
5. **Test Detection**: Verify object detection accuracy and adjust as needed

## Additional Resources

- [JetsonExample README](../JetsonExample/README.md) - Vision processing system documentation
- [React Documentation](https://react.dev/) - React framework reference
- [Material-UI Documentation](https://mui.com/) - UI component library reference
- [Konva Documentation](https://konvajs.org/) - Canvas rendering library reference
