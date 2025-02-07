#include <stdint.h>
#include <Adafruit_GFX.h>
#include <Adafruit_GC9A01A.h>
#include <Adafruit_NeoPixel.h>
#include <SPI.h>
#include "image.h"

#define LED_PIN 26       // WS2812B data line
#define LED_COUNT 4      // Number of WS2812B LEDs
#define CONTROL_PIN 16

#define SCK   18
#define MOSI  23

// Display 1
#define CS1   5
#define DC1   22
#define RST1  14

// Display 2
#define CS2   4
#define DC2   21
#define RST2  27

Adafruit_GC9A01A tft1(CS1, DC1, MOSI, SCK, RST1, -1);  // -1 means no MISO
Adafruit_GC9A01A tft2(CS2, DC2, MOSI, SCK, RST2, -1);
Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

void setup() {
  Serial.begin(115200);
  pinMode(CONTROL_PIN, OUTPUT);
  digitalWrite(CONTROL_PIN, HIGH);

  strip.begin();
  strip.show();
  
  // Initialize first display
  tft1.begin();
  tft1.setRotation(3);
  delay(500);

  tft1.drawRGBBitmap(0, 0, (const uint16_t*)gimp_image.pixel_data, gimp_image.width, gimp_image.height);

  // Initialize second display
  tft2.begin();
  tft2.setRotation(3);

  tft2.drawRGBBitmap(0, 0, (const uint16_t*)gimp_image.pixel_data, gimp_image.width, gimp_image.height);
}

void loop() {
    strip.setPixelColor(0, strip.Color(64, 0, 0));
    strip.setPixelColor(1, strip.Color(32, 32, 32));
    strip.setPixelColor(2, strip.Color(0, 0, 64));
    strip.setPixelColor(3, strip.Color(64, 0, 0));
    strip.show();
}

void setColor(uint8_t red, uint8_t green, uint8_t blue) {
    for (int i = 0; i < LED_COUNT; i++) {
        strip.setPixelColor(i, strip.Color(red, green, blue));
    }
    strip.show();
}
