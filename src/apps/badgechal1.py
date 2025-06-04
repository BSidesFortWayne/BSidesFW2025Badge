from lib.smart_config import Config
from icontroller import IController
import badgechal
from apps.app import BaseApp

class BadgeChal1(BaseApp):
    name = "CTF Challenge 1"
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.display1 = self.controller.bsp.displays.display1
        self.display2 = self.controller.bsp.displays.display2
        self.display_center_text = self.controller.bsp.displays.display_center_text
        self.display_text = self.controller.bsp.displays.display_text

    async def setup(self):
        self.display_center_text("You Art?")
        print("Running Badge Challenge 1")
        badgechal.chal1()
        return None
