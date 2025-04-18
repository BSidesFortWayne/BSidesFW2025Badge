from apps.app import BaseApp
import gc9a01 
from machine import RTC

import time

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

        self.mv_average = RollingAverage(100)
        # self.raw_average = RollingAverage(100)
        # self.max_readings = 100
        # self.readings_mv = [0 for _ in range(self.max_readings)]
        # self.readings_raw = [0 for _ in range(self.max_readings)]
        # self.readings_index = 0
        
        self.last_log_time = 0

        self.seconds_between_log = 60

        self.controller.bsp.imu.adc_callbacks.append(self.adc_callback)


    async def adc_callback(self, value):
        print(f'adc_callback: {value}')
        self.mv_average.add(value)
        now = time.time()
        time_since_log = now - self.last_log_time
        if time_since_log > self.seconds_between_log:
            rtc_datetime = self.controller.bsp.rtc.datetime()
            time_str = f'{rtc_datetime[0]}-{rtc_datetime[1]}-{rtc_datetime[2]} {rtc_datetime[4]}:{rtc_datetime[5]}:{rtc_datetime[6]}'
            csv_line = f'{time_str},{value}'
            print(csv_line)
            with open('voltages.csv', 'a') as f:
                f.write(f'{time_str},{self.mv_average.average()}\n')
            self.last_log_time = now


    def draw_voltage_meter(self):
        # print(f'{raw}raw, {mv}mv')
        # self.raw_average.add(raw)

        self.display1.fill(gc9a01.BLACK)

        self.display1.write(
            self.font,
            f'{self.mv_average.average()} mv',
            30,
            120,
            gc9a01.WHITE,
            gc9a01.BLACK
        )

    async def update(self):
        self.draw_voltage_meter()


if __name__ == "__main__":
    from single_app_runner import run_app
    run_app(VoltageMeter, perf=True)