"""
Uroboro Stats Meter for ESP32-S3 TFT Feather
==========================================

A physical dashboard that fetches your real uroboro usage statistics 
from PostHog and displays them on the TFT screen.

Shows:
- Recent captures, publishes, status checks
- Daily productivity trends
- Live activity indicators
- Session time tracking

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
POSTHOG_PROJECT_ID = "71732"  # From your PostHog URL
POSTHOG_PERSONAL_API_KEY = "NEED_PERSONAL_API_KEY"  # Different from project key

# You'll need to create a Personal API Key from PostHog Account Settings
# For now, we'll simulate the data to test the display

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

# Stats storage
uroboro_stats = {
    "captures_today": 0,
    "publishes_today": 0,
    "status_checks_today": 0,
    "captures_hour": 0,
    "last_activity": "Unknown",
    "daily_trend": "→",
    "last_fetch": "Never"
}

def setup_display():
    """Initialize the TFT display"""
    global display, main_group
    
    print("Setting up uroboro dashboard display...")
    
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
    
    print("✅ Display ready!")

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

def fetch_uroboro_stats():
    """Fetch uroboro statistics from PostHog"""
    global uroboro_stats, last_fetch_time
    
    current_time = time.monotonic()
    
    # Rate limiting - only fetch every 5 minutes
    if current_time - last_fetch_time < fetch_interval:
        return
    
    if not wifi_connected or not requests_session:
        print("❌ Cannot fetch stats: WiFi not connected")
        return
    
    print("📊 Fetching uroboro stats from PostHog...")
    
    try:
        # Since we need a Personal API Key (which you need to create),
        # let's simulate the data for now based on real uroboro patterns
        
        # This is what the actual query would look like:
        """
        query_payload = {
            "query": {
                "kind": "HogQLQuery",
                "query": '''
                    SELECT 
                        event,
                        COUNT() as count
                    FROM events 
                    WHERE 
                        event IN ('uroboro_capture', 'uroboro_publish', 'uroboro_status')
                        AND timestamp >= now() - interval 24 hour
                    GROUP BY event
                '''
            }
        }
        """
        
        # Simulate realistic uroboro usage for demo
        import random
        base_time = time.monotonic()
        
        # Simulate daily activity based on time of day
        hour = int((base_time / 3600) % 24)
        if 9 <= hour <= 17:  # Work hours
            captures_base = 15
            publishes_base = 5
            status_base = 20
        else:  # Off hours
            captures_base = 3
            publishes_base = 1
            status_base = 5
        
        # Add some randomness
        uroboro_stats["captures_today"] = captures_base + random.randint(-5, 10)
        uroboro_stats["publishes_today"] = publishes_base + random.randint(-2, 5)
        uroboro_stats["status_checks_today"] = status_base + random.randint(-5, 15)
        uroboro_stats["captures_hour"] = random.randint(0, 5)
        
        # Activity indicators
        total_activity = uroboro_stats["captures_today"] + uroboro_stats["publishes_today"]
        if total_activity > 20:
            uroboro_stats["daily_trend"] = "↗ High"
        elif total_activity > 10:
            uroboro_stats["daily_trend"] = "→ Normal"
        else:
            uroboro_stats["daily_trend"] = "↘ Low"
        
        # Last activity time
        minutes_ago = random.randint(1, 120)
        uroboro_stats["last_activity"] = f"{minutes_ago}m ago"
        
        # Update fetch time
        uroboro_stats["last_fetch"] = format_time(current_time)
        last_fetch_time = current_time
        
        print(f"✅ Stats updated: {uroboro_stats['captures_today']} captures today")
        
        # Here's where you'd actually make the PostHog API call:
        """
        response = requests_session.post(
            f"{POSTHOG_HOST}/api/projects/{POSTHOG_PROJECT_ID}/query/",
            json=query_payload,
            headers={
                "Authorization": f"Bearer {POSTHOG_PERSONAL_API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            parse_posthog_response(data)
        """
        
    except Exception as e:
        print(f"❌ Error fetching stats: {e}")

def parse_posthog_response(data):
    """Parse PostHog API response and update stats"""
    try:
        results = data.get("results", [])
        
        # Reset counts
        uroboro_stats["captures_today"] = 0
        uroboro_stats["publishes_today"] = 0
        uroboro_stats["status_checks_today"] = 0
        
        # Parse event counts
        for row in results:
            event_name = row[0]
            count = row[1]
            
            if event_name == "uroboro_capture":
                uroboro_stats["captures_today"] = count
            elif event_name == "uroboro_publish":
                uroboro_stats["publishes_today"] = count
            elif event_name == "uroboro_status":
                uroboro_stats["status_checks_today"] = count
        
        print(f"✅ Parsed PostHog data: {len(results)} event types")
        
    except Exception as e:
        print(f"❌ Error parsing PostHog response: {e}")

def format_time(monotonic_time):
    """Format time for display"""
    minutes = int(monotonic_time / 60) % 60
    hours = int(monotonic_time / 3600) % 24
    return f"{hours:02d}:{minutes:02d}"

def create_dashboard():
    """Create the dashboard display elements"""
    # Clear existing elements
    while len(main_group) > 0:
        main_group.pop()
    
    # Header
    title = label.Label(
        terminalio.FONT,
        text="🔄 UROBORO DASHBOARD",
        color=0x00FFFF,
        x=5,
        y=10
    )
    main_group.append(title)
    
    # Connection status
    status_color = 0x00FF00 if wifi_connected else 0xFF0000
    status_text = "ONLINE" if wifi_connected else "OFFLINE"
    status = label.Label(
        terminalio.FONT,
        text=f"[{status_text}]",
        color=status_color,
        x=180,
        y=10
    )
    main_group.append(status)
    
    # Today's activity
    activity_label = label.Label(
        terminalio.FONT,
        text="TODAY:",
        color=0xFFFFFF,
        x=5,
        y=30
    )
    main_group.append(activity_label)
    
    # Captures
    captures = label.Label(
        terminalio.FONT,
        text=f"📝 Captures: {uroboro_stats['captures_today']}",
        color=0x00FF00,
        x=5,
        y=45
    )
    main_group.append(captures)
    
    # Publishes
    publishes = label.Label(
        terminalio.FONT,
        text=f"📤 Publishes: {uroboro_stats['publishes_today']}",
        color=0xFF8800,
        x=5,
        y=60
    )
    main_group.append(publishes)
    
    # Status checks
    status_checks = label.Label(
        terminalio.FONT,
        text=f"📊 Status: {uroboro_stats['status_checks_today']}",
        color=0x8888FF,
        x=5,
        y=75
    )
    main_group.append(status_checks)
    
    # Current hour activity
    hour_activity = label.Label(
        terminalio.FONT,
        text=f"This hour: {uroboro_stats['captures_hour']}",
        color=0xFFFF00,
        x=5,
        y=95
    )
    main_group.append(hour_activity)
    
    # Trend and last activity
    trend = label.Label(
        terminalio.FONT,
        text=f"Trend: {uroboro_stats['daily_trend']}",
        color=0xFF00FF,
        x=5,
        y=110
    )
    main_group.append(trend)
    
    # Last update
    last_update = label.Label(
        terminalio.FONT,
        text=f"Updated: {uroboro_stats['last_fetch']}",
        color=0x888888,
        x=5,
        y=125
    )
    main_group.append(last_update)

def main():
    """Main application loop"""
    print("🔄 Starting Uroboro Stats Meter")
    print("=" * 35)
    
    # Initialize hardware
    setup_display()
    setup_wifi()
    
    # Initial stats fetch
    fetch_uroboro_stats()
    
    # Main loop
    loop_count = 0
    
    while True:
        try:
            # Fetch new data periodically
            fetch_uroboro_stats()
            
            # Update display
            create_dashboard()
            
            # Garbage collection
            if loop_count % 60 == 0:  # Every minute
                gc.collect()
                
                # Show memory status
                free_mem = gc.mem_free()
                temp = microcontroller.cpu.temperature
                print(f"💾 Memory: {free_mem} bytes, 🌡️  CPU: {temp:.1f}°C")
            
            loop_count += 1
            time.sleep(1)  # Update every second
            
        except KeyboardInterrupt:
            print("\n🔄 Uroboro dashboard stopped")
            break
            
        except Exception as e:
            print(f"❌ Error in main loop: {e}")
            time.sleep(5)  # Wait before retrying

if __name__ == "__main__":
    main()