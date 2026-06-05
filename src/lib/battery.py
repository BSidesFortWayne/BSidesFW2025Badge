import gc9a01
from lib.rolling_average import RollingAverage
from machine import RTC
import time
import framebuf

# These are the battery voltages from 100% to 0%. This is used to find the battery percentage.
voltages = [4068.217, 4065.885, 4062.535, 4059.359, 4053.812, 4051.108, 4047.370, 4044.907, 4042.505, 4040.251, 4039.417, 4037.283, 4033.661, 4031.169, 4029.149, 4026.184, 4024.077, 4022.027, 4020.127, 4018.794, 4017.220, 4013.983, 4011.136, 4009.059, 4007.159, 4005.052, 4001.521, 3997.250, 3995.646, 3993.629, 3992.145, 3991.582, 3990.453, 3988.168, 3987.070, 3985.411, 3982.621, 3978.554, 3976.862, 3976.149, 3972.765, 3971.549, 3969.442, 3966.564, 3964.725, 3962.588, 3959.945, 3959.442, 3958.819, 3955.348, 3952.973, 3950.960, 3949.144, 3947.215, 3945.643, 3945.111, 3944.873, 3943.895, 3941.459, 3941.342, 3939.560, 3937.751, 3936.531, 3933.714, 3932.823, 3932.793, 3932.113, 3931.459, 3930.451, 3929.858, 3929.322, 3927.185, 3926.475, 3924.632, 3924.575, 3923.329, 3922.291, 3921.905, 3921.044, 3919.232, 3919.115, 3918.937, 3918.344, 3917.869, 3916.415, 3914.308, 3913.922, 3913.299, 3911.045, 3909.829, 3909.678, 3909.115, 3908.700, 3906.087, 3905.437, 3905.139, 3902.586, 3902.080, 3900.774, 3899.886, 3899.233, 3898.134, 3897.035, 3895.909, 3894.486, 3892.583, 3890.506, 3889.085, 3888.995, 3888.817, 3888.164, 3885.611, 3883.149, 3883.089, 3882.791, 3881.072, 3880.298, 3879.558, 3878.814, 3875.226, 3873.890, 3873.592, 3873.206, 3872.345, 3870.714, 3868.282, 3867.689, 3867.062, 3864.898, 3862.228, 3861.870, 3861.009, 3858.577, 3858.101, 3857.002, 3854.778, 3854.718, 3853.592, 3851.334, 3850.711, 3849.555, 3846.557, 3846.024, 3844.571, 3844.333, 3843.978, 3840.474, 3840.149, 3838.487, 3836.169, 3835.549, 3834.835, 3833.026, 3830.651, 3829.050, 3828.665, 3828.604, 3828.487, 3826.973, 3826.437, 3821.543, 3819.998, 3819.851, 3817.566, 3815.697, 3813.261, 3812.906, 3812.344, 3809.553, 3809.020, 3807.714, 3805.309, 3801.808, 3800.860, 3799.285, 3798.930, 3798.160, 3797.446, 3797.386, 3796.763, 3791.687, 3791.393, 3791.332, 3789.523, 3788.307, 3786.110, 3783.768, 3781.838, 3781.212, 3780.502, 3778.988, 3777.296, 3774.509, 3772.013, 3770.472, 3769.879, 3767.949, 3766.911, 3765.042, 3761.983, 3761.333, 3760.442, 3758.569, 3756.881, 3754.151, 3751.538, 3750.499, 3749.581, 3748.392, 3747.444, 3746.081, 3743.290, 3739.756, 3737.531, 3737.471, 3737.293, 3735.722, 3733.883, 3732.667, 3731.210, 3728.630, 3726.788, 3725.069, 3723.733, 3722.396, 3720.409, 3718.748, 3718.688, 3716.939, 3715.217, 3714.296, 3713.435, 3712.872, 3710.112, 3707.710, 3707.381, 3707.204, 3703.405, 3700.350, 3700.082, 3699.104, 3696.494, 3695.660, 3695.187, 3694.976, 3693.522, 3692.397, 3690.705, 3689.874, 3687.291, 3686.015, 3685.750, 3682.099, 3681.506, 3681.151, 3679.754, 3679.546, 3679.071, 3676.729, 3675.777, 3675.245, 3672.394, 3670.079, 3669.784, 3667.885, 3665.332, 3664.709, 3663.878, 3663.553, 3663.346, 3661.178, 3658.535, 3657.409, 3656.193, 3654.827, 3654.294, 3653.135, 3651.205, 3650.495, 3650.374, 3649.098, 3647.497, 3646.874, 3646.251, 3645.627, 3643.641, 3640.820, 3640.167, 3638.241, 3638.000, 3637.142, 3634.382, 3633.578, 3632.660, 3632.127, 3631.236, 3630.877, 3628.355, 3628.087, 3628.000, 3625.062, 3623.906, 3622.600, 3621.293, 3619.987, 3618.030, 3617.702, 3617.554, 3615.417, 3614.261, 3613.283, 3611.977, 3611.173, 3610.164, 3608.386, 3608.061, 3607.200, 3606.191, 3602.510, 3601.324, 3601.320, 3600.670, 3599.217, 3598.208, 3597.850, 3596.811, 3596.573, 3595.475, 3593.635, 3591.736, 3591.113, 3590.342, 3589.126, 3588.681, 3588.296, 3587.910, 3585.415, 3583.160, 3582.480, 3582.477, 3580.905, 3579.304, 3577.730, 3576.664, 3575.445, 3574.380, 3574.229, 3572.239, 3570.936, 3569.867, 3568.236, 3567.851, 3566.665, 3564.822, 3562.625, 3561.737, 3561.053, 3558.856, 3556.631, 3555.740, 3554.966, 3553.308, 3551.616, 3550.430, 3549.687, 3548.173, 3545.978, 3543.191, 3541.647, 3541.201, 3540.076, 3538.116, 3536.364, 3535.979, 3533.989, 3531.885, 3530.367, 3528.796, 3527.047, 3525.533, 3523.098, 3520.783, 3519.892, 3518.706, 3517.309, 3515.262, 3514.703, 3513.899, 3509.832, 3506.894, 3505.323, 3504.077, 3503.544, 3502.268, 3500.874, 3499.685, 3497.253, 3495.561, 3494.522, 3492.888, 3491.732, 3490.278, 3488.941, 3487.786, 3485.441, 3483.303, 3481.910, 3480.694, 3479.179, 3477.401, 3476.094, 3474.697, 3473.391, 3472.382, 3471.106, 3469.950, 3468.764, 3467.042, 3465.173, 3463.361, 3461.729, 3460.041, 3458.228, 3456.239, 3454.312, 3452.470, 3450.095, 3447.904, 3446.122, 3444.162, 3441.700, 3439.177, 3436.477, 3433.361, 3430.099, 3425.375, 3420.450, 3414.990, 3408.494, 3403.540, 3399.948, 3395.851, 3389.825, 3381.932, 3373.417, 3364.901, 3356.117, 3347.926, 3337.333, 3326.560, 3316.559, 3305.639, 3293.443, 3280.831, 3267.179, 3252.224, 3235.812, 3220.292, 3205.633, 3188.837, 3171.240, 3148.450, 3126.578, 3107.082, 3082.037, 3054.408, 3032.954, 3022.152, 3016.929, 3015.030, 3015.000]

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
        # Update voltage based on resistor divider on the schematic
        value *= 67 / 20
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
