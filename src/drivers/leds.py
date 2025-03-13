from machine import Pin  
import neopixel 
import time

# Number of LEDs in the chain
NUM_LEDS = 7

def scale_color(color, scale):
    """Scale the color values by the given scale factor."""
    return tuple(int(c * scale) for c in color)

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return (pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return (0, pos * 3, 255 - pos * 3)

class LEDs:
    def __init__(self):
        # Pin where WS2812 LEDs are connected
        LEDpin = Pin(26)

        # Maximum brightness constant (0 to 1)
        self.max_brightness = 0.4

        # Create a NeoPixel object
        self.leds = neopixel.NeoPixel(LEDpin, NUM_LEDS)

    def set_led_color(self, led_index, color):
        """Turn on the LED at the given index with the specified color."""
        self.leds[led_index] = scale_color(color, self.max_brightness)
        self.leds.write()
    
    def turn_off_all(self):
        for led_num in range(NUM_LEDS):
            self.leds[led_num] = (0, 0, 0)
        
        self.leds.write()

    def turn_on_led(self, led_index):
        self.leds[led_index] = (0xFF, 0xFF, 0xFF)
        self.leds.write()

    def turn_off_led(self, led_index):
        """Turn off the LED at the given index."""
        self.set_led_color(led_index, (0, 0, 0))

    def rainbow_test_single_led(self, led_index, wait):
        """Perform the rainbow test on a specific LED."""
        for j in range(255):
            color = wheel(j & 255)
            self.leds[led_index] = scale_color(color, self.max_brightness)
            self.leds.write()
            time.sleep_ms(wait) # Delay in milliseconds
    
    def rainbow_test_all_leds(self, wait: int):
        for j in range(255):
            for led_num in range(NUM_LEDS):
                index_offset = (255 // NUM_LEDS) * led_num
                color = wheel((j + index_offset) & 255)
                self.leds[led_num] = scale_color(color, self.max_brightness)
                self.leds.write()
            
            time.sleep_ms(wait)

# while True:
#     # Perform the rainbow test on LED at index 3 (change the index as needed)
#     rainbow_test_single_led(1, 100)  # Adjust the speed by changing the delay (in milliseconds)