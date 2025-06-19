"""
Simple Analytics Test for ESP32-S3 TFT Feather
==============================================

Minimal test to verify PostHog analytics integration step by step.
"""

import board
import displayio
import digitalio
import adafruit_st7789
import fourwire
import time
import microcontroller
import gc
from adafruit_display_text import label
import terminalio

# Try WiFi imports
try:
    import wifi
    import socketpool
    import ssl
    import adafruit_requests
    import json
    wifi_available = True
    print("✅ WiFi libraries imported successfully")
except ImportError as e:
    wifi_available = False
    print(f"❌ WiFi import failed: {e}")

# Configuration
WIFI_SSID = "telenet-0637807"
WIFI_PASSWORD = "nfu3prubctJc"
POSTHOG_API_KEY = "phc_iBTiBdPMkRH0WFb8Ty3YoNM6qbnQtyyMOn1eOpuy6zj"
POSTHOG_HOST = "https://eu.posthog.com"

# Display setup
print("Setting up display...")

# Release displays
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
    width=240,
    height=135,
    rotation=270,
    rowstart=40,
    colstart=53
)

# Create display group
main_group = displayio.Group()
display.root_group = main_group

# Add title
title_label = label.Label(
    terminalio.FONT,
    text="Analytics Test",
    color=0xFFFFFF,
    x=5,
    y=10
)
main_group.append(title_label)

# Add status
status_label = label.Label(
    terminalio.FONT,
    text="Starting...",
    color=0x00FF00,
    x=5,
    y=25
)
main_group.append(status_label)

print("✅ Display initialized!")

# Test WiFi if available
if wifi_available:
    try:
        status_label.text = "Connecting WiFi..."
        print(f"Connecting to WiFi: {WIFI_SSID}")
        
        wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
        ip = wifi.radio.ipv4_address
        
        status_label.text = f"WiFi: {ip}"
        print(f"✅ WiFi connected: {ip}")
        
        # Test HTTP request setup
        pool = socketpool.SocketPool(wifi.radio)
        ssl_context = ssl.create_default_context()
        requests = adafruit_requests.Session(pool, ssl_context)
        
        print("✅ HTTP client ready")
        
    except Exception as e:
        status_label.text = f"WiFi failed: {str(e)[:20]}"
        print(f"❌ WiFi error: {e}")
else:
    status_label.text = "WiFi libs missing"

# Add device info
device_label = label.Label(
    terminalio.FONT,
    text=f"CPU: {microcontroller.cpu.temperature:.1f}C",
    color=0xFFFF00,
    x=5,
    y=40
)
main_group.append(device_label)

# Add memory info
memory_label = label.Label(
    terminalio.FONT,
    text=f"RAM: {gc.mem_free()} bytes",
    color=0xFF00FF,
    x=5,
    y=55
)
main_group.append(memory_label)

print("📊 Starting test loop...")

# Test loop
counter = 0
start_time = time.monotonic()

while True:
    try:
        counter += 1
        current_time = time.monotonic()
        
        # Update device stats
        device_label.text = f"CPU: {microcontroller.cpu.temperature:.1f}C"
        memory_label.text = f"RAM: {gc.mem_free()} bytes"
        
        # Every 10 seconds, simulate an analytics event
        if counter % 100 == 0:  # Every 10 seconds at 0.1s interval
            session_duration = current_time - start_time
            
            # This is what we'd send to PostHog
            event_data = {
                "api_key": POSTHOG_API_KEY,
                "event": "esp32_test_event",
                "distinct_id": f"esp32_test_{microcontroller.cpu.uid}",
                "properties": {
                    "device_type": "ESP32-S3",
                    "cpu_temp": microcontroller.cpu.temperature,
                    "free_memory": gc.mem_free(),
                    "session_duration": session_duration,
                    "counter": counter,
                    "wifi_available": wifi_available
                }
            }
            
            print(f"📊 TEST EVENT #{counter//100}:")
            print(f"   Temperature: {microcontroller.cpu.temperature:.1f}°C")
            print(f"   Free RAM: {gc.mem_free()} bytes")
            print(f"   Session: {session_duration:.1f}s")
            print(f"   WiFi: {wifi_available}")
            
            # Update counter on display
            if len(main_group) > 4:
                main_group.pop()
            
            counter_label = label.Label(
                terminalio.FONT,
                text=f"Events: {counter//100}",
                color=0x00FFFF,
                x=5,
                y=70
            )
            main_group.append(counter_label)
        
        # Garbage collection every 50 loops
        if counter % 50 == 0:
            gc.collect()
        
        time.sleep(0.1)  # 10 FPS
        
    except KeyboardInterrupt:
        print("Test stopped by user")
        break
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(1)

print("Test completed!")