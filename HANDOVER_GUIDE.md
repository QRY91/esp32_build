# ESP32-S3 CircuitPython Development Handover Guide

**Project**: DeskHog Embedded Game Development  
**Hardware**: Adafruit ESP32-S3 Reverse TFT Feather  
**Status**: Display working, ready for game development  
**Date**: June 19, 2025  

---

## 🎯 **Current Status**

### ✅ **What's Working**
- **Hardware**: ESP32-S3 Reverse TFT Feather fully functional
- **CircuitPython**: Version 9.2.8 installed and running
- **Display**: 240x135 TFT working perfectly with manual initialization
- **Graphics**: Full color display, animation, patterns all working
- **Backlight Control**: TFT_BACKLIGHT pin working correctly
- **Serial Communication**: /dev/ttyACM0 accessible for debugging
- **Library Management**: Adafruit CircuitPython bundle integrated
- **Development Workflow**: File copy → auto-reload established

### ✅ **Resolved Issues**
- **Display Initialization**: Fixed with CircuitPython 9.2.8 API updates
- **Backlight Control**: Working with `board.TFT_BACKLIGHT` after soft reboot
- **API Changes**: Updated for `fourwire` module and `display.root_group`
- **Pin Naming**: Discovered correct pin names through systematic testing

### 🔧 **Key Technical Discoveries**
- **Board Type**: Must use `adafruit_feather_esp32s3_reversetft` (not regular TFT)
- **TinyUF2 Bootloader**: Designed for CircuitPython, not Arduino framework
- **CircuitPython 9.2.8 API**: Uses `fourwire.FourWire` and `display.root_group`
- **Backlight Pin**: `board.TFT_BACKLIGHT` works after displayio.release_displays()
- **Arduino Framework**: Incompatible with TinyUF2 bootloader on this board

---

## 🖥️ **Hardware Configuration**

### **ESP32-S3 Reverse TFT Feather Specs**
- **MCU**: ESP32-S3 dual-core, 240MHz
- **RAM**: 320KB + 2MB PSRAM
- **Flash**: 4MB
- **Display**: 240x135 ST7789 TFT (mounted on back)
- **USB**: Type-C with TinyUF2 bootloader
- **CircuitPython**: 9.2.8 (2025-05-28)

### **Pin Assignments**
```python
TFT_CS = board.IO42
TFT_DC = board.IO40  
TFT_RST = board.IO41
TFT_BACKLIGHT = board.IO45
```

### **Planned Button Connections** (From Arduino Kit)
```
GPIO 12 → UP button + 10kΩ pull-up
GPIO 13 → DOWN button + 10kΩ pull-up
GPIO 14 → LEFT button + 10kΩ pull-up  
GPIO 15 → RIGHT button + 10kΩ pull-up
GPIO 16 → A button + 10kΩ pull-up
GPIO 17 → B button + 10kΩ pull-up
```

---

## 💻 **Software Environment**

### **CircuitPython Setup**
- **Version**: 9.2.8 on ESP32-S3 Reverse TFT
- **Libraries Installed**:
  - `adafruit_display_text` (folder)
  - `adafruit_st7789.mpy` (compiled)
- **Library Source**: `adafruit-circuitpython-bundle-9.x-mpy-20250618`

### **Development Workflow**
1. **Edit code** in any text editor
2. **Copy to device**: `cp your_code.py /media/qry/CIRCUITPY/code.py`
3. **Auto-reload**: CircuitPython automatically restarts
4. **Debug output**: `screen /dev/ttyACM0 115200`

### **File Structure**
```
esp32_build/
├── circuitpython_demo.py          # Full-featured demo (needs debugging)
├── manual_display_test.py         # Working display test
├── simple_print_test.py           # Basic functionality test  
├── debug_test.py                  # Step-by-step diagnostic
├── WIRING_GUIDE.md                # Button wiring instructions
├── adafruit-circuitpython-bundle-9.x-mpy-20250618/  # Library bundle
└── /media/qry/CIRCUITPY/          # Device filesystem
    ├── code.py                    # Currently running code
    ├── lib/                       # Installed libraries
    └── boot_out.txt              # System info
```

---

## 🎮 **Working Code Examples**

### **Display Initialization (WORKING - CircuitPython 9.2.8)**
```python
import board
import displayio
import digitalio
import adafruit_st7789
import fourwire  # FourWire moved to separate module in 9.2.8

# Release displays
displayio.release_displays()

# Backlight control (use board.TFT_BACKLIGHT)
backlight = digitalio.DigitalInOut(board.TFT_BACKLIGHT)
backlight.direction = digitalio.Direction.OUTPUT
backlight.value = True

# Initialize display manually with correct pins
spi = board.SPI()
display_bus = fourwire.FourWire(
    spi, 
    command=board.TFT_DC, 
    chip_select=board.TFT_CS, 
    reset=board.TFT_RESET
)
display = adafruit_st7789.ST7789(
    display_bus,
    width=240,
    height=135,
    rotation=270,
    rowstart=40,
    colstart=53
)
```

### **Simple Graphics Test (CircuitPython 9.2.8)**
```python
# Create display group (use root_group, not .show())
main_group = displayio.Group()
display.root_group = main_group

# Create colored rectangle
bitmap = displayio.Bitmap(100, 50, 1)
palette = displayio.Palette(1)
palette[0] = 0xFF0000  # Red
tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette, x=70, y=40)
main_group.append(tile_grid)
```

---

## 🛠️ **Troubleshooting Guide**

### **Display Issues**
- **Black Screen**: Use manual initialization with `fourwire.FourWire`
- **API Errors**: Update to CircuitPython 9.2.8 API (`display.root_group`, not `.show()`)
- **Backlight Issues**: Use `board.TFT_BACKLIGHT`, ensure `displayio.release_displays()` first
- **Pin Errors**: Use `board.TFT_CS`, `board.TFT_DC`, `board.TFT_RESET` (not IO## notation)
- **Wrong Colors**: Check rotation=270 and offset parameters (rowstart=40, colstart=53)

### **Serial Debug**
```bash
# Connect to CircuitPython REPL
screen /dev/ttyACM0 115200

# Commands in REPL:
# Ctrl+D = Reload code.py
# Ctrl+C = Stop running program  
# Ctrl+A, K, Y = Exit screen
```

### **Library Issues**
```bash
# Check installed libraries
ls /media/qry/CIRCUITPY/lib/

# Install new library from bundle
cp adafruit-circuitpython-bundle-9.x-mpy-20250618/lib/library_name.mpy /media/qry/CIRCUITPY/lib/
```

---

## 🚀 **Next Development Steps**

### **Immediate Tasks**
1. **Wire Buttons**: Connect 6 buttons per `WIRING_GUIDE.md`
2. **Input Testing**: Create button press detection code
3. **Game Framework**: Build basic game loop structure
4. **First Game**: Implement Snake or Pong using working display code

### **Game Development Roadmap**
1. **Snake Game**: Classic implementation for DeskHog
2. **Pong Clone**: Two-player with button controls
3. **Tetris**: Puzzle game with rotation controls
4. **Menu System**: Navigate between games
5. **PostHog Integration**: Game analytics/usage tracking

### **Code Architecture Goals**
```python
# Suggested structure
class GameEngine:
    def __init__(self, display, buttons):
        self.display = display
        self.buttons = buttons
        
    def run_game(self, game_class):
        # Main game loop
        pass

class SnakeGame:
    def update(self, inputs):
        # Game logic
        pass
        
    def render(self, display):
        # Graphics
        pass
```

---

## 📊 **Performance Notes**

### **CircuitPython Limitations**
- **Speed**: ~100-200 FPS possible for simple graphics
- **Memory**: 320KB RAM, manage bitmap sizes carefully
- **Flash**: 4MB total, ~3MB available for code/assets

### **Optimization Tips**
- **Use .mpy files** instead of .py for libraries (faster load)
- **Minimize bitmap allocations** during gameplay
- **Pre-compute graphics** where possible
- **Use displayio.Group** for layered graphics

---

## 🔍 **Debugging Commands**

### **Quick Tests**
```bash
# Upload simple test
cp simple_print_test.py /media/qry/CIRCUITPY/code.py

# Check serial output
timeout 10s cat /dev/ttyACM0

# Manual display test  
cp manual_display_test.py /media/qry/CIRCUITPY/code.py
```

### **System Info**
```bash
# CircuitPython version
cat /media/qry/CIRCUITPY/boot_out.txt

# Available libraries
ls /media/qry/CIRCUITPY/lib/

# Device detection
lsusb | grep Adafruit
ls /dev/ttyACM*
```

---

## 💡 **Key Learnings**

### **Hardware Insights**
- **"Reverse TFT"** has different pin mappings than regular TFT
- **TinyUF2 bootloader** is CircuitPython-optimized, not Arduino-compatible
- **Manual initialization** more reliable than built-in display objects

### **Development Workflow**
- **File copy method** faster than complex upload tools
- **Serial debugging essential** for embedded development
- **Start simple, add complexity** - basic tests first, then features

### **CircuitPython vs Arduino**
- **CircuitPython**: Better for rapid prototyping, Python familiarity
- **Arduino**: More low-level control, but compatibility issues with TinyUF2
- **Performance**: CircuitPython sufficient for simple games

---

## 📞 **Handover Checklist**

### **Verified Working**
- [x] ESP32-S3 boots CircuitPython 9.2.8
- [x] Display shows colors and graphics perfectly
- [x] Animation and patterns working
- [x] Backlight control functional
- [x] Serial communication on /dev/ttyACM0
- [x] Libraries load correctly
- [x] File copy workflow functional

### **Ready for Next Developer**
- [ ] Hardware documented and tested
- [ ] Working code examples provided
- [ ] Troubleshooting guide complete
- [ ] Development workflow established
- [ ] Next steps clearly defined

---

**Status**: ✅ FULLY FUNCTIONAL - Display working perfectly with colors, graphics, and animation.

**Next Steps**: Wire buttons and implement first game (Snake/Pong).

**Working Code**: `fixed_display_test.py` contains complete working display setup.

**Key Files**: All technical details captured in uroboro development log for reference.

**Cloud AI Cost**: Probably exceeded hardware cost! 😄 But we got there through systematic debugging.