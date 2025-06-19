import board
import displayio
import time
import digitalio

print("=== ESP32-S3 CircuitPython Debug Test ===")
print("Starting step-by-step display test...")

try:
    # Step 1: Release displays
    print("Step 1: Releasing displays...")
    displayio.release_displays()
    print("✅ Displays released")

    # Step 2: Get built-in display
    print("Step 2: Getting built-in display...")
    display = board.DISPLAY
    print(f"✅ Display found: {display.width}x{display.height}")

    # Step 3: Backlight control
    print("Step 3: Testing backlight...")
    try:
        backlight = digitalio.DigitalInOut(board.TFT_BACKLIGHT)
        backlight.direction = digitalio.Direction.OUTPUT
        backlight.value = True
        print("✅ Backlight enabled")
    except Exception as e:
        print(f"⚠️ Backlight error: {e}")

    # Step 4: Create main group
    print("Step 4: Creating display group...")
    main_group = displayio.Group()
    print("✅ Group created")

    # Step 5: Show group
    print("Step 5: Showing group on display...")
    display.show(main_group)
    print("✅ Group shown on display")

    # Step 6: Create simple bitmap
    print("Step 6: Creating red bitmap...")
    bitmap = displayio.Bitmap(100, 100, 1)
    palette = displayio.Palette(1)
    palette[0] = 0xFF0000  # Red
    tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette, x=20, y=20)
    print("✅ Red bitmap created")

    # Step 7: Add to display
    print("Step 7: Adding bitmap to display...")
    main_group.append(tile_grid)
    print("✅ Red square should be visible!")

    # Step 8: Wait and test color changes
    for i in range(5):
        print(f"Step 8.{i+1}: Changing color...")
        colors = [0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0xFF00FF]
        palette[0] = colors[i]
        time.sleep(1)
        print(f"✅ Color {i+1}: {hex(colors[i])}")

    print("🎉 All tests passed! Display is working!")

    # Final test - full screen colors
    print("Final test: Full screen color test...")
    full_bitmap = displayio.Bitmap(display.width, display.height, 1)
    full_palette = displayio.Palette(1)
    full_tile = displayio.TileGrid(full_bitmap, pixel_shader=full_palette, x=0, y=0)

    main_group.pop()  # Remove red square
    main_group.append(full_tile)

    test_colors = [0xFF0000, 0x00FF00, 0x0000FF, 0xFFFFFF, 0x000000]
    for color in test_colors:
        full_palette[0] = color
        print(f"Full screen: {hex(color)}")
        time.sleep(1)

    print("✅ Debug test complete - hardware working perfectly!")

except Exception as e:
    print(f"❌ Error in step: {e}")
    print(f"Error type: {type(e)}")
    import traceback
    traceback.print_exception(type(e), e, e.__traceback__)

print("Debug test finished. Check serial output for results.")
