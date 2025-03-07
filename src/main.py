from bsp import BSP
import json
import time
from apps import view, view0, view1, view2, view3, view4
import random

import gc
gc.enable()
gc.collect()

class Controller:
    current_view: view.View
    def __init__(self):
        # some things that the views will need
        self.bsp = BSP()

        self.bsp.buttons.button_pressed_callbacks.append(self.button_press)
        self.bsp.buttons.button_released_callbacks.append(self.button_release)

        try:
            name_file = open('name.json')
            self.name = json.loads(name_file.read())
            name_file.close()
        except:
           self.name = {
               'first': "Bilbo",
               'last': "Baggins"
           }

        self.view_objects = [
            view0.View,
            view1.View,
            view2.View,
            view3.View,
            view4.View
        ]

        self.switch_view(0)


    # TODO temporary shadow property for backwards compatibility
    @property
    def displays(self):
        return self.bsp.displays

    @property
    def neopixel(self):
        return self.bsp.leds.leds
    
    def button_press(self, button: int):
        print(f"Button Press {button}")
        self.bsp.leds.set_led_color(button, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        
        # self.current_view.button_press(button)


    def button_release(self, button: int):
        print(f"Button Relased {button}")
        self.bsp.leds.turn_off_led(button)


    def update(self):
        self.current_view.update()


    def switch_view(self, view: int):
        print("Switch View")
        self.current_view = self.view_objects[view](self)

v = Controller()

while True:
    v.update()
    time.sleep(0.05)
