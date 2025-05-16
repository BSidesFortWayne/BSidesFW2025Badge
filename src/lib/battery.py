import gc9a01
from lib.rolling_average import RollingAverage
from machine import RTC
import time
import framebuf

# These are the battery voltages from 100% to 0%. This is used to find the battery percentage.
voltages = [1124.6666666666667, 1103.6666666666667, 1100.3333333333333, 1098.6666666666667, 1096.6666666666667, 1095.0, 1093.6666666666667, 1091.6666666666667, 1090.0, 1088.3333333333333, 1086.3333333333333, 1085.6666666666667, 1083.3333333333333, 1082.0, 1080.3333333333333, 1078.6666666666667, 1077.0, 1075.3333333333333, 1074.0, 1072.3333333333333, 1072.0, 1070.6666666666667, 1069.3333333333333, 1067.6666666666667, 1066.6666666666667, 1065.0, 1063.6666666666667, 1062.3333333333333, 1061.3333333333333, 1059.6666666666667, 1058.3333333333333, 1057.3333333333333, 1056.0, 1055.0, 1054.0, 1052.6666666666667, 1051.6666666666667, 1050.3333333333333, 1048.0, 1047.0, 1046.3333333333333, 1045.3333333333333, 1043.6666666666667, 1042.6666666666667, 1042.0, 1040.6666666666667, 1039.6666666666667, 1039.0, 1038.0, 1036.6666666666667, 1035.0, 1034.6666666666667, 1034.6666666666667, 1034.6666666666667, 1033.0, 1032.6666666666667, 1031.6666666666667, 1031.3333333333333, 1030.0, 1029.6666666666667, 1029.0, 1028.3333333333333, 1027.3333333333333, 1026.3333333333333, 1025.3333333333333, 1024.0, 1022.6666666666666, 1022.0, 1020.6666666666666, 1020.0, 1019.3333333333334, 1018.3333333333334, 1016.6666666666666, 1015.6666666666666, 1014.3333333333334, 1013.3333333333334, 1013.0, 1012.0, 1010.6666666666666, 1009.3333333333334, 1008.3333333333334, 1006.6666666666666, 1005.3333333333334, 1003.6666666666666, 1002.6666666666666, 1001.3333333333334, 1000.0, 999.0, 997.6666666666666, 996.3333333333334, 995.3333333333334, 993.3333333333334, 991.6666666666666, 990.0, 988.0, 985.0, 982.3333333333334, 978.3333333333334, 973.3333333333334, 967.0, 959.3333333333334, 949.6666666666666, 937.0, 924.0, 908.3333333333334, 900.3333333333334, 900.0, 1124.6666666666667, 1103.6666666666667, 1100.3333333333333, 1098.6666666666667, 1096.6666666666667, 1095.0, 1093.6666666666667, 1091.6666666666667, 1090.0, 1088.3333333333333, 1086.3333333333333, 1085.6666666666667, 1083.3333333333333, 1082.0, 1080.3333333333333, 1078.6666666666667, 1077.0, 1075.3333333333333, 1074.0, 1072.3333333333333, 1072.0, 1070.6666666666667, 1069.3333333333333, 1067.6666666666667, 1066.6666666666667, 1065.0, 1063.6666666666667, 1062.3333333333333, 1061.3333333333333, 1059.6666666666667, 1058.3333333333333, 1057.3333333333333, 1056.0, 1055.0, 1054.0, 1052.6666666666667, 1051.6666666666667, 1050.3333333333333, 1048.0, 1047.0, 1046.3333333333333, 1045.3333333333333, 1043.6666666666667, 1042.6666666666667, 1042.0, 1040.6666666666667, 1039.6666666666667, 1039.0, 1038.0, 1036.6666666666667, 1035.0, 1034.6666666666667, 1034.6666666666667, 1034.6666666666667, 1033.0, 1032.6666666666667, 1031.6666666666667, 1031.3333333333333, 1030.0, 1029.6666666666667, 1029.0, 1028.3333333333333, 1027.3333333333333, 1026.3333333333333, 1025.3333333333333, 1024.0, 1022.6666666666666, 1022.0, 1020.6666666666666, 1020.0, 1019.3333333333334, 1018.3333333333334, 1016.6666666666666, 1015.6666666666666, 1014.3333333333334, 1013.3333333333334, 1013.0, 1012.0, 1010.6666666666666, 1009.3333333333334, 1008.3333333333334, 1006.6666666666666, 1005.3333333333334, 1003.6666666666666, 1002.6666666666666, 1001.3333333333334, 1000.0, 999.0, 997.6666666666666, 996.3333333333334, 995.3333333333334, 993.3333333333334, 991.6666666666666, 990.0, 988.0, 985.0, 982.3333333333334, 978.3333333333334, 973.3333333333334, 967.0, 959.3333333333334, 949.6666666666666, 937.0, 924.0, 908.3333333333334, 900.3333333333334, 900.0]


class Battery:
    def __init__(self, controller):
        self.controller = controller
        self.battery_mem_buf = bytearray(30*30*2)
        self.battery_fbuf_mv = memoryview(self.battery_mem_buf)
        self.battery_fbuf = framebuf.FrameBuffer(
            self.battery_mem_buf,
            30,
            30,
            framebuf.RGB565
        )
        self.battery_fbuf.fill(gc9a01.BLACK)
        # Draw battery outline
        for y in range(1, 4):
            self.battery_fbuf.hline(9, 3+y, 9, gc9a01.WHITE)
            self.battery_fbuf.rect(5+y, 5+y, 17-(y*2), 23-(y*2), gc9a01.WHITE, False)

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
    
    def find_closest_voltage(self, current_voltage):
        current_voltage = self.mv_average.average()

        lo, hi = 0, len(voltages) - 1

        # Handle current_voltages outside the list’s range fast
        if current_voltage >= voltages[0]:
            return voltages[0]
        if current_voltage <= voltages[-1]:
            return voltages[-1]

        # Binary search to find the last element ≥ current_voltage (since list is voltagesending)
        while lo <= hi:
            mid = (lo + hi) // 2
            if voltages[mid] == current_voltage:          # exact hit
                return voltages[mid]
            elif voltages[mid] > current_voltage:
                lo = mid + 1                 # current_voltage is farther right (smaller indices hold larger numbers)
            else:                            # voltages[mid] < current_voltage
                hi = mid - 1                 # current_voltage is farther left

        # After the loop, hi is the index of the biggest element smaller than current_voltage
        # and lo is the index of the smallest element larger than current_voltage.
        left_idx, right_idx = hi, lo
        left_val, right_val = voltages[left_idx], voltages[right_idx]

        # Decide which neighbor is closer; tie goes to the larger value (left_val)
        if abs(left_val - current_voltage) <= abs(right_val - current_voltage):
            return left_val
        else:
            return right_val
        
    def get_battery_percentage(self):
        closest_voltage = self.find_closest_voltage(self.mv_average.average())
        return 100-round((voltages.index(closest_voltage)/(len(voltages)-1))*100, 2)

    def rgb_to_565(self, r: int, g: int, b: int):
        return (r & 0xF8) | ((g & 0xE0) >> 5) | ((g & 0x1C) << 11) | ((b & 0xF8) << 5)

    def get_battery_color(self, percentage):
        s = max(0, min(100, percentage))

        # Gradient key-points: (percentage, (R, G, B))
        stops = [
            (100, (  0, 255,   0)),   # green
            ( 66, (255, 255,   0)),   # yellow
            ( 33, (255, 165,   0)),   # orange
            (  0, (255,   0,   0)),   # red
        ]

        # Find the two surrounding stops
        for (hi_v, hi_c), (lo_v, lo_c) in zip(stops, stops[1:]):
            if s >= lo_v:
                # Percentage between the two stops
                t = (s - lo_v) / (hi_v - lo_v) if hi_v != lo_v else 0
                # Linear interpolation of each channel
                return tuple(
                    int(round(lo + t * (hi - lo)))
                    for lo, hi in zip(lo_c, hi_c)
                )

        # Fallback (shouldn’t be reached)
        return stops[-1][1]

    def draw_battery(self, display, position):
        percentage = self.get_battery_percentage()
        battery_color = self.get_battery_color(percentage)
        battery_color = self.rgb_to_565(battery_color[0], battery_color[1], battery_color[2])

        self.battery_fbuf.rect( # clear battery
            9,
            9,
            9,
            15,
            gc9a01.BLACK,
            True
        )

        self.battery_fbuf.rect(
            9,
            9+(15-round(((percentage/100)*15))),
            9,
            round(((percentage/100)*15)),
            battery_color,
            True
        )

        if type(display) == gc9a01.GC9A01:
            display.blit_buffer(self.battery_fbuf_mv, position[0], position[1], 30, 30)
        else: # Framebuffer
            display.blit(self.battery_fbuf, position[0], position[1])
