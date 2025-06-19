"""
DeskHog Multi-Mode Device for ESP32-S3 TFT Feather
===============================================

A versatile desk companion with multiple modes:
- Mode 0: Live Uroboro Stats Dashboard  
- Mode 1: Snake Game (deskhog gaming library contribution)
- Mode 2: Device Info & Settings

Controls:
- D0 (BOOT): Switch modes / Menu
- D1: Action/Confirm
- D2: Action/Cancel

Perfect for demonstrating community involvement and technical skills!

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
import random

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

# Mode definitions
MODE_STATS = 0
MODE_GAME = 1
MODE_INFO = 2
MODE_COUNT = 3

# Global variables
display = None
main_group = None
wifi_connected = False
requests_session = None
current_mode = MODE_STATS
last_fetch_time = 0
fetch_interval = 300

# Button setup with proper pin assignments
button_d0 = None  # Boot button (D0) - inverted logic
button_d1 = None  # D1 button - normal logic  
button_d2 = None  # D2 button - normal logic

# Button debouncing
button_states = {"d0": False, "d1": False, "d2": False}
button_timers = {"d0": 0, "d1": 0, "d2": 0}
DEBOUNCE_DELAY = 200  # milliseconds

# Stats storage
uroboro_stats = {
    "captures_today": 0,
    "publishes_today": 0, 
    "status_checks_today": 0,
    "daily_trend": "→",
    "last_fetch": "Never",
    "data_source": "Starting..."
}

# Snake game state
snake_game = {
    "snake": [(12, 6), (11, 6), (10, 6)],  # Head to tail
    "food": (15, 8),
    "direction": (1, 0),  # (dx, dy) 
    "score": 0,
    "game_over": False,
    "last_move": 0,
    "move_delay": 300  # milliseconds
}

def setup_display():
    """Initialize the TFT display"""
    global display, main_group
    
    print("🖥️ Setting up multi-mode display...")
    
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

def setup_buttons():
    """Initialize the front panel buttons"""
    global button_d0, button_d1, button_d2
    
    print("🎮 Setting up front panel buttons...")
    
    try:
        # D0 (Boot button) - inverted logic with internal pull-up
        button_d0 = digitalio.DigitalInOut(board.D0)
        button_d0.direction = digitalio.Direction.INPUT
        button_d0.pull = digitalio.Pull.UP
        
        # D1 and D2 - normal logic with internal pull-down
        button_d1 = digitalio.DigitalInOut(board.D1)
        button_d1.direction = digitalio.Direction.INPUT
        button_d1.pull = digitalio.Pull.DOWN
        
        button_d2 = digitalio.DigitalInOut(board.D2)
        button_d2.direction = digitalio.Direction.INPUT
        button_d2.pull = digitalio.Pull.DOWN
        
        print("✅ Buttons initialized!")
        print("   D0 (Boot): Mode switcher")
        print("   D1: Action/Confirm")
        print("   D2: Action/Cancel")
        
    except Exception as e:
        print(f"❌ Button setup error: {e}")

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
        print(f"❌ WiFi failed: {e}")
        wifi_connected = False

def read_buttons():
    """Read button states with debouncing"""
    global button_states, button_timers
    
    current_time = time.monotonic_ns() // 1_000_000  # Convert to milliseconds
    buttons_pressed = []
    
    if button_d0 and button_d1 and button_d2:
        # Read current states
        d0_pressed = not button_d0.value  # Inverted logic for boot button
        d1_pressed = button_d1.value      # Normal logic
        d2_pressed = button_d2.value      # Normal logic
        
        # Check each button with debouncing
        for btn_name, pressed, last_state in [
            ("d0", d0_pressed, button_states["d0"]),
            ("d1", d1_pressed, button_states["d1"]),
            ("d2", d2_pressed, button_states["d2"])
        ]:
            if pressed != last_state:
                button_timers[btn_name] = current_time
            
            if (current_time - button_timers[btn_name]) > DEBOUNCE_DELAY:
                if pressed and not last_state:  # Button just pressed
                    buttons_pressed.append(btn_name)
                button_states[btn_name] = pressed
    
    return buttons_pressed

def fetch_uroboro_stats():
    """Fetch real uroboro statistics from PostHog"""
    global uroboro_stats, last_fetch_time
    
    current_time = time.monotonic()
    
    # Rate limiting
    if current_time - last_fetch_time < fetch_interval:
        return
    
    if not wifi_connected or not requests_session:
        uroboro_stats["data_source"] = "WiFi: Offline"
        return
    
    print("📊 Fetching uroboro stats...")
    uroboro_stats["data_source"] = "PostHog: Querying..."
    
    try:
        query_payload = {
            "query": {
                "kind": "HogQLQuery",
                "query": """
                    SELECT event, COUNT() as count
                    FROM events 
                    WHERE event IN ('uroboro_capture', 'uroboro_publish', 'uroboro_status')
                    AND timestamp >= now() - interval 24 hour
                    GROUP BY event
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
            parse_posthog_data(data)
            uroboro_stats["data_source"] = "PostHog: Live ✅"
        else:
            uroboro_stats["data_source"] = f"PostHog: Error {response.status_code}"
            fallback_stats()
        
        response.close()
        
    except Exception as e:
        print(f"❌ PostHog error: {e}")
        uroboro_stats["data_source"] = "PostHog: Connection Error"
        fallback_stats()
    
    uroboro_stats["last_fetch"] = format_time(current_time)
    last_fetch_time = current_time

def parse_posthog_data(data):
    """Parse PostHog response"""
    results = data.get("results", [])
    
    # Reset counts
    uroboro_stats["captures_today"] = 0
    uroboro_stats["publishes_today"] = 0
    uroboro_stats["status_checks_today"] = 0
    
    for row in results:
        if len(row) >= 2:
            event_name, count = row[0], int(row[1])
            
            if event_name == "uroboro_capture":
                uroboro_stats["captures_today"] = count
            elif event_name == "uroboro_publish":
                uroboro_stats["publishes_today"] = count
            elif event_name == "uroboro_status":
                uroboro_stats["status_checks_today"] = count
    
    # Calculate trend
    total = uroboro_stats["captures_today"] + uroboro_stats["publishes_today"]
    if total > 20:
        uroboro_stats["daily_trend"] = "↗ High Productivity"
    elif total > 5:
        uroboro_stats["daily_trend"] = "→ Normal Activity"
    elif total > 0:
        uroboro_stats["daily_trend"] = "↘ Light Usage"
    else:
        uroboro_stats["daily_trend"] = "💤 Quiet Day"

def fallback_stats():
    """Fallback to simulated stats"""
    uroboro_stats["captures_today"] = random.randint(5, 20)
    uroboro_stats["publishes_today"] = random.randint(1, 8)
    uroboro_stats["status_checks_today"] = random.randint(10, 30)
    
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

def draw_mode_stats():
    """Draw uroboro stats dashboard"""
    # Clear screen
    while len(main_group) > 0:
        main_group.pop()
    
    # Header
    title = label.Label(terminalio.FONT, text="🔄 UROBORO LIVE", color=0x00FFFF, x=5, y=10)
    main_group.append(title)
    
    # WiFi status
    wifi_color = 0x00FF00 if wifi_connected else 0xFF0000
    wifi_text = "ONLINE" if wifi_connected else "OFFLINE"
    wifi_status = label.Label(terminalio.FONT, text=f"[{wifi_text}]", color=wifi_color, x=145, y=10)
    main_group.append(wifi_status)
    
    # Data source
    data_source = label.Label(terminalio.FONT, text=uroboro_stats["data_source"], color=0x888888, x=5, y=22)
    main_group.append(data_source)
    
    # Stats
    stats_y = 40
    captures = label.Label(terminalio.FONT, text=f"📝 Captures: {uroboro_stats['captures_today']}", color=0x00FF00, x=5, y=stats_y)
    main_group.append(captures)
    
    publishes = label.Label(terminalio.FONT, text=f"📤 Publishes: {uroboro_stats['publishes_today']}", color=0xFF8800, x=5, y=stats_y + 15)
    main_group.append(publishes)
    
    status_checks = label.Label(terminalio.FONT, text=f"📊 Status: {uroboro_stats['status_checks_today']}", color=0x8888FF, x=5, y=stats_y + 30)
    main_group.append(status_checks)
    
    trend = label.Label(terminalio.FONT, text=f"Trend: {uroboro_stats['daily_trend']}", color=0xFF00FF, x=5, y=stats_y + 50)
    main_group.append(trend)
    
    # Controls
    controls = label.Label(terminalio.FONT, text="D0:Mode D1:Refresh", color=0x666666, x=5, y=120)
    main_group.append(controls)

def init_snake_game():
    """Initialize/reset snake game"""
    global snake_game
    
    snake_game = {
        "snake": [(12, 6), (11, 6), (10, 6)],
        "food": (random.randint(2, 28), random.randint(2, 15)),
        "direction": (1, 0),
        "score": 0,
        "game_over": False,
        "last_move": 0,
        "move_delay": 300
    }

def update_snake_game():
    """Update snake game logic"""
    if snake_game["game_over"]:
        return
    
    current_time = time.monotonic_ns() // 1_000_000
    
    if current_time - snake_game["last_move"] < snake_game["move_delay"]:
        return
    
    # Move snake
    head_x, head_y = snake_game["snake"][0]
    dx, dy = snake_game["direction"]
    new_head = (head_x + dx, head_y + dy)
    
    # Check boundaries
    if (new_head[0] < 1 or new_head[0] > 29 or 
        new_head[1] < 1 or new_head[1] > 16):
        snake_game["game_over"] = True
        return
    
    # Check self collision
    if new_head in snake_game["snake"]:
        snake_game["game_over"] = True
        return
    
    # Add new head
    snake_game["snake"].insert(0, new_head)
    
    # Check food collision
    if new_head == snake_game["food"]:
        snake_game["score"] += 10
        # Generate new food
        while True:
            new_food = (random.randint(2, 28), random.randint(2, 15))
            if new_food not in snake_game["snake"]:
                snake_game["food"] = new_food
                break
        # Increase speed slightly
        snake_game["move_delay"] = max(150, snake_game["move_delay"] - 5)
    else:
        # Remove tail
        snake_game["snake"].pop()
    
    snake_game["last_move"] = current_time

def draw_mode_game():
    """Draw snake game"""
    # Clear screen
    while len(main_group) > 0:
        main_group.pop()
    
    # Create game bitmap (30x17 grid, scaled 8x8 pixels)
    game_bitmap = displayio.Bitmap(240, 136, 4)
    game_palette = displayio.Palette(4)
    game_palette[0] = 0x000000  # Black background
    game_palette[1] = 0x00FF00  # Green snake
    game_palette[2] = 0xFF0000  # Red food
    game_palette[3] = 0x888888  # Gray border
    
    # Draw border
    for x in range(30):
        game_bitmap[x * 8:(x + 1) * 8, 0:8] = [3] * 64
        game_bitmap[x * 8:(x + 1) * 8, 128:136] = [3] * 64
    for y in range(17):
        game_bitmap[0:8, y * 8:(y + 1) * 8] = [3] * 64
        game_bitmap[232:240, y * 8:(y + 1) * 8] = [3] * 64
    
    # Draw snake
    for segment in snake_game["snake"]:
        x, y = segment
        for px in range(8):
            for py in range(8):
                game_bitmap[x * 8 + px, y * 8 + py] = 1
    
    # Draw food
    fx, fy = snake_game["food"]
    for px in range(8):
        for py in range(8):
            game_bitmap[fx * 8 + px, fy * 8 + py] = 2
    
    game_tilegrid = displayio.TileGrid(game_bitmap, pixel_shader=game_palette)
    main_group.append(game_tilegrid)
    
    # Game over overlay
    if snake_game["game_over"]:
        game_over_label = label.Label(terminalio.FONT, text=f"GAME OVER! Score: {snake_game['score']}", 
                                    color=0xFFFFFF, x=30, y=70)
        main_group.append(game_over_label)
        
        restart_label = label.Label(terminalio.FONT, text="D1: Restart  D0: Mode", 
                                  color=0x888888, x=30, y=85)
        main_group.append(restart_label)

def draw_mode_info():
    """Draw device info and settings"""
    # Clear screen
    while len(main_group) > 0:
        main_group.pop()
    
    # Header
    title = label.Label(terminalio.FONT, text="🔧 DEVICE INFO", color=0x00FFFF, x=5, y=10)
    main_group.append(title)
    
    # System info
    info_y = 30
    device_info = label.Label(terminalio.FONT, text="ESP32-S3 TFT Feather", color=0xFFFFFF, x=5, y=info_y)
    main_group.append(device_info)
    
    temp_info = label.Label(terminalio.FONT, text=f"CPU: {microcontroller.cpu.temperature:.1f}C", color=0xFF8800, x=5, y=info_y + 15)
    main_group.append(temp_info)
    
    mem_info = label.Label(terminalio.FONT, text=f"RAM: {gc.mem_free()} bytes", color=0x8888FF, x=5, y=info_y + 30)
    main_group.append(mem_info)
    
    wifi_info = label.Label(terminalio.FONT, text=f"WiFi: {WIFI_SSID}", color=0x00FF00 if wifi_connected else 0xFF0000, x=5, y=info_y + 45)
    main_group.append(wifi_info)
    
    # Version info
    version_info = label.Label(terminalio.FONT, text="DeskHog Multi-Mode v1.0", color=0x888888, x=5, y=info_y + 65)
    main_group.append(version_info)
    
    # Controls
    controls = label.Label(terminalio.FONT, text="D0: Next Mode", color=0x666666, x=5, y=120)
    main_group.append(controls)

def update_current_mode():
    """Update the current mode display"""
    if current_mode == MODE_STATS:
        fetch_uroboro_stats()
        draw_mode_stats()
    elif current_mode == MODE_GAME:
        update_snake_game()
        draw_mode_game()
    elif current_mode == MODE_INFO:
        draw_mode_info()

def handle_button_press(button):
    """Handle button press based on current mode"""
    global current_mode
    
    if button == "d0":  # Mode switch button
        current_mode = (current_mode + 1) % MODE_COUNT
        print(f"🎮 Switched to mode {current_mode}")
        
        if current_mode == MODE_GAME:
            init_snake_game()
    
    elif current_mode == MODE_STATS:
        if button == "d1":  # Refresh stats
            global last_fetch_time
            last_fetch_time = 0  # Force refresh
            print("🔄 Force refreshing stats...")
    
    elif current_mode == MODE_GAME:
        if snake_game["game_over"]:
            if button == "d1":  # Restart game
                init_snake_game()
                print("🎮 Game restarted!")
        else:
            # Game controls
            if button == "d1":  # Change direction (rotate clockwise)
                dx, dy = snake_game["direction"]
                if dx == 1 and dy == 0:     # Right -> Down
                    snake_game["direction"] = (0, 1)
                elif dx == 0 and dy == 1:   # Down -> Left
                    snake_game["direction"] = (-1, 0)
                elif dx == -1 and dy == 0:  # Left -> Up
                    snake_game["direction"] = (0, -1)
                elif dx == 0 and dy == -1:  # Up -> Right
                    snake_game["direction"] = (1, 0)
            
            elif button == "d2":  # Change direction (rotate counter-clockwise)
                dx, dy = snake_game["direction"]
                if dx == 1 and dy == 0:     # Right -> Up
                    snake_game["direction"] = (0, -1)
                elif dx == 0 and dy == -1:  # Up -> Left
                    snake_game["direction"] = (-1, 0)
                elif dx == -1 and dy == 0:  # Left -> Down
                    snake_game["direction"] = (0, 1)
                elif dx == 0 and dy == 1:   # Down -> Right
                    snake_game["direction"] = (1, 0)

def main():
    """Main application loop"""
    print("🎮 Starting DeskHog Multi-Mode Device")
    print("🔄 Mode 0: Uroboro Stats Dashboard")
    print("🐍 Mode 1: Snake Game") 
    print("🔧 Mode 2: Device Info")
    print("=" * 45)
    
    # Initialize everything
    setup_display()
    setup_buttons()
    setup_wifi()
    
    # Initialize snake game
    init_snake_game()
    
    # Initial display
    update_current_mode()
    
    loop_count = 0
    
    while True:
        try:
            # Read button presses
            pressed_buttons = read_buttons()
            for button in pressed_buttons:
                handle_button_press(button)
            
            # Update current mode
            update_current_mode()
            
            # Maintenance
            if loop_count % 300 == 0:  # Every 5 minutes
                gc.collect()
                print(f"💾 Memory: {gc.mem_free()} bytes, Mode: {current_mode}")
            
            loop_count += 1
            time.sleep(0.1)  # 10 FPS
            
        except KeyboardInterrupt:
            print("\n🎮 DeskHog Multi-Mode stopped")
            break
            
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()