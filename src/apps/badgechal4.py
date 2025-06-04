from lib.smart_config import Config
from icontroller import IController
import badgechal
from apps.app import BaseApp
import vga1_bold_16x32
import _thread, time
import machine, neopixel

class BadgeChal4(BaseApp):
    name = "CTF Challenge 4"
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.display1 = self.controller.bsp.displays.display1
        self.display2 = self.controller.bsp.displays.display2
        self.np = neopixel.NeoPixel(machine.Pin(26), 7)

    # LED thread
    def led_sync(self):
        print("[*] LED sync started")
        while True:
            if badgechal.buzzer_state():
                self.np.fill((0, 0, 10))  # dim blue
            else:
                self.np.fill((0, 0, 0))
            self.np.write()
            time.sleep(0.01)  # Check every 10ms

    # Buzzer thread
    def start_challenge(self):
        print("[*] Starting chal4")
        badgechal.chal4()
        print("[*] chal4 complete")

    async def setup(self):
        self.display1.text(vga1_bold_16x32, "Beeping", 70, 100)
        self.display2.text(vga1_bold_16x32, "Badges", 70, 100)
        print("Running Badge Challenge 4")
        # Start both threads
        _thread.start_new_thread(self.led_sync, ())
        _thread.start_new_thread(self.start_challenge, ())
        return None