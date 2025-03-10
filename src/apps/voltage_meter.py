from apps import BaseApp
import gc9a01 
import math
from machine import RTC 

import fonts.arial16px as arial16px
import fonts.arial32px as arial32px


class VoltageMeter(BaseApp):
    def __init__(self, controller):
        self.controller = controller
        self.display1 = self.controller.bsp.displays.display1

        self.bg_color = gc9a01.WHITE
        self.fg_color = gc9a01.BLACK
        
        self.font = arial16px

        self.center = self.display1.width() // 2

        self.rtc = RTC()

        self.rtc.datetime((2025, 3, 8, 6, 9, 18, 50, 0))

        mv = self.controller.bsp.imu.read_adc_mV(1)


    def draw_voltage_meter(self):
        mv = self.controller.bsp.imu.read_adc_mV(1)
        print(f'{mv}mv')
        self.display1.fill(gc9a01.BLACK)

        # Draw something like a battery bar
        # self.display1.rect(10, 10, 20, 100, gc9a01.WHITE)
        # self.display1.fill_rect(10, 10, 20, 100, gc9a01.WHITE)
        # self.display1.fill_rect(10, 10, 20, 100 - int(mv / 10), gc9a01.BLACK)
        # self.display1.rect(10, 10, 20, 100, gc9a01.WHITE)
        
        self.display1.write(
            arial16px,
            f'{mv}mv',
            10,
            120,
            gc9a01.WHITE,
            gc9a01.BLACK
        )

    def update(self):
        self.draw_voltage_meter()