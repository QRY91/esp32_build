import board
import displayio
import terminalio
import time
import digitalio
from adafruit_display_text import label

# Release any resources currently in use for the displays
displayio.release_displays()

# Initialize the built-in display
display = board.DISPLAY

# Turn on the backlight if available
try:
    backlight = digitalio.DigitalInOut(board.TFT_BACKLIGHT)
    backlight.direction = digitalio.Direction.OUTPUT
    backlight.value = True
    print("Backlight enabled")
except AttributeError:
    print("No backlight control available")

# Create the main display group
main_group = displayio.Group()
display.show(main_group)

# Colors
BLACK = 0x000000
WHITE = 0xFFFFFF
RED = 0xFF0000
GREEN = 0x00FF00
BLUE = 0x0000FF
YELLOW = 0xFFFF00
CYAN = 0x00FFFF
MAGENTA = 0xFF00FF

def create_background(color):
    """Create a solid color background"""
    bg_bitmap = displayio.Bitmap(display.width, display.height, 1)
    bg_palette = displayio.Palette(1)
    bg_palette[0] = color
    return displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette, x=0, y=0)

def create_rectangle(width, height, color, x=0, y=0):
    """Create a colored rectangle"""
    rect_bitmap = displayio.Bitmap(width, height, 1)
    rect_palette = displayio.Palette(1)
    rect_palette[0] = color
    return displayio.TileGrid(rect_bitmap, pixel_shader=rect_palette, x=x, y=y)

def main():
    print("ESP32-S3 CircuitPython Simple Demo!")
    print(f"Display size: {display.width}x{display.height}")

    try:
        # Clear display with black background
        bg = create_background(BLACK)
        main_group.append(bg)

        # Add title text
        try:
            title_text = "DeskHog Dev"
            title_label = label.Label(terminalio.FONT, text=title_text, color=CYAN, scale=2)
            title_label.x = 20
            title_label.y = 20
            main_group.append(title_label)

            subtitle_text = "CircuitPython Works!"
            subtitle_label = label.Label(terminalio.FONT, text=subtitle_text, color=WHITE)
            subtitle_label.x = 20
            subtitle_label.y = 50
            main_group.append(subtitle_label)
        except ImportError:
            print("Text labels not available, showing graphics only")

        time.sleep(2)

        # Show colorful rectangles
        colors = [RED, GREEN, BLUE, YELLOW, MAGENTA, CYAN]
        rectangles = []

        for i, color in enumerate(colors):
            rect = create_rectangle(20, 20, color, x=30 + i * 25, y=70)
            rectangles.append(rect)
            main_group.append(rect)
            time.sleep(0.3)

        time.sleep(2)

        # Simple animation - moving rectangle
        moving_rect = create_rectangle(10, 10, RED, x=10, y=100)
        main_group.append(moving_rect)

        print("Starting animation - press Ctrl+C to stop")

        # Animation loop
        x_pos = 10
        direction = 1

        while True:
            x_pos += direction * 2

            # Bounce off edges
            if x_pos >= display.width - 20 or x_pos <= 10:
                direction = -direction

            moving_rect.x = x_pos
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nDemo stopped!")

        # Clear and show final message
        for item in main_group:
            main_group.remove(item)

        final_bg = create_background(BLACK)
        main_group.append(final_bg)

        try:
            final_text = "Ready to Code!"
            final_label = label.Label(terminalio.FONT, text=final_text, color=GREEN, scale=2)
            final_label.x = 30
            final_label.y = 60
            main_group.append(final_label)
        except ImportError:
            # Just show a colored rectangle if text fails
            final_rect = create_rectangle(100, 30, GREEN, x=70, y=50)
            main_group.append(final_rect)

if __name__ == "__main__":
    main()
