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
#include "../secrets.h"

// Display dimensions - LANDSCAPE orientation (240x135)
#define SCREEN_WIDTH 240
#define SCREEN_HEIGHT 135

// Backlight pin
#define TFT_BL 45

// Create display object using hardware SPI
Adafruit_ST7789 tft = Adafruit_ST7789(TFT_CS, TFT_DC, TFT_RST);

// WiFi credentials (from secrets.h)
const char* wifi_ssid = WIFI_SSID;
const char* wifi_password = WIFI_PASSWORD;

// PostHog configuration (from secrets.h)
const char* posthog_host = POSTHOG_HOST;
const char* posthog_project_id = POSTHOG_PROJECT_ID;
const char* posthog_api_key = POSTHOG_PERSONAL_API_KEY;

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

// Colors (matching Python implementation)
#define COLOR_BG       0x0000     // Black
#define COLOR_PRIMARY  0x00FFFF   // Cyan (like Python version)
#define COLOR_TEXT     0xFFFF     // White  
#define COLOR_ERROR    0xF800     // Red
#define COLOR_SUCCESS  0x07E0     // Green
#define COLOR_ORANGE   0xFD20     // Orange (16-bit RGB565)
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
    
    // Initialize display for LANDSCAPE (240x135)
    Serial.println("🔧 Initializing TFT display (240x135 landscape)...");
    tft.init(SCREEN_WIDTH, SCREEN_HEIGHT);
    tft.setRotation(3);  // Landscape orientation (270 degrees)
    
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
            // Demo mode fallback with realistic data
            stats.captures_today = random(5, 25);
            stats.publishes_today = random(1, 8);
            stats.status_checks = random(10, 40);
            
            // Calculate realistic trend
            int total = stats.captures_today + stats.publishes_today;
            if (total > 15) {
                stats.trend = "↗ Demo High";
            } else if (total > 5) {
                stats.trend = "→ Demo Normal";
            } else {
                stats.trend = "↘ Demo Low";
            }
            
            stats.last_update = String(millis() / 1000) + "s ago";
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
    
    // PostHog HogQL query for uroboro events (based on Python implementation)
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
        DeserializationError error = deserializeJson(doc, response);
        
        if (error) {
            Serial.printf("❌ JSON parsing failed: %s\n", error.c_str());
            http.end();
            return;
        }
        
        // Reset stats
        stats.captures_today = 0;
        stats.publishes_today = 0;
        stats.status_checks = 0;
        
        // Parse results (matching Python implementation logic)
        JsonArray results = doc["results"];
        for (JsonArray row : results) {
            if (row.size() >= 2) {
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
        }
        
        // Calculate trend (matching Python logic)
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
        stats.last_update = "API Auth Failed";
    } else if (httpResponseCode == 403) {
        Serial.println("❌ PostHog API: Forbidden (check permissions)");
        stats.trend = "Permission Error";
        stats.last_update = "API Forbidden";
    } else {
        Serial.printf("❌ PostHog API error: %d\n", httpResponseCode);
        stats.trend = "API Error";
        stats.last_update = "API Failed";
    }
    
    http.end();
}

void updateDisplay() {
    drawConnectionStatus();
    drawUroboroStats();
    
    Serial.printf("🖥️ Display updated - Captures: %d, Publishes: %d, Status: %d\n",
                 stats.captures_today, stats.publishes_today, stats.status_checks);
}