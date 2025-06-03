from apps.app import BaseApp
import random

class App(BaseApp):
    name = "Lucky Number"
    def __init__(self, controller):
        super().__init__(controller)

        self.config.add("lucky_range", 10000)


    async def setup(self):
        self.button_press(0)

    def button_press(self, button: int):
        print(f"Button Press {button}")
        displays = self.controller.bsp.displays
        displays.display1.fill(0x0000)
        lucky_range: int = self.config['lucky_range']
        displays.display_center_text(str(random.randint(0, lucky_range)))
