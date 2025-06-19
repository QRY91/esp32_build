import board
import displayio
import digitalio
import adafruit_st7789
import fourwire
import time

print("=== Fixed Display Test ===")
print("CircuitPython 9.2.8 API")

try:
    # Step 1: Release any existing displays
    print("Step 1: Releasing displays...")
    displayio.release_displays()
    print("✅ Displays released")

    # Step 2: Setup backlight
    print("Step 2: Setting up backlight...")
    backlight = digitalio.DigitalInOut(board.TFT_BACKLIGHT)
    backlight.direction = digitalio.Direction.OUTPUT
    backlight.value = True
    print("✅ Backlight ON")

    # Step 3: Setup SPI and display pins
    print("Step 3: Setting up SPI...")
    spi = board.SPI()
    print("✅ SPI ready")

    print("Step 4: Setting up display pins...")
    tft_cs = board.TFT_CS
    tft_dc = board.TFT_DC
    tft_reset = board.TFT_RESET
    print("✅ Display pins configured")

    # Step 5: Create display bus (using fourwire module)
    print("Step 5: Creating display bus...")
    display_bus = fourwire.FourWire(
        spi,
        command=tft_dc,
        chip_select=tft_cs,
        reset=tft_reset
    )
    print("✅ Display bus created")

    # Step 6: Initialize ST7789 display
    print("Step 6: Initializing ST7789...")
    display = adafruit_st7789.ST7789(
        display_bus,
        width=240,
        height=135,
        rotation=270,
        rowstart=40,
        colstart=53
    )
    print("✅ ST7789 initialized")

    # Step 7: Create display group (using root_group)
    print("Step 7: Creating display group...")
    main_group = displayio.Group()
    display.root_group = main_group
    print("✅ Display group assigned")

    # Step 8: Test colors
    print("Step 8: Testing colors...")
    colors = [0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0xFF00FF, 0x00FFFF, 0xFFFFFF]
    color_names = ["Red", "Green", "Blue", "Yellow", "Magenta", "Cyan", "White"]

    for color, name in zip(colors, color_names):
        print(f"Showing: {name}")

        # Create full screen bitmap
        bitmap = displayio.Bitmap(240, 135, 1)
        palette = displayio.Palette(1)
        palette[0] = color
        tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette, x=0, y=0)

        # Clear and show new color
        while len(main_group) > 0:
            main_group.pop()
        main_group.append(tile_grid)

        time.sleep(1)

    print("✅ Color test complete")

    # Step 9: Graphics test
    print("Step 9: Graphics test...")

    # Black background
    bg_bitmap = displayio.Bitmap(240, 135, 1)
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
            x=20 + i * 50,
            y=50
        )
        main_group.append(rect_tile)

    print("✅ Graphics test complete")

    # Step 10: Animation test
    print("Step 10: Animation test...")

    # Moving rectangle
    moving_bitmap = displayio.Bitmap(20, 20, 1)
    moving_palette = displayio.Palette(1)
    moving_palette[0] = 0x00FFFF
    moving_tile = displayio.TileGrid(moving_bitmap, pixel_shader=moving_palette, x=0, y=10)
    main_group.append(moving_tile)

    # Animate for 5 seconds
    for frame in range(50):
        x_pos = (frame * 4) % 220
        moving_tile.x = x_pos
        time.sleep(0.1)

    print("🎉 ALL TESTS PASSED!")
    print("Display working perfectly!")

    # Final success pattern
    while len(main_group) > 0:
        main_group.pop()

    # Success checkered pattern
    pattern_bitmap = displayio.Bitmap(240, 135, 2)
    pattern_palette = displayio.Palette(2)
    pattern_palette[0] = 0x00FF00  # Green
    pattern_palette[1] = 0x0000FF  # Blue

    for y in range(135):
        for x in range(240):
            if (x // 20 + y // 20) % 2 == 0:
                pattern_bitmap[x, y] = 0
            else:
                pattern_bitmap[x, y] = 1

    pattern_tile = displayio.TileGrid(pattern_bitmap, pixel_shader=pattern_palette, x=0, y=0)
    main_group.append(pattern_tile)

    print("SUCCESS! Ready for games!")

except Exception as e:
    print(f"❌ Error: {e}")
    print(f"Error type: {type(e)}")
    import traceback
    traceback.print_exception(type(e), e, e.__traceback__)

print("=== Test Complete ===")

# Keep running
while True:
    time.sleep(1)
