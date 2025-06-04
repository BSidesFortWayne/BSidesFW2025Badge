from lib.smart_config import Config
from icontroller import IController
import badgechal
from apps.app import BaseApp
import vga1_bold_16x32
import time
import neopixel
import micropython
from machine import Pin
import _thread

class BadgeChal3(BaseApp):
    name = "CTF Challenge 3"
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.display1 = self.controller.bsp.displays.display1
        self.display2 = self.controller.bsp.displays.display2
        self.running = False
        self.NUM_LEDS = 7
        PIN_NUM = 26
        self.np = neopixel.NeoPixel(Pin(PIN_NUM), self.NUM_LEDS)

    async def teardown(self):
        self.running = False
        # Turn off all LEDs
        
        self.np.fill((0, 0, 0))
        
        self.np.write()
    
    async def setup(self):
        self.display1.text(vga1_bold_16x32, "Blinky", 70, 100)
        self.display2.text(vga1_bold_16x32, "Lights", 70, 100)
        print("Running Badge Challenge 3")
        _thread.start_new_thread(self.challenge, ())
    
    def challenge(self):
        pos = 0
        self.running = True
        while self.running:
            try:
                # Setup 7 WS2812B LEDs on GPIO 5
                
                bits = badgechal.chal3(pos)
                for i in range(self.NUM_LEDS):
                    if bits[i] == '1':
                        self.np[i] = (0, 0, 10)  # Blue for '1'
                    else:
                        self.np[i] = (0, 0, 0)    # Off for '0'
                self.np.write()
                time.sleep(1)
                pos += 1
            except ValueError as e:    
                break
        time.sleep(1)
        for i in range(self.NUM_LEDS):
            self.np[i] = (0, 0, 0)    # Off for '0'
        self.np.write()
        time.sleep(0.2)
        for i in range(self.NUM_LEDS):
            self.np[i] = (0, 0, 10)  # Blue for '1'
        self.np.write()
        time.sleep(0.2)
        for i in range(self.NUM_LEDS):
            self.np[i] = (0, 0, 0)    # Off for '0'
        self.np.write()
        time.sleep(0.2)
        for i in range(self.NUM_LEDS):
            self.np[i] = (0, 0, 10)  # Blue for '1'
        self.np.write()
        time.sleep(0.2)
        for i in range(self.NUM_LEDS):
            self.np[i] = (0, 0, 0)    # Off for '0'
        self.np.write()
