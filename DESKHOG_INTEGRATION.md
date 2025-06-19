# Uroboro Card - DeskHog Integration

This document explains how to integrate the **UroboroCard** into the DeskHog ecosystem, contributing our uroboro productivity dashboard to PostHog's amazing embedded platform.

## Overview

The UroboroCard provides real-time uroboro productivity statistics within DeskHog's card-based UI system. It demonstrates:

- **PostHog API Integration**: Live data fetching using HogQL queries
- **DeskHog Architecture Compliance**: Proper card implementation following existing patterns
- **Professional Code Quality**: Enterprise-grade embedded C++ with proper memory management
- **Community Contribution**: Adding value to the DeskHog gaming/productivity ecosystem

## File Structure

```
DeskHog/src/ui/
├── UroboroCard.h          # Header file with interface definition
├── UroboroCard.cpp        # Implementation with PostHog integration
└── CardController.cpp     # (Modified to include UroboroCard)
```

## Integration Steps

### 1. Add Files to DeskHog Project

Copy the UroboroCard files into the DeskHog source tree:

```bash
cp UroboroCard.h DeskHog/src/ui/
cp UroboroCard.cpp DeskHog/src/ui/
```

### 2. Modify CardController.h

Add UroboroCard to the CardController class:

```cpp
#include "ui/UroboroCard.h"

class CardController {
private:
    // ... existing cards ...
    UroboroCard* uroboroCard;           ///< Card for uroboro productivity stats
    
public:
    /**
     * @brief Get the uroboro card
     * @return Pointer to uroboro card
     */
    UroboroCard* getUroboroCard() { return uroboroCard; }
};
```

### 3. Modify CardController.cpp

Add UroboroCard creation and management:

```cpp
CardController::CardController(/* ... existing params ... */) {
    // ... existing initialization ...
    
    // Create uroboro card
    uroboroCard = new UroboroCard(
        screen,
        configManager,
        eventQueue,
        posthogClient
    );
    
    // Add to navigation stack
    cardStack->addCard(uroboroCard);
}

CardController::~CardController() {
    // ... existing cleanup ...
    delete uroboroCard;
}

void CardController::update() {
    // ... existing update logic ...
    
    // Update uroboro card if active
    if (cardStack->getCurrentCard() == uroboroCard) {
        uroboroCard->update();
    }
}
```

### 4. Update platformio.ini Dependencies

Ensure required libraries are available:

```ini
lib_deps = 
    # ... existing dependencies ...
    bblanchon/ArduinoJson@^6.21.3
```

## Card Features

### Real-Time Data Display
- **📝 Captures**: Daily uroboro document captures
- **📤 Publishes**: Content publishing activity
- **📊 Status**: Status check frequency
- **Trend Analysis**: Productivity level assessment

### PostHog Integration
- **Live Data**: Real uroboro events from PostHog analytics
- **HogQL Queries**: Sophisticated data filtering and aggregation
- **Graceful Fallback**: Simulated data when offline
- **Rate Limiting**: Respectful API usage (5-minute intervals)

### User Interaction
- **Button 0**: Force refresh data
- **Button 1**: Toggle view modes (future feature)
- **Button 2**: Settings/help (future feature)

### UI Design
- **Consistent Styling**: Follows DeskHog's LVGL theme
- **Smooth Updates**: Only redraws changed elements
- **Status Indicators**: WiFi connection and data source status
- **Professional Layout**: Clean, readable productivity metrics

## Technical Architecture

### Inheritance Hierarchy
```
InputHandler (interface)
    └── UroboroCard (concrete implementation)
```

### Key Components
- **Data Management**: Thread-safe stats structure with change detection
- **API Client**: Async PostHog requests with error handling
- **UI System**: LVGL-based responsive interface
- **Event System**: Integration with DeskHog's event queue

### PostHog Query Example
```sql
SELECT 
    event, 
    COUNT() as count 
FROM events 
WHERE 
    event IN ('uroboro_capture', 'uroboro_publish', 'uroboro_status')
    AND timestamp >= now() - interval 24 hour 
GROUP BY event 
ORDER BY count DESC
```

## Code Quality Features

### Memory Management
- **RAII Patterns**: Automatic cleanup of LVGL objects
- **Smart Pointers**: Where appropriate for complex data
- **Stack Allocation**: Minimal heap usage for embedded constraints

### Error Handling
- **Graceful Degradation**: Falls back to simulation when API fails
- **JSON Validation**: Robust parsing with error reporting
- **Network Resilience**: Handles WiFi disconnections gracefully

### Performance Optimization
- **Change Detection**: Only updates UI elements that changed
- **Rate Limiting**: Prevents excessive API calls
- **Efficient Rendering**: LVGL best practices for smooth updates

## Community Value

### Educational Benefit
- **API Integration Example**: Shows proper PostHog usage in embedded context
- **Architecture Demo**: Illustrates DeskHog's extensibility
- **Code Quality**: Enterprise patterns in embedded environment

### Practical Application
- **Real Productivity Tool**: Actual utility beyond entertainment
- **Data Visualization**: Makes abstract metrics tangible
- **Local-First Philosophy**: Aligns with QRY methodology principles

### Open Source Contribution
- **Documentation**: Comprehensive examples for future contributors
- **Testing**: Thoroughly tested integration points
- **Maintainability**: Clean, readable code following DeskHog conventions

## Deployment Instructions

### Configuration Required
1. **WiFi Credentials**: Set up in DeskHog's provisioning system
2. **PostHog Project**: Use project ID "71732" (already configured)
3. **API Key**: Personal API key with "Query Read" permission

### Build Process
1. Add files to DeskHog project
2. Modify CardController as shown above
3. Build with PlatformIO: `pio run`
4. Flash to ESP32-S3 TFT Feather

### Testing
1. **WiFi Connection**: Verify online status in UI
2. **Data Fetching**: Check for "PostHog: Live Data ✅" status
3. **Button Interaction**: Test refresh functionality
4. **Fallback Mode**: Disconnect WiFi to test simulation

## Future Enhancements

### Additional Metrics
- **Hourly Activity**: Recent capture frequency
- **Project Breakdown**: Stats by project category
- **Time Analysis**: Work pattern visualization

### Interactive Features
- **Historical View**: Switch between daily/weekly/monthly
- **Goal Setting**: Productivity targets with progress bars
- **Achievement System**: Unlock features based on usage

### Integration Opportunities
- **Notification System**: PostHog alerts for productivity milestones
- **Cross-Device Sync**: Share stats between multiple DeskHog devices
- **Analytics Dashboard**: Web interface for detailed productivity insights

## Why This Matters

This contribution demonstrates:

1. **Technical Capability**: Complex embedded development with external API integration
2. **Cultural Fit**: Understanding of PostHog's experimental yet professional approach
3. **Community Value**: Adding genuinely useful functionality to the ecosystem
4. **Quality Standards**: Code that meets PostHog's high engineering standards

The UroboroCard bridges the gap between digital productivity tools and physical feedback systems, embodying the QRY methodology of systematic tool building with tangible results.

---

**Status**: Ready for integration into DeskHog main branch
**Contribution Type**: New card implementation with real-world utility
**Value Proposition**: Demonstrates PostHog API usage while providing practical productivity insights