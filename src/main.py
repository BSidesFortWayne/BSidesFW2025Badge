from apps.analog_clock import AnalogClock
from apps.menu import Menu
from apps.settings import Settings
from apps.voltage_meter import VoltageMeter
from bsp import BSP
import json
import time
from apps import view, view0, view1, view2, view3, view4
import random

import gc

from hardware_rev import HardwareRev

gc.enable()
gc.collect()

class Controller(object):
    current_view: view.BaseApp

    # This is a singleton pattern which gives us a single instance of the 
    # controller object. This is useful for global state 
    def __new__(cls):
        """ creates a singleton object, if it is not created, 
        or else returns the previous singleton object"""
        if not hasattr(cls, 'instance'):
            cls.instance = super(Controller, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        # some things that the views will need
        self.bsp = BSP(HardwareRev.V2)

        print("Callback handlers")

        try:
            name_file = open('name.json')
            self.name = json.loads(name_file.read())
            name_file.close()
        except:
           print("Name file not found")
           self.name = {
               'first': "Bilbo",
               'last': "Baggins",
                'background_image': [
                    'img/bsides_logo.jpg',
                    'img/bsides_logo.jpg'
                ],
                'fg_color': [
                    '#FFFFFF',
                    '#FFFFFF'
                ],
                'bg_color': [
                    '#000000',
                    '#000000'
                ],
                'company': 'Company',
                'title': 'Title'
           }

        print("Make views")
        self.view_objects = [
            view0.View,
            # view1.View,
            # view2.View,
            # view3.View,
            # view4.View
        ]

        print("Register buttons")
        self.bsp.buttons.button_pressed_callbacks.append(self.button_press)
        self.bsp.buttons.button_released_callbacks.append(self.button_release)

        print("Switch to view 0")
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
        
        self.current_view.button_press(button)


    def button_release(self, button: int):
        print(f"Button Relased {button}")
        self.bsp.leds.turn_off_led(button)


    def update(self):
        self.current_view.update()


    def switch_view(self, view: int):
        print("Switch View")
        self.current_view = self.view_objects[view](self)


def main():
    controller = Controller()

    # clock = AnalogClock(controller)
    # main_menu = Menu(controller)

    settings = Settings(controller)

    total_times = 0
    total_counts = 0
    while True:
        # controller.update()
        print("loop")
        x = time.ticks_ms()
        # clock.update()
        settings.update()
        time.sleep(0.05)
        d = time.ticks_diff(time.ticks_ms(), x)
        total_times += d
        total_counts += 1
        if total_counts % 100 == 0:
            average = total_times/total_counts
            print(f"Average: {average} ms")
            print(f"Average Hz: {int(1000/average)} Hz")
        # main_menu.update()

if __name__ == "__main__":
    main()