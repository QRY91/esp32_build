import board
import digitalio
import time

print("=== Minimal Backlight Test ===")
print("Testing basic hardware control...")

try:
    # Just control the backlight pin - no display initialization
    print("Setting up backlight pin...")
    backlight = digitalio.DigitalInOut(board.IO45)
    backlight.direction = digitalio.Direction.OUTPUT
    print("✅ Backlight pin configured")

    # Test backlight control
    for i in range(10):
        print(f"Backlight ON - cycle {i+1}")
        backlight.value = True
        time.sleep(1)

        print(f"Backlight OFF - cycle {i+1}")
        backlight.value = False
        time.sleep(1)

    print("✅ Backlight test complete")

    # Leave backlight on
    backlight.value = True
    print("Backlight left ON")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exception(type(e), e, e.__traceback__)

print("=== Test finished - check for blinking ===")

# Keep running
while True:
    time.sleep(1)
