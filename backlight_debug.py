import board
import digitalio
import time

print("=== TFT_BACKLIGHT Debug ===")

try:
    print("Step 1: Check TFT_BACKLIGHT type")
    backlight_pin = board.TFT_BACKLIGHT
    print(f"Type: {type(backlight_pin)}")
    print(f"Value: {backlight_pin}")

    print("Step 2: Try digitalio setup")
    try:
        backlight = digitalio.DigitalInOut(backlight_pin)
        print("✅ DigitalInOut created")

        print("Step 3: Set direction")
        backlight.direction = digitalio.Direction.OUTPUT
        print("✅ Direction set to OUTPUT")

        print("Step 4: Test control")
        backlight.value = True
        print("✅ Set HIGH")
        time.sleep(1)

        backlight.value = False
        print("✅ Set LOW")
        time.sleep(1)

        backlight.value = True
        print("✅ Backlight working!")

    except Exception as inner_e:
        print(f"❌ DigitalIO Error: {inner_e}")
        print(f"Error type: {type(inner_e)}")

        print("Step 5: Try PWM instead")
        try:
            import pwmio
            backlight_pwm = pwmio.PWMOut(backlight_pin)
            backlight_pwm.duty_cycle = 65535  # Full brightness
            print("✅ PWM backlight worked!")
            backlight_pwm.deinit()
        except Exception as pwm_e:
            print(f"❌ PWM Error: {pwm_e}")

        print("Step 6: Check if pin in use")
        try:
            print(f"Pin dir: {dir(backlight_pin)}")
        except:
            print("Can't get pin details")

except Exception as e:
    print(f"❌ Major Error: {e}")
    print(f"Error type: {type(e)}")

    print("Checking if TFT_BACKLIGHT exists...")
    if hasattr(board, 'TFT_BACKLIGHT'):
        print("✅ TFT_BACKLIGHT exists")
    else:
        print("❌ TFT_BACKLIGHT missing")

print("=== Debug Complete ===")

# Try working without backlight control
print("Testing display without backlight...")
try:
    import displayio
    displayio.release_displays()

    # Use built-in display if available
    if hasattr(board, 'DISPLAY'):
        print("Using board.DISPLAY")
        display = board.DISPLAY

        # Create simple test
        main_group = displayio.Group()
        display.show(main_group)

        # Red rectangle
        bitmap = displayio.Bitmap(100, 50, 1)
        palette = displayio.Palette(1)
        palette[0] = 0xFF0000
        tile = displayio.TileGrid(bitmap, pixel_shader=palette, x=70, y=40)
        main_group.append(tile)

        print("✅ Display test without backlight")

except Exception as disp_e:
    print(f"❌ Display Error: {disp_e}")

while True:
    time.sleep(1)
