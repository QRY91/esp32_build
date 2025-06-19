import board
import displayio
import terminalio
import time
import digitalio
import adafruit_st7789
from adafruit_display_text import label
import random

# Release any resources currently in use for the displays
displayio.release_displays()

# Initialize SPI and display for ESP32-S3 Reverse TFT
spi = board.SPI()
tft_cs = board.TFT_CS
tft_dc = board.TFT_DC
tft_reset = board.TFT_RESET
tft_backlight = board.TFT_BACKLIGHT

# Initialize the display
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_reset)
display = adafruit_st7789.ST7789(display_bus, width=240, height=135, rotation=270)

# Turn on the backlight
backlight = digitalio.DigitalInOut(tft_backlight)
backlight.direction = digitalio.Direction.OUTPUT
backlight.value = True

# Create the main display group
main_group = displayio.Group()
display.show(main_group)

# Color palette
colors = [
    0xFF0000,  # Red
    0x00FF00,  # Green
    0x0000FF,  # Blue
    0xFFFF00,  # Yellow
    0xFF00FF,  # Magenta
    0x00FFFF,  # Cyan
    0xFFFFFF,  # White
    0x000000,  # Black
]

def create_welcome_screen():
    """Create the welcome screen with title and info"""
    welcome_group = displayio.Group()

    # Background
    bg_bitmap = displayio.Bitmap(240, 135, 1)
    bg_palette = displayio.Palette(1)
    bg_palette[0] = 0x000000  # Black background
    bg_sprite = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette, x=0, y=0)
    welcome_group.append(bg_sprite)

    # Title
    title_text = "DeskHog Dev"
    title_label = label.Label(terminalio.FONT, text=title_text, color=0x00FFFF, scale=2)
    title_label.x = 10
    title_label.y = 20
    welcome_group.append(title_label)

    # Subtitle
    subtitle_text = "CircuitPython ESP32-S3"
    subtitle_label = label.Label(terminalio.FONT, text=subtitle_text, color=0xFFFFFF, scale=1)
    subtitle_label.x = 10
    subtitle_label.y = 50
    welcome_group.append(subtitle_label)

    # Status
    status_text = "Display: OK"
    status_label = label.Label(terminalio.FONT, text=status_text, color=0x00FF00, scale=1)
    status_label.x = 10
    status_label.y = 70
    welcome_group.append(status_label)

    # Hardware info
    hw_text = "Python on Hardware!"
    hw_label = label.Label(terminalio.FONT, text=hw_text, color=0xFFFF00, scale=1)
    hw_label.x = 10
    hw_label.y = 90
    welcome_group.append(hw_label)

    return welcome_group

def create_graphics_demo():
    """Create animated graphics demo"""
    demo_group = displayio.Group()

    # Background
    bg_bitmap = displayio.Bitmap(240, 135, 1)
    bg_palette = displayio.Palette(1)
    bg_palette[0] = 0x000020  # Dark blue background
    bg_sprite = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette, x=0, y=0)
    demo_group.append(bg_sprite)

    # Create colorful rectangles
    for i in range(6):
        rect_bitmap = displayio.Bitmap(20, 20, 1)
        rect_palette = displayio.Palette(1)
        rect_palette[0] = colors[i]
        rect_sprite = displayio.TileGrid(rect_bitmap, pixel_shader=rect_palette,
                                       x=30 + i * 25, y=30)
        demo_group.append(rect_sprite)

    # Add some dots
    for i in range(10):
        dot_bitmap = displayio.Bitmap(4, 4, 1)
        dot_palette = displayio.Palette(1)
        dot_palette[0] = colors[i % len(colors)]
        dot_sprite = displayio.TileGrid(dot_bitmap, pixel_shader=dot_palette,
                                      x=random.randint(0, 220),
                                      y=random.randint(60, 120))
        demo_group.append(dot_sprite)

    # Demo title
    demo_text = "Graphics Demo"
    demo_label = label.Label(terminalio.FONT, text=demo_text, color=0xFFFFFF, scale=1)
    demo_label.x = 10
    demo_label.y = 10
    demo_group.append(demo_label)

    return demo_group

def create_game_demo():
    """Create simple interactive demo"""
    game_group = displayio.Group()

    # Background
    bg_bitmap = displayio.Bitmap(240, 135, 1)
    bg_palette = displayio.Palette(1)
    bg_palette[0] = 0x000000  # Black background
    bg_sprite = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette, x=0, y=0)
    game_group.append(bg_sprite)

    # Game area border
    border_bitmap = displayio.Bitmap(220, 100, 1)
    border_palette = displayio.Palette(1)
    border_palette[0] = 0xFFFFFF  # White border
    border_sprite = displayio.TileGrid(border_bitmap, pixel_shader=border_palette, x=10, y=25)
    game_group.append(border_sprite)

    # Inner game area
    inner_bitmap = displayio.Bitmap(216, 96, 1)
    inner_palette = displayio.Palette(1)
    inner_palette[0] = 0x000000  # Black inner area
    inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=12, y=27)
    game_group.append(inner_sprite)

    # Bouncing cursor
    cursor_bitmap = displayio.Bitmap(8, 8, 1)
    cursor_palette = displayio.Palette(1)
    cursor_palette[0] = 0xFF0000  # Red cursor
    cursor_sprite = displayio.TileGrid(cursor_bitmap, pixel_shader=cursor_palette, x=120, y=60)
    game_group.append(cursor_sprite)

    # Title
    title_text = "Ready for Games!"
    title_label = label.Label(terminalio.FONT, text=title_text, color=0x00FF00, scale=1)
    title_label.x = 10
    title_label.y = 10
    game_group.append(title_label)

    return game_group, cursor_sprite

def main():
    """Main demo loop"""
    print("ESP32-S3 CircuitPython TFT Demo Starting!")

    # Show welcome screen
    welcome = create_welcome_screen()
    main_group.append(welcome)
    time.sleep(3)

    # Show graphics demo
    main_group.pop()
    graphics = create_graphics_demo()
    main_group.append(graphics)
    time.sleep(3)

    # Show game demo with simple animation
    main_group.pop()
    game, cursor = create_game_demo()
    main_group.append(game)

    # Simple cursor animation
    cursor_x = 120
    cursor_y = 60
    dx = 2
    dy = 1

    print("Demo running! Press Ctrl+C to stop.")

    try:
        counter = 0
        while True:
            # Animate cursor
            cursor_x += dx
            cursor_y += dy

            # Bounce off walls
            if cursor_x <= 15 or cursor_x >= 215:
                dx = -dx
            if cursor_y <= 30 or cursor_y >= 115:
                dy = -dy

            cursor.x = cursor_x
            cursor.y = cursor_y

            # Change cursor color occasionally
            if counter % 30 == 0:
                cursor.pixel_shader[0] = colors[random.randint(0, len(colors)-1)]

            counter += 1
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nDemo stopped!")

        # Show final message
        main_group.pop()
        final_group = displayio.Group()

        bg_bitmap = displayio.Bitmap(240, 135, 1)
        bg_palette = displayio.Palette(1)
        bg_palette[0] = 0x000000
        bg_sprite = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette, x=0, y=0)
        final_group.append(bg_sprite)

        final_text = "Ready to Build Games!"
        final_label = label.Label(terminalio.FONT, text=final_text, color=0x00FFFF, scale=2)
        final_label.x = 10
        final_label.y = 60
        final_group.append(final_label)

        main_group.append(final_group)

if __name__ == "__main__":
    main()
