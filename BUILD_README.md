# ESP32 Uroboro Dashboard Builds

This repository contains multiple ESP32 firmware builds for the Uroboro productivity dashboard, designed for the **ESP32-S3 Reverse TFT Feather (Adafruit 5691)**.

## Quick Start

Use the build selection script to choose and flash different firmware versions:

```bash
./flash_build.sh
```

## Available Builds

### 1. **PostHog Integration** (Landscape Mode)
- **File**: `src/main_posthog.cpp`
- **Description**: Real PostHog integration with landscape display (240x135)
- **Features**:
  - Live uroboro statistics from PostHog API
  - Landscape orientation for wider data display
  - Real-time WiFi connectivity
  - HogQL query integration
  - Two-column layout for better data presentation
- **Configuration**: Requires `secrets.h` with WiFi and PostHog credentials

### 2. **Demo Mode** (Portrait Mode)  
- **File**: `src/main_demo.cpp`
- **Description**: Portrait demo with simulated stats (135x240)
- **Features**:
  - Portrait orientation display
  - Simulated uroboro activity
  - No network requirements
  - Card-based UI layout

### 3. **Simple Test**
- **File**: `src/main_simple.cpp` (auto-generated)
- **Description**: Basic display test
- **Features**:
  - Simple text display
  - Hardware verification
  - No network connectivity

### 4. **Debug Version**
- **File**: `src/main_debug.cpp` (auto-generated)
- **Description**: Debug build with extensive serial output
- **Features**:
  - Detailed serial logging
  - Memory usage monitoring
  - Hardware diagnostics

## Configuration

### PostHog Integration Setup

1. Copy `secrets.h` and configure your credentials:
```cpp
#define WIFI_SSID "your_wifi_network"
#define WIFI_PASSWORD "your_password"
#define POSTHOG_HOST "https://eu.posthog.com"
#define POSTHOG_PROJECT_ID "your_project_id"
#define POSTHOG_PERSONAL_API_KEY "phx_your_api_key"
```

2. Ensure your PostHog project tracks these events:
   - `uroboro_capture` - Work capture events
   - `uroboro_publish` - Publishing events  
   - `uroboro_status` - Status check events

### Hardware Requirements

- **Board**: ESP32-S3 Reverse TFT Feather (Adafruit 5691)
- **Display**: ST7789 TFT (240x135 or 135x240)
- **Connection**: USB-C for programming and power

## Build System

### Manual Build & Flash
```bash
# Build and upload current main.cpp
pio run --target upload

# Monitor serial output
pio device monitor
```

### Using the Build Script
```bash
# Interactive build selection
./flash_build.sh

# The script will:
# 1. Detect connected ESP32
# 2. Show available builds
# 3. Copy selected build to main.cpp
# 4. Compile and flash firmware
# 5. Optional serial monitoring
```

## Display Orientations

### Landscape Mode (240x135) - PostHog Version
- **Rotation**: `tft.setRotation(3)` (270 degrees)
- **Layout**: Two-column stats display
- **Use Case**: More data, better for productivity metrics
- **Colors**: Cyan header, multi-colored stats

### Portrait Mode (135x240) - Demo Version
- **Rotation**: `tft.setRotation(0)` (0 degrees, native)
- **Layout**: Single-column vertical layout
- **Use Case**: Traditional mobile-style interface
- **Colors**: Green header, card-based design

## Development Notes

### Python Implementation Reference
The PostHog C++ version is converted from a working Python (CircuitPython) implementation that includes:
- Real-time PostHog API integration
- HogQL query processing
- Landscape orientation display
- Efficient data parsing and trend analysis

### Key Technical Details
- **PostHog API**: Uses HogQL queries for real-time analytics
- **Display Driver**: ST7789 with Adafruit GFX library
- **Network**: WiFi with HTTPClient for API calls
- **Data Format**: JSON parsing with ArduinoJson library
- **Memory**: Optimized for ESP32-S3 with PSRAM support

## Troubleshooting

### Common Issues

1. **Build Conflicts**: Remove duplicate source files in `src/`
2. **Color Warnings**: 16-bit RGB565 color format required
3. **WiFi Connection**: Check credentials in `secrets.h`
4. **PostHog API**: Verify project ID and API key permissions
5. **Display Issues**: Confirm orientation settings match hardware

### Serial Output Examples

**PostHog Version**:
```
🔄 UROBORO LIVE - PostHog Integration
🔧 Initializing TFT display (240x135 landscape)...
✅ Display initialized in landscape mode!
🔗 Connecting to WiFi: your_network
✅ WiFi connected: 192.168.1.100
🔗 Querying PostHog for real uroboro data...
✅ Real data loaded: 15 captures, 3 publishes
```

**Demo Version**:
```
DeskHog 0.1.2 + UroboroCard Demo
🔧 Initializing TFT display...
✅ Display initialized successfully!
📊 Uroboro Stats - Captures: 12, Publishes: 2, Status: 28
```

## File Structure
```
├── src/
│   ├── main.cpp              # Active build (currently PostHog version)
│   ├── main_posthog.cpp      # PostHog landscape version
│   ├── main_demo.cpp         # Portrait demo version (if available)
│   ├── main_simple.cpp       # Basic test (auto-generated)
│   └── main_debug.cpp        # Debug version (auto-generated)
├── secrets.h                 # WiFi & PostHog credentials
├── platformio.ini            # PlatformIO configuration
├── flash_build.sh            # Build selection script
└── BUILD_README.md           # This file
```

## Current Status

✅ **PostHog Landscape Version**: Successfully created and flashed
- Displays real uroboro statistics in landscape mode (240x135)
- Matches the functional Python implementation mentioned by user
- Includes WiFi connectivity and PostHog API integration
- Two-column layout for better data presentation

🔧 **Build Selection Script**: Ready for use
- Allows easy switching between firmware versions
- Handles ESP32 detection and flashing
- Auto-generates template builds as needed

📋 **Next Steps**: Configure `secrets.h` with actual credentials to enable live data