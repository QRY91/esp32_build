"""
DeskHog PostHog Analytics Demo for ESP32-S3 TFT Feather
=====================================================

This demo integrates the working display demo with PostHog analytics,
tracking user interactions and device metrics.

Features:
- Cursor movement tracking
- Button press analytics
- Device health metrics (temperature, memory)
- Session duration tracking
- Game score analytics

Author: QRY
Date: June 19, 2025
"""

import board
import displayio
import digitalio
import adafruit_st7789
import fourwire
import time
import microcontroller
import gc
import wifi
import socketpool
import ssl
import adafruit_requests
import json
import binascii
from adafruit_display_text import label
import terminalio

# Import secrets from separate file
try:
    from secrets import (
        WIFI_SSID,
        WIFI_PASSWORD,
        POSTHOG_API_KEY,
        POSTHOG_HOST
    )
except ImportError:
    print("❌ ERROR: secrets.py not found!")
    print("📝 Copy secrets_template.py to secrets.py and configure your credentials")
    raise
DEVICE_ID = "deskhog_esp32_" + str(binascii.hexlify(microcontroller.cpu.uid))[:8]

# Test mode - set to True to show events without sending
TEST_MODE = True

# Display Configuration
TFT_WIDTH = 240
TFT_HEIGHT = 135

# Button pins (for future use)
BUTTON_UP = board.IO12
BUTTON_DOWN = board.IO13
BUTTON_LEFT = board.IO14
BUTTON_RIGHT = board.IO15
BUTTON_A = board.IO16
BUTTON_B = board.IO17

# Global variables
cursor_x = TFT_WIDTH // 2
cursor_y = TFT_HEIGHT // 2
score = 0
session_start_time = time.monotonic()
last_analytics_time = 0
button_press_count = 0
wifi_connected = False
requests_session = None
display = None
main_group = None
status_label = None

def setup_display():
    """Initialize the TFT display"""
    global display, main_group, status_label

    print("Setting up display...")

    # Release any existing displays
    displayio.release_displays()

    # Initialize backlight
    backlight = digitalio.DigitalInOut(board.TFT_BACKLIGHT)
    backlight.direction = digitalio.Direction.OUTPUT
    backlight.value = True

    # Initialize display
    spi = board.SPI()
    display_bus = fourwire.FourWire(
        spi,
        command=board.TFT_DC,
        chip_select=board.TFT_CS,
        reset=board.TFT_RESET
    )

    display = adafruit_st7789.ST7789(
        display_bus,
        width=TFT_WIDTH,
        height=TFT_HEIGHT,
        rotation=270,
        rowstart=40,
        colstart=53
    )

    # Create main display group
    main_group = displayio.Group()
    display.root_group = main_group

    # Create status label
    status_label = label.Label(
        terminalio.FONT,
        text="DeskHog Analytics Demo",
        color=0xFFFFFF,
        x=5,
        y=10
    )
    main_group.append(status_label)

    # Draw border
    border_bitmap = displayio.Bitmap(TFT_WIDTH, TFT_HEIGHT, 1)
    border_palette = displayio.Palette(1)
    border_palette[0] = 0x888888
    border_tilegrid = displayio.TileGrid(border_bitmap, pixel_shader=border_palette)
    main_group.append(border_tilegrid)

    # Clear center area
    center_bitmap = displayio.Bitmap(TFT_WIDTH - 4, TFT_HEIGHT - 20, 1)
    center_palette = displayio.Palette(1)
    center_palette[0] = 0x000000
    center_tilegrid = displayio.TileGrid(center_bitmap, pixel_shader=center_palette, x=2, y=18)
    main_group.append(center_tilegrid)

    print("Display setup complete!")

def setup_wifi():
    """Connect to WiFi"""
    global wifi_connected, requests_session

    print(f"Connecting to WiFi: {WIFI_SSID}")

    try:
        wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
        print(f"Connected! IP: {wifi.radio.ipv4_address}")

        # Create requests session
        pool = socketpool.SocketPool(wifi.radio)
        ssl_context = ssl.create_default_context()
        requests_session = adafruit_requests.Session(pool, ssl_context)

        wifi_connected = True
        update_status("WiFi: Connected")

    except Exception as e:
        print(f"WiFi connection failed: {e}")
        wifi_connected = False
        update_status("WiFi: Failed")

def update_status(message):
    """Update the status label"""
    if status_label:
        status_label.text = f"DeskHog | {message}"

def send_posthog_event(event_name, properties=None):
    """Send an event to PostHog (or show in test mode)"""

    # Build event data
    event_data = {
        "api_key": POSTHOG_API_KEY,
        "event": event_name,
        "distinct_id": DEVICE_ID,
        "properties": {
            "device_type": "ESP32-S3",
            "firmware": "CircuitPython",
            "project": "deskhog_demo",
            "cpu_temp": microcontroller.cpu.temperature,
            "free_memory": gc.mem_free(),
            "session_duration": time.monotonic() - session_start_time,
            "timestamp": time.monotonic(),
            **(properties or {})
        }
    }

    if TEST_MODE:
        # Test mode - just show what would be sent
        print(f"📊 TEST MODE - Event: {event_name}")
        print(f"   Properties: {len(event_data['properties'])} fields")
        print(f"   Device: {DEVICE_ID}")
        print(f"   Temperature: {microcontroller.cpu.temperature}°C")
        if properties:
            for key, value in properties.items():
                print(f"   {key}: {value}")
        print("   (Event not actually sent)")
        return True

    # Real mode - send to PostHog
    if not wifi_connected or not requests_session:
        print(f"❌ Cannot send {event_name}: WiFi not connected")
        return False

    try:
        print(f"📊 Sending event: {event_name}")

        response = requests_session.post(
            f"{POSTHOG_HOST}/capture/",
            json=event_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )

        success = response.status_code == 200
        response.close()

        if success:
            print(f"✅ Event sent: {event_name}")
        else:
            print(f"❌ Event failed: {response.status_code}")

        return success

    except Exception as e:
        print(f"❌ PostHog error: {e}")
        return False

def setup_buttons():
    """Initialize button pins"""
    print("Setting up buttons...")

    # Configure all buttons as inputs with pull-up resistors
    buttons = [BUTTON_UP, BUTTON_DOWN, BUTTON_LEFT, BUTTON_RIGHT, BUTTON_A, BUTTON_B]

    for button_pin in buttons:
        try:
            button = digitalio.DigitalInOut(button_pin)
            button.direction = digitalio.Direction.INPUT
            button.pull = digitalio.Pull.UP
        except Exception as e:
            print(f"Button setup warning: {e}")

def draw_cursor():
    """Draw the cursor on screen"""
    # Create cursor bitmap
    cursor_bitmap = displayio.Bitmap(10, 10, 1)
    cursor_palette = displayio.Palette(1)
    cursor_palette[0] = 0xFF0000  # Red cursor

    cursor_tilegrid = displayio.TileGrid(
        cursor_bitmap,
        pixel_shader=cursor_palette,
        x=cursor_x - 5,
        y=cursor_y - 5
    )

    # Remove old cursor if exists
    if len(main_group) > 3:
        main_group.pop()

    main_group.append(cursor_tilegrid)

def simulate_interaction():
    """Simulate user interactions for demo purposes"""
    global cursor_x, cursor_y, score, button_press_count

    # Simulate cursor movement
    import random

    # Move cursor randomly
    cursor_x += random.randint(-5, 5)
    cursor_y += random.randint(-3, 3)

    # Keep cursor in bounds
    cursor_x = max(10, min(TFT_WIDTH - 10, cursor_x))
    cursor_y = max(25, min(TFT_HEIGHT - 10, cursor_y))

    # Simulate occasional button presses
    if random.randint(1, 20) == 1:  # 5% chance per loop
        button_press_count += 1

        # Simulate different button types
        button_types = ["up", "down", "left", "right", "action_a", "action_b"]
        button_pressed = random.choice(button_types)

        if button_pressed == "action_a":
            score += 1
            print(f"Score increased: {score}")
        elif button_pressed == "action_b":
            score = 0
            print("Score reset!")

        # Send button press analytics
        send_posthog_event("button_pressed", {
            "button_type": button_pressed,
            "cursor_x": cursor_x,
            "cursor_y": cursor_y,
            "current_score": score
        })

def send_periodic_analytics():
    """Send periodic analytics data"""
    global last_analytics_time

    current_time = time.monotonic()

    # Send analytics every 30 seconds
    if current_time - last_analytics_time > 30:
        last_analytics_time = current_time

        # Device health metrics
        send_posthog_event("device_health", {
            "cpu_temperature": microcontroller.cpu.temperature,
            "free_memory": gc.mem_free(),
            "total_button_presses": button_press_count,
            "current_score": score,
            "cursor_position": f"{cursor_x},{cursor_y}"
        })

        # Session duration milestone
        session_duration = current_time - session_start_time
        if session_duration > 60:  # After 1 minute
            send_posthog_event("session_milestone", {
                "duration_seconds": session_duration,
                "interactions_count": button_press_count,
                "max_score": score
            })

def main():
    """Main application loop"""
    global cursor_x, cursor_y

    print("Starting DeskHog PostHog Analytics Demo")
    print("=" * 40)

    # Initialize hardware
    setup_display()
    setup_buttons()

    # Connect to WiFi and PostHog
    setup_wifi()

    # Send startup event
    if wifi_connected:
        send_posthog_event("device_startup", {
            "device_id": DEVICE_ID,
            "firmware_version": "1.0.0",
            "display_resolution": f"{TFT_WIDTH}x{TFT_HEIGHT}"
        })

    # Main loop
    loop_count = 0

    while True:
        try:
            # Simulate user interactions
            simulate_interaction()

            # Update display
            draw_cursor()

            # Update status
            session_time = int(time.monotonic() - session_start_time)
            update_status(f"Score: {score} | Time: {session_time}s | Presses: {button_press_count}")

            # Send periodic analytics
            send_periodic_analytics()

            # Garbage collection
            if loop_count % 100 == 0:
                gc.collect()

            loop_count += 1
            time.sleep(0.1)  # 10 FPS

        except KeyboardInterrupt:
            print("\nShutting down...")

            # Send shutdown event
            if wifi_connected:
                send_posthog_event("device_shutdown", {
                    "session_duration": time.monotonic() - session_start_time,
                    "total_interactions": button_press_count,
                    "final_score": score
                })

            break

        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
