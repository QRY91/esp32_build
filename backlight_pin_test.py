import board
import digitalio
import time

print("=== Backlight Pin Test ===")

# Try different possible backlight pin names
backlight_pins = [
    "TFT_BACKLIGHT",
    "BACKLIGHT",
    "BL",
    "LCD_BACKLIGHT",
    "DISPLAY_BACKLIGHT",
    "IO45",
    "GPIO45",
    "D45",
    "PIN45"
]

working_pin = None

for pin_name in backlight_pins:
    print(f"Testing: {pin_name}")

    try:
        if hasattr(board, pin_name):
            pin = getattr(board, pin_name)
            backlight = digitalio.DigitalInOut(pin)
            backlight.direction = digitalio.Direction.OUTPUT

            print(f"SUCCESS: {pin_name} works!")

            # Blink test
            for i in range(3):
                print(f"Blink {i+1}")
                backlight.value = True
                time.sleep(0.5)
                backlight.value = False
                time.sleep(0.5)

            backlight.value = True
            working_pin = pin_name
            print(f"FOUND: {pin_name}")
            break

        else:
            print(f"SKIP: {pin_name} not found")

    except Exception as e:
        print(f"FAIL: {pin_name} error")

if working_pin:
    print(f"BACKLIGHT PIN: {working_pin}")
else:
    print("NO BACKLIGHT PIN FOUND")

print("=== Test Complete ===")

while True:
    time.sleep(1)
