from lib.smart_config import Config
from icontroller import IController
import badgechal
from apps.app import BaseApp
import vga1_bold_16x32
import micropython
import _thread

class BadgeChal2(BaseApp):
    name = "CTF Challenge 2"
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.display1 = self.controller.bsp.displays.display1
        self.display2 = self.controller.bsp.displays.display2

    async def setup(self):
        self.display1.text(vga1_bold_16x32, "Verifying", 50, 100)
        self.display2.text(vga1_bold_16x32, "Keys...", 70, 100)
        print("Running Badge Challenge 2")
        _thread.start_new_thread(badgechal.chal2, ())
        return None
