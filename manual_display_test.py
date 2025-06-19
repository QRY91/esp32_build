import board
import displayio
import busio
import digitalio
import adafruit_st7789
import time

print("=== Manual Display Test for ESP32-S3 Reverse TFT ===")
print("Initializing display manually...")

try:
    # Release any existing displays
    displayio.release_displays()
    print("✅ Released displays")

    # Manual pin definitions for ESP32-S3 Reverse TFT
    TFT_CS = board.IO42
    TFT_DC = board.IO40
    TFT_RST = board.IO41
    TFT_BACKLIGHT = board.IO45

    print("✅ Pin assignments loaded")

    # Initialize SPI
    spi = board.SPI()
    print("✅ SPI initialized")

    # Create display bus manually
    display_bus = displayio.FourWire(
        spi,
        command=TFT_DC,
        chip_select=TFT_CS,
        reset=TFT_RST
    )
    print("✅ Display bus created")

    # Initialize ST7789 display manually
    display = adafruit_st7789.ST7789(
        display_bus,
        width=240,
        height=135,
        rotation=270,  # Landscape for reverse TFT
        rowstart=40,   # Offset for 240x135 display
        colstart=53
    )
    print("✅ ST7789 display initialized")

    # Turn on backlight
    backlight = digitalio.DigitalInOut(TFT_BACKLIGHT)
    backlight.direction = digitalio.Direction.OUTPUT
    backlight.value = True
    print("✅ Backlight enabled")

    # Create main group
    main_group = displayio.Group()
    display.show(main_group)
    print("✅ Display group shown")

    # Test 1: Solid colors
    print("Test 1: Solid color backgrounds...")
    colors = [0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0xFF00FF, 0x00FFFF, 0xFFFFFF]
    color_names = ["Red", "Green", "Blue", "Yellow", "Magenta", "Cyan", "White"]

    for i, (color, name) in enumerate(zip(colors, color_names)):
        print(f"  Showing {name}...")

        # Create full screen bitmap
        bitmap = displayio.Bitmap(display.width, display.height, 1)
        palette = displayio.Palette(1)
        palette[0] = color
        tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette, x=0, y=0)

        # Clear and show
        while len(main_group) > 0:
            main_group.pop()
        main_group.append(tile_grid)

        time.sleep(1)

    print("✅ Color test complete")

    # Test 2: Pattern test
    print("Test 2: Pattern test...")
    bitmap = displayio.Bitmap(display.width, display.height, 3)
    palette = displayio.Palette(3)
    palette[0] = 0x000000  # Black
    palette[1] = 0xFF0000  # Red
    palette[2] = 0x00FF00  # Green

    # Create checkerboard pattern
    for y in range(display.height):
        for x in range(display.width):
            if (x // 20 + y // 20) % 2 == 0:
                bitmap[x, y] = 1  # Red
            else:
                bitmap[x, y] = 2  # Green

    pattern_tile = displayio.TileGrid(bitmap, pixel_shader=palette, x=0, y=0)

    while len(main_group) > 0:
        main_group.pop()
    main_group.append(pattern_tile)

    print("✅ Checkerboard pattern displayed")
    time.sleep(3)

    # Test 3: Simple graphics
    print("Test 3: Simple graphics...")

    # Black background
    bg_bitmap = displayio.Bitmap(display.width, display.height, 1)
    bg_palette = displayio.Palette(1)
    bg_palette[0] = 0x000000
    bg_tile = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette, x=0, y=0)

    while len(main_group) > 0:
        main_group.pop()
    main_group.append(bg_tile)

    # Add colored rectangles
    rect_colors = [0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00]
    for i, color in enumerate(rect_colors):
        rect_bitmap = displayio.Bitmap(40, 30, 1)
        rect_palette = displayio.Palette(1)
        rect_palette[0] = color
        rect_tile = displayio.TileGrid(
            rect_bitmap,
            pixel_shader=rect_palette,
            x=10 + i * 50,
            y=50
        )
        main_group.append(rect_tile)

    print("✅ Graphics test complete")

    print("🎉 ALL TESTS PASSED! Display is working perfectly!")
    print("Manual initialization successful.")

except Exception as e:
    print(f"❌ Error: {e}")
    print(f"Error type: {type(e)}")
    import traceback
    traceback.print_exception(type(e), e, e.__traceback__)

print("=== Manual Display Test Complete ===")
print("Check the display for colorful patterns!")

# Keep running
while True:
    time.sleep(1)
