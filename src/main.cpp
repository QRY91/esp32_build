#include <Arduino.h>

// Simple blink test for ESP32-S3 Reverse TFT Feather
// This isolates hardware/bootloader issues from TFT complexity

void setup() {
  // Initialize serial for debugging
  Serial.begin(115200);
  
  // Initialize built-in LED pin
  pinMode(LED_BUILTIN, OUTPUT);
  
  // Wait for serial to initialize
  delay(1000);
  
  Serial.println("ESP32-S3 Reverse TFT Feather - Blink Test");
  Serial.println("========================================");
  Serial.printf("LED pin: %d\n", LED_BUILTIN);
  Serial.println("If you see this message, firmware is running!");
}

void loop() {
  // Turn LED on
  digitalWrite(LED_BUILTIN, HIGH);
  Serial.println("LED ON");
  delay(1000);
  
  // Turn LED off  
  digitalWrite(LED_BUILTIN, LOW);
  Serial.println("LED OFF");
  delay(1000);
}