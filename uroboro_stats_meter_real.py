"""
Real Uroboro Stats Meter for ESP32-S3 TFT Feather
================================================

Now with REAL PostHog data integration! Shows your actual uroboro usage.

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

# Import secrets from separate file
try:
    from secrets import (
        WIFI_SSID,
        WIFI_PASSWORD,
        POSTHOG_HOST,
        POSTHOG_PROJECT_ID,
        POSTHOG_PERSONAL_API_KEY
    )
except ImportError:
    print("❌ ERROR: secrets.py not found!")
    print("📝 Copy secrets_template.py to secrets.py and configure your credentials")
    raise

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
    "data_source": None,
    "today_label": None,
    "captures": None,
    "publishes": None,
    "status_checks": None,
    "hour_activity": None,
    "trend": None,
    "last_update": None
}

# Stats storage
uroboro_stats = {
    "captures_today": 0,
    "publishes_today": 0,
    "status_checks_today": 0,
    "captures_hour": 0,
    "daily_trend": "→",
    "last_fetch": "Never",
    "data_source": "Starting..."
}

# Previous stats for change detection
prev_stats = dict(uroboro_stats)
prev_wifi_status = False

def setup_display():
    """Initialize the TFT display"""
    global display, main_group

    print("🔄 Setting up REAL uroboro dashboard...")

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

    # Create all display elements
    create_static_elements()

    print("✅ Real data dashboard ready!")

def setup_wifi():
    """Connect to WiFi"""
    global wifi_connected, requests_session

    print(f"🔗 Connecting to WiFi: {WIFI_SSID}")

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
    """Create all display elements once"""
    global display_elements

    # Clear existing elements
    while len(main_group) > 0:
        main_group.pop()

    # Header
    display_elements["title"] = label.Label(
        terminalio.FONT,
        text="🔄 UROBORO LIVE",
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
        x=145,
        y=10
    )
    main_group.append(display_elements["status"])

    # Data source indicator
    display_elements["data_source"] = label.Label(
        terminalio.FONT,
        text="PostHog: Connecting...",
        color=0x888888,
        x=5,
        y=22
    )
    main_group.append(display_elements["data_source"])

    # Today's activity
    display_elements["today_label"] = label.Label(
        terminalio.FONT,
        text="TODAY:",
        color=0xFFFFFF,
        x=5,
        y=38
    )
    main_group.append(display_elements["today_label"])

    # Stats
    display_elements["captures"] = label.Label(
        terminalio.FONT,
        text="📝 Captures: --",
        color=0x00FF00,
        x=5,
        y=53
    )
    main_group.append(display_elements["captures"])

    display_elements["publishes"] = label.Label(
        terminalio.FONT,
        text="📤 Publishes: --",
        color=0xFF8800,
        x=5,
        y=68
    )
    main_group.append(display_elements["publishes"])

    display_elements["status_checks"] = label.Label(
        terminalio.FONT,
        text="📊 Status: --",
        color=0x8888FF,
        x=5,
        y=83
    )
    main_group.append(display_elements["status_checks"])

    display_elements["trend"] = label.Label(
        terminalio.FONT,
        text="Trend: --",
        color=0xFF00FF,
        x=5,
        y=103
    )
    main_group.append(display_elements["trend"])

    display_elements["last_update"] = label.Label(
        terminalio.FONT,
        text="Updated: Starting...",
        color=0x888888,
        x=5,
        y=118
    )
    main_group.append(display_elements["last_update"])

def fetch_real_uroboro_stats():
    """Fetch REAL uroboro statistics from PostHog"""
    global uroboro_stats, last_fetch_time

    current_time = time.monotonic()

    # Rate limiting
    if current_time - last_fetch_time < fetch_interval:
        return

    if not wifi_connected or not requests_session:
        print("❌ Cannot fetch: WiFi not connected")
        uroboro_stats["data_source"] = "WiFi: Offline"
        return

    print("🔗 Querying PostHog for REAL uroboro data...")
    uroboro_stats["data_source"] = "PostHog: Querying..."

    try:
        # Real PostHog query for uroboro events
        query_payload = {
            "query": {
                "kind": "HogQLQuery",
                "query": """
                    SELECT
                        event,
                        COUNT() as count
                    FROM events
                    WHERE
                        event IN ('uroboro_capture', 'uroboro_publish', 'uroboro_status')
                        AND timestamp >= now() - interval 24 hour
                    GROUP BY event
                    ORDER BY count DESC
                """
            }
        }

        response = requests_session.post(
            f"{POSTHOG_HOST}/api/projects/{POSTHOG_PROJECT_ID}/query/",
            json=query_payload,
            headers={
                "Authorization": f"Bearer {POSTHOG_PERSONAL_API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            parse_real_posthog_data(data)
            uroboro_stats["data_source"] = "PostHog: Live Data ✅"
            print(f"✅ REAL DATA: {uroboro_stats['captures_today']} captures today!")

        elif response.status_code == 401:
            print("❌ PostHog API: Unauthorized (check API key)")
            uroboro_stats["data_source"] = "PostHog: Auth Error"
            fallback_to_simulation()

        elif response.status_code == 403:
            print("❌ PostHog API: Forbidden (check permissions)")
            uroboro_stats["data_source"] = "PostHog: Permission Error"
            fallback_to_simulation()

        else:
            print(f"❌ PostHog API error: {response.status_code}")
            uroboro_stats["data_source"] = f"PostHog: Error {response.status_code}"
            fallback_to_simulation()

        response.close()

    except Exception as e:
        print(f"❌ PostHog query failed: {e}")
        uroboro_stats["data_source"] = "PostHog: Connection Error"
        fallback_to_simulation()

    # Update timing
    uroboro_stats["last_fetch"] = format_time(current_time)
    last_fetch_time = current_time

def parse_real_posthog_data(data):
    """Parse real PostHog response"""
    try:
        results = data.get("results", [])

        # Reset counts
        uroboro_stats["captures_today"] = 0
        uroboro_stats["publishes_today"] = 0
        uroboro_stats["status_checks_today"] = 0

        print(f"📊 PostHog returned {len(results)} event types")

        # Parse event counts
        for row in results:
            if len(row) >= 2:
                event_name = row[0]
                count = int(row[1])

                print(f"   {event_name}: {count}")

                if event_name == "uroboro_capture":
                    uroboro_stats["captures_today"] = count
                elif event_name == "uroboro_publish":
                    uroboro_stats["publishes_today"] = count
                elif event_name == "uroboro_status":
                    uroboro_stats["status_checks_today"] = count

        # Calculate trend
        total_activity = uroboro_stats["captures_today"] + uroboro_stats["publishes_today"]
        if total_activity > 20:
            uroboro_stats["daily_trend"] = "↗ High Productivity"
        elif total_activity > 5:
            uroboro_stats["daily_trend"] = "→ Normal Activity"
        elif total_activity > 0:
            uroboro_stats["daily_trend"] = "↘ Light Usage"
        else:
            uroboro_stats["daily_trend"] = "💤 Quiet Day"

        print(f"✅ Real uroboro stats loaded successfully!")

    except Exception as e:
        print(f"❌ Error parsing PostHog data: {e}")
        fallback_to_simulation()

def fallback_to_simulation():
    """Fallback to simulated data if PostHog fails"""
    print("📊 Falling back to simulated data")

    import random
    current_time = time.monotonic()
    hour = int((current_time / 3600) % 24)

    if 9 <= hour <= 17:  # Work hours
        uroboro_stats["captures_today"] = random.randint(10, 25)
        uroboro_stats["publishes_today"] = random.randint(3, 8)
        uroboro_stats["status_checks_today"] = random.randint(15, 30)
    else:  # Off hours
        uroboro_stats["captures_today"] = random.randint(0, 5)
        uroboro_stats["publishes_today"] = random.randint(0, 2)
        uroboro_stats["status_checks_today"] = random.randint(2, 8)

    total = uroboro_stats["captures_today"] + uroboro_stats["publishes_today"]
    if total > 15:
        uroboro_stats["daily_trend"] = "↗ Simulated High"
    elif total > 5:
        uroboro_stats["daily_trend"] = "→ Simulated Normal"
    else:
        uroboro_stats["daily_trend"] = "↘ Simulated Low"

def format_time(monotonic_time):
    """Format time for display"""
    minutes = int(monotonic_time / 60) % 60
    hours = int(monotonic_time / 3600) % 24
    return f"{hours:02d}:{minutes:02d}"

def update_display_element(element_key, new_text, new_color=None):
    """Update display element if changed"""
    element = display_elements[element_key]
    if element and element.text != new_text:
        element.text = new_text
        if new_color:
            element.color = new_color
        return True
    return False

def update_dashboard():
    """Update display elements that have changed"""
    global prev_stats, prev_wifi_status

    changes_made = False

    # WiFi status
    if wifi_connected != prev_wifi_status:
        status_color = 0x00FF00 if wifi_connected else 0xFF0000
        status_text = "ONLINE" if wifi_connected else "OFFLINE"
        if update_display_element("status", f"[{status_text}]", status_color):
            changes_made = True
        prev_wifi_status = wifi_connected

    # Data source
    if uroboro_stats["data_source"] != prev_stats.get("data_source", ""):
        if update_display_element("data_source", uroboro_stats["data_source"]):
            changes_made = True

    # Stats
    if uroboro_stats["captures_today"] != prev_stats["captures_today"]:
        if update_display_element("captures", f"📝 Captures: {uroboro_stats['captures_today']}"):
            changes_made = True

    if uroboro_stats["publishes_today"] != prev_stats["publishes_today"]:
        if update_display_element("publishes", f"📤 Publishes: {uroboro_stats['publishes_today']}"):
            changes_made = True

    if uroboro_stats["status_checks_today"] != prev_stats["status_checks_today"]:
        if update_display_element("status_checks", f"📊 Status: {uroboro_stats['status_checks_today']}"):
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
        print("🖥️ Display updated with new data")

def main():
    """Main application loop"""
    print("🔄 Starting REAL Uroboro Stats Meter")
    print("🔗 Connecting to PostHog for live data...")
    print("=" * 45)

    # Initialize
    setup_display()
    setup_wifi()

    # Initial fetch
    fetch_real_uroboro_stats()
    update_dashboard()

    # Main loop
    loop_count = 0

    while True:
        try:
            # Fetch real data periodically
            fetch_real_uroboro_stats()

            # Update display
            update_dashboard()

            # Maintenance
            if loop_count % 120 == 0:  # Every 2 minutes
                gc.collect()
                free_mem = gc.mem_free()
                temp = microcontroller.cpu.temperature
                print(f"💾 Memory: {free_mem} bytes, 🌡️ CPU: {temp:.1f}°C")

            loop_count += 1
            time.sleep(1)  # 1 FPS for real data

        except KeyboardInterrupt:
            print("\n🔄 Real uroboro dashboard stopped")
            break

        except Exception as e:
            print(f"❌ Error in main loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
