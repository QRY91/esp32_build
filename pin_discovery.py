import board
import time

print("=== ESP32-S3 Reverse TFT Pin Discovery ===")
print("Discovering all available pins and attributes...")

try:
    # Get all attributes from board module
    board_attrs = dir(board)

    print(f"Total attributes found: {len(board_attrs)}")
    print("\n=== ALL BOARD ATTRIBUTES ===")

    # Print all attributes
    for attr in sorted(board_attrs):
        if not attr.startswith('_'):  # Skip private attributes
            try:
                value = getattr(board, attr)
                print(f"{attr} = {value}")
            except Exception as e:
                print(f"{attr} = <Error: {e}>")

    print("\n=== TFT-RELATED PINS ===")
    tft_pins = [attr for attr in board_attrs if 'TFT' in attr.upper()]
    if tft_pins:
        for pin in tft_pins:
            try:
                value = getattr(board, pin)
                print(f"✅ {pin} = {value}")
            except Exception as e:
                print(f"❌ {pin} = <Error: {e}>")
    else:
        print("No TFT-specific pins found")

    print("\n=== GPIO PINS ===")
    gpio_pins = [attr for attr in board_attrs if attr.startswith('IO') or 'GPIO' in attr.upper()]
    if gpio_pins:
        for pin in sorted(gpio_pins):
            try:
                value = getattr(board, pin)
                print(f"✅ {pin} = {value}")
            except Exception as e:
                print(f"❌ {pin} = <Error: {e}>")
    else:
        print("No obvious GPIO pins found")

    print("\n=== DISPLAY-RELATED PINS ===")
    display_pins = [attr for attr in board_attrs if any(x in attr.upper() for x in ['DISPLAY', 'LCD', 'SCREEN', 'BACKLIGHT'])]
    if display_pins:
        for pin in display_pins:
            try:
                value = getattr(board, pin)
                print(f"✅ {pin} = {value}")
            except Exception as e:
                print(f"❌ {pin} = <Error: {e}>")
    else:
        print("No display-specific pins found")

    print("\n=== SPI PINS ===")
    spi_pins = [attr for attr in board_attrs if 'SPI' in attr.upper() or attr in ['SCK', 'MOSI', 'MISO']]
    if spi_pins:
        for pin in spi_pins:
            try:
                value = getattr(board, pin)
                print(f"✅ {pin} = {value}")
            except Exception as e:
                print(f"❌ {pin} = <Error: {e}>")
    else:
        print("No SPI pins found")

    print("\n=== SEARCHING FOR PINS 40-47 ===")
    # Try different naming conventions for pins 40-47
    for pin_num in range(40, 48):
        possible_names = [
            f"IO{pin_num}",
            f"GPIO{pin_num}",
            f"D{pin_num}",
            f"PIN{pin_num}",
            f"P{pin_num}"
        ]

        for name in possible_names:
            if hasattr(board, name):
                try:
                    value = getattr(board, name)
                    print(f"✅ Found pin {pin_num} as: {name} = {value}")
                    break
                except Exception as e:
                    print(f"❌ {name} = <Error: {e}>")

except Exception as e:
    print(f"❌ Discovery failed: {e}")
    import traceback
    traceback.print_exception(type(e), e, e.__traceback__)

print("\n=== Pin Discovery Complete ===")
print("Check output above for correct pin names!")

# Keep running so we can examine output
while True:
    time.sleep(1)
