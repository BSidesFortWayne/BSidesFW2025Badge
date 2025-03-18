from apps.app import BaseApp
import gc9a01 
from machine import RTC 

import fonts.arial32px as arial32px
from lib.rolling_average import RollingAverage


class VoltageMeter(BaseApp):
    name = "Voltage Meter"
    version = "0.0.3"
    def __init__(self, controller):
        super().__init__(controller)
        self.display1 = self.controller.bsp.displays.display1

        self.bg_color = gc9a01.WHITE
        self.fg_color = gc9a01.BLACK
        
        self.font = arial32px

        self.center = self.display1.width() // 2

        self.rtc = RTC()

        self.rtc.datetime((2025, 3, 8, 6, 9, 18, 50, 0))

        self.mv_average = RollingAverage(100)
        self.raw_average = RollingAverage(100)
        # self.max_readings = 100
        # self.readings_mv = [0 for _ in range(self.max_readings)]
        # self.readings_raw = [0 for _ in range(self.max_readings)]
        # self.readings_index = 0


    def draw_voltage_meter(self):
        raw = self.controller.bsp.imu.read_adc_raw(1)
        mv = self.controller.bsp.imu.read_adc_mV(1)

        # print(f'{raw}raw, {mv}mv')
        self.mv_average.add(mv)
        self.raw_average.add(raw)

        self.display1.fill(gc9a01.BLACK)
        
        self.display1.write(
            self.font,
            f'{self.raw_average.average()}mv',
            10,
            100,
            gc9a01.WHITE,
            gc9a01.BLACK
        )

        self.display1.write(
            self.font,
            f'{self.mv_average.average()}mv',
            10,
            140,
            gc9a01.WHITE,
            gc9a01.BLACK
        )

    def update(self):
        self.draw_voltage_meter()