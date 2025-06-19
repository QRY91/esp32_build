import board
import displayio
import time
import digitalio

# Release any resources currently in use for the displays
displayio.release_displays()

# Initialize the built-in display
display = board.DISPLAY

# Turn on the backlight
try:
    backlight = digitalio.DigitalInOut(board.TFT_BACKLIGHT)
    backlight.direction = digitalio.Direction.OUTPUT
    backlight.value = True
    print("Backlight enabled")
except:
    print("Backlight control not available")

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

def create_rect(width, height, color, x=0, y=0):
    """Create a colored rectangle"""
    bitmap = displayio.Bitmap(width, height, 1)
    palette = displayio.Palette(1)
    palette[0] = color
    tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette, x=x, y=y)
    return tile_grid

def clear_display():
    """Clear all items from display"""
    while len(main_group) > 0:
        main_group.pop()

def main():
    print("ESP32-S3 CircuitPython Built-in Demo!")
    print(f"Display size: {display.width}x{display.height}")

    try:
        # Black background
        bg = create_rect(display.width, display.height, BLACK)
        main_group.append(bg)

        # Welcome sequence - flash colors
        colors = [RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, WHITE]

        print("Color flash sequence...")
        for color in colors:
            flash_rect = create_rect(100, 50, color, x=70, y=40)
            main_group.append(flash_rect)
            time.sleep(0.5)
            main_group.pop()  # Remove the flash rectangle

        # Draw a pattern of rectangles
        print("Drawing pattern...")

        # Grid of colored squares
        square_size = 20
        spacing = 25
        start_x = 10
        start_y = 20

        for row in range(4):
            for col in range(8):
                if col + row * 8 < len(colors) * 3:  # Repeat colors
                    color = colors[(col + row * 8) % len(colors)]
                    x = start_x + col * spacing
                    y = start_y + row * spacing

                    if x + square_size <= display.width and y + square_size <= display.height:
                        square = create_rect(square_size, square_size, color, x, y)
                        main_group.append(square)
                        time.sleep(0.1)

        time.sleep(2)

        # Simple animation - bouncing rectangle
        print("Starting animation - press Ctrl+C to stop")

        # Clear for animation
        clear_display()
        bg = create_rect(display.width, display.height, BLACK)
        main_group.append(bg)

        # Create bouncing rectangle
        rect_size = 15
        rect = create_rect(rect_size, rect_size, RED)
        main_group.append(rect)

        # Animation variables
        x_pos = 0
        y_pos = 0
        x_speed = 3
        y_speed = 2
        color_index = 0
        frame_count = 0

        while True:
            # Update position
            x_pos += x_speed
            y_pos += y_speed

            # Bounce off edges
            if x_pos <= 0 or x_pos >= display.width - rect_size:
                x_speed = -x_speed
                color_index = (color_index + 1) % len(colors)

            if y_pos <= 0 or y_pos >= display.height - rect_size:
                y_speed = -y_speed
                color_index = (color_index + 1) % len(colors)

            # Update rectangle position and color every few frames
            rect.x = max(0, min(x_pos, display.width - rect_size))
            rect.y = max(0, min(y_pos, display.height - rect_size))

            if frame_count % 10 == 0:  # Change color periodically
                # Remove old rectangle and create new one with different color
                main_group.pop()
                rect = create_rect(rect_size, rect_size, colors[color_index],
                                 x=rect.x, y=rect.y)
                main_group.append(rect)

            frame_count += 1
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nDemo stopped!")

        # Final screen
        clear_display()
        final_bg = create_rect(display.width, display.height, BLACK)
        main_group.append(final_bg)

        # Success indicator - green screen flash
        success_rect = create_rect(display.width, display.height, GREEN)
        main_group.append(success_rect)
        time.sleep(0.5)
        main_group.pop()

        # Final pattern - checkered
        checker_size = 20
        for row in range(0, display.height, checker_size):
            for col in range(0, display.width, checker_size):
                if (row // checker_size + col // checker_size) % 2 == 0:
                    color = CYAN
                else:
                    color = MAGENTA

                checker = create_rect(min(checker_size, display.width - col),
                                    min(checker_size, display.height - row),
                                    color, x=col, y=row)
                main_group.append(checker)

        print("Demo complete - hardware working perfectly!")

if __name__ == "__main__":
    main()
