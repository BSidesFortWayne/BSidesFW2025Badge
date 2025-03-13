from apps.view import BaseApp
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
        
        self.font = arial32px

        self.center = self.display1.width() // 2

        self.rtc = RTC()

        self.rtc.datetime((2025, 3, 8, 6, 9, 18, 50, 0))

        self.max_readings = 100
        self.readings_mv = [0 for _ in range(self.max_readings)]
        self.readings_raw = [0 for _ in range(self.max_readings)]
        self.readings_index = 0


    def draw_voltage_meter(self):
        raw = self.controller.bsp.imu.read_adc_raw(1)
        mv = self.controller.bsp.imu.read_adc_mV(1)

        index = self.readings_index
        self.readings_mv[index] = mv
        self.readings_raw[index] = raw
        self.readings_index = (index + 1) % self.max_readings

        print(f'{mv}mv')
        self.display1.fill(gc9a01.BLACK)
        
        self.display1.write(
            self.font,
            f'{sum(self.readings_mv) / self.max_readings}mv',
            10,
            100,
            gc9a01.WHITE,
            gc9a01.BLACK
        )

        self.display1.write(
            self.font,
            f'{sum(self.readings_raw) / self.max_readings} counts',
            10,
            140,
            gc9a01.WHITE,
            gc9a01.BLACK
        )

    def update(self):
        self.draw_voltage_meter()