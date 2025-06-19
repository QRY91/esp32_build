#include <Arduino.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7789.h>
#include <SPI.h>

// TFT display pins for ESP32-S3 TFT Feather
#define TFT_CS         7
#define TFT_RST        40
#define TFT_DC         39
#define TFT_BACKLIGHT  45

// Display dimensions
#define TFT_WIDTH  240
#define TFT_HEIGHT 135

// Create display object
Adafruit_ST7789 tft = Adafruit_ST7789(TFT_CS, TFT_DC, TFT_RST);

// Button pins (using your Arduino kit buttons on breadboard)
// Connect these to GPIO pins with pull-up resistors
#define BUTTON_UP    12
#define BUTTON_DOWN  13
#define BUTTON_LEFT  14
#define BUTTON_RIGHT 15
#define BUTTON_A     16
#define BUTTON_B     17

// Game state variables
int cursor_x = TFT_WIDTH / 2;
int cursor_y = TFT_HEIGHT / 2;
int score = 0;
unsigned long last_update = 0;
bool demo_mode = true;

// Function prototypes
void drawWelcomeScreen();
void drawGameScreen();
void drawTestGraphics();
void handleButtons();
void handleButtonPress(int button);
void updateDisplay();

void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  while (!Serial) delay(10);
  
  Serial.println("ESP32-S3 TFT Feather - DeskHog Development");
  Serial.println("=========================================");
  
  // Initialize button pins with internal pull-up resistors
  pinMode(BUTTON_UP, INPUT_PULLUP);
  pinMode(BUTTON_DOWN, INPUT_PULLUP);  
  pinMode(BUTTON_LEFT, INPUT_PULLUP);
  pinMode(BUTTON_RIGHT, INPUT_PULLUP);
  pinMode(BUTTON_A, INPUT_PULLUP);
  pinMode(BUTTON_B, INPUT_PULLUP);
  
  // Initialize TFT display
  Serial.println("Initializing TFT display...");
  
  // Turn on backlight
  pinMode(TFT_BACKLIGHT, OUTPUT);
  digitalWrite(TFT_BACKLIGHT, HIGH);
  
  // Initialize display with correct orientation
  tft.init(TFT_WIDTH, TFT_HEIGHT);
  tft.setRotation(1);  // Landscape mode
  
  // Clear screen with black background
  tft.fillScreen(ST77XX_BLACK);
  
  Serial.println("Display initialized successfully!");
  
  // Welcome screen
  drawWelcomeScreen();
  delay(2000);
  
  // Switch to interactive mode
  demo_mode = false;
  drawGameScreen();
  
  Serial.println("Ready for input! Use your breadboard buttons:");
  Serial.println("- Arrow keys: Move cursor");
  Serial.println("- A button: Increment score");
  Serial.println("- B button: Reset");
}

void loop() {
  // Handle button input
  handleButtons();
  
  // Update display periodically
  if (millis() - last_update > 100) {
    updateDisplay();
    last_update = millis();
  }
  
  // Small delay to prevent overwhelming the system
  delay(10);
}

void drawWelcomeScreen() {
  tft.fillScreen(ST77XX_BLACK);
  
  // Title
  tft.setTextColor(ST77XX_CYAN);
  tft.setTextSize(2);
  tft.setCursor(20, 20);
  tft.println("DeskHog Dev");
  
  // Subtitle
  tft.setTextColor(ST77XX_WHITE);
  tft.setTextSize(1);
  tft.setCursor(20, 50);
  tft.println("ESP32-S3 TFT Feather");
  
  // Status
  tft.setTextColor(ST77XX_GREEN);
  tft.setCursor(20, 70);
  tft.println("Display: OK");
  tft.setCursor(20, 85);
  tft.println("Buttons: Ready");
  
  // Fun graphics
  drawTestGraphics();
}

void drawGameScreen() {
  tft.fillScreen(ST77XX_BLACK);
  
  // Header
  tft.setTextColor(ST77XX_YELLOW);
  tft.setTextSize(1);
  tft.setCursor(5, 5);
  tft.println("Cursor Demo - Use Buttons!");
  
  // Draw border
  tft.drawRect(0, 15, TFT_WIDTH, TFT_HEIGHT - 15, ST77XX_WHITE);
}

void drawTestGraphics() {
  // Draw some colorful rectangles
  tft.fillRect(150, 30, 20, 20, ST77XX_RED);
  tft.fillRect(175, 30, 20, 20, ST77XX_GREEN);
  tft.fillRect(200, 30, 20, 20, ST77XX_BLUE);
  
  // Draw a circle
  tft.fillCircle(160, 70, 15, ST77XX_MAGENTA);
  
  // Draw some lines
  for (int i = 0; i < 5; i++) {
    tft.drawLine(150 + i * 5, 90, 150 + i * 5, 110, ST77XX_CYAN);
  }
}

void handleButtons() {
  static bool button_states[6] = {false};
  static unsigned long button_timers[6] = {0};
  const unsigned long debounce_delay = 50;
  
  // Button pins array
  int buttons[] = {BUTTON_UP, BUTTON_DOWN, BUTTON_LEFT, BUTTON_RIGHT, BUTTON_A, BUTTON_B};
  
  for (int i = 0; i < 6; i++) {
    bool current_state = !digitalRead(buttons[i]); // Inverted because of pull-up
    
    // Debouncing
    if (current_state != button_states[i]) {
      button_timers[i] = millis();
    }
    
    if ((millis() - button_timers[i]) > debounce_delay) {
      if (current_state && !button_states[i]) {
        // Button just pressed
        handleButtonPress(i);
      }
      button_states[i] = current_state;
    }
  }
}

void handleButtonPress(int button) {
  const int move_speed = 5;
  
  switch (button) {
    case 0: // UP
      cursor_y = max(20, cursor_y - move_speed);
      Serial.println("UP pressed");
      break;
      
    case 1: // DOWN
      cursor_y = min(TFT_HEIGHT - 10, cursor_y + move_speed);
      Serial.println("DOWN pressed");
      break;
      
    case 2: // LEFT
      cursor_x = max(5, cursor_x - move_speed);
      Serial.println("LEFT pressed");
      break;
      
    case 3: // RIGHT
      cursor_x = min(TFT_WIDTH - 10, cursor_x + move_speed);
      Serial.println("RIGHT pressed");
      break;
      
    case 4: // A
      score++;
      Serial.printf("A pressed - Score: %d\n", score);
      break;
      
    case 5: // B
      score = 0;
      cursor_x = TFT_WIDTH / 2;
      cursor_y = TFT_HEIGHT / 2;
      Serial.println("B pressed - Reset");
      break;
  }
}

void updateDisplay() {
  if (demo_mode) return;
  
  // Clear previous cursor (draw black rectangle)
  static int last_x = cursor_x;
  static int last_y = cursor_y;
  
  if (last_x != cursor_x || last_y != cursor_y) {
    tft.fillRect(last_x - 2, last_y - 2, 9, 9, ST77XX_BLACK);
  }
  
  // Draw new cursor
  tft.fillRect(cursor_x - 2, cursor_y - 2, 5, 5, ST77XX_RED);
  tft.drawRect(cursor_x - 3, cursor_y - 3, 7, 7, ST77XX_WHITE);
  
  // Update score display
  static int last_score = -1;
  if (score != last_score) {
    // Clear previous score
    tft.fillRect(150, 5, 80, 10, ST77XX_BLACK);
    
    // Draw new score
    tft.setTextColor(ST77XX_GREEN);
    tft.setTextSize(1);
    tft.setCursor(150, 5);
    tft.printf("Score: %d", score);
    
    last_score = score;
  }
  
  // Update position tracking
  last_x = cursor_x;
  last_y = cursor_y;
  
  // Display coordinates in serial for debugging
  static unsigned long coord_timer = 0;
  if (millis() - coord_timer > 1000) {
    Serial.printf("Position: (%d, %d), Score: %d\n", cursor_x, cursor_y, score);
    coord_timer = millis();
  }
}