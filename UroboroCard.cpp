/**
 * @file UroboroCard.cpp
 * @brief Implementation of the Uroboro productivity stats card
 * 
 * Provides real-time display of uroboro productivity metrics within
 * the DeskHog ecosystem. Demonstrates proper integration with PostHog
 * API and DeskHog's card-based UI architecture.
 * 
 * @author QRY
 * @date June 19, 2025
 */

#include "UroboroCard.h"
#include "Style.h"
#include <ArduinoJson.h>
#include <WiFi.h>

UroboroCard::UroboroCard(
    lv_obj_t* parent, 
    ConfigManager& config, 
    EventQueue& eventQueue,
    PostHogClient& posthogClient
) : _config(config), 
    _event_queue(eventQueue), 
    _posthog_client(posthogClient),
    _card_root(nullptr) {
    
    Serial.println("🔄 Creating UroboroCard...");
    
    // Create UI
    createUI();
    
    // Subscribe to PostHog response events
    _event_queue.subscribe(EventType::POSTHOG_RESPONSE, 
        [this](const Event& event) {
            this->onPostHogResponse(event);
        }
    );
    
    // Initial data fetch
    fetchUroboroData();
    
    Serial.println("✅ UroboroCard created successfully");
}

UroboroCard::~UroboroCard() {
    if (_card_root) {
        lv_obj_del(_card_root);
        _card_root = nullptr;
    }
}

bool UroboroCard::handleButtonPress(uint8_t button_index) {
    switch (button_index) {
        case 0: // Button 0 - Force refresh
            Serial.println("🔄 Force refreshing uroboro data...");
            _ui_state.last_data_refresh = 0; // Force immediate refresh
            fetchUroboroData();
            return true;
            
        case 1: // Button 1 - Toggle data source info
            // Could toggle between different time periods or views
            return true;
            
        case 2: // Button 2 - Settings or help
            // Could show help or configuration options
            return true;
            
        default:
            return false;
    }
}

void UroboroCard::update() {
    uint32_t current_time = millis();
    
    // Check if we need to fetch new data
    if (current_time - _ui_state.last_data_refresh > REFRESH_INTERVAL_MS) {
        fetchUroboroData();
    }
    
    // Update UI periodically
    if (current_time - _ui_state.last_ui_update > UPDATE_INTERVAL_MS) {
        updateUI();
        _ui_state.last_ui_update = current_time;
    }
}

lv_obj_t* UroboroCard::getCardObject() const {
    return _card_root;
}

void UroboroCard::createUI() {
    // Create main card container
    _card_root = lv_obj_create(nullptr);
    lv_obj_set_size(_card_root, CARD_WIDTH, CARD_HEIGHT);
    lv_obj_set_style_bg_color(_card_root, lv_color_black(), 0);
    lv_obj_set_style_border_width(_card_root, 1, 0);
    lv_obj_set_style_border_color(_card_root, lv_color_hex(0x333333), 0);
    lv_obj_set_style_radius(_card_root, 8, 0);
    lv_obj_set_style_pad_all(_card_root, 8, 0);
    
    // Create title
    _title_label = lv_label_create(_card_root);
    lv_label_set_text(_title_label, "🔄 UROBORO LIVE");
    lv_obj_set_style_text_color(_title_label, lv_color_hex(0x00FFFF), 0);
    lv_obj_set_style_text_font(_title_label, &lv_font_montserrat_14, 0);
    lv_obj_align(_title_label, LV_ALIGN_TOP_LEFT, 0, 0);
    
    // Create WiFi/connection status
    _status_label = lv_label_create(_card_root);
    lv_label_set_text(_status_label, "[CONNECTING]");
    lv_obj_set_style_text_color(_status_label, lv_color_hex(0xFFFF00), 0);
    lv_obj_set_style_text_font(_status_label, &lv_font_montserrat_10, 0);
    lv_obj_align(_status_label, LV_ALIGN_TOP_RIGHT, 0, 0);
    
    // Create data source indicator
    _data_source_label = lv_label_create(_card_root);
    lv_label_set_text(_data_source_label, "PostHog: Connecting...");
    lv_obj_set_style_text_color(_data_source_label, lv_color_hex(0x888888), 0);
    lv_obj_set_style_text_font(_data_source_label, &lv_font_montserrat_10, 0);
    lv_obj_align(_data_source_label, LV_ALIGN_TOP_LEFT, 0, 20);
    
    // Create stats labels
    _captures_label = lv_label_create(_card_root);
    lv_label_set_text(_captures_label, "📝 Captures: --");
    lv_obj_set_style_text_color(_captures_label, lv_color_hex(0x00FF00), 0);
    lv_obj_set_style_text_font(_captures_label, &lv_font_montserrat_12, 0);
    lv_obj_align(_captures_label, LV_ALIGN_TOP_LEFT, 0, 45);
    
    _publishes_label = lv_label_create(_card_root);
    lv_label_set_text(_publishes_label, "📤 Publishes: --");
    lv_obj_set_style_text_color(_publishes_label, lv_color_hex(0xFF8800), 0);
    lv_obj_set_style_text_font(_publishes_label, &lv_font_montserrat_12, 0);
    lv_obj_align(_publishes_label, LV_ALIGN_TOP_LEFT, 0, 65);
    
    _status_checks_label = lv_label_create(_card_root);
    lv_label_set_text(_status_checks_label, "📊 Status: --");
    lv_obj_set_style_text_color(_status_checks_label, lv_color_hex(0x8888FF), 0);
    lv_obj_set_style_text_font(_status_checks_label, &lv_font_montserrat_12, 0);
    lv_obj_align(_status_checks_label, LV_ALIGN_TOP_LEFT, 0, 85);
    
    _trend_label = lv_label_create(_card_root);
    lv_label_set_text(_trend_label, "Trend: --");
    lv_obj_set_style_text_color(_trend_label, lv_color_hex(0xFF00FF), 0);
    lv_obj_set_style_text_font(_trend_label, &lv_font_montserrat_12, 0);
    lv_obj_align(_trend_label, LV_ALIGN_TOP_LEFT, 0, 105);
    
    // Create controls hint
    _controls_label = lv_label_create(_card_root);
    lv_label_set_text(_controls_label, "BTN0:Refresh");
    lv_obj_set_style_text_color(_controls_label, lv_color_hex(0x666666), 0);
    lv_obj_set_style_text_font(_controls_label, &lv_font_montserrat_10, 0);
    lv_obj_align(_controls_label, LV_ALIGN_BOTTOM_LEFT, 0, 0);
    
    Serial.println("✅ UroboroCard UI created");
}

void UroboroCard::fetchUroboroData() {
    uint32_t current_time = millis();
    
    // Rate limiting
    if (current_time - _ui_state.last_data_refresh < REFRESH_INTERVAL_MS) {
        return;
    }
    
    // Check WiFi connection
    if (WiFi.status() != WL_CONNECTED) {
        _current_stats.data_source = "WiFi: Offline";
        generateFallbackData();
        return;
    }
    
    Serial.println("📊 Fetching uroboro stats from PostHog...");
    _current_stats.data_source = "PostHog: Querying...";
    
    // Build HogQL query
    String query = buildHogQLQuery();
    
    // Make async PostHog request
    _posthog_client.makeAsyncRequest("query", query, [this](const String& response) {
        if (parsePostHogResponse(response)) {
            _current_stats.data_source = "PostHog: Live Data ✅";
            _current_stats.is_live_data = true;
            Serial.println("✅ Real PostHog data loaded");
        } else {
            _current_stats.data_source = "PostHog: Parse Error";
            generateFallbackData();
        }
    });
    
    _ui_state.last_data_refresh = current_time;
    _current_stats.last_fetch = formatTime(current_time);
}

String UroboroCard::buildHogQLQuery() const {
    // Build HogQL query for uroboro events in last 24 hours
    return R"({
        "query": {
            "kind": "HogQLQuery",
            "query": "SELECT event, COUNT() as count FROM events WHERE event IN ('uroboro_capture', 'uroboro_publish', 'uroboro_status') AND timestamp >= now() - interval 24 hour GROUP BY event ORDER BY count DESC"
        }
    })";
}

bool UroboroCard::parsePostHogResponse(const String& json_response) {
    StaticJsonDocument<2048> doc;
    DeserializationError error = deserializeJson(doc, json_response);
    
    if (error) {
        Serial.printf("❌ JSON parse error: %s\n", error.c_str());
        return false;
    }
    
    // Reset counts
    _current_stats.captures_today = 0;
    _current_stats.publishes_today = 0;
    _current_stats.status_checks_today = 0;
    
    // Parse results
    JsonArray results = doc["results"];
    if (results) {
        Serial.printf("📊 PostHog returned %d event types\n", results.size());
        
        for (JsonArray row : results) {
            if (row.size() >= 2) {
                String event_name = row[0].as<String>();
                uint32_t count = row[1].as<uint32_t>();
                
                Serial.printf("   %s: %d\n", event_name.c_str(), count);
                
                if (event_name == "uroboro_capture") {
                    _current_stats.captures_today = count;
                } else if (event_name == "uroboro_publish") {
                    _current_stats.publishes_today = count;
                } else if (event_name == "uroboro_status") {
                    _current_stats.status_checks_today = count;
                }
            }
        }
    }
    
    // Calculate trend
    _current_stats.daily_trend = calculateTrend();
    
    return true;
}

void UroboroCard::generateFallbackData() {
    Serial.println("📊 Using fallback simulated data");
    
    // Generate realistic fallback data based on time of day
    uint32_t current_hour = (millis() / 3600000) % 24;
    
    if (current_hour >= 9 && current_hour <= 17) { // Work hours
        _current_stats.captures_today = random(10, 25);
        _current_stats.publishes_today = random(3, 8);
        _current_stats.status_checks_today = random(15, 30);
    } else { // Off hours
        _current_stats.captures_today = random(0, 5);
        _current_stats.publishes_today = random(0, 2);
        _current_stats.status_checks_today = random(2, 8);
    }
    
    _current_stats.daily_trend = calculateTrend();
    _current_stats.is_live_data = false;
    _current_stats.data_source = "Simulated Data";
}

String UroboroCard::calculateTrend() const {
    uint32_t total_activity = _current_stats.captures_today + _current_stats.publishes_today;
    
    if (total_activity > 20) {
        return "↗ High Productivity";
    } else if (total_activity > 5) {
        return "→ Normal Activity";
    } else if (total_activity > 0) {
        return "↘ Light Usage";
    } else {
        return "💤 Quiet Day";
    }
}

void UroboroCard::updateUI() {
    bool updated = false;
    
    // Update WiFi status
    lv_color_t wifi_color = (WiFi.status() == WL_CONNECTED) ? lv_color_hex(0x00FF00) : lv_color_hex(0xFF0000);
    String wifi_text = (WiFi.status() == WL_CONNECTED) ? "[ONLINE]" : "[OFFLINE]";
    if (updateLabel(_status_label, wifi_text, wifi_color)) {
        updated = true;
    }
    
    // Update data source
    if (updateLabel(_data_source_label, _current_stats.data_source)) {
        updated = true;
    }
    
    // Update stats only if changed
    if (_current_stats.captures_today != _ui_state.prev_stats.captures_today) {
        String captures_text = "📝 Captures: " + String(_current_stats.captures_today);
        updateLabel(_captures_label, captures_text);
        updated = true;
    }
    
    if (_current_stats.publishes_today != _ui_state.prev_stats.publishes_today) {
        String publishes_text = "📤 Publishes: " + String(_current_stats.publishes_today);
        updateLabel(_publishes_label, publishes_text);
        updated = true;
    }
    
    if (_current_stats.status_checks_today != _ui_state.prev_stats.status_checks_today) {
        String status_text = "📊 Status: " + String(_current_stats.status_checks_today);
        updateLabel(_status_checks_label, status_text);
        updated = true;
    }
    
    if (_current_stats.daily_trend != _ui_state.prev_stats.daily_trend) {
        String trend_text = "Trend: " + _current_stats.daily_trend;
        updateLabel(_trend_label, trend_text);
        updated = true;
    }
    
    // Update previous stats
    _ui_state.prev_stats = _current_stats;
    
    if (updated) {
        Serial.println("🖥️ UI updated with new data");
    }
}

bool UroboroCard::updateLabel(lv_obj_t* label, const String& new_text, lv_color_t color) {
    if (!label) return false;
    
    const char* current_text = lv_label_get_text(label);
    if (new_text != String(current_text)) {
        lv_label_set_text(label, new_text.c_str());
        if (color.full != lv_color_white().full) {
            lv_obj_set_style_text_color(label, color, 0);
        }
        return true;
    }
    return false;
}

String UroboroCard::formatTime(uint32_t timestamp_ms) const {
    uint32_t seconds = timestamp_ms / 1000;
    uint32_t minutes = (seconds / 60) % 60;
    uint32_t hours = (seconds / 3600) % 24;
    
    char time_buffer[10];
    snprintf(time_buffer, sizeof(time_buffer), "%02d:%02d", hours, minutes);
    return String(time_buffer);
}

void UroboroCard::onPostHogResponse(const Event& event) {
    // Handle async PostHog responses
    if (event.data.indexOf("uroboro") >= 0) {
        parsePostHogResponse(event.data);
    }
}