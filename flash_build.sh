#!/bin/bash

# ESP32 Build Selection and Flash Script
# =====================================
# Choose from different ESP32 firmware builds for testing
# Author: QRY

set -e

echo "🔄 ESP32 Build Selection & Flash Tool"
echo "====================================="

# Build options configuration
declare -A BUILDS=(
    ["demo"]="Current demo mode with simulated stats"
    ["posthog"]="Real PostHog integration with landscape display"
    ["simple"]="Basic display test"
    ["debug"]="Debug version with serial output"
    ["uroboro_real"]="Uroboro Stats with Real PostHog Data (CircuitPython)"
    ["uroboro_optimized"]="Uroboro Stats Optimized Version (CircuitPython)"
    ["uroboro_basic"]="Basic Uroboro Stats Meter (CircuitPython)"
)

declare -A BUILD_FILES=(
    ["demo"]="src/main.cpp"
    ["posthog"]="src/main_posthog.cpp"
    ["simple"]="src/main_simple.cpp"
    ["debug"]="src/main_debug.cpp"
    ["uroboro_real"]="uroboro_stats_meter_real.py"
    ["uroboro_optimized"]="uroboro_stats_meter_optimized.py"
    ["uroboro_basic"]="uroboro_stats_meter.py"
)

# Check if ESP32 is connected
check_device() {
    echo "🔍 Checking for ESP32 device..."

    if [ -e "/dev/ttyACM0" ]; then
        echo "✅ ESP32-S3 found on /dev/ttyACM0"
        return 0
    elif [ -e "/dev/ttyUSB0" ]; then
        echo "✅ ESP32 found on /dev/ttyUSB0"
        return 0
    else
        echo "❌ No ESP32 device found"
        echo "   Make sure your ESP32 is connected via USB"
        return 1
    fi
}

# Display available builds
show_builds() {
    echo ""
    echo "📦 Available builds:"
    echo ""

    local i=1
    for build in "${!BUILDS[@]}"; do
        echo "  $i) $build - ${BUILDS[$build]}"
        ((i++))
    done

    echo ""
}

# Select build
select_build() {
    local build_array=($(printf '%s\n' "${!BUILDS[@]}" | sort))

    while true; do
        echo "Select build (1-${#build_array[@]}) or 'q' to quit: "
        read -r choice

        if [[ "$choice" == "q" ]]; then
            echo "👋 Exiting..."
            exit 0
        fi

        if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le "${#build_array[@]}" ]; then
            selected_build="${build_array[$((choice-1))]}"
            echo ""
            echo "✅ Selected: $selected_build - ${BUILDS[$selected_build]}"
            return 0
        else
            echo "❌ Invalid selection. Please try again."
        fi
    done
}

# Setup source file for build
setup_build() {
    local build="$1"
    local source_file="${BUILD_FILES[$build]}"

    echo "🔧 Setting up build: $build"

    # Check if this is a CircuitPython build
    if [[ "$source_file" == *.py ]]; then
        setup_circuitpython_build "$build" "$source_file"
        return 0
    fi

    # Handle C++ builds
    if [ ! -f "$source_file" ]; then
        echo "❌ Source file not found: $source_file"

        if [ "$build" == "posthog" ]; then
            echo "🔄 Creating PostHog integration file..."
            create_posthog_build
        else
            echo "   Creating from template..."
            create_build_template "$build"
        fi
    fi

    # Copy to main.cpp for compilation
    if [ "$source_file" != "src/main.cpp" ]; then
        echo "📝 Copying $source_file to src/main.cpp"
        cp "$source_file" src/main.cpp
    fi

    echo "✅ Build ready: $build"
}

# Setup CircuitPython build
setup_circuitpython_build() {
    local build="$1"
    local source_file="$2"

    echo "🐍 Setting up CircuitPython build: $build"

    # Check if source file exists
    if [ ! -f "$source_file" ]; then
        echo "❌ CircuitPython file not found: $source_file"
        return 1
    fi

    echo "📋 CircuitPython builds require:"
    echo "   1. CircuitPython firmware flashed to ESP32"
    echo "   2. Copy Python file to CIRCUITPY drive"
    echo "   3. Required libraries in /lib folder"
    echo ""
    echo "🔄 Would you like to:"
    echo "   1) Flash CircuitPython firmware first"
    echo "   2) Copy Python file to existing CircuitPython setup"
    echo "   3) Skip (manual setup)"
    echo ""
    read -p "Choice (1/2/3): " cp_choice

    case $cp_choice in
        1)
            flash_circuitpython_firmware
            ;;
        2)
            copy_to_circuitpython "$source_file"
            ;;
        3)
            echo "📝 Manual setup required:"
            echo "   cp $source_file /media/*/CIRCUITPY/code.py"
            ;;
        *)
            echo "❌ Invalid choice"
            return 1
            ;;
    esac

    echo "✅ CircuitPython build ready: $build"
}

# Flash CircuitPython firmware
flash_circuitpython_firmware() {
    echo "🔄 Flashing CircuitPython firmware..."

    if [ -f "firmware.uf2" ]; then
        echo "📦 Using firmware.uf2"

        echo "🔄 Put ESP32 in bootloader mode:"
        echo "   1. Hold BOOT button"
        echo "   2. Press and release RESET button"
        echo "   3. Release BOOT button"
        echo "   4. ESP32S3 drive should appear"
        echo ""
        read -p "Press Enter when ESP32S3 drive is visible..."

        # Find the ESP32S3 drive
        for mount_point in /media/*/ESP32S3 /mnt/ESP32S3 /Volumes/ESP32S3; do
            if [ -d "$mount_point" ]; then
                echo "📋 Copying firmware to $mount_point"
                cp firmware.uf2 "$mount_point/"
                echo "✅ CircuitPython firmware flashed!"
                sleep 3
                return 0
            fi
        done

        echo "❌ ESP32S3 drive not found. Please flash manually:"
        echo "   cp firmware.uf2 /path/to/ESP32S3/"
    else
        echo "❌ firmware.uf2 not found"
        echo "   Download from: https://circuitpython.org/board/adafruit_feather_esp32s3_reverse_tft/"
    fi
}

# Copy to CircuitPython device
copy_to_circuitpython() {
    local source_file="$1"

    echo "🔄 Copying $source_file to CircuitPython device..."

    # Find CIRCUITPY drive
    for mount_point in /media/*/CIRCUITPY /mnt/CIRCUITPY /Volumes/CIRCUITPY; do
        if [ -d "$mount_point" ]; then
            echo "📋 Found CircuitPython at $mount_point"

            # Copy main file
            cp "$source_file" "$mount_point/code.py"
            echo "✅ Copied $source_file to code.py"

            # Copy secrets template if needed
            if [ -f "secrets_template.py" ] && [ ! -f "$mount_point/secrets.py" ]; then
                cp secrets_template.py "$mount_point/secrets.py"
                echo "📝 Copied secrets template - please configure WiFi credentials"
            fi

            # Check for required libraries
            echo "📚 Checking required libraries..."
            if [ ! -d "$mount_point/lib" ]; then
                echo "⚠️  /lib directory not found - please install required libraries"
                echo "   Download bundle: https://circuitpython.org/libraries"
            fi

            sync
            echo "✅ Files copied successfully!"
            return 0
        fi
    done

    echo "❌ CIRCUITPY drive not found"
    echo "   Make sure CircuitPython is installed and device is connected"
}

# Create PostHog build from Python implementation
create_posthog_build() {
    echo "🔄 Converting Python PostHog implementation to C++..."

    cat > src/main_posthog.cpp << 'EOF'
/**
 * Uroboro Dashboard with Real PostHog Integration
 * ESP32-S3 TFT Feather - Landscape orientation with live data
 * Converted from Python implementation for real stats display
 */

#include <Arduino.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7789.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// Display dimensions - LANDSCAPE orientation (240x135)
#define SCREEN_WIDTH 240
#define SCREEN_HEIGHT 135

// Backlight pin
#define TFT_BL 45

// Create display object using hardware SPI
Adafruit_ST7789 tft = Adafruit_ST7789(TFT_CS, TFT_DC, TFT_RST);

// WiFi credentials (configure these)
const char* wifi_ssid = "your_network";
const char* wifi_password = "your_password";

// PostHog configuration (configure these)
const char* posthog_host = "https://eu.posthog.com";
const char* posthog_project_id = "71732";
const char* posthog_api_key = "your_personal_api_key_here";

// Function declarations
void drawHeader();
void drawUroboroStats();
void fetchPostHogData();
void drawConnectionStatus();
void updateDisplay();

// Uroboro stats structure
struct UroboroStats {
    int captures_today = 0;
    int publishes_today = 0;
    int status_checks = 0;
    String last_update = "Never";
    String trend = "Starting...";
    bool is_connected = false;
    bool data_loaded = false;
    unsigned long last_fetch = 0;
} stats;

// Colors
#define COLOR_BG       0x0000     // Black
#define COLOR_PRIMARY  0x00FFFF   // Cyan (like Python version)
#define COLOR_TEXT     0xFFFF     // White
#define COLOR_ERROR    0xF800     // Red
#define COLOR_SUCCESS  0x07E0     // Green
#define COLOR_ORANGE   0xFF8000   // Orange
#define COLOR_BLUE     0x001F     // Blue
#define COLOR_MAGENTA  0xF81F     // Magenta
#define COLOR_GRAY     0x8410     // Gray

void setup() {
    Serial.begin(115200);
    delay(1000);

    Serial.println("=================================");
    Serial.println("🔄 UROBORO LIVE - PostHog Integration");
    Serial.println("Landscape Display with Real Data");
    Serial.println("=================================");

    // Initialize display for LANDSCAPE
    Serial.println("🔧 Initializing TFT display (240x135 landscape)...");
    tft.init(SCREEN_WIDTH, SCREEN_HEIGHT);
    tft.setRotation(3);  // Landscape orientation

    // Turn on backlight
    pinMode(TFT_BL, OUTPUT);
    digitalWrite(TFT_BL, HIGH);

    // Clear screen with black background
    tft.fillScreen(COLOR_BG);

    // Draw initial UI
    drawHeader();
    drawConnectionStatus();

    Serial.println("✅ Display initialized in landscape mode!");

    // Connect to WiFi
    Serial.printf("🔗 Connecting to WiFi: %s\n", wifi_ssid);
    WiFi.begin(wifi_ssid, wifi_password);

    int wifi_attempts = 0;
    while (WiFi.status() != WL_CONNECTED && wifi_attempts < 20) {
        delay(500);
        Serial.print(".");
        wifi_attempts++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.printf("\n✅ WiFi connected: %s\n", WiFi.localIP().toString().c_str());
        stats.is_connected = true;
    } else {
        Serial.println("\n❌ WiFi connection failed - using demo mode");
        stats.is_connected = false;
    }

    // Initial display update
    updateDisplay();

    Serial.println("🔄 Starting real-time PostHog data loop...");
}

void loop() {
    // Fetch PostHog data every 5 minutes
    if (millis() - stats.last_fetch > 300000 || stats.last_fetch == 0) {
        if (stats.is_connected) {
            fetchPostHogData();
        } else {
            // Demo mode fallback
            stats.captures_today = random(5, 25);
            stats.publishes_today = random(1, 8);
            stats.status_checks = random(10, 40);
            stats.trend = "Demo Mode";
            stats.last_update = "Simulated";
        }

        updateDisplay();
        stats.last_fetch = millis();
    }

    // Check WiFi connection periodically
    if (millis() % 30000 == 0) {  // Every 30 seconds
        bool was_connected = stats.is_connected;
        stats.is_connected = (WiFi.status() == WL_CONNECTED);

        if (was_connected != stats.is_connected) {
            drawConnectionStatus();
        }
    }

    delay(1000);  // 1 second update cycle
}

void drawHeader() {
    // Header background bar
    tft.fillRect(0, 0, SCREEN_WIDTH, 25, COLOR_PRIMARY);

    // Title
    tft.setTextColor(COLOR_BG);
    tft.setTextSize(1);
    tft.setCursor(5, 5);
    tft.print("🔄 UROBORO LIVE");

    // Version info
    tft.setCursor(5, 15);
    tft.print("PostHog Integration");
}

void drawConnectionStatus() {
    // Connection status area (top right)
    tft.fillRect(160, 0, 80, 25, COLOR_PRIMARY);

    tft.setTextColor(COLOR_BG);
    tft.setTextSize(1);
    tft.setCursor(165, 8);

    if (stats.is_connected) {
        tft.print("[ONLINE]");
    } else {
        tft.print("[OFFLINE]");
    }
}

void drawUroboroStats() {
    // Clear stats area
    tft.fillRect(0, 30, SCREEN_WIDTH, SCREEN_HEIGHT - 30, COLOR_BG);

    // Data source indicator
    tft.setTextColor(COLOR_GRAY);
    tft.setTextSize(1);
    tft.setCursor(5, 35);
    if (stats.is_connected && stats.data_loaded) {
        tft.print("PostHog: Live Data ✅");
    } else if (stats.is_connected) {
        tft.print("PostHog: Connecting...");
    } else {
        tft.print("Demo Mode (No WiFi)");
    }

    // Today's stats header
    tft.setTextColor(COLOR_TEXT);
    tft.setTextSize(1);
    tft.setCursor(5, 50);
    tft.print("TODAY:");

    // Stats in landscape layout (side by side)
    int col1_x = 5;
    int col2_x = 120;
    int stats_y = 65;
    int line_height = 18;

    // Column 1
    tft.setTextColor(COLOR_SUCCESS);
    tft.setCursor(col1_x, stats_y);
    tft.printf("📝 Captures: %d", stats.captures_today);

    tft.setTextColor(COLOR_ORANGE);
    tft.setCursor(col1_x, stats_y + line_height);
    tft.printf("📤 Publishes: %d", stats.publishes_today);

    // Column 2
    tft.setTextColor(COLOR_BLUE);
    tft.setCursor(col2_x, stats_y);
    tft.printf("📊 Status: %d", stats.status_checks);

    tft.setTextColor(COLOR_MAGENTA);
    tft.setCursor(col2_x, stats_y + line_height);
    tft.printf("Trend: %s", stats.trend.c_str());

    // Last update (bottom)
    tft.setTextColor(COLOR_GRAY);
    tft.setCursor(5, SCREEN_HEIGHT - 15);
    tft.printf("Updated: %s", stats.last_update.c_str());
}

void fetchPostHogData() {
    if (!stats.is_connected) {
        Serial.println("❌ Cannot fetch: WiFi not connected");
        return;
    }

    Serial.println("🔗 Querying PostHog for real uroboro data...");

    HTTPClient http;
    String url = String(posthog_host) + "/api/projects/" + String(posthog_project_id) + "/query/";

    http.begin(url);
    http.addHeader("Authorization", "Bearer " + String(posthog_api_key));
    http.addHeader("Content-Type", "application/json");

    // PostHog HogQL query for uroboro events
    String payload = R"({
        "query": {
            "kind": "HogQLQuery",
            "query": "SELECT event, COUNT() as count FROM events WHERE event IN ('uroboro_capture', 'uroboro_publish', 'uroboro_status') AND timestamp >= now() - interval 24 hour GROUP BY event ORDER BY count DESC"
        }
    })";

    int httpResponseCode = http.POST(payload);

    if (httpResponseCode == 200) {
        String response = http.getString();
        Serial.println("✅ PostHog response received");

        // Parse JSON response
        DynamicJsonDocument doc(2048);
        deserializeJson(doc, response);

        // Reset stats
        stats.captures_today = 0;
        stats.publishes_today = 0;
        stats.status_checks = 0;

        // Parse results
        JsonArray results = doc["results"];
        for (JsonArray row : results) {
            String event = row[0];
            int count = row[1];

            Serial.printf("   %s: %d\n", event.c_str(), count);

            if (event == "uroboro_capture") {
                stats.captures_today = count;
            } else if (event == "uroboro_publish") {
                stats.publishes_today = count;
            } else if (event == "uroboro_status") {
                stats.status_checks = count;
            }
        }

        // Calculate trend
        int total_activity = stats.captures_today + stats.publishes_today;
        if (total_activity > 20) {
            stats.trend = "↗ High Productivity";
        } else if (total_activity > 5) {
            stats.trend = "→ Normal Activity";
        } else if (total_activity > 0) {
            stats.trend = "↘ Light Usage";
        } else {
            stats.trend = "💤 Quiet Day";
        }

        stats.data_loaded = true;
        stats.last_update = String(millis() / 1000) + "s ago";

        Serial.printf("✅ Real data loaded: %d captures, %d publishes\n",
                     stats.captures_today, stats.publishes_today);

    } else if (httpResponseCode == 401) {
        Serial.println("❌ PostHog API: Unauthorized (check API key)");
        stats.trend = "Auth Error";
    } else {
        Serial.printf("❌ PostHog API error: %d\n", httpResponseCode);
        stats.trend = "API Error";
    }

    http.end();
}

void updateDisplay() {
    drawConnectionStatus();
    drawUroboroStats();

    Serial.printf("🖥️ Display updated - Captures: %d, Publishes: %d, Status: %d\n",
                 stats.captures_today, stats.publishes_today, stats.status_checks);
}
EOF

    echo "✅ PostHog C++ implementation created"
}

# Create simple build template
create_build_template() {
    local build="$1"
    local file="${BUILD_FILES[$build]}"

    echo "📝 Creating template for build: $build"

    case "$build" in
        "simple")
            cat > "$file" << 'EOF'
// Simple ESP32 TFT Display Test
#include <Arduino.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7789.h>

#define SCREEN_WIDTH 135
#define SCREEN_HEIGHT 240
#define TFT_BL 45

Adafruit_ST7789 tft = Adafruit_ST7789(TFT_CS, TFT_DC, TFT_RST);

void setup() {
    Serial.begin(115200);

    // Initialize display
    tft.init(SCREEN_WIDTH, SCREEN_HEIGHT);
    tft.setRotation(0);  // Portrait

    pinMode(TFT_BL, OUTPUT);
    digitalWrite(TFT_BL, HIGH);

    tft.fillScreen(0x0000);
    tft.setTextColor(0x07E0);
    tft.setTextSize(2);
    tft.setCursor(10, 50);
    tft.print("ESP32");
    tft.setCursor(10, 80);
    tft.print("Simple");
    tft.setCursor(10, 110);
    tft.print("Test");

    Serial.println("Simple display test ready");
}

void loop() {
    delay(1000);
}
EOF
            ;;
        "debug")
            cat > "$file" << 'EOF'
// Debug ESP32 Build with Serial Output
#include <Arduino.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7789.h>

#define SCREEN_WIDTH 135
#define SCREEN_HEIGHT 240
#define TFT_BL 45

Adafruit_ST7789 tft = Adafruit_ST7789(TFT_CS, TFT_DC, TFT_RST);

void setup() {
    Serial.begin(115200);
    delay(2000);

    Serial.println("=== ESP32 Debug Build ===");
    Serial.println("Starting initialization...");

    // Initialize display
    Serial.println("Initializing display...");
    tft.init(SCREEN_WIDTH, SCREEN_HEIGHT);
    tft.setRotation(0);

    pinMode(TFT_BL, OUTPUT);
    digitalWrite(TFT_BL, HIGH);
    Serial.println("Backlight enabled");

    tft.fillScreen(0x0000);
    tft.setTextColor(0xFFFF);
    tft.setTextSize(1);
    tft.setCursor(5, 10);
    tft.print("DEBUG MODE");

    Serial.println("Setup complete");
}

void loop() {
    static int counter = 0;

    Serial.printf("Loop %d - Free heap: %d bytes\n", counter, ESP.getFreeHeap());

    tft.fillRect(5, 30, 120, 20, 0x0000);
    tft.setCursor(5, 30);
    tft.printf("Count: %d", counter);

    counter++;
    delay(2000);
}
EOF
            ;;
    esac

    echo "✅ Template created: $file"
}

# Flash the firmware
flash_firmware() {
    echo ""
    echo "🔥 Flashing firmware to ESP32..."
    echo "This may take a moment..."
    echo ""

    if command -v pio &> /dev/null; then
        echo "📦 Using PlatformIO to build and upload..."
        pio run --target upload
    else
        echo "❌ PlatformIO not found!"
        echo "   Please install PlatformIO: pip install platformio"
        exit 1
    fi
}

# Monitor serial output
monitor_serial() {
    echo ""
    echo "🔍 Would you like to monitor serial output? (y/n): "
    read -r monitor_choice

    if [[ "$monitor_choice" == "y" ]] || [[ "$monitor_choice" == "Y" ]]; then
        echo "📡 Starting serial monitor (Ctrl+C to exit)..."
        sleep 2
        pio device monitor
    fi
}

# Main execution
main() {
    if ! check_device; then
        exit 1
    fi

    show_builds
    select_build
    setup_build "$selected_build"

    echo ""
    echo "🔥 Ready to flash '$selected_build' to ESP32"
    echo "Continue? (y/n): "
    read -r flash_choice

    if [[ "$flash_choice" == "y" ]] || [[ "$flash_choice" == "Y" ]]; then
        flash_firmware

        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ Firmware flashed successfully!"
            echo "🔄 Your ESP32 should now be running: $selected_build"
            monitor_serial
        else
            echo "❌ Flash failed!"
            exit 1
        fi
    else
        echo "👋 Flash cancelled"
    fi
}

# Run main function
main "$@"
