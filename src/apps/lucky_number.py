from apps.app import BaseApp
import random

class App(BaseApp):
    name = "Lucky Number"
    def __init__(self, controller):
        super().__init__(controller)

        # This button callback will be automatically unregistered once this object is cleaned up/not in view
        # self.register_button_pressed(self.button_press)

    def button_press(self, button: int):
        print(f"Button Press {button}")
        self.controller.bsp.displays.display_center_text(
            f"Your lucky number is {random.randint(1, 100)}"
        )
