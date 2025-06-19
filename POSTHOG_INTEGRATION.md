# PostHog Analytics Integration for ESP32 DeskHog Demo

This document explains how to integrate PostHog analytics with the ESP32-S3 TFT Feather running CircuitPython.

## Overview

The `deskhog_posthog_demo.py` script demonstrates real-time analytics tracking from an embedded device, sending interaction data to the same PostHog project used by qry.zone.

## Configuration

### 1. WiFi Setup
Edit the script to add your WiFi credentials:
```python
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"
```

### 2. PostHog API Key
Get your PostHog project API key from the qry.zone PostHog dashboard:
- Go to Project Settings → API Keys
- Copy the project API key (starts with `phc_`)
- Update the script:
```python
POSTHOG_API_KEY = "phc_your_actual_api_key_here"
```

### 3. Required Libraries
Ensure these CircuitPython libraries are installed in `/media/qry/CIRCUITPY/lib/`:
- `adafruit_requests.mpy`
- `adafruit_display_text/` (folder)

## Analytics Events

### Device Events
- **device_startup**: When ESP32 boots and connects
- **device_shutdown**: When device shuts down gracefully
- **device_health**: Periodic system metrics (every 30s)

### User Interaction Events
- **button_pressed**: Each button press with context
- **session_milestone**: Session duration milestones

### Event Properties
All events include:
- `device_type`: "ESP32-S3"
- `firmware`: "CircuitPython" 
- `project`: "deskhog_demo"
- `cpu_temp`: Current CPU temperature
- `free_memory`: Available RAM
- `session_duration`: Time since startup
- `distinct_id`: Unique device identifier

## Device Identification

Each ESP32 gets a unique identifier based on its CPU UID:
```python
DEVICE_ID = "deskhog_esp32_" + str(binascii.hexlify(microcontroller.cpu.uid))[:8]
```

This allows tracking individual devices while maintaining privacy.

## Data Flow

```
ESP32 Device → WiFi → PostHog API → qry.zone Analytics Dashboard
```

1. ESP32 collects interaction data and system metrics
2. Data sent via HTTPS POST to PostHog capture endpoint
3. Events appear in PostHog dashboard alongside web analytics
4. Can be visualized in qry.zone analytics section

## Implementation Features

### Robust Error Handling
- WiFi connection retries
- PostHog API error handling
- Graceful degradation when offline

### Performance Optimized
- Non-blocking analytics calls
- Periodic garbage collection
- Configurable event frequency

### Privacy Focused
- No personal data collection
- Device-level anonymization
- Respects same privacy principles as qry.zone

## Usage

1. **Upload to ESP32**:
   ```bash
   cp deskhog_posthog_demo.py /media/qry/CIRCUITPY/code.py
   ```

2. **Monitor Serial Output**:
   ```bash
   screen /dev/ttyACM0 115200
   ```

3. **View Analytics**:
   - Check PostHog dashboard for real-time events
   - Events tagged with `project: "deskhog_demo"`

## Demo Features

Since physical buttons aren't wired yet, the demo simulates:
- **Random cursor movement** (updates display)
- **Simulated button presses** (5% chance per loop)
- **Score tracking** (A button increments, B button resets)
- **Real-time status display** on TFT screen

## Event Examples

### Button Press Event
```json
{
  "event": "button_pressed",
  "properties": {
    "button_type": "action_a",
    "cursor_x": 120,
    "cursor_y": 67,
    "current_score": 5,
    "device_type": "ESP32-S3",
    "cpu_temp": 32.5,
    "session_duration": 45.2
  }
}
```

### Device Health Event
```json
{
  "event": "device_health", 
  "properties": {
    "cpu_temperature": 31.8,
    "free_memory": 142336,
    "total_button_presses": 12,
    "current_score": 3,
    "cursor_position": "115,72"
  }
}
```

## Next Steps

1. **Wire Physical Buttons**: Replace simulation with real button input
2. **Game Implementation**: Add actual Snake/Pong game logic
3. **Advanced Analytics**: Track game-specific metrics (high scores, play patterns)
4. **Device Fleet Management**: Monitor multiple DeskHog devices
5. **A/B Testing**: Use PostHog feature flags for device configuration

## Integration with qry.zone

This creates a unified analytics ecosystem:
- **Web analytics**: User engagement with qry.zone content
- **Device analytics**: Physical interaction with QRY tools
- **Cross-platform insights**: How web visitors become device users

The embedded analytics complement the web analytics to provide complete visibility into the QRY methodology in practice.

## Troubleshooting

### WiFi Connection Issues
- Check SSID/password configuration
- Verify WiFi network allows device connections
- Monitor serial output for connection errors

### PostHog Events Not Appearing
- Verify API key is correct (starts with `phc_`)
- Check PostHog host URL
- Ensure device has internet access
- Look for HTTP status codes in serial output

### Performance Issues
- Reduce event frequency if needed
- Monitor memory usage via `gc.mem_free()`
- Check for memory leaks in long-running sessions

---

**Status**: Ready for testing with WiFi credentials and PostHog API key
**Next**: Wire physical buttons and implement actual games
**Integration**: Part of unified QRY analytics ecosystem