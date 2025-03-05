import gc
gc.enable()
gc.collect()

from machine import Pin
import neopixel
import json
import displays
import accelerometer
import time
import buttons
import views
import audio

class Views:
    def __init__(self):

        # some things that the views will need
        self.buttons = buttons.Buttons(accelerometer.i2c)
        self.buttons.button_callback = self.button_press
        self.neopixel = neopixel.NeoPixel(Pin(26), 7)
        self.neopixel.fill((0, 0, 0))
        self.neopixel.write()
        i2c_scan = accelerometer.i2c.scan()
        if 0x20 in i2c_scan: # IO expander was added in v2
            self.board_version = 2
        else:
            self.board_version = 1
        self.displays = displays
        name_file = open('name.json')
        self.name = json.loads(name_file.read())
        name_file.close()

        self.view_objects = [
            views.view0.View,
            views.view1.View,
            views.view2.View,
            views.view3.View,
            views.view4.View
        ]

        self.switch_view(0)
    
    def button_press(self, button):
        self.current_view.button_press(button)

    def update(self):
        self.current_view.update()

    def switch_view(self, view):
        self.current_view = self.view_objects[view](self)

views = Views()

while True:
    views.update()
    time.sleep(0.05)
