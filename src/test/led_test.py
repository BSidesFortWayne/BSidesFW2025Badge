from drivers.leds import LEDs
leds = LEDs()
led_count = len(leds.leds)
index = 0
direction = 1
color = (0, 0, 0xFF)

# leds.color_bounce(color, 100, fade=False)
while True:
    leds.rainbow_test_all_leds(1)

