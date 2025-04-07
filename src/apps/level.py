from apps.app import BaseApp
import framebuf

from lib.microfont import MicroFont
from single_app_runner import run_app


def get_formatted_acceleration(acceleration):
    acceleration = str(round(acceleration, 2))
    if len(acceleration) < 4:
        acceleration += '           '
    return acceleration

class Level(BaseApp):
    name = "Level"
    def __init__(self, controller):
        super().__init__(controller)

        self.font = MicroFont("fonts/victor_B_32.mfnt", cache_index=True)

        self.fbuf_width = 240
        self.fbuf_height = 240

        self.fbuf_mem = bytearray(self.fbuf_width * self.fbuf_height * 2)
        self.fbuf = framebuf.FrameBuffer(
            self.fbuf_mem,
            self.fbuf_width,
            self.fbuf_height,
            framebuf.RGB565
        )


    async def update(self):
        displays = self.controller.bsp.displays
        display1 = displays[0]
        imu = self.controller.bsp.imu
        font = self.font

        fbuf = self.fbuf
        fbuf.fill(0x0000)
        x,y,z = imu.acceleration
        
        text = "\n".join([
            str(round(x, 2)),
            str(round(y, 2)),
            str(round(z, 2))
        ])

        font.write(
            text,
            fbuf,
            framebuf.RGB565,
            self.fbuf_width,
            self.fbuf_height,
            40,
            40,
            0xFFFF
        )

        display1.blit_buffer(
            self.fbuf_mem,
            0,
            0,
            self.fbuf_width,
            self.fbuf_height,
        )

        
if __name__ == "__main__":
    run_app(Level)
