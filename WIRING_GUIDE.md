# Breadboard Wiring Guide for ESP32-S3 TFT Feather

## 🎮 Button Layout & Connections

This guide shows how to wire up 6 tactile buttons from your Arduino kit to create a game controller interface.

### Pin Assignments
```
ESP32-S3 Pin | Button Function | Arduino Kit Component
-------------|-----------------|--------------------
GPIO 12      | UP             | Tactile Button + 10kΩ Resistor
GPIO 13      | DOWN           | Tactile Button + 10kΩ Resistor  
GPIO 14      | LEFT           | Tactile Button + 10kΩ Resistor
GPIO 15      | RIGHT          | Tactile Button + 10kΩ Resistor
GPIO 16      | A (Action)     | Tactile Button + 10kΩ Resistor
GPIO 17      | B (Action)     | Tactile Button + 10kΩ Resistor
GND          | Ground         | Breadboard ground rail
3.3V         | Power          | Breadboard power rail
```

## 🔌 Step-by-Step Wiring

### 1. Prepare Your Breadboard
- Connect ESP32-S3 **GND** to breadboard **ground rail** (blue/black stripe)
- Connect ESP32-S3 **3.3V** to breadboard **power rail** (red stripe)
- Use jumper wires to extend power/ground to both sides if needed

### 2. Wire Each Button (Repeat for all 6 buttons)

**For each button:**
```
Button Layout on Breadboard:
    [3.3V Rail] ----[10kΩ Resistor]----[Button]----[ESP32 GPIO Pin]
                                        |
                                    [GND Rail]
```

**Detailed Steps:**
1. Insert tactile button across the center gap of breadboard
2. Connect one side of button to **GND rail** (using jumper wire)
3. Connect **10kΩ resistor** from **3.3V rail** to the **same button terminal** as the ESP32 pin
4. Connect **ESP32 GPIO pin** to the **same button terminal** as the resistor

### 3. Complete Wiring List

**Button Connections:**
```
UP Button (GPIO 12):
- Button Pin 1 → ESP32 GPIO 12 + 10kΩ resistor to 3.3V
- Button Pin 2 → GND

DOWN Button (GPIO 13):
- Button Pin 1 → ESP32 GPIO 13 + 10kΩ resistor to 3.3V  
- Button Pin 2 → GND

LEFT Button (GPIO 14):
- Button Pin 1 → ESP32 GPIO 14 + 10kΩ resistor to 3.3V
- Button Pin 2 → GND

RIGHT Button (GPIO 15):
- Button Pin 1 → ESP32 GPIO 15 + 10kΩ resistor to 3.3V
- Button Pin 2 → GND

A Button (GPIO 16):
- Button Pin 1 → ESP32 GPIO 16 + 10kΩ resistor to 3.3V
- Button Pin 2 → GND

B Button (GPIO 17):
- Button Pin 1 → ESP32 GPIO 17 + 10kΩ resistor to 3.3V
- Button Pin 2 → GND
```

## 🎯 Recommended Physical Layout

```
Breadboard Layout (Top View):
    
    3.3V Rail: [+++++++++++++++++++++++++++++++]
    
    Row 10: [UP]    [  ]    [A ]
    Row 15: [LT]    [DN]    [RT]    [B ]
    
    GND Rail:  [------------------------------]
    
    GPIO Connections:
    ESP32 → Breadboard
    12 → UP button
    13 → DN button  
    14 → LT button
    15 → RT button
    16 → A button
    17 → B button
```

## ⚡ Pull-up Resistor Explanation

**Why 10kΩ resistors?**
- Pull-up resistors ensure GPIO pins read HIGH (3.3V) when button is not pressed
- When button is pressed, it connects GPIO to GND (LOW)
- This gives us clean digital signals: HIGH = not pressed, LOW = pressed
- The code uses `INPUT_PULLUP` mode and inverts the reading: `!digitalRead(pin)`

## 🔧 Assembly Tips

### Before You Start
1. **Power off** - Always wire with ESP32 unpowered
2. **Double-check** - Verify each connection before powering on
3. **Use colors** - Red for power, black for ground, other colors for signals

### During Assembly
1. **Seat components firmly** - Push buttons and resistors fully into breadboard
2. **No loose connections** - Wiggle test all jumper wires
3. **Keep it neat** - Route wires cleanly to avoid shorts
4. **Label if needed** - Use tape to mark button functions

### Component Identification
```
Tactile Button:     10kΩ Resistor:
┌─┬─┐              ┌────────────┐
│ │ │              │  Brown │ Black │ Red │ Gold  │
│ │ │              │    1   │   0   │ x100│ ±5%   │
└─┴─┘              └────────────┘

4 pins, but only   Brown-Black-Red = 10,000 ohms
2 connections      Gold = ±5% tolerance
```

## 🚨 Safety & Troubleshooting

### ⚠️ Common Mistakes
- **Forgetting pull-up resistors** → Pins will float and give random readings
- **Wrong GPIO pins** → Buttons won't respond (check pin assignments in code)
- **Loose connections** → Intermittent button presses
- **Short circuits** → Connect power/ground carefully

### ✅ Testing Checklist
1. **Visual inspection** - No exposed wires touching
2. **Continuity test** - Use multimeter if available
3. **Power test** - Check 3.3V and GND with multimeter
4. **Button test** - Each button should show ~3.3V when not pressed, ~0V when pressed

### 🐛 If Buttons Don't Work
1. **Check serial monitor** - Are button presses being detected?
2. **Verify pin assignments** - Match code GPIO numbers to physical connections
3. **Test individual buttons** - Disconnect all but one to isolate issues
4. **Check power** - Verify 3.3V on breadboard power rail
5. **Re-seat connections** - Remove and reconnect jumper wires

## 📡 Upload and Test

### Upload Process
```bash
# Connect ESP32-S3 via USB-C
# Open terminal in project directory
export PATH=$PATH:~/.platformio/penv/bin
pio run --target upload --target monitor
```

### What You Should See
1. **Welcome screen** - 2 seconds of startup display
2. **Game screen** - Cursor demo with button controls
3. **Serial output** - Button press confirmations and coordinates
4. **Display updates** - Cursor moves, score changes

### Expected Behavior
- **Arrow buttons** → Move red cursor around screen
- **A button** → Increment score (displayed top-right)
- **B button** → Reset cursor position and score to zero
- **Serial monitor** → Shows button presses and position updates

## 🎮 Ready to Game!

Once everything is wired and tested, you have a working game controller interface! This foundation can be used for:

- **Pong game** - Left/right paddles, A/B for serve/pause
- **Snake game** - Directional controls, A for start/restart  
- **Tetris** - Rotate/drop pieces, A/B for actions
- **Menu navigation** - Up/down/select interface

**Next Steps:**
1. Test all buttons work correctly
2. Try modifying cursor speed in the code
3. Add sound effects using Arduino kit buzzer
4. Design simple games using this input system

---

**Status**: Ready for development  
**Total Components**: 6 buttons + 6 resistors + jumper wires  
**Power**: USB or bench supply (3.3V/5V tolerant)  
**Estimated Assembly Time**: 15-30 minutes