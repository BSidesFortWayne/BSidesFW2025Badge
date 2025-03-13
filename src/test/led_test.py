from drivers.leds import LEDs, scale_color
import time
leds = LEDs()
led_count = len(leds.leds)
index = 0
direction = 1
color = (0xFF, 0, 0)

leds.color_bounce(color, 500)