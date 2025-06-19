/**
 * @file UroboroCard.h
 * @brief Uroboro productivity stats card for DeskHog
 * 
 * A DeskHog card that displays real-time uroboro productivity metrics
 * fetched from PostHog analytics. Integrates seamlessly with the existing
 * card-based UI architecture.
 * 
 * Features:
 * - Real-time uroboro usage statistics (captures, publishes, status checks)
 * - PostHog API integration for live data
 * - Graceful fallback to simulation when offline
 * - Productivity trend analysis
 * - Follows DeskHog UI patterns and standards
 * 
 * @author QRY
 * @date June 19, 2025
 * @note Contribution to DeskHog gaming/productivity library
 */

#ifndef UROBORO_CARD_H
#define UROBORO_CARD_H

#include "lvgl.h"
#include "ui/InputHandler.h"
#include "ConfigManager.h"
#include "EventQueue.h"
#include "posthog/PostHogClient.h"
#include <Arduino.h>
#include <memory>

/**
 * @class UroboroCard
 * @brief Card displaying uroboro productivity statistics
 * 
 * Integrates with PostHog to fetch real uroboro usage data and display
 * it in a beautiful, real-time dashboard format. Shows captures, publishes,
 * status checks, and productivity trends.
 */
class UroboroCard : public InputHandler {
public:
    /**
     * @brief Constructor
     * 
     * @param parent LVGL parent object
     * @param config Configuration manager for settings persistence
     * @param eventQueue Event queue for async updates
     * @param posthogClient PostHog client for API calls
     */
    UroboroCard(
        lv_obj_t* parent, 
        ConfigManager& config, 
        EventQueue& eventQueue,
        PostHogClient& posthogClient
    );
    
    /**
     * @brief Destructor - cleanup LVGL resources
     */
    ~UroboroCard() override;
    
    // InputHandler interface implementation
    bool handleButtonPress(uint8_t button_index) override;
    void update() override;
    lv_obj_t* getCardObject() const override;

private:
    // Card configuration
    static constexpr uint16_t CARD_WIDTH = 240;
    static constexpr uint16_t CARD_HEIGHT = 135;
    static constexpr uint32_t REFRESH_INTERVAL_MS = 300000; // 5 minutes
    static constexpr uint32_t UPDATE_INTERVAL_MS = 1000;    // 1 second UI updates
    
    // PostHog configuration
    static constexpr const char* POSTHOG_PROJECT_ID = "71732";
    static constexpr const char* POSTHOG_HOST = "https://eu.posthog.com";
    
    /**
     * @brief Uroboro statistics structure
     */
    struct UroboroStats {
        uint32_t captures_today = 0;
        uint32_t publishes_today = 0;
        uint32_t status_checks_today = 0;
        uint32_t captures_hour = 0;
        String daily_trend = "→ Normal";
        String data_source = "Starting...";
        String last_fetch = "Never";
        bool is_live_data = false;
    };
    
    /**
     * @brief UI state tracking
     */
    struct UIState {
        UroboroStats prev_stats;
        uint32_t last_data_refresh = 0;
        uint32_t last_ui_update = 0;
        bool needs_full_refresh = true;
    };
    
    // System references
    ConfigManager& _config;
    EventQueue& _event_queue;
    PostHogClient& _posthog_client;
    
    // Current state
    UroboroStats _current_stats;
    UIState _ui_state;
    
    // LVGL UI elements
    lv_obj_t* _card_root;
    lv_obj_t* _title_label;
    lv_obj_t* _status_label;
    lv_obj_t* _data_source_label;
    lv_obj_t* _captures_label;
    lv_obj_t* _publishes_label;
    lv_obj_t* _status_checks_label;
    lv_obj_t* _trend_label;
    lv_obj_t* _controls_label;
    
    /**
     * @brief Initialize the card UI layout
     */
    void createUI();
    
    /**
     * @brief Fetch fresh uroboro data from PostHog
     */
    void fetchUroboroData();
    
    /**
     * @brief Parse PostHog API response
     * @param json_response Raw JSON response from PostHog
     * @return true if parsing successful
     */
    bool parsePostHogResponse(const String& json_response);
    
    /**
     * @brief Generate fallback simulated data
     */
    void generateFallbackData();
    
    /**
     * @brief Update UI elements if data has changed
     */
    void updateUI();
    
    /**
     * @brief Update a specific label if text has changed
     * @param label LVGL label object
     * @param new_text New text to display
     * @param color Optional color for the label
     * @return true if label was updated
     */
    bool updateLabel(lv_obj_t* label, const String& new_text, lv_color_t color = lv_color_white());
    
    /**
     * @brief Calculate productivity trend from stats
     * @return Trend string with emoji and description
     */
    String calculateTrend() const;
    
    /**
     * @brief Format timestamp for display
     * @param timestamp_ms Timestamp in milliseconds
     * @return Formatted time string
     */
    String formatTime(uint32_t timestamp_ms) const;
    
    /**
     * @brief Generate PostHog HogQL query for uroboro events
     * @return JSON query string
     */
    String buildHogQLQuery() const;
    
    /**
     * @brief Handle async PostHog response
     * @param event Event containing response data
     */
    void onPostHogResponse(const Event& event);
};

#endif // UROBORO_CARD_H