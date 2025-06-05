import gc9a01
from lib.rolling_average import RollingAverage
from machine import RTC
import time
import framebuf

# These are the battery voltages from 100% to 0%. This is used to find the battery percentage.
voltages = [1214.393, 1213.697, 1212.697, 1211.749, 1210.093, 1209.286, 1208.17, 1207.435, 1206.718, 1206.045, 1205.796, 1205.159, 1204.078, 1203.334, 1202.731, 1201.846, 1201.217, 1200.605, 1200.038, 1199.64, 1199.17, 1198.204, 1197.354, 1196.734, 1196.167, 1195.538, 1194.484, 1193.209, 1192.73, 1192.128, 1191.685, 1191.517, 1191.18, 1190.498, 1190.17, 1189.675, 1188.842, 1187.628, 1187.123, 1186.91, 1185.9, 1185.537, 1184.908, 1184.049, 1183.5, 1182.862, 1182.073, 1181.923, 1181.737, 1180.701, 1179.992, 1179.391, 1178.849, 1178.273, 1177.804, 1177.645, 1177.574, 1177.282, 1176.555, 1176.52, 1175.988, 1175.448, 1175.084, 1174.243, 1173.977, 1173.968, 1173.765, 1173.57, 1173.269, 1173.092, 1172.932, 1172.294, 1172.082, 1171.532, 1171.515, 1171.143, 1170.833, 1170.718, 1170.461, 1169.92, 1169.885, 1169.832, 1169.655, 1169.513, 1169.079, 1168.45, 1168.335, 1168.149, 1167.476, 1167.113, 1167.068, 1166.9, 1166.776, 1165.996, 1165.802, 1165.713, 1164.951, 1164.8, 1164.41, 1164.145, 1163.95, 1163.622, 1163.294, 1162.958, 1162.533, 1161.965, 1161.345, 1160.921, 1160.894, 1160.841, 1160.646, 1159.884, 1159.149, 1159.131, 1159.042, 1158.529, 1158.298, 1158.077, 1157.855, 1156.784, 1156.385, 1156.296, 1156.181, 1155.924, 1155.437, 1154.711, 1154.534, 1154.347, 1153.701, 1152.904, 1152.797, 1152.54, 1151.814, 1151.672, 1151.344, 1150.68, 1150.662, 1150.326, 1149.652, 1149.466, 1149.121, 1148.226, 1148.067, 1147.633, 1147.562, 1147.456, 1146.41, 1146.313, 1145.817, 1145.125, 1144.94, 1144.727, 1144.187, 1143.478, 1143.0, 1142.885, 1142.867, 1142.832, 1142.38, 1142.22, 1140.759, 1140.298, 1140.254, 1139.572, 1139.014, 1138.287, 1138.181, 1138.013, 1137.18, 1137.021, 1136.631, 1135.913, 1134.868, 1134.585, 1134.115, 1134.009, 1133.779, 1133.566, 1133.548, 1133.362, 1131.847, 1131.759, 1131.741, 1131.201, 1130.838, 1130.182, 1129.483, 1128.907, 1128.72, 1128.508, 1128.056, 1127.551, 1126.719, 1125.974, 1125.514, 1125.337, 1124.761, 1124.451, 1123.893, 1122.98, 1122.786, 1122.52, 1121.961, 1121.457, 1120.642, 1119.862, 1119.552, 1119.278, 1118.923, 1118.64, 1118.233, 1117.4, 1116.345, 1115.681, 1115.663, 1115.61, 1115.141, 1114.592, 1114.229, 1113.794, 1113.024, 1112.474, 1111.961, 1111.562, 1111.163, 1110.57, 1110.074, 1110.056, 1109.534, 1109.02, 1108.745, 1108.488, 1108.32, 1107.496, 1106.779, 1106.681, 1106.628, 1105.494, 1104.582, 1104.502, 1104.21, 1103.431, 1103.182, 1103.041, 1102.978, 1102.544, 1102.208, 1101.703, 1101.455, 1100.684, 1100.303, 1100.224, 1099.134, 1098.957, 1098.851, 1098.434, 1098.372, 1098.23, 1097.531, 1097.247, 1097.088, 1096.237, 1095.546, 1095.458, 1094.891, 1094.129, 1093.943, 1093.695, 1093.598, 1093.536, 1092.889, 1092.1, 1091.764, 1091.401, 1090.993, 1090.834, 1090.488, 1089.912, 1089.7, 1089.664, 1089.283, 1088.805, 1088.619, 1088.433, 1088.247, 1087.654, 1086.812, 1086.617, 1086.042, 1085.97, 1085.714, 1084.89, 1084.65, 1084.376, 1084.217, 1083.951, 1083.844, 1083.091, 1083.011, 1082.985, 1082.108, 1081.763, 1081.373, 1080.983, 1080.593, 1080.009, 1079.911, 1079.867, 1079.229, 1078.884, 1078.592, 1078.202, 1077.962, 1077.661, 1077.13, 1077.033, 1076.776, 1076.475, 1075.376, 1075.022, 1075.021, 1074.827, 1074.393, 1074.092, 1073.985, 1073.675, 1073.604, 1073.276, 1072.727, 1072.16, 1071.974, 1071.744, 1071.381, 1071.248, 1071.133, 1071.018, 1070.273, 1069.6, 1069.397, 1069.396, 1068.927, 1068.449, 1067.979, 1067.661, 1067.297, 1066.979, 1066.934, 1066.34, 1065.951, 1065.632, 1065.145, 1065.03, 1064.676, 1064.126, 1063.47, 1063.205, 1063.001, 1062.345, 1061.681, 1061.415, 1061.184, 1060.689, 1060.184, 1059.83, 1059.608, 1059.156, 1058.501, 1057.669, 1057.208, 1057.075, 1056.739, 1056.154, 1055.631, 1055.516, 1054.922, 1054.294, 1053.841, 1053.372, 1052.85, 1052.398, 1051.671, 1050.98, 1050.714, 1050.36, 1049.943, 1049.332, 1049.165, 1048.925, 1047.711, 1046.834, 1046.365, 1045.993, 1045.834, 1045.453, 1045.037, 1044.682, 1043.956, 1043.451, 1043.141, 1042.653, 1042.308, 1041.874, 1041.475, 1041.13, 1040.43, 1039.792, 1039.376, 1039.013, 1038.561, 1038.03, 1037.64, 1037.223, 1036.833, 1036.532, 1036.151, 1035.806, 1035.452, 1034.938, 1034.38, 1033.839, 1033.352, 1032.848, 1032.307, 1031.713, 1031.138, 1030.588, 1029.879, 1029.225, 1028.693, 1028.108, 1027.373, 1026.62, 1025.814, 1024.884, 1023.91, 1022.5, 1021.03, 1019.4, 1017.461, 1015.982, 1014.91, 1013.687, 1011.888, 1009.532, 1006.99, 1004.448, 1001.826, 999.3809, 996.2187, 993.0031, 990.0176, 986.758, 983.1174, 979.3525, 975.2773, 970.813, 965.914, 961.2813, 956.9054, 951.8917, 946.6389, 939.8358, 933.3069, 927.4872, 920.0111, 911.7636, 905.3594, 902.1348, 900.5759, 900.0089, 900.0]

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
        # print(f'adc_callback: {value}')
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
