from apps.app import BaseApp
import framebuf

import micropython

from lib.microfont import MicroFont
from single_app_runner import run_app
from lib.rolling_average import RollingAverage


def get_formatted_acceleration(acceleration):
    acceleration = str(round(acceleration, 2))
    if len(acceleration) < 4:
        acceleration += '           '
    return acceleration

class Level(BaseApp):
    name = "Level"
    def __init__(self, controller):
        super().__init__(controller)

        self.font = MicroFont("fonts/victor_B_32.mfnt", cache_index=True, cache_chars=True)

        self.fbuf_width = 240
        self.fbuf_height = 240

        self.fbuf_mem = bytearray(self.fbuf_width * self.fbuf_height * 2)
        self.fbuf_mv = memoryview(self.fbuf_mem)
        self.fbuf = framebuf.FrameBuffer(
            self.fbuf_mv,
            self.fbuf_width,
            self.fbuf_height,
            framebuf.RGB565
        )

        self.imu_average_x = RollingAverage(1)
        self.imu_average_y = RollingAverage(1)
        self.imu_average_z = RollingAverage(1)

        self.controller.bsp.imu._imu_read_rate_s = 0.01

        self.controller.bsp.imu.imu_callbacks.append(self.imu_callback)
        
        self.last_imu_value = (0, 0, 0)

    async def imu_callback(self, value):
        self.imu_average_x.add(value[0])
        self.imu_average_y.add(value[1])
        self.imu_average_z.add(value[2])

        self.last_imu_value = value

    @micropython.native
    async def update(self):
        displays = self.controller.bsp.displays
        display1 = displays[0]

        x, y, z = self.last_imu_value

        # The x and y values will range from -10 to 10 and we will scale it to 0..240
        x_scaled = int((x + 10) * (240 / 20))
        y_scaled = int((y + 10) * (240 / 20))


        fbuf = self.fbuf
        fbuf.fill(0x0000)
        
        # text = "\n".join([
        #     str(round(x, 2)),
        #     str(round(y, 2)),
        #     str(round(z, 2))
        # ])

        # font.write(
        #     text,
        #     fbuf,
        #     framebuf.RGB565,
        #     self.fbuf_width,
        #     self.fbuf_height,
        #     40,
        #     40,
        #     0xFFFF
        # )

        fbuf.ellipse(
            # Yes, these are intentionally reversed because x/y on the accelerometer 
            # are reversed from the display
            y_scaled,
            x_scaled,
            10,
            10,
            0xFFFF,
            True
        )

        display1.blit_buffer(
            self.fbuf_mv,
            0,
            0,
            self.fbuf_width,
            self.fbuf_height,
        )

        self.last_x = x_scaled
        self.last_y = y_scaled

        
if __name__ == "__main__":
    run_app(Level, perf=True)
