from lib.smart_config import Config
from icontroller import IController
import badgechal
from apps.app import BaseApp
import vga1_bold_16x32
import time
import neopixel
from machine import Pin

class BadgeChal3(BaseApp):
    name = "CTF Challenge 3"
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.display1 = self.controller.bsp.displays.display1
        self.display2 = self.controller.bsp.displays.display2

    async def setup(self):
        self.display1.text(vga1_bold_16x32, "Blinky", 70, 100)
        self.display2.text(vga1_bold_16x32, "Lights", 70, 100)
        print("Running Badge Challenge 3")
        # Setup 7 WS2812B LEDs on GPIO 5
        NUM_LEDS = 7
        PIN_NUM = 26
        np = neopixel.NeoPixel(Pin(PIN_NUM), NUM_LEDS)
        pos = 0
        while True:
            try:
                bits = badgechal.chal3(pos)
                for i in range(NUM_LEDS):
                    if bits[i] == '1':
                        np[i] = (0, 0, 10)  # Blue for '1'
                    else:
                        np[i] = (0, 0, 0)    # Off for '0'
                np.write()
                time.sleep(1)
                pos += 1
            except ValueError as e:    
                break
        time.sleep(1)
        for i in range(NUM_LEDS):
            np[i] = (0, 0, 0)    # Off for '0'
        np.write()
        time.sleep(0.2)
        for i in range(NUM_LEDS):
            np[i] = (0, 0, 10)  # Blue for '1'
        np.write()
        time.sleep(0.2)
        for i in range(NUM_LEDS):
            np[i] = (0, 0, 0)    # Off for '0'
        np.write()
        time.sleep(0.2)
        for i in range(NUM_LEDS):
            np[i] = (0, 0, 10)  # Blue for '1'
        np.write()
        time.sleep(0.2)
        for i in range(NUM_LEDS):
            np[i] = (0, 0, 0)    # Off for '0'
        np.write()
