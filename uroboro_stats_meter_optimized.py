"""
Optimized Uroboro Stats Meter for ESP32-S3 TFT Feather
====================================================

Improved version with smoother display updates and better performance.
Only redraws elements that have actually changed.

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
from adafruit_display_text import label
import terminalio

# Configuration
WIFI_SSID = "telenet-0637807"
WIFI_PASSWORD = "nfu3prubctJc"

# PostHog Configuration
POSTHOG_HOST = "https://eu.posthog.com"
POSTHOG_PROJECT_ID = "71732"
POSTHOG_PERSONAL_API_KEY = "phx_BTiiLzjrU3DXKgRB2NcrJau01j9P5TRYAZPR2mZYBIMUcAQ"

# Display Configuration
TFT_WIDTH = 240
TFT_HEIGHT = 135

# Global variables
display = None
main_group = None
wifi_connected = False
requests_session = None
last_fetch_time = 0
fetch_interval = 300  # 5 minutes between fetches

# Display elements (persistent references)
display_elements = {
    "title": None,
    "status": None,
    "today_label": None,
    "captures": None,
    "publishes": None,
    "status_checks": None,
    "hour_activity": None,
    "trend": None,
    "last_update": None
}

# Stats storage with previous values for change detection
uroboro_stats = {
    "captures_today": 0,
    "publishes_today": 0,
    "status_checks_today": 0,
    "captures_hour": 0,
    "last_activity": "Unknown",
    "daily_trend": "→",
    "last_fetch": "Never"
}

# Previous stats for change detection
prev_stats = dict(uroboro_stats)
prev_wifi_status = False

def setup_display():
    """Initialize the TFT display"""
    global display, main_group
    
    print("Setting up optimized uroboro dashboard...")
    
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
    
    # Create all display elements once
    create_static_elements()
    
    print("✅ Optimized display ready!")

def setup_wifi():
    """Connect to WiFi"""
    global wifi_connected, requests_session
    
    print(f"Connecting to WiFi: {WIFI_SSID}")
    
    try:
        wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
        print(f"✅ WiFi connected: {wifi.radio.ipv4_address}")
        
        # Create requests session
        pool = socketpool.SocketPool(wifi.radio)
        ssl_context = ssl.create_default_context()
        requests_session = adafruit_requests.Session(pool, ssl_context)
        
        wifi_connected = True
        
    except Exception as e:
        print(f"❌ WiFi connection failed: {e}")
        wifi_connected = False

def create_static_elements():
    """Create all display elements once and store references"""
    global display_elements
    
    # Clear any existing elements
    while len(main_group) > 0:
        main_group.pop()
    
    # Header (static)
    display_elements["title"] = label.Label(
        terminalio.FONT,
        text="🔄 UROBORO DASHBOARD",
        color=0x00FFFF,
        x=5,
        y=10
    )
    main_group.append(display_elements["title"])
    
    # Connection status
    display_elements["status"] = label.Label(
        terminalio.FONT,
        text="[CONNECTING]",
        color=0xFFFF00,
        x=165,
        y=10
    )
    main_group.append(display_elements["status"])
    
    # Today's activity label (static)
    display_elements["today_label"] = label.Label(
        terminalio.FONT,
        text="TODAY:",
        color=0xFFFFFF,
        x=5,
        y=30
    )
    main_group.append(display_elements["today_label"])
    
    # Dynamic stats
    display_elements["captures"] = label.Label(
        terminalio.FONT,
        text="📝 Captures: --",
        color=0x00FF00,
        x=5,
        y=45
    )
    main_group.append(display_elements["captures"])
    
    display_elements["publishes"] = label.Label(
        terminalio.FONT,
        text="📤 Publishes: --",
        color=0xFF8800,
        x=5,
        y=60
    )
    main_group.append(display_elements["publishes"])
    
    display_elements["status_checks"] = label.Label(
        terminalio.FONT,
        text="📊 Status: --",
        color=0x8888FF,
        x=5,
        y=75
    )
    main_group.append(display_elements["status_checks"])
    
    display_elements["hour_activity"] = label.Label(
        terminalio.FONT,
        text="This hour: --",
        color=0xFFFF00,
        x=5,
        y=95
    )
    main_group.append(display_elements["hour_activity"])
    
    display_elements["trend"] = label.Label(
        terminalio.FONT,
        text="Trend: --",
        color=0xFF00FF,
        x=5,
        y=110
    )
    main_group.append(display_elements["trend"])
    
    display_elements["last_update"] = label.Label(
        terminalio.FONT,
        text="Updated: Starting...",
        color=0x888888,
        x=5,
        y=125
    )
    main_group.append(display_elements["last_update"])

def fetch_uroboro_stats():
    """Fetch uroboro statistics (simulated for now)"""
    global uroboro_stats, last_fetch_time
    
    current_time = time.monotonic()
    
    # Rate limiting - only fetch every 5 minutes
    if current_time - last_fetch_time < fetch_interval:
        return
    
    print("📊 Updating uroboro stats...")
    
    try:
        # Simulate realistic uroboro usage for demo
        import random
        
        # Simulate daily activity based on time of day
        hour = int((current_time / 3600) % 24)
        if 9 <= hour <= 17:  # Work hours
            captures_base = 15
            publishes_base = 5
            status_base = 20
        else:  # Off hours
            captures_base = 3
            publishes_base = 1
            status_base = 5
        
        # Add some randomness but keep changes smaller for smoother demo
        uroboro_stats["captures_today"] = max(0, captures_base + random.randint(-3, 5))
        uroboro_stats["publishes_today"] = max(0, publishes_base + random.randint(-1, 3))
        uroboro_stats["status_checks_today"] = max(0, status_base + random.randint(-5, 10))
        uroboro_stats["captures_hour"] = random.randint(0, 3)
        
        # Activity indicators
        total_activity = uroboro_stats["captures_today"] + uroboro_stats["publishes_today"]
        if total_activity > 20:
            uroboro_stats["daily_trend"] = "↗ High"
        elif total_activity > 10:
            uroboro_stats["daily_trend"] = "→ Normal"
        else:
            uroboro_stats["daily_trend"] = "↘ Low"
        
        # Update fetch time
        uroboro_stats["last_fetch"] = format_time(current_time)
        last_fetch_time = current_time
        
        print(f"✅ Stats: {uroboro_stats['captures_today']} captures, {uroboro_stats['publishes_today']} publishes")
        
    except Exception as e:
        print(f"❌ Error updating stats: {e}")

def format_time(monotonic_time):
    """Format time for display"""
    minutes = int(monotonic_time / 60) % 60
    hours = int(monotonic_time / 3600) % 24
    return f"{hours:02d}:{minutes:02d}"

def update_display_element(element_key, new_text, new_color=None):
    """Update a display element only if it has changed"""
    element = display_elements[element_key]
    if element and element.text != new_text:
        element.text = new_text
        if new_color:
            element.color = new_color
        return True
    return False

def update_dashboard():
    """Update only the parts of the dashboard that have changed"""
    global prev_stats, prev_wifi_status
    
    changes_made = False
    
    # Update WiFi status only if changed
    if wifi_connected != prev_wifi_status:
        status_color = 0x00FF00 if wifi_connected else 0xFF0000
        status_text = "ONLINE" if wifi_connected else "OFFLINE"
        if update_display_element("status", f"[{status_text}]", status_color):
            changes_made = True
        prev_wifi_status = wifi_connected
    
    # Update stats only if they've changed
    if uroboro_stats["captures_today"] != prev_stats["captures_today"]:
        if update_display_element("captures", f"📝 Captures: {uroboro_stats['captures_today']}"):
            changes_made = True
    
    if uroboro_stats["publishes_today"] != prev_stats["publishes_today"]:
        if update_display_element("publishes", f"📤 Publishes: {uroboro_stats['publishes_today']}"):
            changes_made = True
    
    if uroboro_stats["status_checks_today"] != prev_stats["status_checks_today"]:
        if update_display_element("status_checks", f"📊 Status: {uroboro_stats['status_checks_today']}"):
            changes_made = True
    
    if uroboro_stats["captures_hour"] != prev_stats["captures_hour"]:
        if update_display_element("hour_activity", f"This hour: {uroboro_stats['captures_hour']}"):
            changes_made = True
    
    if uroboro_stats["daily_trend"] != prev_stats["daily_trend"]:
        if update_display_element("trend", f"Trend: {uroboro_stats['daily_trend']}"):
            changes_made = True
    
    if uroboro_stats["last_fetch"] != prev_stats["last_fetch"]:
        if update_display_element("last_update", f"Updated: {uroboro_stats['last_fetch']}"):
            changes_made = True
    
    # Update previous stats
    prev_stats = dict(uroboro_stats)
    
    if changes_made:
        print("🖥️ Display updated")

def main():
    """Main application loop"""
    print("🔄 Starting Optimized Uroboro Stats Meter")
    print("=" * 42)
    
    # Initialize hardware
    setup_display()
    setup_wifi()
    
    # Initial stats fetch
    fetch_uroboro_stats()
    update_dashboard()
    
    # Main loop
    loop_count = 0
    
    while True:
        try:
            # Fetch new data periodically
            fetch_uroboro_stats()
            
            # Update display only if needed
            update_dashboard()
            
            # Garbage collection every 2 minutes
            if loop_count % 120 == 0:
                gc.collect()
                
                # Show memory status
                free_mem = gc.mem_free()
                temp = microcontroller.cpu.temperature
                print(f"💾 Memory: {free_mem} bytes, 🌡️ CPU: {temp:.1f}°C")
            
            loop_count += 1
            time.sleep(0.5)  # 2 FPS - slower updates, smoother display
            
        except KeyboardInterrupt:
            print("\n🔄 Optimized uroboro dashboard stopped")
            break
            
        except Exception as e:
            print(f"❌ Error in main loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()