from drivers.leds import LEDs
import time
leds = LEDs()
led_count = len(leds.leds)
index = 0
direction = 1
while True:
    index += direction
    leds.set_led_color(index, (0xFF, 0xFF, 0xFF))
    if index == 0 or index == led_count - 1:
        direction = -direction
    else:
        leds.set_led_color((index - direction) % led_count, (0x00, 0x00, 0x00))
    
    if index == -1:
        direction = -direction
    elif index == led_count:
        direction = -direction

    time.sleep_ms(250)